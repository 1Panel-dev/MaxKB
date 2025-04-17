<template>
  <div class="VerifyCode">
    <canvas
      id="VerifyCode-canvas"
      :width="props.contentWidth"
      :height="props.contentHeight"
      @click="refreshCode"
    ></canvas>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch, computed } from 'vue'
const props = defineProps({
  code: {
    type: String,
    default: '1234',
  },
  fontSizeMin: {
    type: Number,
    default: 25,
  },
  fontSizeMax: {
    type: Number,
    default: 35,
  },
  backgroundColorMin: {
    type: Number,
    default: 255,
  },
  backgroundColorMax: {
    type: Number,
    default: 255,
  },
  colorMin: {
    type: Number,
    default: 0,
  },
  colorMax: {
    type: Number,
    default: 160,
  },
  lineColorMin: {
    type: Number,
    default: 40,
  },
  lineColorMax: {
    type: Number,
    default: 180,
  },
  dotColorMin: {
    type: Number,
    default: 0,
  },
  dotColorMax: {
    type: Number,
    default: 255,
  },
  contentWidth: {
    type: Number,
    default: 112,
  },
  contentHeight: {
    type: Number,
    default: 40,
  },
})

//验证码
const emit = defineEmits(['update:code'])
const verifyCode = computed({
  get: () => {
    return props.code
  },
  set: (data) => {
    emit('update:code', data)
  },
})

// 生成校验码
const makeCode = (len = 4) => {
  let code = ''
  const codeLength = len
  const identifyCodes = '123456789abcdefjhijkinpqrsduvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
  for (let i = 0; i < codeLength; i++) {
    code += identifyCodes[randomNum(0, identifyCodes.length)]
  }
  return code
}

// 生成一个随机数
const randomNum = (min = 0, max: number) => Math.floor(Math.random() * (max - min)) + min

// 生成一个随机的颜色
function randomColor(min: number, max: number) {
  let r = randomNum(min, max)
  let g = randomNum(min, max)
  let b = randomNum(min, max)
  return 'rgb(' + r + ',' + g + ',' + b + ')'
}

// 绘制干扰线
const drawLine = (ctx: CanvasRenderingContext2D) => {
  for (let i = 0; i < 5; i++) {
    ctx.strokeStyle = randomColor(props.lineColorMin, props.lineColorMax)
    ctx.beginPath()
    ctx.moveTo(randomNum(0, props.contentWidth), randomNum(0, props.contentHeight))
    ctx.lineTo(randomNum(0, props.contentWidth), randomNum(0, props.contentHeight))
    ctx.stroke()
  }
}
//在画布上显示数据
const drawText = (ctx: CanvasRenderingContext2D, txt: string, i: number) => {
  ctx.fillStyle = randomColor(props.colorMin, props.colorMax)
  ctx.font = randomNum(props.fontSizeMin, props.fontSizeMax) + 'px SimHei'
  let x = (i + 1) * (props.contentWidth / (txt.length + 1))
  let y = randomNum(props.fontSizeMax, props.contentHeight - 5)
  var deg = randomNum(-45, 45)
  // 修改坐标原点和旋转角度
  ctx.translate(x, y)
  ctx.rotate((deg * Math.PI) / 180)
  ctx.fillText(txt[i], 0, 0)
  // 恢复坐标原点和旋转角度
  ctx.rotate((-deg * Math.PI) / 180)
  ctx.translate(-x, -y)
}
// 绘制干扰点
const drawDot = (ctx: CanvasRenderingContext2D) => {
  for (let i = 0; i < 80; i++) {
    ctx.fillStyle = randomColor(0, 255)
    ctx.beginPath()
    ctx.arc(randomNum(0, props.contentWidth), randomNum(0, props.contentHeight), 1, 0, 2 * Math.PI)
    ctx.fill()
  }
}
//画图
const drawPic = () => {
  let canvas = document.getElementById('VerifyCode-canvas') as HTMLCanvasElement
  if (!canvas) {
    return
  }
  let ctx = canvas.getContext('2d') as CanvasRenderingContext2D
  ctx.textBaseline = 'bottom'
  // 绘制背景
  ctx.fillStyle = randomColor(props.backgroundColorMin, props.backgroundColorMax)
  ctx.fillRect(0, 0, props.contentWidth, props.contentHeight)
  // 绘制文字
  for (let i = 0; i < verifyCode.value.length; i++) {
    drawText(ctx, verifyCode.value, i)
  }
  drawLine(ctx)
  drawDot(ctx)
}

// 重置验证码
const refreshCode = () => {
  emit('update:code', makeCode())
  drawPic()
}

// defineExpose({ refreshCode });

//组件挂载
onMounted(() => {
  drawPic()
})
</script>
<style scoped lang="scss">
.VerifyCode {
  cursor: pointer;
}
</style>
