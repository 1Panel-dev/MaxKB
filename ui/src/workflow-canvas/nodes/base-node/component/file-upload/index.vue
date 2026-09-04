<script setup lang="ts">
import { useTemplateRef } from 'vue'
import type { FileUploadSetting } from '../../types'
import FileUploadSettingDialog from './FileUploadSettingDialog.vue'

defineOptions({ name: 'BaseNodeFileUploadSetting' })

const props = defineProps<{ enabled: boolean; setting: FileUploadSetting }>()
const emit = defineEmits<{
  'update:enabled': [enabled: boolean]
  'update:setting': [setting: FileUploadSetting]
}>()

const dialogRef = useTemplateRef<InstanceType<typeof FileUploadSettingDialog>>('dialogRef')

function handleOpenDialog() {
  dialogRef.value?.open(props.setting)
}

function changeEnabled(value: boolean | number | string) {
  emit('update:enabled', Boolean(value))
}
</script>

<template>
  <div class="mb-4 flex-between w-full">
    <span class="flex items-center gap-1">
      文件上传
      <el-tooltip content="开启后，问答页面会显示上传文件的按钮。" placement="right">
        <MkIcon name="icon_info_outlined" />
      </el-tooltip>
    </span>
    <span class="flex items-center gap-2">
      <el-button v-if="enabled" text type="primary" title="文件上传设置" @click="handleOpenDialog">
        <MkIcon name="icon-setting" />
      </el-button>
      <el-switch :model-value="enabled" size="small" @change="changeEnabled" />
    </span>
  </div>

  <FileUploadSettingDialog ref="dialogRef" @submit="emit('update:setting', $event)" />
</template>
