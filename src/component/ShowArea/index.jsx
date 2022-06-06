// 用于展示自动生成的标题和摘要的文件

import React from 'react';
import { Input, Divider } from 'antd';

const ShowArea = (props) => {
    const {title, abstract} = props
    return (
        <>
            <Input addonBefore="文章标题：" value={title} placeholder="这里是自动生成的文章标题" disabled='false' />
            <Divider />
            <Input addonBefore="文章摘要：" value={abstract} placeholder="这里是自动生成的文章摘要" disabled='false' />
        </>
    );
};

export default ShowArea;