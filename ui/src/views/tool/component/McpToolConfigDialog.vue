<template>
  <el-dialog
    :title="$t('views.tool.mcpConfig')"
    width="600"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="close"
    append-to-body
    class="mcp-config-dialog"
  >
    <el-form label-width="auto" label-position="top">
      <el-form-item @mouseenter.stop="showIcon = true" @mouseleave.stop="showIcon = false">
        <el-input
          type="textarea"
          v-model="mcp_servers"
          rows="8"
          disabled
          class="config-textarea"
        ></el-input>
        <el-button circle class="copy-icon" v-show="showIcon" @click.stop="copyClick(mcp_servers)">
          <AppIcon iconName="app-copy" class="color-secondary" />
        </el-button>
      </el-form-item>
    </el-form>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { copyClick } from '@/utils/clipboard'

const mcp_servers = ref<string>('')
const dialogVisible = ref<boolean>(false)
const showIcon = ref<boolean>(false)

const close = () => {
  dialogVisible.value = false
}
const open = (item: any) => {
  mcp_servers.value = item.code
  dialogVisible.value = true
}

defineExpose({ open })
</script>

<style scoped lang="scss">
.mcp-config-dialog {
  .copy-icon {
    position: absolute;
    top: 12px;
    right: 12px;
    box-shadow: 0px 4px 8px 0px var(--app-text-color-light-1);
    z-index: 2;
  }
  .config-textarea {
    :deep(.el-textarea__inner) {
      color: var(--el-text-color-primary);
      cursor: pointer;
    }
  }
}
</style>
