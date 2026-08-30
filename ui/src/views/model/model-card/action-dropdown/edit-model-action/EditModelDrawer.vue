<script setup lang="ts">
import { computed, nextTick, reactive, ref } from 'vue'
import type ModelApi from '@/api/admin/workspace/model/model'
import type { BaseModelOption, Dict, ModelItem, ModelPayload, ModelProviderItem } from '@/api/types'
import ProviderApi from '@/api/admin/model-provider'
import { MkDynamicsForm, type DynamicFormValue, type FormField } from '@/components/mk-dynamics-form'
import { MODEL_TYPE_LABELS } from '@/constants'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'EditModelDrawer' })

const props = defineProps<{ api: typeof ModelApi }>()

const emit = defineEmits<{ closed: []; refresh: [] }>()

type ModelDetail = ModelItem & Pick<ModelPayload, 'credential'>

const dynamicsFormRef = ref<InstanceType<typeof MkDynamicsForm>>()
const visible = ref(false)
const loading = ref(false)
const formLoading = ref(false)
const selectedProvider = ref<ModelProviderItem>()
const currentModelId = ref('')
const baseModelOptions = ref<BaseModelOption[]>([])
const credentialFields = ref<FormField[]>([])

const modelForm = reactive<ModelPayload>({ credential: {}, model_name: '', model_type: '', name: '', provider: '' })

const drawerTitle = computed(() => `编辑 ${selectedProvider.value?.name ?? ''}`)

const modelFormData = computed<Dict<DynamicFormValue>>({
  get: () => ({ ...modelForm.credential, model_name: modelForm.model_name, model_type: modelForm.model_type, name: modelForm.name }),
  set: (value) => {
    const credential = { ...value }
    delete credential.model_name
    delete credential.model_type
    delete credential.name
    modelForm.credential = credential
  },
})

function open(provider: ModelProviderItem, model: ModelItem) {
  resetData()
  selectedProvider.value = provider
  currentModelId.value = model.id
  visible.value = true
  formLoading.value = true

  props.api
    .getModelDetail(model.id)
    .then((response) => {
      const detail = response as ModelDetail
      modelForm.credential = detail.credential ?? {}
      modelForm.model_name = detail.model_name
      modelForm.model_type = detail.model_type
      modelForm.name = detail.name
      modelForm.provider = detail.provider

      return Promise.all([ProviderApi.getBaseModelList(detail.provider, detail.model_type), ProviderApi.getModelCreateForm(detail.provider, detail.model_type, detail.model_name)])
    })
    .then(([baseModels, fields]) => {
      baseModelOptions.value = baseModels
      credentialFields.value = fields
      return nextTick(() => dynamicsFormRef.value?.render(fields, modelFormData.value))
    })
    .finally(() => {
      formLoading.value = false
    })
}

function handleBaseModelChange() {
  modelForm.credential = {}
  credentialFields.value = []
  void dynamicsFormRef.value?.render([], modelFormData.value)
  if (!modelForm.model_name) return

  formLoading.value = true
  ProviderApi.getModelCreateForm(modelForm.provider, modelForm.model_type, modelForm.model_name)
    .then((fields) => {
      credentialFields.value = fields
      return dynamicsFormRef.value?.render(fields, modelFormData.value)
    })
    .finally(() => {
      formLoading.value = false
    })
}

function handleSubmit() {
  dynamicsFormRef.value?.validate().then(() => {
    loading.value = true
    return props.api
      .putModel(currentModelId.value, modelForm)
      .then(() => {
        MsgSuccess('修改成功')
        visible.value = false
        emit('refresh')
      })
      .finally(() => {
        loading.value = false
      })
  })
}

function resetData() {
  selectedProvider.value = undefined
  currentModelId.value = ''
  modelForm.credential = {}
  modelForm.model_name = ''
  modelForm.model_type = ''
  modelForm.name = ''
  modelForm.provider = ''
  baseModelOptions.value = []
  credentialFields.value = []
  loading.value = false
  formLoading.value = false
}

function handleClosed() {
  resetData()
  emit('closed')
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" :title="drawerTitle" direction="btt" @closed="handleClosed">
    <div v-loading="formLoading" class="mx-auto w-full max-w-200">
      <MkDynamicsForm ref="dynamicsFormRef" v-model="modelFormData" :render-data="credentialFields">
        <template #default>
          <el-form-item class="mk-hide-asterisk" prop="name" :rules="{ required: true, message: '请输入模型名称', trigger: 'blur' }">
            <template #label>
              <span class="inline-flex items-center gap-2">
                <span class="mk-required"> 模型名称</span>

                <el-tooltip content="MaxKB 中自定义的模型名称" placement="right">
                  <MkIcon name="icon_info_outlined" class="text-N600!"></MkIcon>
                </el-tooltip>
              </span>
            </template>
            <el-input v-model="modelForm.name" maxlength="64" placeholder="请给基础模型设置一个名称" @blur="modelForm.name = modelForm.name.trim()" />
          </el-form-item>

          <el-form-item prop="model_type" label="模型类型" required>
            <el-select v-model="modelForm.model_type" class="w-full" disabled>
              <el-option v-for="(label, value) in MODEL_TYPE_LABELS" :key="value" :label="label" :value="value" />
            </el-select>
          </el-form-item>

          <el-form-item class="mk-hide-asterisk" prop="model_name" :rules="{ required: true, message: '请选择模型类型', trigger: 'change' }">
            <template #label>
              <span class="inline-flex items-center gap-2">
                <span class="mk-required"> 基础模型</span>
                <span class="text-warning"> 列表中未列出的模型，直接输入模型名称，回车即可添加 </span>
              </span>
            </template>
            <el-select
              v-model="modelForm.model_name"
              allow-create
              class="w-full"
              default-first-option
              filterable
              placeholder="请选择基础模型，自定义输入基础模型后回车即可"
              @change="handleBaseModelChange"
            >
              <el-option v-for="option in baseModelOptions" :key="option.name" :label="option.name" :value="option.name">
                <template #default>
                  <div class="flex items-center gap-2">
                    <span>{{ option.name }} </span>
                    <el-tooltip v-if="option.desc" :content="option.desc" placement="right">
                      <MkIcon name="icon_info_outlined" class="text-N600!"></MkIcon>
                    </el-tooltip>
                  </div>
                </template>
              </el-option>
            </el-select>
          </el-form-item>
        </template>
      </MkDynamicsForm>
    </div>

    <template #footer>
      <el-button plain :disabled="loading" @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">保存</el-button>
    </template>
  </MkDrawer>
</template>
