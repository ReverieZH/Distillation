import React, { useState } from 'react';
import { Layout } from 'antd';
import TextLoader from './component/TextLoader'
import ShowArea from './component/ShowArea';
import MyAvatar from './component/MyAvatar';


const { Header, Content, Footer } = Layout;

const App = () => {

  const [title, setTitle] = useState('')
  const [abstract, setAbstract] = useState('')

  return (
    <Layout
      style={{
        height: '100%'
      }}
    >
      <Header
        style={{
          position: 'fixed',
          zIndex: 1,
          width: '100%',
        }}
      >
        <div style={{ float: 'right' }}>
          <MyAvatar></MyAvatar>
        </div>
      </Header>
      <Content
        className="site-layout"
        style={{
          padding: '0 50px',
          marginTop: 64,
        }}
      >
        <div
          className="site-layout-background"
          style={{
            margin: '16px 0',
            padding: 24,
            // minHeight: 380,
            height: '100%',
          }}
        >
          <div style={{
            height: '20%',
            width: '70%',
            margin: '0 auto',
          }}>
            <ShowArea title={title} abstract={abstract}></ShowArea>
          </div>
          <div style={{
            height: '75%',
            width: '70%',
            margin: '0 auto',
            paddingTop: '1.2em',
            borderRadius: '0.75em',
            boxShadow: '0px 5px 16px -2px rgb(42 115 217 / 20%)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
          }}>
            <TextLoader setTitle={setTitle} setAbstract={setAbstract}></TextLoader>
          </div>
        </div>
      </Content>
      <Footer
        style={{
          textAlign: 'center',
        }}
      >
        Distillation ©2022 Created by Truly Bai
      </Footer>
    </Layout>
  )
};

export default App;