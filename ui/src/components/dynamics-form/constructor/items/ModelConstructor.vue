<template>
  <el-form-item
    :label="$t('views.model.modelForm.model_type.label')"
    required
    prop="model_type"
    :rules="[{ required: true, message: $t('views.model.modelForm.model_type.requiredMessage') }]"
  >
    <el-select
      v-model="formValue.model_type"
      :placeholder="$t('views.model.modelForm.model_type.placeholder')"
      @change="handleModelTypeChange"
    >
      <el-option
        v-for="item in modelTypeList"
        :key="item.value"
        :label="item.text"
        :value="item.value"
      />
    </el-select>
  </el-form-item>

  <el-form-item
    :label="$t('views.model.modelForm.model_type.kexuan', '可选模型')"
    required
    prop="provider_list"
    :rules="[
      {
        required: true,
        message: $t('views.model.modelForm.model_type.requiredMessage'),
        type: 'array',
      },
    ]"
  >
    <div class="flex-between w-full">
      <ModelSelect
        multiple
        v-model="selectedIds"
        :placeholder="$t('views.application.form.voicePlay.placeholder')"
        :options="groupedModelOptions"
        @change="handleProviderListChange"
        :model-type="formValue.model_type"
      >
        <template #tag>
          <el-tag
            v-for="provider in formValue.provider_list"
            :key="provider.model_id"
            closable
            type="info"
            @close="removeSelectedModel(provider.model_id)"
            style="margin-right: 4px"
          >
            <div class="flex align-center">
              <span
                v-html="
                  relatedObject(
                    providerOptions,
                    getModelInfo(provider.model_id)?.provider,
                    'provider',
                  )?.icon
                "
                class="model-icon mr-4"
              ></span>
              <span class="mr-4">{{
                relatedObject(
                  providerOptions,
                  getModelInfo(provider.model_id)?.provider,
                  'provider',
                )?.name
              }}</span>
              <span class="mr-4"> > </span>
              <span>{{ getModelInfo(provider.model_id)?.name }}</span>
            </div>
          </el-tag>
        </template>
      </ModelSelect>
    </div>
  </el-form-item>
  <el-form-item
    :label="$t('views.model.modelForm.model_type.moren', '默认模型')"
    required
    :rules="[
      {
        required: true,
        message: $t('views.model.modelForm.model_type.requiredMessage'),
      },
    ]"
    v-if="formValue.provider_list && formValue.provider_list.length > 0"
  >
    <div class="flex-between w-full">
      <el-select
        v-model="formValue.default_value"
        value-key="model_id"
        placeholder="请选择默认模型"
      >
        <el-option-group
          v-for="(modelList, providerName) in selectedModelsOptions"
          :key="providerName"
          :label="relatedObject(providerOptions, providerName, 'provider')?.name"
        >
          <el-option
            v-for="item in modelList"
            :key="item.id"
            :label="item.name"
            :value="getProviderItem(item.id)"
          >
            <div class="flex">
              <span
                v-html="relatedObject(providerOptions, providerName, 'provider')?.icon"
                class="model-icon mr-8"
              ></span>
              <span>{{ item.name }}</span>
            </div>
          </el-option>
        </el-option-group>
      </el-select>
      <div class="ml-8">
        <el-button @click="openParamSetting" @refreshForm="handleParamRefresh">
          <el-icon>
            <Operation />
          </el-icon>
        </el-button>
      </div>
    </div>
  </el-form-item>
  <AIModeParamSettingDialog ref="AIModeParamSettingDialogRef" @refresh="handleParamRefresh" />
</template>
<script setup lang="ts">
import { computed, onMounted, inject, ref } from 'vue'
import { modelTypeList } from '@/views/model/component/data'
import AIModeParamSettingDialog from '@/views/application/component/AIModeParamSettingDialog.vue'
import { groupBy } from 'lodash'
import { providerList as providerOptions } from '../../items/model/provider-data'
import { relatedObject } from '@/utils/array'

const getSelectModelList = inject('getSelectModelList') as Function
const getModelParamsForm = inject('getModelParamsForm') as Function

const props = defineProps<{
  modelValue: any
}>()

const emit = defineEmits(['update:modelValue'])

const formValue = computed({
  set: (item: any) => {
    emit('update:modelValue', item)
  },
  get: () => {
    return props.modelValue
  },
})

const selectedIds = computed({
  get: () => (formValue.value.provider_list || []).map((p: any) => p.model_id),
  set: (newIds: string[]) => {
    const oldList = formValue.value.provider_list || []
    const newList = newIds.map((id: string) => {
      const existing = oldList.find((p: any) => p.model_id === id)
      return existing || { model_id: id, model_params_setting: {} }
    })
    formValue.value.provider_list = newList
    // find new model then get it default value
    const oldIds = oldList.map((p: any) => p.model_id)
    const addedIds = newIds.filter((id: string) => !oldIds.includes(id))
    addedIds.forEach((id: string) => {
      fetchDefaultParams(id)
    })
  },
})

const selectedModelsOptions = computed(() => {
  const ids = (formValue.value.provider_list || []).map((p: any) => p.model_id)
  const filtered = rawModelOptions.value.filter((m: any) => ids.includes(m.id))
  return groupBy(filtered, 'provider')
})

function fetchDefaultParams(modelId: string) {
  if (!getModelParamsForm) return
  getModelParamsForm(modelId).then((res: any) => {
    const formFields = res?.data || []
    const defaults = (res?.data || [])
      .map((item: any) => {
        if (item.show_default_value === false) {
          return { [item.field]: undefined }
        } else {
          return { [item.field]: item.default_value }
        }
      })
      .reduce((x: any, y: any) => ({ ...x, ...y }), {})
    // update to model_params_setting
    const target = formValue.value.provider_list.find((p: any) => p.model_id === modelId)
    if (target) {
      target.model_params_setting = defaults
      target.model_form_field = formFields
    }
  })
}
const AIModeParamSettingDialogRef = ref<InstanceType<typeof AIModeParamSettingDialog>>()

const openParamSetting = () => {
  const dv = formValue.value.default_value
  if (!dv?.model_id) return
  AIModeParamSettingDialogRef.value?.open(dv.model_id, undefined, dv?.model_params_setting)
}

const handleParamRefresh = (paramData: any) => {
  const dv = formValue.value.default_value
  if (dv?.model_id) {
    formValue.value.default_value = { ...dv, model_params_setting: paramData }
    const target = formValue.value.provider_list.find((p: any) => p.model_id === dv.model_id)
    if (target) {
      target.model_params_setting = paramData
    }
  }
}

const rawModelOptions = ref<any[]>([])
const groupedModelOptions = ref<Record<string, any[]>>({})

const fetchModelByType = (type: string) => {
  if (!type || !getSelectModelList) return

  getSelectModelList({ model_type: type }).then((res: any) => {
    rawModelOptions.value = res?.data || []

    groupedModelOptions.value = groupBy(res?.data, 'provider')
  })
}

const handleModelTypeChange = (val: string) => {
  formValue.value.provider_list = []
  formValue.value.default_value = ''

  if (val) {
    fetchModelByType(val)
  } else {
    rawModelOptions.value = []
    groupedModelOptions.value = {}
  }
}

const getModelInfo = (modelId: string) => {
  return rawModelOptions.value.find((item: any) => item.id === modelId)
}

// default_value 赋值
const getProviderItem = (modelId: string) => {
  const found = formValue.value.provider_list.find((p: any) => p.model_id === modelId)
  if (found) {
    const { model_form_field, ...rest } = found
    return rest
  }
  return { model_id: modelId, model_params_setting: {} }
}

function handleProviderListChange() {
  const ids = (formValue.value.provider_list || []).map((p: any) => p.model_id)
  const currentId = formValue.value.default_value?.model_id

  if (currentId && !ids.includes(currentId)) {
    formValue.value.default_value = {}
  }
}

function removeSelectedModel(modelId: string) {
  formValue.value.provider_list = formValue.value.provider_list.filter(
    (p: any) => p.model_id !== modelId,
  )
  handleProviderListChange()
}

const getData = () => {
  const providerList = (formValue.value.provider_list || []).map((p: any) => {
    const modelInfo = getModelInfo(p.model_id)
    return {
      model_id: p.model_id,
      model_name: modelInfo?.name || '',
      provider: modelInfo?.provider || '',
      model_params_setting: p.model_params_setting || {},
      model_form_field: p.model_form_field || [],
    }
  })
  return {
    input_type: 'Model',
    model_type: formValue.value.model_type,
    default_value: formValue.value.default_value,
    attrs: {
      provider_list: providerList,
    },
  }
}

const rander = (form_data: any) => {
  formValue.value.model_type = form_data.model_type
  formValue.value.provider_list = form_data.attrs?.provider_list || []
  formValue.value.default_value = form_data.default_value || ''

  if (form_data.model_type) {
    fetchModelByType(form_data.model_type)
  }
}

defineExpose({ getData, rander })
</script>
<style lang="scss" scoped>
// AI模型选择：添加模型hover样式

.model-icon {
  width: 18px;
}
</style>
