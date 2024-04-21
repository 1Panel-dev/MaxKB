<template>
  <el-dialog
    v-model="dialogVisible"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="close"
  >
    <template #header="{ close, titleId, titleClass }">
      <el-breadcrumb separator=">">
        <el-breadcrumb-item
        ><span class="active-breadcrumb">{{
            `编辑 ${providerValue?.name}`
          }}</span></el-breadcrumb-item
        >
      </el-breadcrumb>
    </template>

    <DynamicsForm
      v-loading="formLoading"
      v-model="form_data"
      :render_data="model_form_field"
      :model="form_data"
      ref="dynamicsFormRef"
      label-position="top"
      require-asterisk-position="right"
    >
      <template #default>
        <el-form-item prop="name" :rules="base_form_data_rule.name">
          <template #label>
            <span>模型名称</span>
            <el-tooltip effect="light" placement="right">
              <el-icon style="margin-left: 4px;">
                <QuestionFilled />
              </el-icon>
              <template #content>
                <p>MaxKB 中自定义的模型名称</p>
              </template>
            </el-tooltip>
          </template>
          <el-input
            v-model="base_form_data.name"
            maxlength="20"
            show-word-limit
            placeholder="请给基础模型设置一个名称"
          />
        </el-form-item>
        <el-form-item prop="model_type" :rules="base_form_data_rule.model_type">
          <template #label>
            <span>模型类型</span>
            <el-tooltip effect="light" placement="right">
              <el-icon style="margin-left: 4px;">
                <QuestionFilled />
              </el-icon>
              <template #content>
                <p>大语言模型</p>
              </template>
            </el-tooltip>
          </template>
          <el-select
            v-loading="model_type_loading"
            @change="list_base_model($event)"
            v-model="base_form_data.model_type"
            class="w-full m-2"
            placeholder="请选择模型类型"
          >
            <el-option
              v-for="item in model_type_list"
              :key="item.value"
              :label="item.key"
              :value="item.value"
            ></el-option
            >
          </el-select>
        </el-form-item>
        <el-form-item prop="model_name" :rules="base_form_data_rule.model_name">
          <template #label>
            <span>基础模型</span>
            <el-tooltip effect="light" placement="right">
              <el-icon style="margin-left: 4px;">
                <QuestionFilled />
              </el-icon>
              <template #content>
                <p>为供应商的 LLM 模型，支持自定义输入</p>
                <p>下拉选项是 OpenAI 常用的一些大语言模型如：gpt-3.5-turbo-0613、gpt-3.5-turbo、gpt-4 等</p>
              </template>
            </el-tooltip>
          </template>
          <el-select
            @change="getModelForm($event)"
            v-loading="base_model_loading"
            v-model="base_form_data.model_name"
            class="w-full m-2"
            placeholder="请选择基础模型"
            filterable
            allow-create
            default-first-option
          >
            <el-option
              v-for="item in base_model_list"
              :key="item.name"
              :label="item.name"
              :value="item.name"
            ></el-option
            >
          </el-select>
        </el-form-item>
      </template>
    </DynamicsForm>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="close">取消</el-button>
        <el-button type="primary" @click="submit" :loading="loading"> 修改 </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Provider, BaseModel, Model } from '@/api/type/model'
import type { Dict, KeyValue } from '@/api/type/common'
import ModelApi from '@/api/model'
import type { FormField } from '@/components/dynamics-form/type'
import DynamicsForm from '@/components/dynamics-form/index.vue'
import type { FormRules } from 'element-plus'
import { MsgSuccess } from '@/utils/message'
import { QuestionFilled } from '@element-plus/icons-vue'

const providerValue = ref<Provider>()
const dynamicsFormRef = ref<InstanceType<typeof DynamicsForm>>()
const emit = defineEmits(['change', 'submit'])
const loading = ref<boolean>(false)
const formLoading = ref<boolean>(false)
const model_type_loading = ref<boolean>(false)
const base_model_loading = ref<boolean>(false)
const model_type_list = ref<Array<KeyValue<string, string>>>([])
const modelValue = ref<Model>()
const base_model_list = ref<Array<BaseModel>>([])
const model_form_field = ref<Array<FormField>>([])
const dialogVisible = ref<boolean>(false)

const base_form_data_rule = ref<FormRules>({
  name: { required: true, trigger: 'blur', message: '模型名不能为空' },
  model_type: { required: true, trigger: 'change', message: '模型类型不能为空' },
  model_name: { required: true, trigger: 'change', message: '基础模型不能为空' }
})

const base_form_data = ref<{
  name: string

  model_type: string

  model_name: string
}>({ name: '', model_type: '', model_name: '' })

const credential_form_data = ref<Dict<any>>({})

const form_data = computed({
  get: () => {
    return { ...credential_form_data.value, ...base_form_data.value }
  },
  set: (event: any) => {
    credential_form_data.value = event
  }
})

const getModelForm = (model_name: string) => {
  if (providerValue.value) {
    ModelApi.getModelCreateForm(
      providerValue.value.provider,
      form_data.value.model_type,
      model_name
    ).then((ok) => {
      model_form_field.value = ok.data
      if (modelValue.value) {
        // 渲染动态表单
        dynamicsFormRef.value?.render(model_form_field.value, modelValue.value.credential)
      }
    })
  }
}
const list_base_model = (model_type: any) => {
  if (providerValue.value) {
    ModelApi.listBaseModel(providerValue.value.provider, model_type, base_model_loading).then(
      (ok) => {
        base_model_list.value = ok.data
      }
    )
  }
}
const open = (provider: Provider, model: Model) => {
  modelValue.value = model
  ModelApi.getModelById(model.id, formLoading).then((ok) => {
    modelValue.value = ok.data
    ModelApi.listModelType(model.provider, model_type_loading).then((ok) => {
      model_type_list.value = ok.data
      list_base_model(model.model_type)
    })
    providerValue.value = provider

    base_form_data.value = {
      name: model.name,
      model_type: model.model_type,
      model_name: model.model_name
    }
    form_data.value = model.credential
    getModelForm(model.model_name)
  })
  dialogVisible.value = true
}

const close = () => {
  base_form_data.value = { name: '', model_type: '', model_name: '' }
  dynamicsFormRef.value?.ruleFormRef?.resetFields()
  credential_form_data.value = {}
  dialogVisible.value = false
}

const submit = () => {
  dynamicsFormRef.value?.validate().then(() => {
    if (modelValue.value) {
      ModelApi.updateModel(
        modelValue.value.id,
        {
          ...base_form_data.value,
          credential: credential_form_data.value
        },
        loading
      ).then((ok) => {
        MsgSuccess('修改模型成功')
        close()
        emit('submit')
      })
    }
  })
}

defineExpose({ open, close })
</script>
<style lang="scss" scoped>
.select-provider {
  font-size: 16px;
  color: rgba(100, 106, 115, 1);
  font-weight: 400;
  line-height: 24px;
  cursor: pointer;

  &:hover {
    color: var(--el-color-primary);
  }
}

.active-breadcrumb {
  font-size: 16px;
  color: rgba(31, 35, 41, 1);
  font-weight: 500;
  line-height: 24px;
}
</style>
