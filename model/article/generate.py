#coding=utf-8
import os
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICE"] = '0'
import torch
from transformers.models.gpt2.modeling_gpt2 import GPT2LMHeadModel
from transformers import BertTokenizer
import torch.nn.functional as F
from harvesttext import HarvestText

class Options:
    def __init__(
        self, model_path="./model/", 
        vocab_path="./model/vocab.txt",
        model_input_max_len=1024,
        repetition_penalty=1.2,
        top_k=5,
        top_p=0.95,
        title_max_len=42,
        abstract_sentences_num=10
    ) -> None:
        self.model_path = model_path
        self.vocab_path = vocab_path
        self.model_input_max_len = model_input_max_len
        self.repetition_penalty = repetition_penalty
        self.top_k = top_k
        self.top_p = top_p
        self.title_max_len = title_max_len
        self.abstract_sentences_num = abstract_sentences_num


class Generate:
    def __init__(self, options:Options) -> None:
        self.options = options
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = BertTokenizer.from_pretrained(options.vocab_path, do_lower_case=True)
        self.model = GPT2LMHeadModel.from_pretrained(options.model_path)
        self.model.to(self.device)
        self.ht = HarvestText()
    
    def get_title_and_abstract(self, article:str):
        sentences = self.ht.cut_sentences(article)
        sentences_num = len(sentences)
        top_k_sents = self.ht.get_summary(sentences, topK=min(25, sentences_num), maxlen=(self.options.model_input_max_len - 3 - self.options.title_max_len))
        article = ''.join(top_k_sents)
        abstract = self.ht.get_summary(sentences, topK=min(self.options.abstract_sentences_num, sentences_num), maxlen=512, avoid_repeat=True)
        abstract = ''.join(abstract)
        self.model.eval()
        title = self.predict_title(self.model, self.tokenizer, self.device, self.options, article)
        return {'title':title, 'abstract':abstract}
    
    def predict_title(self, model, tokenizer, device, options:Options, article):
        """
        对单个样本进行预测
        Args:
            model: 模型
            tokenizer: 分词器
            device: 设备信息
            args: 配置项信息
            article: 新闻正文

        Returns:

        """
        # 对新闻正文进行预处理，并判断如果超长则进行截断
        content_tokens = tokenizer.tokenize(article)
        if len(content_tokens) > options.model_input_max_len - 3 - options.title_max_len:
            content_tokens = content_tokens[:options.model_input_max_len - 3 - options.title_max_len]
        
        # 获取content_id、title_id、unk_id、sep_id值
        content_id = tokenizer.convert_tokens_to_ids("[Content]")
        title_id = tokenizer.convert_tokens_to_ids("[Title]")
        unk_id = tokenizer.convert_tokens_to_ids("[UNK]")
        sep_id = tokenizer.convert_tokens_to_ids("[SEP]")
        # 将tokens索引化，变成模型所需格式
        content_tokens = ["[CLS]"] + content_tokens + ["[SEP]"]
        input_ids = tokenizer.convert_tokens_to_ids(content_tokens)
        # 将input_ids和token_type_ids进行扩充，扩充到需要预测标题的个数，即batch_size
        input_ids = [input_ids]
        token_type_ids = [[content_id] * len(content_tokens)]
        # 将input_ids和token_type_ids变成tensor
        input_tensors = torch.tensor(input_ids).long().to(device)
        token_type_tensors = torch.tensor(token_type_ids).long().to(device)
        next_token_type = torch.tensor([[title_id]]).long().to(device)

        # 用于存放每一步解码的结果
        generated = []
        # 用于存放，完成解码序列的序号
        with torch.no_grad():
            # 遍历生成标题最大长度
            for _ in range(options.title_max_len):
                outputs = model(input_ids=input_tensors,
                                token_type_ids=token_type_tensors)
                # 获取预测结果序列的最后一个标记，next_token_logits size：[batch_size, vocab_size]
                next_token_logits = outputs[0][:, -1, :]
                # 对batch_size进行遍历，将词表中出现在序列中的词的概率进行惩罚
                for token_id in set([token_ids[0] for token_ids in generated]):
                    next_token_logits[0][token_id] /= options.repetition_penalty
                # 对batch_size进行遍历，将词表中的UNK的值设为无穷小
                for next_token_logit in next_token_logits:
                    next_token_logit[unk_id] = -float("Inf")
                # 使用top_k_top_p_filtering函数，按照top_k和top_p的值，对预测结果进行筛选
                filter_logits = self.top_k_top_p_filtering(next_token_logits, top_k=options.top_k, top_p=options.top_p)
                # 对filter_logits的每一行做一次取值，输出结果是每一次取值时filter_logits对应行的下标，即词表位置（词的id）
                # filter_logits中的越大的值，越容易被选中
                next_tokens = torch.multinomial(F.softmax(filter_logits, dim=-1), num_samples=1)
                # 判断如果哪个序列的预测标记为sep_id时，则加入到finish_set
                for index, token_id in enumerate(next_tokens[:, 0]):
                    if token_id == sep_id:
                        break
                generated.append([token.item() for token in next_tokens[:, 0]])
                # 将预测结果拼接到input_tensors和token_type_tensors上，继续下一次预测
                input_tensors = torch.cat((input_tensors, next_tokens), dim=-1)
                token_type_tensors = torch.cat((token_type_tensors, next_token_type), dim=-1)
            
            # 用于存储预测结果
            # 对batch_size进行遍历，并将token_id变成对应汉字
            responses = []
            for token_index in range(len(generated)):
                # 判断，当出现sep_id时，停止在该序列中添加token
                if generated[token_index][index] != sep_id:
                    responses.append(generated[token_index][index])
                else:
                    break
                # 将token_id序列变成汉字序列，去除"##"，并将[Space]替换成空格
            title = "".join(tokenizer.convert_ids_to_tokens(responses)).replace("##", "").replace("[space]", " ")
        return title

    def top_k_top_p_filtering(self, logits, top_k, top_p, filter_value=-float("Inf")):
        """
        top_k或top_p解码策略，仅保留top_k个或累积概率到达top_p的标记，其他标记设为filter_value，后续在选取标记的过程中会取不到值设为无穷小。
        Args:
            logits: 预测结果，即预测成为词典中每个词的分数
            top_k: 只保留概率最高的top_k个标记
            top_p: 只保留概率累积达到top_p的标记
            filter_value: 过滤标记值

        Returns:

        """
        # logits的维度必须为2，即size:[batch_size, vocab_size]
        assert logits.dim() == 2
        # 获取top_k和字典大小中较小的一个，也就是说，如果top_k大于字典大小，则取字典大小个标记
        top_k = min(top_k, logits[0].size(-1))
        # 如果top_k不为0，则将在logits中保留top_k个标记
        if top_k > 0:
            # 由于有batch_size个预测结果，因此对其遍历，选取每个预测结果的top_k标记
            for logit in logits:
                indices_to_remove = logit < torch.topk(logit, top_k)[
                    0][..., -1, None]
                logit[indices_to_remove] = filter_value
        # 如果top_p不为0，则将在logits中保留概率值累积达到top_p的标记
        if top_p > 0.0:
            # 对logits进行递减排序
            sorted_logits, sorted_indices = torch.sort(
                logits, descending=True, dim=-1)
            # 对排序后的结果使用softmax归一化，再获取累积概率序列
            # 例如：原始序列[0.1, 0.2, 0.3, 0.4]，则变为：[0.1, 0.3, 0.6, 1.0]
            cumulative_probs = torch.cumsum(
                F.softmax(sorted_logits, dim=-1), dim=-1)
            # 删除累积概率高于top_p的标记
            sorted_indices_to_remove = cumulative_probs > top_p
            # 将索引向右移动，使第一个标记也保持在top_p之上
            sorted_indices_to_remove[...,
                                    1:] = sorted_indices_to_remove[..., :-1].clone()
            sorted_indices_to_remove[..., 0] = 0
            for index, logit in enumerate(logits):
                # 由于有batch_size个预测结果，因此对其遍历，选取每个预测结果的累积概率达到top_p的标记
                indices_to_remove = sorted_indices[index][sorted_indices_to_remove[index]]
                logit[indices_to_remove] = filter_value
        return logits
        
# 获取设备信息
# options = Options()
# generate = Generate(options=options)
# article = "最近，一个“年终奖”版的《黄河大合唱》视频流传在网络上。历史不是一个什么都可以装的“空袋子”，承载着历史记忆和民族情感的文艺作品，同样不是什么都可装的“空袋子”、想怎么改就怎么改的“草稿纸”。《黄河大合唱》中所歌唱的，是八路军东渡黄河、饮马太行抗击日寇的坚定决心，是全民族觉醒、同日寇抗战到底的不屈精神，说它是“民族之魂”“不朽之作”毫不夸张。《汉书·艺文志》中就提到了“哗众取宠”的问题，以浮夸的言行迎合观众，借此骗取信赖和支持，说白了就是一种对观众的欺骗。“不懂自己出生前历史的人，永远是个孩子。”娱乐有娱乐的底线，严肃有严肃的必要，调侃经典作品、愚弄历史记忆，既超出了娱乐的边界也亵渎了艺术的神圣，根本无法传递会心的笑声。之所以说恶搞经典作品危害甚深，不仅因为恶搞本身的解构负能量很大，也在于“集体无意识”的破坏力量不容小觑。正因为解构和恶搞经典来得容易，博得的笑声也很廉价，所以表演形式容易被更多人模仿。有记者发现，恶搞《黄河大合唱》不仅堂而皇之出现在某些公司年会上，还出现在幼儿园、中学、大学等教育机构的晚会上，甚至登上了电视荧幕。以无所谓的态度恶搞和篡改经典作品，会在温水煮青蛙中撕毁本应坚守和捍卫的道义底线、价值认同，从而拉低人们的审美品位，混淆正常的社会认知。对我们每个人而言，同样需要保持对历史冷漠病和虚无症等和平积习的警惕。以恶搞经典作品的形式取乐观众，既不是传承经典，也绝非艺术再创作。历史里不仅有先辈的奋斗，更维系着我辈的过去和未来；经典作品承载着的不仅是艺术创作的高峰，更有民族的兴衰和荣辱。尊重历史、尊重经典，其实就是对自己的尊重，对未来的尊重。为图搞笑而篡改这一反映民族救亡之声的代表作，显然是一种对历史的亵渎、对民族精神的挥霍，与浑浑噩噩的“蓬间雀”何异？低俗的歌词、夸张的表演，大多数观众看后不仅没有发出笑声甚至想“咆哮”：“怎么能这样糟蹋我们的经典歌曲！”生活的确需要逗笑和欢笑，但一种表演能否达到逗笑别人的效果，靠的是实实在在的功力和水平。调侃经典作品、愚弄历史记忆，既超出了娱乐的边界，也亵渎了艺术的神圣伴着《黄河大合唱》的旋律，一群人一边吼着“年终奖，年终奖，我们在嚎叫，我们在嚎叫”，一边摇头晃脑故作癫狂，时而瞪大眼时而张大嘴，时而扭动屁股乱舞手臂……对待先辈们燃烧生命谱写的历史，抱持温情与敬意是最起码的要求。"
# print(generate.get_title_and_abstract(article=article))