<template>
  <div class="login-form-container">
    <div class="login-card-wrapper">
      <div class="login-card-glow"></div>
      <div class="login-card-inner">
        <div class="login-header">
          <div class="logo-container">
            <div class="logo-icon">
              <svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" class="logo-svg">
                <defs>
                  <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#ff9800;stop-opacity:1" />
                    <stop offset="50%" style="stop-color:#ff5722;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#e64a19;stop-opacity:1" />
                  </linearGradient>
                  <linearGradient id="logoInnerGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#ffcc80;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#ffab40;stop-opacity:1" />
                  </linearGradient>
                </defs>
                <circle cx="32" cy="32" r="30" fill="url(#logoGradient)" stroke="#ffab40" stroke-width="2"/>
                <circle cx="32" cy="32" r="22" fill="url(#logoInnerGradient)" opacity="0.3"/>
                <path d="M20 38 L32 26 L44 38" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="32" cy="20" r="4" fill="#fff"/>
              </svg>
            </div>
            <div class="logo-text">
              <h1 class="main-title">蓝星晴RAG</h1>
              <p class="sub-title" v-if="subTitle">{{ subTitle }}</p>
            </div>
          </div>
        </div>
        <div class="login-content-area">
          <slot></slot>
        </div>
        <div class="login-footer">
          <p class="footer-text">智能检索增强 · 高效知识问答</p>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
defineProps({
  title: String,
  subTitle: String,
})
</script>
<style lang="scss" scoped>
.login-form-container {
  width: 100%;
  max-width: 480px;
  padding: 20px;
}

.login-card-wrapper {
  position: relative;
  width: 100%;
}

.login-card-glow {
  position: absolute;
  top: -10px;
  left: -10px;
  right: -10px;
  bottom: -10px;
  background: linear-gradient(135deg, rgba(255, 152, 0, 0.3) 0%, rgba(255, 87, 34, 0.2) 100%);
  border-radius: 32px;
  filter: blur(20px);
  z-index: 0;
}

.login-card-inner {
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 28px;
  padding: 40px 36px;
  box-shadow: 
    0 20px 60px rgba(255, 87, 34, 0.15),
    0 8px 24px rgba(255, 152, 0, 0.1),
    0 2px 8px rgba(255, 152, 0, 0.05);
  border: 1px solid rgba(255, 152, 0, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 36px;
}

.logo-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.logo-icon {
  margin-bottom: 20px;
}

.logo-svg {
  width: 80px;
  height: 80px;
  filter: drop-shadow(0 4px 12px rgba(255, 87, 34, 0.3));
  animation: logoPulse 3s ease-in-out infinite;
}

@keyframes logoPulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.logo-text {
  text-align: center;
}

.main-title {
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #ff9800 0%, #ff5722 50%, #e64a19 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  line-height: 1.2;
  letter-spacing: 2px;
}

.sub-title {
  font-size: 15px;
  color: #8b7355;
  margin: 12px 0 0 0;
  font-weight: 400;
  letter-spacing: 0.5px;
}

.login-content-area {
  position: relative;
}

.login-footer {
  margin-top: 32px;
  text-align: center;
}

.footer-text {
  font-size: 13px;
  color: #b8860b;
  margin: 0;
  font-weight: 400;
  opacity: 0.8;
  letter-spacing: 1px;
}
</style>
