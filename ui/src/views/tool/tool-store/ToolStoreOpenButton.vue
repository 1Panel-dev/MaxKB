<script setup lang="ts">
import { useTemplateRef } from 'vue'
import ToolStoreDialog from './ToolStoreDialog.vue'

defineOptions({ name: 'ToolStoreOpenButton' })

const props = defineProps<{
  folderId: string
}>()

const emit = defineEmits<{
  refresh: []
}>()

const toolStoreDialogRef =
  useTemplateRef<InstanceType<typeof ToolStoreDialog>>('toolStoreDialogRef')

function handleOpenToolStore() {
  toolStoreDialogRef.value?.open(props.folderId)
}
</script>

<template>
  <el-button plain @click="handleOpenToolStore">
    <MkIcon name="icon_application-shop_filled" />
    <span>工具商店</span>
  </el-button>
  <ToolStoreDialog ref="toolStoreDialogRef" @refresh="emit('refresh')" />
</template>
