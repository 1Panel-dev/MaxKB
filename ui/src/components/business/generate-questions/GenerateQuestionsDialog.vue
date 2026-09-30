<script setup lang="ts">
import { computed, provide, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import { DOCUMENT_TASK_STATE, MODEL_STATUS } from '@/api/enums'
import type { DocumentTaskState, ModelItem, ModelProviderItem, RelatedQuestionsConfig } from '@/api/types'
import ModelApi from '@/api/admin/workspace/model'
import SystemResourceModelApi from '@/api/admin/system/resource-management/model'
import SystemSharedModelApi from '@/api/admin/system/shared-resources/model'
import ModelProviderApi from '@/api/admin/model-provider'
import SelectModel from '@/components/business/select-model/index.vue'
import { useStore } from '@/stores'
import { isSystemResource, isSystemSharedResource } from '@/utils/resource-context'
import { getPromptConfig, savePromptConfig } from './prompt-cache'

defineOptions({ name: 'GenerateQuestionsDialog' })
const props = withDefaults(defineProps<{ loading: boolean; showParagraphScope?: boolean }>(), {
  showParagraphScope: true,
})
const emit = defineEmits<{ submit: [config: RelatedQuestionsConfig, stateList: DocumentTaskState[]]; closed: [] }>()
const { user } = useStore()
const promptTip =
  '提示词中的 {data} 是分段内容占位符，执行时会替换为分段内容并发送给 AI 模型；\nAI 模型根据分段内容生成相关问题，请将生成的问题放至<question></question>标签中，系统会自动关联标签中的问题；\n生成效果依赖于所选模型和提示词，用户可自行调整至最佳效果。'

const modelLoading = ref(false)
provide('getModelParamsForm', (modelId: string) => {
  modelLoading.value = true
  return requestModelApi.value.getModelParamsForm(modelId).finally(() => {
    modelLoading.value = false
  })
})
/* 模型接口：按当前资源范围选择。 */
const requestModelApi = computed(() => {
  if (isSystemResource()) return SystemResourceModelApi
  if (isSystemSharedResource()) return SystemSharedModelApi
  return ModelApi
})

/* 生成配置：每次打开恢复最近提交的配置，处理范围始终重置。 */
const visible = ref(false)
const formRef = useTemplateRef<FormInstance>('formRef')
const form = ref<RelatedQuestionsConfig>({ model_id: '', model_params_setting: {}, prompt: '' })
const scope = ref<'error' | 'all'>('error')
const targetUserId = ref('')

const modelOptions = ref<ModelItem[]>([])
const providerOptions = ref<ModelProviderItem[]>([])
const modelAvailable = computed(() => modelOptions.value.some(({ id, status }) => id === form.value.model_id && status === MODEL_STATUS.SUCCESS))

function loadModels() {
  modelLoading.value = true
  return Promise.all([requestModelApi.value.getModelListWithShared({ model_type: 'LLM' }), ModelProviderApi.getProviderListByModelType('LLM')])
    .then(([models, providers]) => {
      modelOptions.value = models
      providerOptions.value = providers
      if (!modelAvailable.value) {
        form.value.model_id = models.find(({ status }) => status === MODEL_STATUS.SUCCESS)?.id ?? ''
        form.value.model_params_setting = {}
      }
    })
    .catch(() => {
      // 请求层提示错误；保留弹窗，允许重试加载。
    })
    .finally(() => {
      modelLoading.value = false
    })
}

function open() {
  targetUserId.value = user.userInfo?.id ?? ''
  form.value = getPromptConfig(targetUserId.value)
  visible.value = true
  return loadModels()
}

/* 校验后只返回配置与范围，接口请求、提示和关闭由各 Action 负责。 */
async function handleSubmit() {
  if (props.loading || modelLoading.value || !modelAvailable.value) return
  if (!(await formRef.value?.validate().catch(() => false))) return
  if (props.loading || modelLoading.value || !modelAvailable.value) return
  const config = cloneDeep(form.value)
  const stateList = props.showParagraphScope
    ? Object.values(DOCUMENT_TASK_STATE).filter((state) => scope.value === 'all' || state !== DOCUMENT_TASK_STATE.SUCCESS)
    : []
  savePromptConfig(targetUserId.value, config)
  emit('submit', config, stateList)
}

function close() {
  visible.value = false
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog v-model="visible" title="生成问题" @closed="emit('closed')">
    <el-form ref="formRef" :model="form" label-position="top" :disabled="loading || modelLoading" @submit.prevent>
      <el-alert :closable="false" :title="promptTip" type="primary" class="mb-4! items-start! whitespace-pre-line" show-icon>
        <template #icon><MkIcon name="icon_info_filled" class="mt-2" /></template>
      </el-alert>
      <el-form-item label="AI 模型" prop="model_id" :rules="[{ required: true, message: '请选择 AI 模型', trigger: 'change' }]">
        <SelectModel
          v-model="form.model_id"
          v-model:model-params="form.model_params_setting"
          :options="modelOptions"
          :provider-options="providerOptions"
          can-edit-params
          can-add
          teleported
          :disabled="loading || modelLoading"
          @refresh="loadModels"
        />
      </el-form-item>
      <el-form-item label="提示词" prop="prompt" :rules="[{ required: true, whitespace: true, message: '请输入提示词', trigger: 'blur' }]">
        <el-input v-model="form.prompt" type="textarea" :rows="8" />
      </el-form-item>
      <el-form-item v-if="showParagraphScope" label="选择分段">
        <el-radio-group v-model="scope">
          <el-radio value="error">仅执行未成功部分</el-radio>
          <el-radio value="all">全部分段</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消生成问题配置 -->
      <el-button plain :disabled="loading || modelLoading" @click="close">取消</el-button>
      <!-- 提交生成问题任务 -->
      <el-button type="primary" :loading="loading" :disabled="loading || modelLoading || !modelAvailable" @click="handleSubmit">确认</el-button>
    </template>
  </MkDialog>
</template>
