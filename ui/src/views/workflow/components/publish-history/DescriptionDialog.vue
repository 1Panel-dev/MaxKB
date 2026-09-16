<script setup lang="ts">
import { ref } from 'vue'

defineOptions({ name: 'DescriptionDialog' })

const visible = ref(false)
const description = ref('')

function open(content: string) {
  description.value = content
  visible.value = true
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="更新说明" align-center @closed="description = ''">
    {{ description || '暂无更新说明' }}
  </MkDialog>
</template>

<style scoped></style>
