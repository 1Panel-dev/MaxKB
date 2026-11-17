<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { KnowledgeCreatePayload, ModelItem, ModelProviderItem } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import { MODEL_STATUS } from '@/api/enums'
import ModelProviderApi from '@/api/admin/model-provider'
import SystemModelApi from '@/api/admin/system/resource-management/model'
import SystemSharedModelApi from '@/api/admin/system/shared-resources/model'
import ModelApi from '@/api/admin/workspace/model'
import SelectModel from '@/components/business/select-model/index.vue'
import { isSystemResource, isSystemSharedResource, isWorkspaceSharedResource } from '@/utils/resource-context'

defineOptions({ name: 'KnowledgeBaseForm' })
const { t } = useI18n({ useScope: 'global' })
const props = withDefaults(defineProps<{ mode?: 'create' | 'setting'; disabled?: boolean }>(), {
  mode: 'create',
})

type KnowledgeBaseDraft = Pick<KnowledgeCreatePayload, 'name' | 'desc' | 'embedding_model_id'>

/* 基本信息与校验 */
const formRef = ref<FormInstance>()
const form = reactive<KnowledgeBaseDraft>({ name: '', desc: '', embedding_model_id: '' })
const rules = computed<FormRules<KnowledgeBaseDraft>>(() => ({
  name: [{ required: true, whitespace: true, message: t('knowledge.fields.name.requiredMessage'), trigger: 'blur' }],
  desc: [{ required: true, whitespace: true, message: t('knowledge.fields.description.requiredMessage'), trigger: 'blur' }],
  embedding_model_id: [{ required: true, message: t('knowledge.fields.embeddingModel.requiredMessage'), trigger: 'change' }],
}))

function validate() {
  return formRef.value?.validate().catch(() => false) ?? Promise.resolve(false)
}

function validateEmbeddingModel() {
  return formRef.value?.validateField('embedding_model_id').catch(() => false) ?? Promise.resolve(false)
}

function reset() {
  Object.assign(form, {
    name: '',
    desc: '',
    embedding_model_id: props.mode === 'create' ? (modelOptions.value.find((model) => model.status === MODEL_STATUS.SUCCESS)?.id ?? '') : '',
  })
  formRef.value?.clearValidate()
}

/* 当前资源范围可用的 Embedding 模型 */
const loading = ref(false)
const modelOptions = ref<ModelItem[]>([])
const providerOptions = ref<ModelProviderItem[]>([])

function loadModelOptions() {
  loading.value = true
  const requestModelApi = isSystemResource() ? SystemModelApi : isSystemSharedResource() ? SystemSharedModelApi : ModelApi
  return Promise.all([
    requestModelApi.getModelListWithShared({ model_type: 'EMBEDDING' }),
    ModelProviderApi.getProviderList({ model_type: 'EMBEDDING' }),
  ])
    .then(([models, providers]) => {
      modelOptions.value = models
      providerOptions.value = providers
      // 仅新建时默认选择首个可用模型；设置时保留详情回填值，包括空值。
      if (props.mode === 'create' && !form.embedding_model_id) {
        form.embedding_model_id = models.find((model) => model.status === MODEL_STATUS.SUCCESS)?.id ?? ''
      }
    })
    .finally(() => {
      loading.value = false
    })
}

onMounted(() => loadModelOptions())
defineExpose({ form, validate, validateEmbeddingModel, reset })
</script>

<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    :validate-on-rule-change="false"
    :disabled="disabled"
    label-position="top"
    require-asterisk-position="right"
    @submit.prevent
  >
    <el-form-item :label="t('common.name.label')" prop="name">
      <el-input
        v-model="form.name"
        :placeholder="t('knowledge.fields.name.placeholder')"
        maxlength="64"
        show-word-limit
        @blur="form.name = form.name.trim()"
      />
    </el-form-item>
    <el-form-item :label="t('common.description.label')" prop="desc">
      <el-input
        v-model="form.desc"
        type="textarea"
        :placeholder="t('knowledge.fields.description.placeholder')"
        maxlength="256"
        show-word-limit
        :rows="3"
        @blur="form.desc = form.desc.trim()"
      />
    </el-form-item>
    <el-form-item v-loading="loading" :label="t('model.types.embedding.label')" prop="embedding_model_id">
      <SelectModel
        teleported
        v-model="form.embedding_model_id"
        :options="modelOptions"
        :provider-options="providerOptions"
        :disabled="disabled || loading"
        :placeholder="t('knowledge.fields.embeddingModel.placeholder')"
        :can-add="!isWorkspaceSharedResource()"
        @refresh="loadModelOptions"
      />
    </el-form-item>
  </el-form>
</template>
