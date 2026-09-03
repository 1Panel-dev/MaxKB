<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { Operation, QuestionFilled } from '@element-plus/icons-vue'
import type { ReasoningSetting } from '../../types'
import ReasoningSettingDialog from './ReasoningSettingDialog.vue'

defineOptions({ name: 'AiChatNodeReasoningSetting' })

const props = defineProps<{ setting: ReasoningSetting }>()
const emit = defineEmits<{ update: [setting: ReasoningSetting] }>()

const dialogRef = useTemplateRef<InstanceType<typeof ReasoningSettingDialog>>('dialogRef')

function changeEnabled(value: boolean | number | string) {
  emit('update', { ...props.setting, reasoning_content_enable: Boolean(value) })
}
</script>

<template>
  <el-form-item>
    <template #label>
      <div class="flex-between w-full">
        <span class="flex items-center gap-1">
          返回思考过程
          <el-tooltip content="保留模型的思考内容，并输出到 reasoning_content 字段" placement="right">
            <MkIcon :icon="QuestionFilled" class="cursor-help text-N600" />
          </el-tooltip>
        </span>
        <span class="flex items-center gap-2">
          <el-button v-if="setting.reasoning_content_enable" link title="思考过程设置" type="primary" @click="dialogRef?.open(setting)">
            <MkIcon :icon="Operation" />
          </el-button>
          <el-switch :model-value="setting.reasoning_content_enable" size="small" @change="changeEnabled" />
        </span>
      </div>
    </template>
  </el-form-item>

  <ReasoningSettingDialog ref="dialogRef" @submit="emit('update', $event)" />
</template>
