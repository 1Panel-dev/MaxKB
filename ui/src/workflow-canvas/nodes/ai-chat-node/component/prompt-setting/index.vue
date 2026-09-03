<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import { MagicStick, QuestionFilled } from '@element-plus/icons-vue'
import type { AiModelSetting, PromptSetting } from '../../types'
import PromptGenerateDialog from './PromptGenerateDialog.vue'
import PromptTextEditor from './PromptTextEditor.vue'

defineOptions({ name: 'AiChatNodePromptSetting' })

const props = defineProps<{ applicationId: string; modelSetting: AiModelSetting; setting: PromptSetting }>()
const emit = defineEmits<{ update: [setting: PromptSetting] }>()

const generateDialogRef = useTemplateRef<InstanceType<typeof PromptGenerateDialog>>('generateDialogRef')
const generateDisabled = computed(() => !props.applicationId || props.modelSetting.model_id_type !== 'custom' || !props.modelSetting.model_id)

function updateSetting(changes: Partial<PromptSetting>) {
  emit('update', { ...props.setting, ...changes })
}

function openGenerateDialog() {
  if (generateDisabled.value) return
  generateDialogRef.value?.open(props.applicationId, props.modelSetting.model_id)
}
</script>

<template>
  <el-form-item>
    <template #label>
      <div class="flex-between w-full gap-3">
        <span class="flex items-center gap-1">
          系统提示词
          <el-tooltip content="设定模型扮演的角色、工作目标和需要遵循的指令" placement="right">
            <MkIcon :icon="QuestionFilled" class="cursor-help text-N600" />
          </el-tooltip>
        </span>
        <el-tooltip :content="generateDisabled ? '选择自定义模型后可使用 AI 生成提示词' : 'AI 生成提示词'" placement="top">
          <el-button :disabled="generateDisabled" link type="primary" @click="openGenerateDialog">
            <MkIcon :icon="MagicStick" />
          </el-button>
        </el-tooltip>
      </div>
    </template>
    <PromptTextEditor
      :model-value="setting.system"
      placeholder="系统提示词，可以引用变量，如 {{开始.question}}"
      :rows="4"
      title="系统提示词"
      @update:model-value="updateSetting({ system: $event })"
    />
  </el-form-item>

  <el-form-item prop="prompt" :rules="{ required: true, message: '请输入用户提示词', trigger: 'blur' }">
    <template #label>
      <span class="flex items-center gap-1">
        用户提示词
        <el-tooltip content="发送给模型的用户问题或任务指令，可通过 {{节点名称.字段}} 引用变量" placement="right">
          <MkIcon :icon="QuestionFilled" class="cursor-help text-N600" />
        </el-tooltip>
      </span>
    </template>
    <PromptTextEditor
      :model-value="setting.prompt"
      placeholder="用户提示词，可以引用变量，如 {{开始.question}}"
      :rows="6"
      title="用户提示词"
      @update:model-value="updateSetting({ prompt: $event })"
    />
  </el-form-item>

  <PromptGenerateDialog ref="generateDialogRef" @replace="updateSetting({ system: $event })" />
</template>
