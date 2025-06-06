<template>
  <el-card
    shadow="hover"
    class="paragraph-box cursor"
    @mouseenter="cardEnter()"
    @mouseleave="cardLeave()"
  >
    <h2 class="mb-16">{{ data.title || '-' }}</h2>
    <MdPreview
      ref="editorRef"
      editorId="preview-only"
      :modelValue="data.content"
      class="maxkb-md"
    />
  </el-card>
</template>
<script setup lang="ts">
import { ref, useSlots } from 'vue'
import { t } from '@/locales'
const props = defineProps<{
  data: any
}>()

const show = ref(false)
// card上面存在dropdown菜单
const subHovered = ref(false)
function cardEnter() {
  show.value = true
  subHovered.value = false
}

function cardLeave() {
  show.value = subHovered.value
}

function subHoveredEnter() {
  subHovered.value = true
}
</script>
<style lang="scss" scoped>
.paragraph-box {
  background: var(--app-layout-bg-color);
  border: 1px solid #ffffff;
  box-shadow: none !important;
  &:hover {
    background: rgba(31, 35, 41, 0.1);
    border: 1px solid #dee0e3;
  }
}
</style>
