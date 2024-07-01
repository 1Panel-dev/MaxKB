<template>
  <el-avatar
    :size="30"
    :style="{ background: props.pinyinColor && getAvatarColour(firstUserName) }"
    style="flex-shrink: 0"
    v-bind="$attrs"
  >
    <slot> {{ firstUserName }} </slot>
  </el-avatar>
</template>
<script setup lang="ts">
import { pinyin } from 'pinyin-pro'
import { computed } from 'vue'
defineOptions({ name: 'AppAvatar' })
const props = defineProps({
  name: {
    type: String,
    default: ''
  },
  //是否用拼音字母颜色
  pinyinColor: {
    type: Boolean,
    default: false
  }
})

const firstUserName = computed(() => {
  return props.name?.substring(0, 1)
})

const getAvatarColour = (name: string) => {
  const colours = [
    '#3370FF',
    '#4954E6',
    '#F54A45',
    '#00B69D',
    '#2CA91F',
    '#98B600',
    '#F80F80',
    '#D136D1',
    '#F01D94',
    '#7F3BF5',
    '#8F959E'
  ]
  let charIndex = name
    ? pinyin(name).charAt(0).toUpperCase().charCodeAt(0) - 65 >= 0
      ? pinyin(name).charAt(0).toUpperCase().charCodeAt(0) - 65
      : 0
    : 0

  function getColor() {
    return colours[Math.abs(charIndex % colours.length)]
  }

  return getColor()
}
</script>
<style lang="scss" scoped></style>
