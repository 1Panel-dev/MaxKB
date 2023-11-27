<template>
  <el-avatar
    :size="30"
    :style="{ background: props.pinyinColor && getAvatarColour(firstUserName) }"
    v-bind="$attrs"
  >
    <slot> {{ firstUserName }} </slot>
  </el-avatar>
</template>
<script setup lang="ts">
import { pinyin } from 'pinyin-pro';
import { computed } from 'vue'
defineOptions({ name: 'AppAvatar' })
const props = defineProps({
  name: {
    type: String,
    default: ''
  },
  pinyinColor: {
    type: Boolean,
    default: false
  }
})

const firstUserName = computed(() => {
  return props.name?.substring(0, 1)
})

function getAvatarColour(name: string) {
  const charIndex = pinyin.getFullChars(name).charAt(0).toUpperCase().charCodeAt(0) - 65
  const colours = [
    '#ACA9E5',
    '#BCC934',
    '#B3CFE8',
    '#DCDEB5',
    '#D65A4A',
    '#E0C78B',
    '#E59191',
    '#E99334',
    '#FF6632',
    '#F4B7EF',
    '#F7D407',
    '#F8BB98',
    '#2BCBB1',
    '#3594F1',
    '#486660',
    '#4B689F',
    '#5976F6',
    '#72B1B2',
    '#778293',
    '#7D6624',
    '#82CBB5',
    '#837F6A',
    '#87B087',
    '#9AC0C4',
    '#958E55',
    '#99E4F2'
  ]
  return colours[charIndex]
}
</script>
<style lang="scss" scoped></style>
