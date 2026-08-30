<script setup lang="ts">
import { computed } from 'vue'
import WorkspaceToolStoreApi from '@/api/admin/workspace/tool/store'
import type { ToolItem, ToolStoreResponse } from '@/api/types'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'UpdateVersionButton' })

const props = defineProps<{ storeTools: ToolStoreResponse['apps']; tool: ToolItem }>()

const loading = defineModel<boolean>('loading', { default: false })

const emit = defineEmits<{ update: [tool: ToolItem] }>()

const availableStoreTool = computed(() => props.storeTools.find((storeTool) => storeTool.id === props.tool.template_id && storeTool.version !== props.tool.version))

function handleUpdateStoreTool() {
  const storeTool = availableStoreTool.value
  if (!storeTool) return Promise.resolve(false)

  return MsgConfirm(`确认更新工具：${props.tool.name}？`, '更新工具可能会影响正在使用的资源，请谨慎操作。', { cancelButtonText: '取消', confirmButtonText: '确认' })
    .then(() => {
      loading.value = true
      return WorkspaceToolStoreApi.postStoreToolUpdate(props.tool.id, {
        download_callback_url: storeTool.downloadCallbackUrl ?? '',
        download_url: storeTool.downloadUrl ?? '',
        icon: storeTool.icon ?? '',
        label: storeTool.label ?? '',
        versions: storeTool.versions ?? [],
      })
        .then((updatedTool) => {
          emit('update', updatedTool)
          MsgSuccess('更新成功')
          return true
        })
        .finally(() => {
          loading.value = false
        })
    })
    .catch(() => false)
}
</script>

<template>
  <span v-if="availableStoreTool" class="group/update relative inline-flex h-[6px] w-[6px] shrink-0 items-center justify-center">
    <span class="mk-dot-success group-hover/update:opacity-0" />
    <el-tooltip content="更新版本">
      <el-button class="absolute-center invisible opacity-0 group-hover/update:visible group-hover/update:opacity-100" text @click.stop="handleUpdateStoreTool">
        <MkIcon name="icon_replace_outlined" />
      </el-button>
    </el-tooltip>
  </span>
</template>
