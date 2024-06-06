<template>
  <div>
    <el-button-group>
      <el-button size="small" @click="zoomIn">放大</el-button>
      <el-button size="small" @click="zoomOut">缩小</el-button>
      <el-button size="small" @click="fitView">适应</el-button>
    </el-button-group>
  </div>
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
  // props.lf?.fitView()
}
</script>
<style scoped></style>
