<template>
  <Codemirror v-bind="$attrs" border :options="cmOption" ref="cmRef" :style="codemirrorStyle" />
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Codemirror } from 'vue-codemirror'

defineOptions({ name: 'CodemirrorEditor' })
const cmOption = {
  tabSize: 4,
  lineWrapping: true,
  lineNumbers: true,
  line: true
}
const codemirrorStyle = {
  height: '210px!important'
}
const cmRef = ref()
onMounted(() => {})

onUnmounted(() => {
  cmRef.value?.destroy()
})
</script>

<style lang="scss"></style>
