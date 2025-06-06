<template>
  <div ref="htmlRef" :innerHTML="source"></div>
</template>
<script setup lang="ts">
import { onMounted, ref } from 'vue'
const htmlRef = ref<HTMLElement>()
const props = withDefaults(
  defineProps<{
    source?: string
    script_exec?: boolean
  }>(),
  {
    source: '',
    script_exec: true
  }
)
onMounted(() => {
  if (htmlRef.value && props.script_exec) {
    const range = document.createRange()
    range.selectNode(htmlRef.value)
    const scripts = htmlRef.value.getElementsByTagName('script')
    if (scripts) {
      var documentFragment = range.createContextualFragment(
        [...scripts]
          .map((item: HTMLElement) => {
            htmlRef.value?.removeChild(item)
            return item.outerHTML
          })
          .join('\n')
      )
      htmlRef.value.appendChild(documentFragment)
    }
  }
})
</script>
<style lang="scss" scoped></style>
