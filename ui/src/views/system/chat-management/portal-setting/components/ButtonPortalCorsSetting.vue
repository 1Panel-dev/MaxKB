<script setup lang="ts">
import { ref } from 'vue'

defineProps<{ disabled?: boolean }>()

/* 跨域设置入口 */
const corsVisible = ref(false)
function handleOpenCorsSetting() {
  corsVisible.value = true
}
</script>

<template>
  <!-- 查看跨域配置说明 -->
  <el-button text type="primary" title="跨域设置" :disabled="disabled" @click="handleOpenCorsSetting">
     <MkIcon name="icon-setting" />
  </el-button>
  <MkDialog v-model="corsVisible" title="跨域设置" :width="480">
    <p class="text-N600">跨域访问配置暂未开放，请联系管理员配置允许访问的来源。</p>
    <template #footer>
      <!-- 关闭跨域设置说明 -->
      <el-button type="primary" @click="corsVisible = false">知道了</el-button>
    </template>
  </MkDialog>
</template>
