<script setup lang="ts">
import { ref } from 'vue'

defineOptions({ name: 'EmbedThirdPartyDialog' })

const visible = ref(false)

function open() {
  visible.value = true
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="嵌入第三方">
    <!-- TODO：按确认后的设计接入嵌入第三方业务。 -->
    <p class="text-N600">嵌入第三方配置待接入。</p>
  </MkDialog>
</template>
