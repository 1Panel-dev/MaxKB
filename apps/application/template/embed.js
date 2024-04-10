const guideHtml=`
<div class="maxkb-mask">
  <div class="maxkb-content"></div>
</div>
<div class="maxkb-tips">
  <div class="maxkb-close">
      <svg style="vertical-align: middle;overflow: hidden;" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M9.95317 8.73169L15.5511 3.13376C15.7138 2.97104 15.9776 2.97104 16.1403 3.13376L16.7296 3.72301C16.8923 3.88573 16.8923 4.14955 16.7296 4.31227L11.1317 9.9102L16.7296 15.5081C16.8923 15.6708 16.8923 15.9347 16.7296 16.0974L16.1403 16.6866C15.9776 16.8494 15.7138 16.8494 15.5511 16.6866L9.95317 11.0887L4.35524 16.6866C4.19252 16.8494 3.9287 16.8494 3.76598 16.6866L3.17673 16.0974C3.01401 15.9347 3.01401 15.6708 3.17673 15.5081L8.77465 9.9102L3.17673 4.31227C3.01401 4.14955 3.01401 3.88573 3.17673 3.72301L3.76598 3.13376C3.9287 2.97104 4.19252 2.97104 4.35524 3.13376L9.95317 8.73169Z" fill="#ffffff"></path>
          </svg>
  </div>
 
  <div class="maxkb-title"> 🌟 遇见问题，不再有障碍！</div>
  <p>你好，我是你的智能小助手。<br/>
      点我，开启高效解答模式，让问题变成过去式。</p>
  <div class="maxkb-button">
      <button>我知道了</button>
  </div>
  <span class="maxkb-arrow" ></span>
</div>
`
const chatButtonHtml=
`<div class="maxkb-chat-button" ><svg style="vertical-align: middle;overflow: hidden;" width="48" height="56" viewBox="0 0 48 56" fill="none" xmlns="http://www.w3.org/2000/svg">
<g filter="url(#filter0_d_349_49711)">
<path d="M8 24C8 12.9543 16.9543 4 28 4H48V44H28C16.9543 44 8 35.0457 8 24Z" fill="url(#paint0_linear_349_49711)"/>
</g>
<path d="M31.2632 30.2754H28.1992L27.0636 31.411C26.9971 31.4775 26.9518 31.5623 26.9335 31.6546C26.9151 31.7468 26.9245 31.8425 26.9605 31.9294C26.9965 32.0163 27.0575 32.0906 27.1357 32.1429C27.2139 32.1951 27.3059 32.223 27.4 32.223H32.0625C32.1566 32.223 32.2486 32.1951 32.3268 32.1429C32.405 32.0906 32.466 32.0163 32.502 31.9294C32.538 31.8425 32.5474 31.7468 32.529 31.6546C32.5107 31.5623 32.4654 31.4775 32.3989 31.411L31.2632 30.2754Z" fill="white"/>
<path d="M39.6831 21.3652H39.0791V25.6142H39.6831C39.8051 25.6142 39.9221 25.5657 40.0083 25.4795C40.0945 25.3932 40.143 25.2763 40.143 25.1543V21.8251C40.143 21.7031 40.0945 21.5862 40.0083 21.4999C39.9221 21.4137 39.8051 21.3652 39.6831 21.3652Z" fill="white"/>
<path d="M20.9208 21.3652H20.3168C20.1948 21.3652 20.0779 21.4137 19.9916 21.4999C19.9054 21.5862 19.8569 21.7031 19.8569 21.8251V25.1543C19.8569 25.2763 19.9054 25.3932 19.9916 25.4795C20.0779 25.5657 20.1948 25.6142 20.3168 25.6142H20.9208V21.3652Z" fill="white"/>
<path d="M32.3323 21.9277C32.1041 21.9277 31.8854 22.0184 31.7241 22.1796C31.5628 22.3409 31.4722 22.5597 31.4722 22.7878V23.4045C31.4722 23.6326 31.5628 23.8514 31.7241 24.0127C31.8854 24.174 32.1042 24.2646 32.3323 24.2646C32.5604 24.2646 32.7792 24.174 32.9405 24.0127C33.1018 23.8514 33.1924 23.6326 33.1924 23.4045V22.7878C33.1924 22.6749 33.1702 22.563 33.1269 22.4587C33.0837 22.3543 33.0204 22.2595 32.9405 22.1796C32.8606 22.0998 32.7658 22.0364 32.6614 21.9932C32.5571 21.95 32.4452 21.9277 32.3323 21.9277Z" fill="white"/>
<path d="M27.8464 21.9277C27.6183 21.9277 27.3995 22.0184 27.2382 22.1796C27.0769 22.3409 26.9863 22.5597 26.9863 22.7878V23.4045C26.9863 23.6326 27.0769 23.8514 27.2383 24.0127C27.3996 24.174 27.6183 24.2646 27.8465 24.2646C28.0746 24.2646 28.2933 24.174 28.4547 24.0127C28.616 23.8514 28.7066 23.6326 28.7066 23.4045V22.7878C28.7066 22.6749 28.6843 22.563 28.6411 22.4587C28.5979 22.3543 28.5345 22.2595 28.4546 22.1796C28.3748 22.0998 28.2799 22.0364 28.1756 21.9932C28.0712 21.95 27.9594 21.9277 27.8464 21.9277Z" fill="white"/>
<path d="M35.2258 17.0488H24.7738C23.8508 17.0499 22.9659 17.417 22.3133 18.0696C21.6606 18.7223 21.2935 19.6071 21.2925 20.5301V26.4227C21.2935 27.3457 21.6606 28.2306 22.3133 28.8832C22.9659 29.5359 23.8508 29.903 24.7738 29.904H35.2258C36.1488 29.903 37.0336 29.5359 37.6863 28.8832C38.3389 28.2306 38.7061 27.3457 38.7071 26.4227V20.5301C38.7061 19.6071 38.3389 18.7223 37.6863 18.0696C37.0336 17.417 36.1488 17.0499 35.2258 17.0488ZM35.5181 26.3875C35.5181 26.5538 35.452 26.7133 35.3344 26.8309C35.2168 26.9485 35.0573 27.0146 34.891 27.0146H29.7929C29.0215 27.0146 28.2631 27.2129 27.5904 27.5903L25.8801 28.55V27.0146H25.1086C24.9422 27.0146 24.7827 26.9486 24.6651 26.831C24.5475 26.7134 24.4815 26.5539 24.4815 26.3876V20.1408C24.4815 19.9745 24.5475 19.815 24.6651 19.6974C24.7827 19.5798 24.9422 19.5137 25.1086 19.5137H34.891C35.0573 19.5137 35.2168 19.5798 35.3344 19.6974C35.452 19.815 35.5181 19.9745 35.5181 20.1408V26.3875Z" fill="white"/>
<defs>
<filter id="filter0_d_349_49711" x="0" y="0" width="56" height="56" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
<feFlood flood-opacity="0" result="BackgroundImageFix"/>
<feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
<feOffset dy="4"/>
<feGaussianBlur stdDeviation="4"/>
<feComposite in2="hardAlpha" operator="out"/>
<feColorMatrix type="matrix" values="0 0 0 0 0.168627 0 0 0 0 0.372549 0 0 0 0 0.85098 0 0 0 0.24 0"/>
<feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_349_49711"/>
<feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_349_49711" result="shape"/>
</filter>
<linearGradient id="paint0_linear_349_49711" x1="48" y1="25.6667" x2="8" y2="25.6667" gradientUnits="userSpaceOnUse">
<stop stop-color="#9258F7"/>
<stop offset="1" stop-color="#3370FF"/>
</linearGradient>
</defs>
</svg>

</div>`

 

const getChatContainerHtml=(protocol,host,token)=>{
 return `<div id="maxkb-chat-container">
<iframe id="maxkb-chat" src=${protocol}://${host}/ui/chat/${token}></iframe>
<div class="maxkb-operate"><div class="maxkb-closeviewport maxkb-viewportnone"><svg style="vertical-align: middle;overflow: hidden;" t="1710214539671"  viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg"  fill="rgb(100, 106, 115)" width="16" height="16"><path d="M85.333333 384c25.6 0 42.666667-17.066667 42.666667-42.666667V128h213.333333c25.6 0 42.666667-17.066667 42.666667-42.666667s-17.066667-42.666667-42.666667-42.666666H85.333333c-25.6 0-42.666667 17.066667-42.666666 42.666666v256c0 25.6 17.066667 42.666667 42.666666 42.666667zM938.666667 640c-25.6 0-42.666667 17.066667-42.666667 42.666667v213.333333h-213.333333c-25.6 0-42.666667 17.066667-42.666667 42.666667s17.066667 42.666667 42.666667 42.666666h256c25.6 0 42.666667-17.066667 42.666666-42.666666v-256c0-25.6-17.066667-42.666667-42.666666-42.666667zM601.6 401.066667c4.266667 8.533333 12.8 17.066667 21.333333 21.333333 4.266667 4.266667 12.8 4.266667 17.066667 4.266667h256c25.6 0 42.666667-17.066667 42.666667-42.666667s-17.066667-42.666667-42.666667-42.666667h-153.6l226.133333-226.133333c17.066667-17.066667 17.066667-42.666667 0-59.733333-8.533333-8.533333-17.066667-12.8-29.866666-12.8s-21.333333 4.266667-29.866667 12.8L682.666667 281.6V128c0-25.6-17.066667-42.666667-42.666667-42.666667s-42.666667 17.066667-42.666667 42.666667v256c0 4.266667 0 12.8 4.266667 17.066667zM115.2 968.533333L341.333333 742.4V896c0 25.6 17.066667 42.666667 42.666667 42.666667s42.666667-17.066667 42.666667-42.666667v-256c0-4.266667 0-12.8-4.266667-17.066667-4.266667-8.533333-12.8-17.066667-21.333333-21.333333-4.266667-4.266667-12.8-4.266667-17.066667-4.266667H128c-25.6 0-42.666667 17.066667-42.666667 42.666667s17.066667 42.666667 42.666667 42.666667h153.6l-226.133333 226.133333c-17.066667 17.066667-17.066667 42.666667 0 59.733333s42.666667 17.066667 59.733333 0z" p-id="10189"></path></svg></div>
<div class="maxkb-openviewport">
            <svg t="1710150885892"  style="vertical-align: middle;overflow: hidden;" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg"  fill="rgb(100, 106, 115)" width="16" height="16" ><path d="M85.333333 384c25.6 0 42.666667-17.066667 42.666667-42.666667V128h213.333333c25.6 0 42.666667-17.066667 42.666667-42.666667s-17.066667-42.666667-42.666667-42.666666H85.333333c-25.6 0-42.666667 17.066667-42.666666 42.666666v256c0 25.6 17.066667 42.666667 42.666666 42.666667zM938.666667 640c-25.6 0-42.666667 17.066667-42.666667 42.666667v213.333333h-213.333333c-25.6 0-42.666667 17.066667-42.666667 42.666667s17.066667 42.666667 42.666667 42.666666h256c25.6 0 42.666667-17.066667 42.666666-42.666666v-256c0-25.6-17.066667-42.666667-42.666666-42.666667zM977.066667 68.266667c-4.266667-8.533333-12.8-17.066667-21.333334-21.333334-4.266667-4.266667-12.8-4.266667-17.066666-4.266666h-256c-25.6 0-42.666667 17.066667-42.666667 42.666666s17.066667 42.666667 42.666667 42.666667h153.6l-226.133334 226.133333c-17.066667 17.066667-17.066667 42.666667 0 59.733334 8.533333 8.533333 17.066667 12.8 29.866667 12.8s21.333333-4.266667 29.866667-12.8L896 187.733333V341.333333c0 25.6 17.066667 42.666667 42.666667 42.666667s42.666667-17.066667 42.666666-42.666667V85.333333c0-4.266667 0-12.8-4.266666-17.066666zM354.133333 610.133333L128 836.266667V682.666667c0-25.6-17.066667-42.666667-42.666667-42.666667s-42.666667 17.066667-42.666666 42.666667v256c0 4.266667 0 12.8 4.266666 17.066666 4.266667 8.533333 12.8 17.066667 21.333334 21.333334 4.266667 4.266667 12.8 4.266667 17.066666 4.266666h256c25.6 0 42.666667-17.066667 42.666667-42.666666s-17.066667-42.666667-42.666667-42.666667H187.733333l226.133334-226.133333c17.066667-17.066667 17.066667-42.666667 0-59.733334s-42.666667-17.066667-59.733334 0z" p-id="8645"></path></svg>
</div>
           <div class="maxkb-chat-close"><svg style="vertical-align: middle;overflow: hidden;" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M9.95317 8.73169L15.5511 3.13376C15.7138 2.97104 15.9776 2.97104 16.1403 3.13376L16.7296 3.72301C16.8923 3.88573 16.8923 4.14955 16.7296 4.31227L11.1317 9.9102L16.7296 15.5081C16.8923 15.6708 16.8923 15.9347 16.7296 16.0974L16.1403 16.6866C15.9776 16.8494 15.7138 16.8494 15.5511 16.6866L9.95317 11.0887L4.35524 16.6866C4.19252 16.8494 3.9287 16.8494 3.76598 16.6866L3.17673 16.0974C3.01401 15.9347 3.01401 15.6708 3.17673 15.5081L8.77465 9.9102L3.17673 4.31227C3.01401 4.14955 3.01401 3.88573 3.17673 3.72301L3.76598 3.13376C3.9287 2.97104 4.19252 2.97104 4.35524 3.13376L9.95317 8.73169Z" fill="#646A73"/>
  </svg>
 </div></div>
`
}
/**
 * 初始化引导
 * @param {*} root  
 */
const initGuide=(root)=>{
   root.insertAdjacentHTML("beforeend",guideHtml)
   const button=root.querySelector(".maxkb-button")
   const close_icon=root.querySelector('.maxkb-close')
   const close_func=()=>{
     root.removeChild(root.querySelector('.maxkb-tips'))
     root.removeChild(root.querySelector('.maxkb-mask'))
     localStorage.setItem('maxkbMaskTip',true)
   }
   button.onclick=close_func
   close_icon.onclick=close_func
}
const initChat=(root)=>{
  // 添加对话icon
  root.insertAdjacentHTML("beforeend",chatButtonHtml)
  // 添加对话框
  root.insertAdjacentHTML('beforeend',getChatContainerHtml('{{protocol}}','{{host}}','{{token}}'))
  // 按钮元素
  const chat_button=root.querySelector('.maxkb-chat-button')
  //  对话框元素
  const chat_container=root.querySelector('#maxkb-chat-container')

  const viewport=root.querySelector('.maxkb-openviewport')
  const closeviewport=root.querySelector('.maxkb-closeviewport')
  const close_func=()=>{
    chat_container.style['display']=chat_container.style['display']=='block'?'none':'block'
  }
  close_icon=chat_container.querySelector('.maxkb-chat-close')
  chat_button.onclick = close_func
  close_icon.onclick=close_func
  const viewport_func=()=>{
    if(chat_container.classList.contains('maxkb-enlarge')){
      chat_container.classList.remove("maxkb-enlarge");
      viewport.classList.remove('maxkb-viewportnone')
      closeviewport.classList.add('maxkb-viewportnone')
    }else{
      chat_container.classList.add("maxkb-enlarge");
      viewport.classList.add('maxkb-viewportnone')
      closeviewport.classList.remove('maxkb-viewportnone')
    }
  }
  viewport.onclick=viewport_func
  closeviewport.onclick=viewport_func
}
/**
 * 第一次进来的引导提示
 */
function initMaxkb(){
  const maxkb=document.createElement('div')
  const root=document.createElement('div')
  root.id="maxkb"
  initMaxkbStyle(maxkb)
  maxkb.appendChild(root)
  document.body.appendChild(maxkb)
  const maxkbMaskTip=localStorage.getItem('maxkbMaskTip')
  if(maxkbMaskTip==null){
    initGuide(root)
  }
  initChat(root)
}

 
// 初始化全局样式
function initMaxkbStyle(root){
  style=document.createElement('style')
  style.type='text/css'
  style.innerText=  `
  /* 放大 */
  #maxkb .maxkb-enlarge {
      width: 50%!important;
      height: 100%!important;
      bottom: 0!important;
      right: 0 !important;
  }
  @media only screen and (max-width: 768px){
  #maxkb .maxkb-enlarge {
      width: 100%!important;
      height: 100%!important;
      right: 0 !important;
      bottom: 0!important;
  }
  }
  
  /* 引导 */
  
  #maxkb .maxkb-mask {
      position: fixed;
      z-index: 999;
      background-color: transparent;
      height: 100%;
      width: 100%;
      top: 0;
      left: 0;
  }
  #maxkb .maxkb-mask .maxkb-content {
      width: 45px;
      height: 48px;
      box-shadow: 1px 1px 1px 2000px rgba(0,0,0,.6);
      border-radius: 50% 0 0 50%;
      position: absolute;
      right: 0;
      bottom: 38px;
      z-index: 1000;
  }
  #maxkb .maxkb-tips {
      position: fixed;
      bottom: 30px;
      right: 60px;
      padding: 22px 24px 24px;
      border-radius: 6px;
      color: #ffffff;
      font-size: 14px;
      background: #3370FF;
      z-index: 1000;
  }
  #maxkb .maxkb-tips .maxkb-arrow {
      position: absolute;
      background: #3370FF;
      width: 10px;
      height: 10px;
      pointer-events: none;
      transform: rotate(45deg);
      box-sizing: border-box;
      /* left  */
      right: -5px;
      bottom: 33px;
      border-left-color: transparent;
      border-bottom-color: transparent
  }
  #maxkb .maxkb-tips .maxkb-title {
      font-size: 20px;
      font-weight: 500;
      margin-bottom: 8px;
  }
  #maxkb .maxkb-tips .maxkb-button {
      text-align: right;
      margin-top: 24px;
  }
  #maxkb .maxkb-tips .maxkb-button button {
      border-radius: 4px;
      background: #FFF;
      padding: 3px 12px;
      color: #3370FF;
      cursor: pointer;
      outline: none;
      border: none;
  }
  #maxkb .maxkb-tips .maxkb-button button::after{
      border: none;
    }
  #maxkb .maxkb-tips .maxkb-close {
      position: absolute;
      right: 20px;
      top: 20px;
      cursor: pointer;
  
  }
  #maxkb-chat-container {
        width: 420px;
        height: 600px;
        display:none;
      }
  @media only screen and (max-width: 768px) {
        #maxkb-chat-container {
          width: 100%;
          height: 70%;
          right: 0 !important;
        }
      }
      
      #maxkb .maxkb-chat-button{
        position: fixed;
        bottom: 30px;
        right: 0;
        cursor: pointer;
    }
    #maxkb #maxkb-chat-container{
        z-index:10000;position: relative;
              border-radius: 8px;
              border: 1px solid var(--N300, #DEE0E3);
              background: linear-gradient(188deg, rgba(235, 241, 255, 0.20) 39.6%, rgba(231, 249, 255, 0.20) 94.3%), #EFF0F1;
              box-shadow: 0px 4px 8px 0px rgba(31, 35, 41, 0.10);
              position: fixed;bottom: 20px;right: 45px;overflow: hidden;
    }

     #maxkb #maxkb-chat-container .maxkb-operate{
     top: 15px;
     right: 10px;
     position: absolute;
     display: flex;
     align-items: center;
     }
    #maxkb #maxkb-chat-container .maxkb-operate .maxkb-chat-close{
            margin-left:15px;
            cursor: pointer;
    }
    #maxkb #maxkb-chat-container .maxkb-operate .maxkb-openviewport{

            cursor: pointer;
    }
    #maxkb #maxkb-chat-container .maxkb-operate .maxkb-closeviewport{

      cursor: pointer;
    }
    #maxkb #maxkb-chat-container .maxkb-viewportnone{
      display:none;
    }
    #maxkb #maxkb-chat-container #maxkb-chat{
     height:100%;
     width:100%;
     border: none;
}
    #maxkb #maxkb-chat-container {
                animation: appear .4s ease-in-out;
              }
              @keyframes appear {
                from {
                  height: 0;;
                }
        
                to {
                  height: 600px;
                }
              }`
  root.appendChild(style)
}

function embedChatbot() {
  white_list_str='{{white_list_str}}'
  white_list=white_list_str.split(',')

  if ({{is_auth}}&&({{white_active}}?white_list.includes(window.location.origin):true)) {
    // 初始化maxkb智能小助手
    initMaxkb()
  } else console.error('invalid parameter')
}
window.onload = embedChatbot
