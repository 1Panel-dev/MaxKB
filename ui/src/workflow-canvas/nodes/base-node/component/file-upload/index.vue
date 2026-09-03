<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { Operation, QuestionFilled } from '@element-plus/icons-vue'
import type { FileUploadSetting } from '../../types'
import FileUploadSettingDialog from './FileUploadSettingDialog.vue'

defineOptions({ name: 'BaseNodeFileUploadSetting' })

const props = defineProps<{ enabled: boolean; setting: FileUploadSetting }>()
const emit = defineEmits<{
  'update:enabled': [enabled: boolean]
  'update:setting': [setting: FileUploadSetting]
}>()

const dialogRef = useTemplateRef<InstanceType<typeof FileUploadSettingDialog>>('dialogRef')

function changeEnabled(value: boolean | number | string) {
  emit('update:enabled', Boolean(value))
}
</script>

<template>
  <el-form-item>
    <template #label>
      <div class="flex-between w-full">
        <span class="flex items-center gap-1">
          文件上传
          <el-tooltip content="允许用户在对话中上传文件，并限制文件数量、大小、类型和上传方式" placement="right">
            <MkIcon :icon="QuestionFilled" class="cursor-help text-N600" />
          </el-tooltip>
        </span>
        <span class="flex items-center gap-2">
          <el-button v-if="enabled" link type="primary" title="文件上传设置" @click="dialogRef?.open(props.setting)">
            <MkIcon :icon="Operation" />
          </el-button>
          <el-switch :model-value="enabled" size="small" @change="changeEnabled" />
        </span>
      </div>
    </template>
  </el-form-item>

  <FileUploadSettingDialog ref="dialogRef" @submit="emit('update:setting', $event)" />
</template>
