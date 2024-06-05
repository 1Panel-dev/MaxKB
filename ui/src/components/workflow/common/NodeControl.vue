<template>
  <div>
    <el-button-group>
      <el-button size="small" @click="$_zoomIn">放大</el-button>
      <el-button size="small" @click="$_zoomOut">缩小</el-button>
      <el-button size="small" @click="$_reset">适应</el-button>
    </el-button-group>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, computed, watch, reactive } from 'vue'
const props = defineProps({
  lf: Object || String
})

function $_zoomIn() {
  props.lf?.zoom(true)
}
function $_zoomOut() {
  props.lf?.zoom(false)
}
function $_reset() {
  props.lf?.resetZoom()
  props.lf?.resetTranslate()
  props.lf?.fitView()
}
</script>
<style scoped></style>
