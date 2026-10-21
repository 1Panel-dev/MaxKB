<script setup lang="ts">
import { ref } from 'vue'

defineOptions({ name: 'DisplaySettingDialog' })

const visible = ref(false)

function open() {
  visible.value = true
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="显示设置">
    <!-- TODO：按确认后的设计接入显示设置业务。 -->
    <p class="text-N600">显示设置配置待接入。</p>
  </MkDialog>
</template>
