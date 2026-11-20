<script setup lang="ts">
import { computed, provide, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { DocumentTaskState, ModelItem, ModelProviderItem, RelatedQuestionsConfig } from '@/api/types'
import type { FormInstance } from 'element-plus'
import { DOCUMENT_TASK_STATE, MODEL_STATUS } from '@/api/enums'
import ModelProviderApi from '@/api/admin/model-provider'
import SystemResourceModelApi from '@/api/admin/system/resource-management/model'
import SystemSharedModelApi from '@/api/admin/system/shared-resources/model'
import ModelApi from '@/api/admin/workspace/model'
import SelectModel from '@/components/business/select-model/index.vue'
import { getPromptConfig, savePromptConfig } from './prompt-cache'
import { useStore } from '@/stores'
import { isSystemResource, isSystemSharedResource } from '@/utils/resource-context'

defineOptions({ name: 'GenerateQuestionsDialog' })
const { t } = useI18n({ useScope: 'global' })
const props = withDefaults(defineProps<{ loading: boolean; showParagraphScope?: boolean }>(), {
  showParagraphScope: true,
})
const emit = defineEmits<{ submit: [config: RelatedQuestionsConfig, stateList: DocumentTaskState[]]; closed: [] }>()
const { user } = useStore()
const promptPlaceholders = { data: '{data}', questionTags: '<question></question>' }
const promptTip = computed(() => t('knowledge.generateQuestions.prompt.description', promptPlaceholders))

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
  return Promise.all([requestModelApi.value.getModelListWithShared({ model_type: 'LLM' }), ModelProviderApi.getProviderList({ model_type: 'LLM' })])
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
  form.value = getPromptConfig(targetUserId.value, t('knowledge.generateQuestions.prompt.defaultValue', promptPlaceholders))
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
  <MkDialog v-model="visible" :title="t('knowledge.generateQuestions.title')" @closed="emit('closed')">
    <el-form
      ref="formRef"
      :model="form"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      v-loading="loading || modelLoading"
      @submit.prevent
    >
      <el-alert :closable="false" type="primary" class="mb-4!" show-icon>
        <template #icon><MkIcon name="icon_info_filled" /></template>
        {{ promptTip }}
      </el-alert>
      <el-form-item
        :label="t('model.ai.label')"
        prop="model_id"
        :rules="[{ required: true, message: t('model.ai.requiredMessage'), trigger: 'change' }]"
      >
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
      <el-form-item
        :label="t('knowledge.generateQuestions.prompt.label')"
        prop="prompt"
        :rules="[{ required: true, whitespace: true, message: t('knowledge.generateQuestions.prompt.requiredMessage'), trigger: 'blur' }]"
      >
        <el-input v-model="form.prompt" type="textarea" :rows="8" />
      </el-form-item>
      <el-form-item v-if="showParagraphScope" :label="t('knowledge.paragraphScope.label')">
        <el-radio-group v-model="scope">
          <el-radio value="error">{{ t('knowledge.paragraphScope.unsuccessful') }}</el-radio>
          <el-radio value="all">{{ t('knowledge.paragraphScope.all') }}</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消生成问题配置 -->
      <el-button plain :disabled="loading || modelLoading" @click="close">{{ t('common.actions.cancel') }}</el-button>
      <!-- 提交生成问题任务 -->
      <el-button type="primary" :loading="loading" :disabled="loading || modelLoading || !modelAvailable" @click="handleSubmit">
        {{ t('common.actions.comfirm') }}
      </el-button>
    </template>
  </MkDialog>
</template>
