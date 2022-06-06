// 扩展头像功能，悬浮提醒，点击登录

import React, { useState } from 'react';
import { Avatar, Popover, Modal, Button, Input, message } from 'antd';
import { UserOutlined } from '@ant-design/icons';

const MyAvatar = () => {
    const loginPopover = (
        <div>
            <p>登录后可保存生成记录</p>
            <p>点击立即登录</p>
        </div>
    );

    const [visible, setVisible] = useState(false);
    const [confirmLoading, setConfirmLoading] = useState(false);
    const [userName, setUserName] = useState("");
    const [password, setPassword] = useState("");

    const showModal = () => {
        setVisible(true);
    };

    const handleOk = () => {
        setConfirmLoading(true);
        // 提交登录信息，判断是否登录成功，若成功调用下面函数
        setTimeout(() => {
            setVisible(false);
            setConfirmLoading(false);
        }, 2000);
        // 如果登录信息错误，调用下面方法
        message.error('登录错误 请检查账号或密码！');
    };

    const handleCancel = () => {
        console.log('Clicked cancel button');
        setPassword("");
        setUserName("");
        setVisible(false);
    };

    const handleRegist = () => {
        // 跳转注册页面，可用路由
    }

    return (
        <>
            {/* 条件判断是否登录，若未登录则包裹popover，若已登录则不需要包裹并且头像图片显示用户头像 */}
            <Popover content={loginPopover} trigger="hover" onClick={showModal}>
                <Avatar
                    style={{
                        backgroundColor: '#87d068',
                        cursor: "pointer"
                    }}
                    size={40}
                    icon={<UserOutlined />} />
            </Popover>
            <Modal
                title="登录账号"
                visible={visible}
                onOk={handleOk}
                onCancel={handleCancel}
                footer={[
                    <Button key="back" onClick={handleCancel} style={{ marginRight: '3em' }}>
                        取消
                    </Button>,
                    <Button
                        key="link"
                        type="primary"
                        onClick={handleRegist}
                    >
                        去注册
                    </Button>,
                    <Button key="submit" type="primary" loading={confirmLoading} onClick={handleOk}>
                        登录
                    </Button>
                ]}
            >
                {/* <p>{modalText}</p> */}
                <Input addonBefore={<span style={{ display: 'inline-block', width: '50px' }}>用户名：</span>}
                    style={{ minWidth: 200, width: '100% - 40px' }}
                    placeholder="请输入用户名"
                    value={userName}
                    onChange={(e) => setUserName(e.target.value)} />
                <br></br>
                <br></br>
                <Input.Password addonBefore={<span style={{ display: 'inline-block', width: '50px' }}>密码：</span>}
                    style={{ minWidth: 200 }}
                    placeholder="请输入密码"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)} />
            </Modal>
        </>
    );
};

export default MyAvatar;