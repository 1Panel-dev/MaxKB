<template>
  <el-dialog
    v-model="dialogVisible"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="close"
  >
    <template #header>
      <el-breadcrumb separator=">">
        <el-breadcrumb-item
          ><span class="active-breadcrumb">{{
            `${$t('common.edit')} ${providerValue?.name}`
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
              <div class="mr-4">
                <span>{{ $t('views.model.modelForm.modeName.label') }} </span>
              </div>
              <el-tooltip effect="dark" placement="right">
                <template #content>
                  <p>{{ $t('views.model.modelForm.modeName.tooltip') }}</p>
                </template>
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>
            </div>
          </template>
          <el-input
            v-model="base_form_data.name"
            maxlength="64"
            show-word-limit
            :placeholder="$t('views.model.modelForm.modeName.placeholder')"
          />
        </el-form-item>
        <el-form-item prop="model_type" :rules="base_form_data_rule.model_type">
          <template #label>
            <span>{{ $t('views.model.modelForm.model_type.label') }}</span>
          </template>
          <el-select
            disabled
            v-loading="model_type_loading"
            @change="list_base_model($event, true)"
            v-model="base_form_data.model_type"
            class="w-full m-2"
            :placeholder="$t('views.model.modelForm.model_type.placeholder')"
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
              <div class="mr-4">
                <span>{{ $t('views.model.modelForm.base_model.label') }} </span>
                <span class="color-danger ml-4" style="color: red">{{
                  $t('views.model.modelForm.base_model.tooltip')
                }}</span>
              </div>
            </div>
          </template>
          <el-select
            @change="getModelForm($event)"
            v-loading="base_model_loading"
            v-model="base_form_data.model_name"
            class="w-full m-2"
            :placeholder="$t('views.model.modelForm.base_model.requiredMessage')"
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
        <el-button @click="close">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submit" :loading="loading">
          {{ $t('common.modify') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import type { Provider, BaseModel, Model } from '@/api/type/model'
import type { Dict, KeyValue } from '@/api/type/common'
import ProviderApi from '@/api/model/provider'
import type { FormField } from '@/components/dynamics-form/type'
import DynamicsForm from '@/components/dynamics-form/index.vue'
import type { FormRules } from 'element-plus'
import { MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'

const route = useRoute()

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

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
  name: {
    required: true,
    trigger: 'blur',
    message: t('views.model.modelForm.modeName.requiredMessage'),
  },
  model_type: {
    required: true,
    trigger: 'change',
    message: t('views.model.modelForm.model_type.requiredMessage'),
  },
  model_name: {
    required: true,
    trigger: 'change',
    message: t('views.model.modelForm.base_model.requiredMessage'),
  },
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
  },
})

const getModelForm = (model_name: string) => {
  if (providerValue.value) {
    ProviderApi.getModelCreateForm(
      providerValue.value.provider,
      form_data.value.model_type,
      model_name,
    ).then((ok) => {
      model_form_field.value = ok.data
      if (modelValue.value) {
        // 渲染动态表单
        dynamicsFormRef.value?.render(model_form_field.value, modelValue.value.credential)
      }
    })
  }
}
const list_base_model = (model_type: any, change?: boolean) => {
  if (change) {
    base_form_data.value.model_name = ''
  }
  if (providerValue.value) {
    ProviderApi.listBaseModel(providerValue.value.provider, model_type, base_model_loading).then(
      (ok) => {
        base_model_list.value = ok.data
      },
    )
  }
}
const open = (provider: Provider, model: Model) => {
  modelValue.value = model
  loadSharedApi({ type: 'model', systemType: apiType.value })
    .getModelById(model.id, formLoading)
    .then((ok: any) => {
      modelValue.value = ok.data
      ProviderApi.listModelType(model.provider, model_type_loading).then((ok) => {
        model_type_list.value = ok.data
        list_base_model(model.model_type)
      })
      providerValue.value = provider

      base_form_data.value = {
        name: model.name,
        model_type: model.model_type,
        model_name: model.model_name,
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
  model_form_field.value = []
  base_model_list.value = []
  dialogVisible.value = false
}

const submit = () => {
  dynamicsFormRef.value?.validate().then(() => {
    if (modelValue.value) {
      loadSharedApi({ type: 'model', systemType: apiType.value })
        .updateModel(
          modelValue.value.id,
          {
            ...base_form_data.value,
            credential: credential_form_data.value,
          },
          loading,
        )
        .then((ok: any) => {
          MsgSuccess(t('views.model.tip.updateSuccessMessage'))
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
  color: var(--el-text-color-primary);
  font-weight: 500;
  line-height: 24px;
}
</style>
