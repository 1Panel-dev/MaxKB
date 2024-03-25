function auth(token, protocol, host) {
  const XML = new XMLHttpRequest()
  XML.open('POST', `${protocol}//${host}/api/application/authentication`, false)
  XML.setRequestHeader('Content-Type', 'application/json')
  res = XML.send(JSON.stringify({ access_token: token }))
  return XML.status == 200
}
 
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
`<div class="maxkb-chat-button"><svg style="vertical-align: middle;overflow: hidden;" xmlns="http://www.w3.org/2000/svg" width="48" height="56" viewBox="0 0 48 56" fill="none">
<g filter="url(#filter0_d_349_49711)">
<path d="M8 24C8 12.9543 16.9543 4 28 4H48V44H28C16.9543 44 8 35.0457 8 24Z" fill="url(#paint0_linear_349_49711)"/>
</g>
<path d="M31.6667 15.6665H28.3333V18.1665H29.1667V19.8332H24.5833C23.6629 19.8332 22.9167 20.5794 22.9167 21.4998V30.6665C22.9167 31.587 23.6629 32.3332 24.5833 32.3332H35.4167C36.3371 32.3332 37.0833 31.587 37.0833 30.6665V21.4998C37.0833 20.5794 36.3371 19.8332 35.4167 19.8332H30.8333V18.1665H31.6667V15.6665ZM25.8333 24.8332H28.3333V27.3332H25.8333V24.8332ZM34.1667 24.8332V27.3332H31.6667V24.8332H34.1667Z" fill="white"/>
<path d="M21.6667 23.9998H20V28.1665H21.6667V23.9998Z" fill="white"/>
<path d="M38.3333 23.9998H40V28.1665H38.3333V23.9998Z" fill="white"/>
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
<iframe id="maxkb-chat" src=${protocol}//${host}/ui/chat/${token}></iframe>
<div class="maxkb-closeviewport maxkb-viewportnone"><svg style="vertical-align: middle;overflow: hidden;" t="1710214539671"  viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg"  fill="rgb(100, 106, 115)" width="16" height="16"><path d="M85.333333 384c25.6 0 42.666667-17.066667 42.666667-42.666667V128h213.333333c25.6 0 42.666667-17.066667 42.666667-42.666667s-17.066667-42.666667-42.666667-42.666666H85.333333c-25.6 0-42.666667 17.066667-42.666666 42.666666v256c0 25.6 17.066667 42.666667 42.666666 42.666667zM938.666667 640c-25.6 0-42.666667 17.066667-42.666667 42.666667v213.333333h-213.333333c-25.6 0-42.666667 17.066667-42.666667 42.666667s17.066667 42.666667 42.666667 42.666666h256c25.6 0 42.666667-17.066667 42.666666-42.666666v-256c0-25.6-17.066667-42.666667-42.666666-42.666667zM601.6 401.066667c4.266667 8.533333 12.8 17.066667 21.333333 21.333333 4.266667 4.266667 12.8 4.266667 17.066667 4.266667h256c25.6 0 42.666667-17.066667 42.666667-42.666667s-17.066667-42.666667-42.666667-42.666667h-153.6l226.133333-226.133333c17.066667-17.066667 17.066667-42.666667 0-59.733333-8.533333-8.533333-17.066667-12.8-29.866666-12.8s-21.333333 4.266667-29.866667 12.8L682.666667 281.6V128c0-25.6-17.066667-42.666667-42.666667-42.666667s-42.666667 17.066667-42.666667 42.666667v256c0 4.266667 0 12.8 4.266667 17.066667zM115.2 968.533333L341.333333 742.4V896c0 25.6 17.066667 42.666667 42.666667 42.666667s42.666667-17.066667 42.666667-42.666667v-256c0-4.266667 0-12.8-4.266667-17.066667-4.266667-8.533333-12.8-17.066667-21.333333-21.333333-4.266667-4.266667-12.8-4.266667-17.066667-4.266667H128c-25.6 0-42.666667 17.066667-42.666667 42.666667s17.066667 42.666667 42.666667 42.666667h153.6l-226.133333 226.133333c-17.066667 17.066667-17.066667 42.666667 0 59.733333s42.666667 17.066667 59.733333 0z" p-id="10189"></path></svg></div>
<div class="maxkb-openviewport">
            <svg style="vertical-align: middle;overflow: hidden;" t="1710150885892"   viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg"  fill="rgb(100, 106, 115)" width="16" height="16" ><path d="M85.333333 384c25.6 0 42.666667-17.066667 42.666667-42.666667V128h213.333333c25.6 0 42.666667-17.066667 42.666667-42.666667s-17.066667-42.666667-42.666667-42.666666H85.333333c-25.6 0-42.666667 17.066667-42.666666 42.666666v256c0 25.6 17.066667 42.666667 42.666666 42.666667zM938.666667 640c-25.6 0-42.666667 17.066667-42.666667 42.666667v213.333333h-213.333333c-25.6 0-42.666667 17.066667-42.666667 42.666667s17.066667 42.666667 42.666667 42.666666h256c25.6 0 42.666667-17.066667 42.666666-42.666666v-256c0-25.6-17.066667-42.666667-42.666666-42.666667zM977.066667 68.266667c-4.266667-8.533333-12.8-17.066667-21.333334-21.333334-4.266667-4.266667-12.8-4.266667-17.066666-4.266666h-256c-25.6 0-42.666667 17.066667-42.666667 42.666666s17.066667 42.666667 42.666667 42.666667h153.6l-226.133334 226.133333c-17.066667 17.066667-17.066667 42.666667 0 59.733334 8.533333 8.533333 17.066667 12.8 29.866667 12.8s21.333333-4.266667 29.866667-12.8L896 187.733333V341.333333c0 25.6 17.066667 42.666667 42.666667 42.666667s42.666667-17.066667 42.666666-42.666667V85.333333c0-4.266667 0-12.8-4.266666-17.066666zM354.133333 610.133333L128 836.266667V682.666667c0-25.6-17.066667-42.666667-42.666667-42.666667s-42.666667 17.066667-42.666666 42.666667v256c0 4.266667 0 12.8 4.266666 17.066666 4.266667 8.533333 12.8 17.066667 21.333334 21.333334 4.266667 4.266667 12.8 4.266667 17.066666 4.266666h256c25.6 0 42.666667-17.066667 42.666667-42.666666s-17.066667-42.666667-42.666667-42.666667H187.733333l226.133334-226.133333c17.066667-17.066667 17.066667-42.666667 0-59.733334s-42.666667-17.066667-59.733334 0z" p-id="8645"></path></svg>
</div>
           <div class="chat_close"><svg style="vertical-align: middle;overflow: hidden;" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M9.95317 8.73169L15.5511 3.13376C15.7138 2.97104 15.9776 2.97104 16.1403 3.13376L16.7296 3.72301C16.8923 3.88573 16.8923 4.14955 16.7296 4.31227L11.1317 9.9102L16.7296 15.5081C16.8923 15.6708 16.8923 15.9347 16.7296 16.0974L16.1403 16.6866C15.9776 16.8494 15.7138 16.8494 15.5511 16.6866L9.95317 11.0887L4.35524 16.6866C4.19252 16.8494 3.9287 16.8494 3.76598 16.6866L3.17673 16.0974C3.01401 15.9347 3.01401 15.6708 3.17673 15.5081L8.77465 9.9102L3.17673 4.31227C3.01401 4.14955 3.01401 3.88573 3.17673 3.72301L3.76598 3.13376C3.9287 2.97104 4.19252 2.97104 4.35524 3.13376L9.95317 8.73169Z" fill="#646A73"/>
  </svg>
 </div>`
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
  root.insertAdjacentHTML('beforeend',getChatContainerHtml(window.maxkbChatConfig.protocol,window.maxkbChatConfig.host,window.maxkbChatConfig.token))
  // 按钮元素
  const chat_button=root.querySelector('.maxkb-chat-button')
  //  对话框元素
  const chat_container=root.querySelector('#maxkb-chat-container')

  const viewport=root.querySelector('.maxkb-openviewport')
  const closeviewport=root.querySelector('.maxkb-closeviewport')
  const close_func=()=>{
    chat_container.style['display']=chat_container.style['display']=='block'?'none':'block'
  }
  close_icon=chat_container.querySelector('.maxkb-close')
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
      height: 50px;
      box-shadow: 1px 1px 1px 2000px rgba(0,0,0,.6);
      border-radius: 50% 0 0 50%;
      position: absolute;
      right: 0;
      bottom: 42px;
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
    #maxkb #maxkb-chat-container .maxkb-chat-close{
        position: absolute;
            top: 15px;
            right: 10px;
            cursor: pointer;
    }
    #maxkb #maxkb-chat-container .maxkb-openviewport{
           position: absolute;
            top: 15px;
            right: 50px;
            cursor: pointer;
    }
    #maxkb #maxkb-chat-container .maxkb-closeviewport{
      position: absolute;
      top: 15px;
      right: 50px;
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
  const t = window.maxkbChatConfig
  check = auth(t.token, t.protocol, t.host)
  if (t && t.token && t.protocol && t.host && check) {
    // 初始化maxkb智能小助手
    initMaxkb()
  } else console.error('invalid parameter')
}
window.onload = embedChatbot
