<template>
  <div class="touch-chat w-full mr-8">
    <el-button
      text
      bg
      class="microphone-button w-full mt-8 ml-8 mb-8"
      style="font-size: 1rem; padding: 1.2rem 0 !important; background-color: #eff0f1"
      @touchstart="onTouchStart"
      @touchmove="onTouchMove"
      @touchend="onTouchEnd"
    >
      按住说话
    </el-button>
    <!-- 使用 custom-class 自定义样式 -->
    <transition name="el-fade-in-linear">
      <el-card class="custom-speech-card" :class="isTouching ? '' : 'active'" v-if="dialogVisible">
        <p>
          <el-text type="info" v-if="isTouching">{{ '00:06' }}</el-text>
          <span class="lighter" v-else>
            {{ message }}
          </span>
        </p>
        <div class="close">
          <el-icon><Close /></el-icon>
        </div>
        <p class="lighter" :style="{ visibility: isTouching ? 'visible' : 'hidden' }">
          {{ message }}
        </p>
        <div class="speech-img flex-center border-r-4 mt-16">
          <img v-if="isTouching" src="@/assets/acoustic-color.svg" alt="" />
          <img v-else src="@/assets/acoustic.svg" alt="" />
        </div>
      </el-card>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
// 移动端语音
const startY = ref(0)
const isTouching = ref(false)
const dialogVisible = ref(false)
const message = ref('按住说话')
function onTouchStart(event: any) {
  isTouching.value = true
  startY.value = event.touches[0].clientY
  dialogVisible.value = true
  message.value = '松开发送，上滑取消'
}
function onTouchMove(event: any) {
  if (!isTouching.value) return
  // 阻止默认滚动行为
  event.preventDefault()
  const currentY = event.touches[0].clientY
  const deltaY = currentY - startY.value
  // 判断是否上滑
  if (deltaY < -50) {
    // -50 是一个阈值，可以根据需要调整
    message.value = '松开取消发送'
    isTouching.value = false
  }
}
function onTouchEnd() {
  if (isTouching.value) {
    message.value = '发送成功'
  } else {
    message.value = '已取消'
  }
  isTouching.value = false
  dialogVisible.value = false
}
</script>

<style lang="scss" scoped>
.custom-speech-card {
  position: fixed;
  bottom: 10px;
  left: 50%; /* 水平居中 */
  transform: translateX(-50%);
  width: 92%;
  background: #ffffff;
  border: 1px solid #ffffff;
  box-shadow: 0px 6px 24px 0px rgba(31, 35, 41, 0.08);
  z-index: 999;
  text-align: center;
  color: var(--app-text-color-secondary);
  user-select: none; /* 禁止选中 */
  -webkit-user-select: none; /* Safari */
  -moz-user-select: none; /* 老版Firefox */
  -ms-user-select: none; /* IE 10及以下 */
  .close {
    box-shadow: 0px 4px 8px 0px rgba(31, 35, 41, 0.1);
    border: 1px solid rgba(222, 224, 227, 1);
    background: rgba(255, 255, 255, 1);
    border-radius: 100px;
    display: inline-block;
    width: 43px;
    height: 43px;
    line-height: 50px;
    font-size: 1.8rem;
    margin: 20px 0;
  }
  .speech-img {
    text-align: center;
    background: #ebf1ff;
    padding: 8px;
    img {
      height: 25px;
    }
  }
  &.active {
    .close {
      background: #f54a45;
      color: #ffffff;
      width: 50px;
      height: 50px;
      line-height: 57px;
      font-size: 2rem;
    }
    .speech-img {
      background: #eff0f1;
    }
  }
}
</style>
