<template>
  <el-card shadow="always" style="--el-card-padding: 8px 12px; --el-card-border-radius: 8px">
    <el-button link @click="zoomOut">
      <el-icon :size="16" title="缩小"><ZoomOut /></el-icon>
    </el-button>
    <el-button link @click="zoomIn">
      <el-icon :size="16" title="放大"><ZoomIn /></el-icon>
    </el-button>

    <el-divider direction="vertical" />
    <el-button link @click="fitView">
      <AppIcon iconName="app-fitview" title="适应"></AppIcon>
    </el-button>
  </el-card>
</template>

<script setup lang="ts">
const props = defineProps({
  lf: Object || String || null
})

function zoomIn() {
  props.lf?.zoom(true)
}
function zoomOut() {
  props.lf?.zoom(false)
}
function fitView() {
  props.lf?.resetZoom()
  props.lf?.resetTranslate()
  props.lf?.fitView()
}
</script>
<style scoped></style>
