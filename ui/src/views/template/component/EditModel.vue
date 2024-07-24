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
            <div class="flex align-center" style="display: inline-flex">
              <div class="flex-between mr-4">
                <span>模型名称 </span>
              </div>
              <el-tooltip effect="dark" placement="right">
                <template #content>
                  <p>MaxKB 中自定义的模型名称</p>
                </template>
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>
            </div>
          </template>
          <el-input
            v-model="base_form_data.name"
            maxlength="64"
            show-word-limit
            placeholder="请给基础模型设置一个名称"
          />
        </el-form-item>
        <el-form-item prop="permission_type" :rules="base_form_data_rule.permission_type">
          <template #label>
            <span>权限</span>
          </template>

          <el-radio-group v-model="base_form_data.permission_type" class="card__radio">
            <el-row :gutter="16">
              <template v-for="(value, key) of PermissionType" :key="key">
                <el-col :span="12">
                  <el-card
                    shadow="never"
                    class="mb-16"
                    :class="base_form_data.permission_type === key ? 'active' : ''"
                  >
                    <el-radio :value="key" size="large">
                      <p class="mb-4">{{ value }}</p>
                      <el-text type="info">
                        {{ PermissionDesc[key] }}
                      </el-text>
                    </el-radio>
                  </el-card>
                </el-col>
              </template>
            </el-row>
          </el-radio-group>
        </el-form-item>
        <el-form-item prop="model_type" :rules="base_form_data_rule.model_type">
          <template #label>
            <span>模型类型</span>
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
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item prop="model_name" :rules="base_form_data_rule.model_name">
          <template #label>
            <div class="flex align-center" style="display: inline-flex">
              <div class="flex-between mr-4">
                <span>基础模型 </span>
              </div>
              <el-tooltip effect="dark" placement="right">
                <template #content>
                  <p>若下拉选项没有列出想要添加的LLM模型，自定义输入模型名称后回车即可</p>
                  <p>注意，基础模型需要与供应商的模型名称一致</p>
                </template>
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>
            </div>
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
            <el-option v-for="item in base_model_list" :key="item.name" :value="item.name">
              <template #default>
                <div class="flex align-center" style="display: inline-flex">
                  <div class="flex-between mr-4">
                    <span>{{ item.name }} </span>
                  </div>
                  <el-tooltip effect="dark" placement="right" v-if="item.desc">
                    <template #content>
                      <p>{{ item.desc }}</p>
                    </template>
                    <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                  </el-tooltip>
                </div>
              </template>
            </el-option>
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
import { PermissionType, PermissionDesc } from '@/enums/model'

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
  permission_type: string
  model_type: string

  model_name: string
}>({ name: '', model_type: '', model_name: '', permission_type: 'PRIVATE' })

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
      permission_type: model.permission_type,
      model_type: model.model_type,
      model_name: model.model_name
    }
    form_data.value = model.credential
    getModelForm(model.model_name)
  })
  dialogVisible.value = true
}

const close = () => {
  base_form_data.value = { name: '', model_type: '', model_name: '', permission_type: '' }
  dynamicsFormRef.value?.ruleFormRef?.resetFields()
  credential_form_data.value = {}
  model_form_field.value = []
  base_model_list.value = []
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
