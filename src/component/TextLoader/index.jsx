// 用于用户上传文本或使用上传文档或使用图片OCR功能的入口文件

import React, { useState } from 'react';
import { Upload, Modal, Input, Button } from 'antd';
import { UploadOutlined, PictureOutlined, PlusOutlined } from '@ant-design/icons';
import './TextLoader.css'
const { TextArea } = Input;

const getBase64 = (file) =>
    new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);

        reader.onload = () => resolve(reader.result);

        reader.onerror = (error) => reject(error);
    });

const TextLoader = (props) => {
    const { setTitle, setAbstract } = props

    const [previewVisible, setPreviewVisible] = useState(false);
    const [previewImage, setPreviewImage] = useState('');
    const [previewTitle, setPreviewTitle] = useState('');
    const [fileList, setFileList] = useState([])
    const [picList, setPicList] = useState([])

    const handleCancel = () => setPreviewVisible(false);

    const handlePreview = async (file) => {
        if (!file.url && !file.preview) {
            file.preview = await getBase64(file.originFileObj);
        }

        setPreviewImage(file.url || file.preview);
        setPreviewVisible(true);
        setPreviewTitle(file.name || file.url.substring(file.url.lastIndexOf('/') + 1));
    };

    const handleFileChange = ({ fileList: newFileList }) => setFileList(newFileList);
    const handlePicChange = ({ fileList: newPicList }) => setPicList(newPicList);

    const uploadFileButton = (
        <div>
            <PlusOutlined />
            <div
                style={{
                    marginTop: 8,
                }}
            >
                上传文件
            </div>
        </div>
    );

    const uploadPicButton = (
        <div>
            <PlusOutlined />
            <div
                style={{
                    marginTop: 8,
                }}
            >
                上传图片
            </div>
        </div>
    );

    const upLoadText = () => {
        // 上传文本文档并获取返回值（标题、摘要）
        setTitle("test")
        setAbstract("test1")
    }

    const OCR = () => {

    }

    const uploadFile = () => {

    }

    return (
        <>
            <div>
                <div style={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    marginBottom: '.7em'
                }}>
                    <Upload
                        action=""
                        listType="picture-card"
                        fileList={fileList}
                        onPreview={handlePreview}
                        onChange={handleFileChange}
                        accept=".doc,.docx,.txt"
                    >
                        {(fileList.length >= 1 || picList.length) ? null : uploadFileButton}
                    </Upload>
                    <Upload
                        action="https://www.mocky.io/v2/5cc8019d300000980a055e76"
                        listType="picture-card"
                        multiple='true'
                        fileList={picList}
                        onPreview={handlePreview}
                        onChange={handlePicChange}
                        accept=".png,.jpg,.jpeg,.bmp"
                    >
                        {(picList.length >= 5 || fileList.length) ? null : uploadPicButton}
                    </Upload>
                </div>
                <div>
                    <Modal visible={previewVisible} title={previewTitle} footer={null} onCancel={handleCancel}>
                        <img
                            alt="example"
                            style={{
                                width: '100%',
                            }}
                            src={previewImage}
                        />
                    </Modal>
                </div>
            </div>

            <TextArea
                showCount
                maxLength={10000}
                style={{
                    height: '70%',
                    width: '80%',
                    margin: '0 auto'
                }}
            />
            <div>
                <Button style={{ marginTop: '.7em' }} onClick={upLoadText} type="primary">自动生成</Button>
            </div>
        </ >
    );
};

export default TextLoader;