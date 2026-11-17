<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import ToolStoreDialog from '../tool-store/ToolStoreDialog.vue'

const { t } = useI18n({ useScope: 'global' })

defineOptions({ name: 'ButtonToolStore' })

const props = defineProps<{ folderId: string }>()

const emit = defineEmits<{ refresh: [] }>()

const toolStoreDialogRef = useTemplateRef<InstanceType<typeof ToolStoreDialog>>('toolStoreDialogRef')

function handleOpenToolStore() {
  toolStoreDialogRef.value?.open(props.folderId)
}
</script>

<template>
  <el-button plain @click="handleOpenToolStore">
    <MkIcon name="icon_application-shop_filled" />
    <span>{{ t('tool.store.title') }}</span>
  </el-button>
  <ToolStoreDialog ref="toolStoreDialogRef" @refresh="emit('refresh')" />
</template>
