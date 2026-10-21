<script setup lang="ts">
import { ref } from 'vue'

defineOptions({ name: 'AccessRestrictionDialog' })

const visible = ref(false)

function open() {
  visible.value = true
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="访问限制">
    <!-- TODO：按确认后的设计接入访问限制业务。 -->
    <p class="text-N600">访问限制配置待接入。</p>
  </MkDialog>
</template>
