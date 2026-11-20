(function() {
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
`<div class="maxkb-chat-button" >
<img style="height:100%;width:100%;" src="{{float_icon}}">
</div>`



const getChatContainerHtml=(protocol,host,token,query,prefix)=>{
 return `<div id="maxkb-chat-container">
<iframe id="maxkb-chat" allow="microphone" src=${protocol}://${host}${prefix}/${token}?mode=embed${query}></iframe>
<div class="maxkb-operate"><div class="maxkb-closeviewport maxkb-viewportnone"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 1024 1024" fill="none"><path d="M384.341333 597.205333a42.538667 42.538667 0 0 1 42.666667 42.666667v220.16a21.333333 21.333333 0 0 1-21.333333 21.333333h-42.666667a21.333333 21.333333 0 0 1-21.333333-21.333333v-113.493333l-167.04 167.04a21.333333 21.333333 0 0 1-30.165334 0l-30.165333-30.208a21.333333 21.333333 0 0 1 0-30.165334l170.709333-170.666666H163.669333a21.333333 21.333333 0 0 1-21.333333-21.333334v-42.666666a21.333333 21.333333 0 0 1 21.333333-21.333334h220.672zM849.92 110.506667a21.333333 21.333333 0 0 1 30.165333 0l30.165334 30.165333a21.333333 21.333333 0 0 1 0 30.165333l-170.709334 170.666667h121.344a21.333333 21.333333 0 0 1 21.333334 21.333333v42.666667a21.333333 21.333333 0 0 1-21.333334 21.333333h-220.672a42.538667 42.538667 0 0 1-42.666666-42.666666v-220.16a21.333333 21.333333 0 0 1 21.333333-21.333334h42.666667a21.333333 21.333333 0 0 1 21.333333 21.333334v113.493333l167.04-166.997333z" fill="{{header_font_color}}"/></svg></div>
<div class="maxkb-openviewport">
<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 1024 1024" fill="none"><path d="M366.165333 593.749333a21.333333 21.333333 0 0 1 30.208 0l30.165334 30.165334a21.333333 21.333333 0 0 1 0 30.208l-170.752 170.666666H377.173333a21.333333 21.333333 0 0 1 21.333334 21.333334v42.666666a21.333333 21.333333 0 0 1-21.333334 21.333334H156.458667a42.538667 42.538667 0 0 1-42.666667-42.666667v-220.16a21.333333 21.333333 0 0 1 21.333333-21.333333h42.666667a21.333333 21.333333 0 0 1 21.333333 21.333333v113.493333l167.04-167.04z m500.992-480a42.538667 42.538667 0 0 1 42.666667 42.666667v220.16a21.333333 21.333333 0 0 1-21.333333 21.333333h-42.666667a21.333333 21.333333 0 0 1-21.333333-21.333333v-113.493333l-167.04 167.04a21.333333 21.333333 0 0 1-30.165334 0l-30.165333-30.165334a21.333333 21.333333 0 0 1 0-30.165333l170.709333-170.666667h-121.344a21.333333 21.333333 0 0 1-21.333333-21.333333v-42.666667a21.333333 21.333333 0 0 1 21.333333-21.333333h220.672z" fill="{{header_font_color}}"/></svg></div>
<div class="maxkb-chat-close"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 1024 1024" fill="none"><path d="M509.525333 447.104L796.16 160.426667a21.333333 21.333333 0 0 1 30.165333 0l30.165334 30.165333a21.333333 21.333333 0 0 1 0 30.165333l-286.634667 286.634667 286.634667 286.592a21.333333 21.333333 0 0 1 0 30.165333l-30.165334 30.208a21.333333 21.333333 0 0 1-30.165333 0l-286.634667-286.634666-286.592 286.634666a21.333333 21.333333 0 0 1-30.165333 0l-30.165333-30.165333a21.333333 21.333333 0 0 1 0-30.208l286.592-286.592-286.592-286.634667a21.333333 21.333333 0 0 1 0-30.165333l30.165333-30.165333a21.333333 21.333333 0 0 1 30.165333 0l286.592 286.634666z" fill="{{header_font_color}}"/></svg>
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
  root.insertAdjacentHTML('beforeend',getChatContainerHtml('{{protocol}}','{{host}}','{{token}}','{{query}}','{{prefix}}'))
  // 按钮元素
  const chat_button=root.querySelector('.maxkb-chat-button')
  const chat_button_img=root.querySelector('.maxkb-chat-button > img')
  //  对话框元素
  const chat_container=root.querySelector('#maxkb-chat-container')
    // 引导层
  const mask_content = root.querySelector('.maxkb-mask > .maxkb-content')
  const mask_tips = root.querySelector('.maxkb-tips')
 chat_button_img.onload=(event)=>{
 if(mask_content){
    mask_content.style.width = chat_button_img.width + 'px'
    mask_content.style.height = chat_button_img.height + 'px'
    if('{{x_type}}'=='left'){
     mask_tips.style.marginLeft = (chat_button_img.naturalWidth>500?500:chat_button_img.naturalWidth)-64 + 'px'
    }else{
    mask_tips.style.marginRight = (chat_button_img.naturalWidth>500?500:chat_button_img.naturalWidth)-64 + 'px'
    }
   }
  }

  const viewport=root.querySelector('.maxkb-openviewport')
  const closeviewport=root.querySelector('.maxkb-closeviewport')
  const close_func=()=>{
    chat_container.style['display']=chat_container.style['display']=='block'?'none':'block'
    chat_button.style['display']=chat_container.style['display']=='block'?'none':'block'
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
     const drag=(e)=>{
            if (['touchmove','touchstart'].includes(e.type)) {
             chat_button.style.top=(e.touches[0].clientY-chat_button_img.naturalHeight/2)+'px'
             chat_button.style.left=(e.touches[0].clientX-chat_button_img.naturalWidth/2)+'px'
          } else {
             chat_button.style.top=(e.y-chat_button_img.naturalHeight/2)+'px'
             chat_button.style.left=(e.x-chat_button_img.naturalWidth/2)+'px'
          }
            chat_button.style.width =chat_button_img.naturalWidth+'px'
            chat_button.style.height =chat_button_img.naturalHeight+'px'
        }
  if({{is_draggable}}){
  chat_button.addEventListener("drag",drag)
  chat_button.addEventListener("dragover",(e)=>{
             e.preventDefault()
   })
  chat_button.addEventListener("dragend",drag)
  chat_button.addEventListener("touchstart",drag)
  chat_button.addEventListener("touchmove",drag)
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
  const maxkbId = 'maxkb-'+'{{max_kb_id}}'
  root.id=maxkbId
  initMaxkbStyle(maxkb, maxkbId)
  maxkb.appendChild(root)
  document.body.appendChild(maxkb)
  const maxkbMaskTip=localStorage.getItem('maxkbMaskTip')
  if(maxkbMaskTip==null && {{show_guide}}){
    initGuide(root)
  }
  initChat(root)
}


// 初始化全局样式
function initMaxkbStyle(root, maxkbId){
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
      z-index: 10001;
      background-color: transparent;
      height: 100%;
      width: 100%;
      top: 0;
      left: 0;
  }
  #maxkb .maxkb-mask .maxkb-content {
      width: 64px;
      height: 64px;
      box-shadow: 1px 1px 1px 9999px rgba(0,0,0,.6);
      position: absolute;
      {{x_type}}: {{x_value}}px;
      {{y_type}}: {{y_value}}px;
      z-index: 10001;
  }
  #maxkb .maxkb-tips {
      position: fixed;
      {{x_type}}:calc({{x_value}}px + 75px);
      {{y_type}}: calc({{y_value}}px + 0px);
      padding: 22px 24px 24px;
      border-radius: 6px;
      color: #ffffff;
      font-size: 14px;
      background: #3370FF;
      z-index: 10001;
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
      {{x_type}}: -5px;
      {{y_type}}: 33px;
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
        width: 460px;
        height: 680px;
        display:none;
      }
 @media only screen and (max-height: 680px) {
  #maxkb-chat-container{
    height: 600px}
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
        {{x_type}}: {{x_value}}px;
        {{y_type}}: {{y_value}}px;
        cursor: pointer;
        z-index:10000;
    }
    #maxkb #maxkb-chat-container{
        z-index:10000;position: relative;
              border-radius: 8px;
              border: 1px solid #ffffff;
              background: linear-gradient(188deg, rgba(235, 241, 255, 0.20) 39.6%, rgba(231, 249, 255, 0.20) 94.3%), #EFF0F1;
              box-shadow: 0px 4px 8px 0px rgba(31, 35, 41, 0.10);
              position: fixed;bottom: 16px;right: 16px;overflow: hidden;
    }

     /* 与对话头部按钮一致：56px 头部内垂直居中，18px 图标 + 4px 内边距，按钮间距 4px */
     #maxkb #maxkb-chat-container .maxkb-operate{
     top: 15px;
     right: 12px;
     position: absolute;
     display: flex;
     align-items: center;
     gap: 4px;
     }
    #maxkb #maxkb-chat-container .maxkb-operate > div{
            padding: 4px;
            line-height: 0;
            border-radius: 6px;
    }
    /* 悬停灰底，与对话头部文字按钮一致 */
    #maxkb #maxkb-chat-container .maxkb-operate > div:hover{
            background: rgba(31, 35, 41, 0.1);
    }
    #maxkb #maxkb-chat-container .maxkb-operate svg{
            display: block;
    }
    #maxkb #maxkb-chat-container .maxkb-operate .maxkb-chat-close{
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
      .replaceAll('#maxkb ',`#${maxkbId} `)
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
window.addEventListener('load',embedChatbot)
})();