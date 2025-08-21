<template>
  <el-dialog
    :title="$t('views.tool.form.mcpConfig')"
    width="600"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="close"
    append-to-body
  >
    <el-form label-width="auto" label-position="top">
      <el-form-item>
        <el-input
          type="textarea"
          v-model="mcp_servers"
          rows="8"
          disabled
        ></el-input>
        <AppIcon
          iconName="app-copy"
          class="copy-icon color-secondary"
          @click="copyClick(mcp_servers)"
        />
      </el-form-item>
    </el-form>
  </el-dialog>
</template>

<script setup lang="ts">
import {ref} from 'vue'
import {copyClick} from '@/utils/clipboard'


const mcp_servers = ref<string>('')
const dialogVisible = ref<boolean>(false)

const close = () => {
  dialogVisible.value = false
}
const open = (item: any) => {
  mcp_servers.value = item.code
  dialogVisible.value = true
}

defineExpose({open,})
</script>

<style scoped lang="scss">

.copy-icon {
  position: absolute;
  top: 6px;
  right: 8px;
  font-size: 16px;
  cursor: pointer;
  z-index: 2;
}

.copy-icon:hover {
  opacity: 0.85;
}

:deep(.el-textarea__inner) {
  padding-right: 34px; // 给右上角图标留空间
}
</style>
