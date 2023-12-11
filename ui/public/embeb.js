 function embedChatbot() { 
   const t = window.maxkbChatConfig
   if (t && t.token) {
    icon = `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="56" viewBox="0 0 48 56" fill="none">
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
    </svg>`;
        chat_button = document.createElement("div");
        chat_button.style =
          "position: absolute;bottom: 40px;right: 20px;cursor: pointer;";
        chat_button.innerHTML = icon;
    
        chat_container = document.createElement("div");
        chat_container.id = "chat_container";
        chat_container.style.cssText = `position: relative;
          width: 420px;
          height: 600px;
          border: none;
          border-radius: 7px 7px 7px 7px;
          position: absolute;bottom: 40px;right: 20px`;
        chat_container.style["display"] = "none";
    
        chat = document.createElement("iframe");
        chat.src = `http://${window.maxkbChatConfig.host}/ui/chat/${window.maxkbChatConfig.token}`;
        chat.id = "chat";
        chat_container.append(chat);
        chat.style.cssText = `border: none;height:100%;width:100%`;
    
        close_button = document.createElement("div");
    
        close_button.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="none">
    <path d="M9.95317 8.73169L15.5511 3.13376C15.7138 2.97104 15.9776 2.97104 16.1403 3.13376L16.7296 3.72301C16.8923 3.88573 16.8923 4.14955 16.7296 4.31227L11.1317 9.9102L16.7296 15.5081C16.8923 15.6708 16.8923 15.9347 16.7296 16.0974L16.1403 16.6866C15.9776 16.8494 15.7138 16.8494 15.5511 16.6866L9.95317 11.0887L4.35524 16.6866C4.19252 16.8494 3.9287 16.8494 3.76598 16.6866L3.17673 16.0974C3.01401 15.9347 3.01401 15.6708 3.17673 15.5081L8.77465 9.9102L3.17673 4.31227C3.01401 4.14955 3.01401 3.88573 3.17673 3.72301L3.76598 3.13376C3.9287 2.97104 4.19252 2.97104 4.35524 3.13376L9.95317 8.73169Z" fill="#646A73"/>
    </svg>`;
        close_button.style.cssText = `position: absolute;
        top: 10px;
        right: 10px;
        cursor: pointer;
        `;
        close_button.onclick = () => {
          chat_container.style["display"] = "none";
          chat_button.style["display"] = "block";
        };
        
        chat_container.append(close_button);
        document.body.append(chat_container);
    
        chat_button.onclick = ($event) => {
          chat_container.style["display"] = "block";
          chat_button.style["display"] = "none";
        };
        sty=document.createElement("style")
        sty.innerText=` #chat_container {
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
        document.head.append(sty)
        document.body.append(chat_button);
   } else console.error('difyChatbotConfig is empty or token is not provided')
 }
 document.body.onload = embedChatbot
