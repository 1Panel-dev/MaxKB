<script setup lang="ts">
import { ref } from 'vue'
import type { FormInstance } from 'element-plus'
import { DOCUMENT_TASK_STATE } from '@/api/enums'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import DocumentApi from '@/api/admin/workspace/knowledge/document'
import ModelApi from '@/api/admin/workspace/model'
import ModelProviderApi from '@/api/admin/model-provider'
import SelectModel from '@/components/business/select-model/index.vue'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'ButtonDocumentTask' })
const props = defineProps<{
  knowledgeId: string
  documentIds: string[]
  action: 'embedding' | 'generate'
  batch?: boolean
  display?: 'menu' | 'button'
  disabled?: boolean
}>()
const emit = defineEmits<{ refresh: [] }>()
const visible = ref(false)
const loading = ref(false)
const optionLoading = ref(false)
const task = ref<'embedding' | 'generate'>('embedding')
const targetDocumentIds = ref<string[]>([])
const scope = ref<'error' | 'all'>('error')
const formRef = ref<FormInstance>()
const form = ref({ model_id: '', model_params_setting: {} as Record<string, unknown>, prompt: '' })
const modelOptions = ref<ModelItem[]>([])
const providerOptions = ref<ModelProviderItem[]>([])

function handleOpenDialog() {
  if (props.disabled || loading.value || optionLoading.value || !props.documentIds.length) return
  const ids = props.documentIds
  const action = props.action
  targetDocumentIds.value = [...ids]
  task.value = action
  scope.value = 'error'
  form.value = {
    model_id: '',
    model_params_setting: {},
    prompt: '请根据以下内容生成相关问题，每个问题使用 <question></question> 标签包裹。只输出问题。\n内容：{data}',
  }
  visible.value = true
  if (action === 'generate') {
    optionLoading.value = true
    Promise.all([ModelApi.getModelListWithShared({ model_type: 'LLM' }), ModelProviderApi.getProviderListByModelType('LLM')])
      .then(([models, providers]) => {
        modelOptions.value = models
        providerOptions.value = providers
      })
      .catch(() => {
        // 请求层统一提示错误，保留当前输入。
      })
      .finally(() => {
        optionLoading.value = false
      })
  }
}

async function handleSubmit() {
  if (loading.value || optionLoading.value) return
  if (task.value === 'generate' && !(await formRef.value?.validate().catch(() => false))) return
  loading.value = true
  const stateList = Object.values(DOCUMENT_TASK_STATE).filter((state) => scope.value === 'all' || state !== DOCUMENT_TASK_STATE.SUCCESS)
  const request =
    task.value === 'embedding'
      ? DocumentApi.putBatchRefreshDocuments(props.knowledgeId, targetDocumentIds.value, stateList)
      : DocumentApi.putGenerateDocumentQuestions(props.knowledgeId, {
          ...form.value,
          document_id_list: targetDocumentIds.value,
          state_list: stateList,
        })
  return request
    .then(() => {
      MsgSuccess('任务已提交')
      visible.value = false
      emit('refresh')
    })
    .catch(() => {
      // 请求层统一提示错误，保留当前输入。
    })
    .finally(() => {
      loading.value = false
    })
}

function handleClosed() {
  targetDocumentIds.value = []
  formRef.value?.clearValidate()
}
</script>

<template>
  <!-- 文档向量化或生成问题入口 -->
  <el-button v-if="batch" :disabled="disabled || loading || !documentIds.length" @click="handleOpenDialog">
    {{ action === 'embedding' ? '向量化' : '生成问题' }}
  </el-button>
  <MkAction
    v-else
    :display="display ?? 'menu'"
    :label="action === 'embedding' ? '向量化' : '生成问题'"
    :icon="action === 'embedding' ? 'icon_refresh_outlined' : 'icon_new-chat_outlined'"
    :disabled="disabled || loading || !documentIds.length"
    @click="handleOpenDialog"
  />
  <MkDialog v-model="visible" :title="task === 'embedding' ? '向量化' : '生成问题'" :show-close="!loading && !optionLoading" @closed="handleClosed">
    <el-form ref="formRef" :model="form" label-position="top" :disabled="loading || optionLoading" @submit.prevent>
      <template v-if="task === 'generate'">
        <p class="mb-4 text-N600">提示词使用 {data} 引用分段内容，生成的问题需使用 &lt;question&gt;&lt;/question&gt; 标签包裹。</p>
        <el-form-item label="AI 模型" prop="model_id" :rules="[{ required: true, message: '请选择 AI 模型', trigger: 'change' }]">
          <SelectModel
            v-model="form.model_id"
            v-model:model-params="form.model_params_setting"
            :options="modelOptions"
            :provider-options="providerOptions"
            can-edit-params
            :disabled="loading || optionLoading"
          />
        </el-form-item>
        <el-form-item
          label="提示词"
          prop="prompt"
          :rules="[
            { required: true, message: '请输入提示词', trigger: 'blur' },
            { whitespace: true, message: '提示词不能为空白', trigger: 'blur' },
          ]"
        >
          <el-input v-model="form.prompt" type="textarea" :rows="7" />
        </el-form-item>
      </template>
      <el-form-item label="选择分段">
        <el-radio-group v-model="scope">
          <el-radio value="error">未成功的分段</el-radio>
          <el-radio value="all">全部分段</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消任务配置 -->
      <el-button :disabled="loading || optionLoading" @click="visible = false">取消</el-button>
      <!-- 提交文档任务 -->
      <el-button type="primary" :loading="loading" :disabled="optionLoading" @click="handleSubmit">确认</el-button>
    </template>
  </MkDialog>
</template>
