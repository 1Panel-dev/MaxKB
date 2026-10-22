<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import { useStore } from '@/stores/admin'
import DisplaySettingDialog from './DisplaySettingDialog.vue'
import XpackDisplaySettingDialog from './XpackDisplaySettingDialog.vue'

defineOptions({ name: 'ButtonDisplaySetting' })

const { auth } = useStore()
const displaySettingDialog = computed(() => (auth.isCE ? DisplaySettingDialog : XpackDisplaySettingDialog))
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
  <component :is="displaySettingDialog" ref="dialogRef" />
</template>
