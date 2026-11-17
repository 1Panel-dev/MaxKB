<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ToolItem, ToolStoreResponse } from '@/api/types'
import WorkspaceToolStoreApi from '@/api/admin/workspace/tool/store'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

const { t } = useI18n({ useScope: 'global' })

defineOptions({ name: 'ButtonUpdateVersion' })

const props = defineProps<{ storeTools: ToolStoreResponse['apps']; tool: ToolItem }>()

const loading = defineModel<boolean>('loading', { default: false })

const emit = defineEmits<{ update: [tool: ToolItem] }>()

const availableStoreTool = computed(() =>
  props.storeTools.find((storeTool) => storeTool.id === props.tool.template_id && storeTool.version !== props.tool.version),
)

function handleUpdateStoreTool() {
  const storeTool = availableStoreTool.value
  if (!storeTool) return Promise.resolve(false)

  return MsgConfirm(t('tool.updateVersion.title', { name: props.tool.name }), t('tool.updateVersion.description'), {
    cancelButtonText: t('common.actions.cancel'),
    confirmButtonText: t('common.actions.confirm'),
  })
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
          MsgSuccess(t('tool.updateVersion.success'))
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
    <MkTooltip :content="t('tool.updateVersion.action')">
      <el-button
        class="absolute-center invisible opacity-0 group-hover/update:visible group-hover/update:opacity-100"
        text
        @click.stop="handleUpdateStoreTool"
      >
        <MkIcon name="icon_replace_outlined" />
      </el-button>
    </MkTooltip>
  </span>
</template>
