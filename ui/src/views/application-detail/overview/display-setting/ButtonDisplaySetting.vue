<script setup lang="ts">
import { useTemplateRef } from 'vue'
import DisplaySettingDialog from './DisplaySettingDialog.vue'

defineOptions({ name: 'ButtonDisplaySetting' })

const dialogRef = useTemplateRef<InstanceType<typeof DisplaySettingDialog>>('dialogRef')

function handleOpenDisplaySetting() {
  dialogRef.value?.open()
}
</script>

<template>
  <!-- 设置对话显示 -->
  <el-button plain @click="handleOpenDisplaySetting">
    <MkIcon name="icon_setting" />
    <span>显示设置</span>
  </el-button>
  <DisplaySettingDialog ref="dialogRef" />
</template>
