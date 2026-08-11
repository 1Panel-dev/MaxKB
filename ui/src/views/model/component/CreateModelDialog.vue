<template>
  <el-dialog
    v-model="dialogVisible"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="handleClose"
    append-to-body
  >
    <template #header>
      <el-breadcrumb separator=">">
        <el-breadcrumb-item>
          <span @click="toSelectProvider" class="select-provider">
            选择供应商
          </span>
        </el-breadcrumb-item>
        <el-breadcrumb-item>
          <span class="active-breadcrumb">{{ isEdit ? '编辑' : '添加' }} {{ providerValue?.name }}</span>
        </el-breadcrumb-item>
      </el-breadcrumb>
    </template>

    <el-tabs v-model="activeName">
      <el-tab-pane label="基础信息" name="base-info">
        <el-form
          ref="baseFormRef"
          :model="baseFormData"
          label-position="top"
          require-asterisk-position="right"
          class="mb-6"
        >
          <el-form-item
            prop="name"
            label="模型名称"
            :rules="[{ required: true, message: '请输入模型名称', trigger: 'blur' }]"
          >
            <el-input v-model="baseFormData.name" maxlength="64" show-word-limit placeholder="请输入模型名称" />
          </el-form-item>

          <el-form-item
            prop="model_type"
            label="模型类型"
            :rules="[{ required: true, message: '请选择模型类型', trigger: 'change' }]"
          >
            <el-select
              v-loading="modelTypeLoading"
              v-model="baseFormData.model_type"
              class="w-full"
              placeholder="请选择模型类型"
              @change="onModelTypeChange"
            >
              <el-option
                v-for="item in modelTypeList"
                :key="item.value"
                :label="item.key"
                :value="item.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item
            prop="model_name"
            label="基础模型"
            :rules="[{ required: true, message: '请选择基础模型', trigger: 'change' }]"
          >
            <el-select
              v-loading="baseModelLoading"
              v-model="baseFormData.model_name"
              class="w-full"
              placeholder="请选择或输入基础模型"
              filterable
              allow-create
              default-first-option
              @change="onBaseModelChange"
            >
              <el-option
                v-for="item in baseModelList"
                :key="item.name"
                :label="item.name"
                :value="item.name"
              >
                <div class="flex items-center gap-2">
                  <span>{{ item.name }}</span>
                  <el-tooltip v-if="item.desc" effect="dark" :content="item.desc" placement="right">
                    <MkIcon name="icon_warning" :size="14" class="text-gray-400" />
                  </el-tooltip>
                </div>
              </el-option>
            </el-select>
          </el-form-item>

          <!-- Dynamic credential form fields -->
          <CredentialForm
            ref="credentialFormRef"
            v-if="credentialFields.length > 0"
            v-model="credentialFormData"
            :fields="credentialFields"
          />
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="高级配置" name="advanced-info">
        <el-empty v-if="!baseFormData.model_type || !baseFormData.model_name" description="请先选择模型类型和基础模型" />
        <el-empty v-else-if="baseFormData.model_type === 'RERANKER'" description="重排模型无需额外参数配置" />
        <template v-else>
          <div class="flex items-center justify-between mb-4">
            <h5 class="m-0">模型参数</h5>
            <el-button
              text
              type="primary"
              @click.stop="openAddParam"
              :disabled="!['TTS', 'LLM', 'IMAGE', 'TTI', 'TTV', 'ITV', 'STT', 'EMBEDDING'].includes(baseFormData.model_type)"
            >
              <MkIcon name="icon_add_outlined" class="mr-1" /> 添加
            </el-button>
          </div>
          <el-table :data="modelParamsForm" v-if="modelParamsForm.length > 0" class="mb-4">
            <el-table-column prop="label" label="参数名称" show-overflow-tooltip>
              <template #default="{ row }">
                {{ typeof row.label === 'string' ? row.label : row.label?.label || '--' }}
              </template>
            </el-table-column>
            <el-table-column prop="field" label="字段" width="100px" />
            <el-table-column label="输入类型" width="110px">
              <template #default="{ row }">
                <el-tag size="small" type="info">{{ row.input_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="default_value" label="默认值" show-overflow-tooltip />
            <el-table-column label="必填" width="60px">
              <template #default="{ row }">
                <el-switch disabled size="small" :model-value="row.required" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="90px" align="left">
              <template #default="{ row, $index }">
                <el-button text type="primary" size="small" @click.stop="editParam(row, $index)">
                  编辑
                </el-button>
                <el-button text type="danger" size="small" @click="removeParam($index)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </template>
      </el-tab-pane>
    </el-tabs>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="submit" :loading="submitLoading">保存</el-button>
      </span>
    </template>
  </el-dialog>

  <ParamSettingDrawer ref="paramSettingDrawerRef" @confirm="onParamConfirm" />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Provider, BaseModel } from '@/api/type/model'
import ProviderApi from '@/api/model/provider'
import modelApi from '@/api/model/model'
import CredentialForm from './CredentialForm.vue'
import { ElMessage } from 'element-plus'
import type { FormRules } from 'element-plus'
import type { FormField } from '@/api/type/common'

const emit = defineEmits<{
  (e: 'change'): void
  (e: 'submit'): void
}>()

const dialogVisible = ref(false)
const isEdit = ref(false)
const editModelId = ref('')
const providerValue = ref<Provider>()
const submitLoading = ref(false)
const modelTypeLoading = ref(false)
const baseModelLoading = ref(false)
const activeName = ref('base-info')

const baseFormRef = ref()
const credentialFormRef = ref()
const paramSettingDrawerRef = ref()

const baseFormData = ref<{
  name: string
  model_type: string
  model_name: string
}>({
  name: '',
  model_type: '',
  model_name: '',
})

const credentialFormData = ref<Record<string, any>>({})
const credentialFields = ref<FormField[]>([])
const modelTypeList = ref<{ key: string; value: string }[]>([])
const baseModelList = ref<BaseModel[]>([])
const modelParamsForm = ref<any[]>([])

const baseFormRules: FormRules = {
  name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  model_type: [{ required: true, message: '请选择模型类型', trigger: 'change' }],
  model_name: [{ required: true, message: '请选择基础模型', trigger: 'change' }],
}

function open(provider: Provider, model_type?: string) {
  isEdit.value = false
  editModelId.value = ''
  providerValue.value = provider
  dialogVisible.value = true
  activeName.value = 'base-info'
  baseFormData.value = { name: '', model_type: model_type || '', model_name: '' }
  credentialFormData.value = {}
  credentialFields.value = []
  modelParamsForm.value = []
  baseModelList.value = []

  ProviderApi.listModelType(provider.provider, modelTypeLoading).then((ok) => {
    modelTypeList.value = ok.data
  })

  if (model_type) {
    loadBaseModels(model_type)
  }
}

function openEdit(provider: Provider, model: any) {
  isEdit.value = true
  editModelId.value = model.id
  providerValue.value = provider
  dialogVisible.value = true
  activeName.value = 'base-info'

  modelApi.getModelById(model.id).then((ok) => {
    const m = ok.data
    baseFormData.value = {
      name: m.name,
      model_type: m.model_type,
      model_name: m.model_name,
    }
    credentialFormData.value = m.credential || {}

    ProviderApi.listModelType(provider.provider, modelTypeLoading).then((ok2) => {
      modelTypeList.value = ok2.data
    })

    loadBaseModels(m.model_type)
    loadCredentialForm(m.model_type, m.model_name, m.credential)
  })
}

function close() {
  dialogVisible.value = false
  isEdit.value = false
  editModelId.value = ''
  baseFormData.value = { name: '', model_type: '', model_name: '' }
  credentialFormData.value = {}
  credentialFields.value = []
  modelParamsForm.value = []
  baseModelList.value = []
}

function handleClose() {
  if (!isEdit.value) {
    close()
    emit('change')
  } else {
    close()
  }
}

function toSelectProvider() {
  close()
  emit('change')
}

function onModelTypeChange(val: string) {
  baseFormData.value.model_name = ''
  modelParamsForm.value = []
  credentialFields.value = []
  credentialFormData.value = {}
  loadBaseModels(val)
}

function loadBaseModels(model_type: string) {
  if (!providerValue.value) return
  ProviderApi.listBaseModel(providerValue.value.provider, model_type, baseModelLoading).then((ok) => {
    baseModelList.value = ok.data
  })
}

function onBaseModelChange(modelName: string) {
  if (!baseFormData.value.model_type) {
    ElMessage.warning('请先选择模型类型')
    baseFormData.value.model_name = ''
    return
  }
  loadCredentialForm(baseFormData.value.model_type, modelName)
  loadModelParamsForm(baseFormData.value.model_type, modelName)
}

function loadCredentialForm(modelType: string, modelName: string, existingCredential?: any) {
  if (!providerValue.value) return
  ProviderApi.getModelCreateForm(providerValue.value.provider, modelType, modelName).then((ok) => {
    credentialFields.value = ok.data
    if (existingCredential) {
      credentialFormData.value = { ...existingCredential }
    }
  })
}

function loadModelParamsForm(modelType: string, modelName: string) {
  if (!providerValue.value) return
  ProviderApi.listBaseModelParamsForm(providerValue.value.provider, modelType, modelName).then((ok) => {
    modelParamsForm.value = ok.data || []
  })
}

function openAddParam(data?: any, index?: any) {
  paramSettingDrawerRef.value?.open(data, index)
}

function editParam(row: any, index: number) {
  paramSettingDrawerRef.value?.open(row, index)
}

function removeParam(index: number) {
  modelParamsForm.value.splice(index, 1)
}

function onParamConfirm(data: any, index: any) {
  if (index !== null && index !== undefined) {
    modelParamsForm.value.splice(index, 1, data)
  } else {
    modelParamsForm.value.push(data)
  }
}

async function submit() {
  const valid = await baseFormRef.value?.validate().catch(() => false)
  if (!valid) return

  if (credentialFields.value.length > 0 && credentialFormRef.value) {
    const credValid = await credentialFormRef.value.validate()
    if (!credValid) return
  }

  submitLoading.value = true
  try {
    const payload = {
      name: baseFormData.value.name,
      model_type: baseFormData.value.model_type,
      model_name: baseFormData.value.model_name,
      credential: credentialFormData.value,
      provider: providerValue.value!.provider,
      model_params_form: modelParamsForm.value,
    }

    if (isEdit.value && editModelId.value) {
      await modelApi.updateModel(editModelId.value, payload)
      ElMessage.success('修改成功')
    } else {
      await modelApi.createModel(payload)
      ElMessage.success('创建成功')
    }

    close()
    emit('submit')
  } catch (e: any) {
    ElMessage.error(e.message || '操作失败')
  } finally {
    submitLoading.value = false
  }
}

defineExpose({ open, openEdit, close })
</script>

<style lang="scss" scoped>
.select-provider {
  font-size: 14px;
  color: #646a73;
  font-weight: 400;
  cursor: pointer;
  &:hover { color: var(--el-color-primary); }
}
.active-breadcrumb {
  font-size: 14px;
  color: var(--el-text-color-primary);
  font-weight: 500;
}
</style>
