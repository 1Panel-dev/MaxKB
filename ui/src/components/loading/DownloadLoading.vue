<template>
  <div class="loading-container loader">
    <div class="download-loading">
      <div></div>
      <div></div>
      <div></div>
      <div></div>
      <div></div>
      <div></div>
      <div></div>
      <div></div>
    </div>
  </div>
</template>
<script setup lang="ts"></script>
<style lang="scss" scoped>
.loading-container {
  display: -webkit-flex; /*safari弹性布局*/
  justify-content: center;
  display: flex;
  align-items: center;
}

@-webkit-keyframes loader {
  0% {
    opacity: 0.3;
  }
  80% {
    opacity: 1;
  }
  100% {
    opacity: 1;
  }
}
.download-loading {
  position: relative;
}
.download-loading div {
  width: 5px;
  height: 12px;
  background: var(--el-color-info);
  position: absolute;
  border-radius: 2px;
  margin: 0 auto;
}
.download-loading div:nth-child(1) {
  top: -20px;
  left: 0;
  -webkit-animation: loader 1s -0.8s infinite ease-in-out;
}
.download-loading div:nth-child(2) {
  top: -13px;
  left: 13px;
  -webkit-transform: rotate(45deg);
  -webkit-animation: loader 1s -0.6s infinite ease-in-out;
}
.download-loading div:nth-child(3) {
  top: 0px;
  left: 20px;
  -webkit-transform: rotate(90deg);
  -webkit-animation: loader 1s -0.5s infinite ease-in-out;
}
.download-loading div:nth-child(4) {
  top: 13px;
  left: 13px;
  -webkit-transform: rotate(-45deg);
  -webkit-animation: loader 1s -0.4s infinite ease-in-out;
}
.download-loading div:nth-child(5) {
  top: 20px;
  left: 0px;
  -webkit-transform: rotate(0deg);
  -webkit-animation: loader 1s -0.3s infinite ease-in-out;
}
.download-loading div:nth-child(6) {
  top: 13px;
  left: -13px;
  -webkit-transform: rotate(45deg);
  -webkit-animation: loader 1s -0.2s infinite ease-in-out;
}
.download-loading div:nth-child(7) {
  top: 0px;
  left: -20px;
  -webkit-transform: rotate(90deg);
  -webkit-animation: loader 1s -0.1s infinite ease-in-out;
}
.download-loading div:nth-child(8) {
  top: -13px;
  left: -13px;
  -webkit-transform: rotate(-45deg);
  -webkit-animation: loader 1s 0s infinite ease-in-out;
}
</style>
