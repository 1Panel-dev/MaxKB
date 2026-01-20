<template>
  <div style="width: 100%; height: calc(100vh - 57px)">
    <embed v-if="is_pdf" style="width: 100%; height: 100%" :src="pdfSrc" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{
  detail?: any
}>()
const is_pdf = computed(() => {
  return props.detail?.meta?.source_file_id
})
const pdfSrc = computed(() => {
  return `${window.MaxKB.prefix}/oss/file/${props.detail?.meta?.source_file_id}`
})
</script>
