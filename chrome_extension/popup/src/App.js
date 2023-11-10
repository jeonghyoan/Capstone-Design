/* global chrome */
import React, {useEffect, useState} from 'react';
import styled from 'styled-components';
import ClipLoader from 'react-spinners/ClipLoader';
import {BsFillEmojiLaughingFill, BsEmojiFrownFill, BsEmojiDizzyFill} from 'react-icons/bs'

function App() {
  const [loading, setLoading] = useState(true);
  const [Result, setResult] = useState("");

  // Send the data of the current tab's link, and get result
  useEffect(()=>{
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      var tab = tabs[0]; //currently activated tab
      //send request and data
      fetch('http://127.0.0.1:5000/classify', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ link: tab.url }),
      })
      //get result
      .then(response => response.json())
      .then(data => {
          let result = data.result;
          console.log(result);
          setResult(result);
          setLoading(false);
      })
      .catch(console.error);
  });
 
  },[])

  //Rendering UI of chrome extension according to result got above
  const renderResult = () => {
    if (Result === -1) {
        return (
        <ContentLayout>
           <BsEmojiDizzyFill style={{marginTop: '30px', marginBottom: '10px', color: '#8E8E8E'}} size={80}/>
            <p className='content'>Sorry!</p>
            <p className='content'>It seems invalid link</p>
        </ContentLayout>
        );
    } else if (Result === 0) {
        return (
        <ContentLayout>
          <BsFillEmojiLaughingFill style={{marginTop: '30px', marginBottom: '10px', color: '#40924D'}} size={80}/>
            <p className='content'>Wow!</p>
            <p className='content'>It`s regarded as genuine review!</p>
            <p className='content'>Enjoy your web-surfing!</p>
        </ContentLayout>
        );
    } else if (Result === 1) {
        return (
        <ContentLayout>
          <BsEmojiFrownFill style={{marginTop: '30px', marginBottom: '10px', color: '#DB4848'}}  size={80}/>
            <p className='content'>Oops!</p>
            <p className='content'>This post is regarded as Ad!</p>
            <p className='content'>Be careful while reading.</p>
    
        </ContentLayout>
          );
    }
  }
  
  //Rendering UI of Idle state
  return (
   <PopupLayout>
      <Header>
          <p className='title'>Blog Post Classifier</p>
      </Header>
      {loading? (
        <ContentLayout>
          <ClipLoader className='spinner' loading={loading} size={80}/>
          <p className='content'>Analyzing...</p>
        </ContentLayout>
      ):
        renderResult()
      }
   </PopupLayout>
  );
}

export default App;

const PopupLayout = styled.div`
  width: 300px;
  height: 300px;
  display: flex;
  flex-direction: column;
  background: #D9D9D9;
`
const Header = styled.div`
  width: 300px;
  height: 60px;
  background: #6F0395;
  
  .title{
    color: #FFF;
    font-family: Noto Sans;
    font-size: 18px;
    font-style: normal;
    font-weight: 400;
    line-height: normal;
    margin-left: 15px;
  }
`
const ContentLayout = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;

  .spinner{
    color:#8E8E8E;
    margin-top: 45px;
  }
  
  .content{
    color: #000;
    font-family: Noto Sans;
    font-size: 18px;
    font-style: normal;
    font-weight: 500;
    line-height: normal;
    margin: 0.1rem;
  }

`