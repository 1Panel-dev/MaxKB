<script setup lang="ts">
import { useTemplateRef } from 'vue'
import TemplateStoreDialog from '../template-store/TemplateStoreDialog.vue'

defineOptions({ name: 'ButtonTemplateStore' })

const props = defineProps<{ folderId: string }>()
const templateStoreDialogRef = useTemplateRef<InstanceType<typeof TemplateStoreDialog>>('templateStoreDialogRef')

function handleOpenTemplateStore() {
  templateStoreDialogRef.value?.open(props.folderId)
}
</script>

<template>
  <!-- 打开模板中心 -->
  <el-button plain @click="handleOpenTemplateStore">
    <MkIcon name="icon_template_outlined" />
    <span>模板中心</span>
  </el-button>
  <TemplateStoreDialog ref="templateStoreDialogRef" />
</template>
