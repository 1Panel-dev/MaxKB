<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { MODEL_STATUS } from '@/api/enums'
import type { KnowledgeCreatePayload, ModelItem, ModelProviderItem } from '@/api/types'
import ModelApi from '@/api/admin/workspace/model/model'
import ModelProviderApi from '@/api/admin/model-provider'
import SelectModel from '@/components/business/select-model/index.vue'

defineOptions({ name: 'KnowledgeBaseForm' })
defineProps<{ disabled?: boolean }>()

type KnowledgeBaseDraft = Pick<KnowledgeCreatePayload, 'name' | 'desc' | 'embedding_model_id'>

/* 基本信息与校验 */
const formRef = ref<FormInstance>()
const form = reactive<KnowledgeBaseDraft>({ name: '', desc: '', embedding_model_id: '' })
const rules: FormRules<KnowledgeBaseDraft> = {
  name: [{ required: true, whitespace: true, message: '请输入知识库名称', trigger: 'blur' }],
  desc: [{ required: true, whitespace: true, message: '请输入知识库描述', trigger: 'blur' }],
  embedding_model_id: [{ required: true, message: '请选择向量模型', trigger: 'change' }],
}

function validate() {
  return formRef.value?.validate().catch(() => false) ?? Promise.resolve(false)
}

function reset() {
  Object.assign(form, {
    name: '',
    desc: '',
    embedding_model_id: modelOptions.value.find((model) => model.status === MODEL_STATUS.SUCCESS)?.id ?? '',
  })
  formRef.value?.clearValidate()
}

/* 可用的工作空间及共享 Embedding 模型 */
const loading = ref(false)
const modelOptions = ref<ModelItem[]>([])
const providerOptions = ref<ModelProviderItem[]>([])

function loadModelOptions() {
  loading.value = true
  return Promise.all([ModelApi.getModelListWithShared({ model_type: 'EMBEDDING' }), ModelProviderApi.getProviderListByModelType('EMBEDDING')])
    .then(([models, providers]) => {
      modelOptions.value = models
      providerOptions.value = providers
      // 新建时默认选择首个可用模型，刷新选项时保留已有选择和详情回填值。
      if (!form.embedding_model_id) {
        form.embedding_model_id = models.find((model) => model.status === MODEL_STATUS.SUCCESS)?.id ?? ''
      }
    })
    .finally(() => {
      loading.value = false
    })
}

onMounted(() => loadModelOptions())
defineExpose({ form, validate, reset })
</script>

<template>
  <el-form ref="formRef" :model="form" :rules="rules" :disabled="disabled" label-position="top" require-asterisk-position="right" @submit.prevent>
    <el-form-item label="名称" prop="name">
      <el-input v-model="form.name" placeholder="请输入知识库名称" maxlength="64" show-word-limit @blur="form.name = form.name.trim()" />
    </el-form-item>
    <el-form-item label="描述" prop="desc">
      <el-input
        v-model="form.desc"
        type="textarea"
        placeholder="请输入知识库描述"
        maxlength="256"
        show-word-limit
        :rows="3"
        @blur="form.desc = form.desc.trim()"
      />
    </el-form-item>
    <el-form-item v-loading="loading" label="向量模型" prop="embedding_model_id">
      <SelectModel
        teleported
        v-model="form.embedding_model_id"
        :options="modelOptions"
        :provider-options="providerOptions"
        :disabled="disabled || loading"
        placeholder="请选择向量模型"
        can-add
        @refresh="loadModelOptions"
      />
    </el-form-item>
  </el-form>
</template>
