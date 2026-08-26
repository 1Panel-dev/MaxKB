<script setup lang="ts">
import type { MkDynamicFormValue } from '../../type'
import { computed, ref } from 'vue'
import type { DynamicFormResponse, FormField } from '../../type'
import DynamicsForm from '../../index.vue'
import type { TabPaneName } from 'element-plus'

const props = defineProps<{
  modelValue?: Array<MkDynamicFormValue>
  formValue?: MkDynamicFormValue
  formfieldList?: Array<FormField>
  field: string
  otherParams: MkDynamicFormValue
  formField: FormField
  view?: boolean
}>()

const getChildFields = () => {
  return Promise.resolve({
    data: props.formField.children as Array<FormField>,
  } satisfies DynamicFormResponse<Array<FormField>>)
}

const emit = defineEmits(['update:modelValue', 'change'])

// 校验实例对象
const dynamicsFormRef = ref<Array<InstanceType<typeof DynamicsForm>>>([])

const _data = computed<Array<MkDynamicFormValue>>({
  get() {
    if (props.modelValue) {
      return props.modelValue
    } else {
      emit('update:modelValue', [{}])
      return []
    }
  },
  set(value) {
    emit('update:modelValue', value)
  },
})

const props_info = computed(() => {
  return props.formField.props_info ? props.formField.props_info : {}
})

const tabs_label = computed(() => {
  return props_info.value.tabs_label ? props_info.value.tabs_label : 'label'
})
/**
 * 组件样式
 */
const formStyle = computed(() => {
  return props_info.value.form_style ? props_info.value.form_style : {}
})

const attr = computed(() => {
  if (props.formField.attrs) {
    return props.formField.attrs
  }
  return {}
})
const activeTab = ref(0)

/**
 * 校验方法
 */
function validate() {
  return Promise.all(dynamicsFormRef.value.map((item) => item.validate()))
}
const other = computed(() => {
  return { ...(props.formValue ? props.formValue : {}), ...props.otherParams }
})
const style = computed(() => {
  return props_info.value.style ? props_info.value.style : {}
})

const handleTabsEdit = (targetName: TabPaneName | undefined, action: 'remove' | 'add') => {
  if (action === 'add') {
    _data.value = [..._data.value, {}]
    activeTab.value = _data.value.length
  } else if (action === 'remove') {
    const update_value = _data.value.filter((item, index) => index !== targetName)
    _data.value = update_value
    activeTab.value = update_value.length - 1
  }
}

defineExpose({
  validate,
  field: props.field,
})
</script>

<template v-loading="_loading">
  <div style="width: 100%">
    <el-tabs v-model="activeTab" editable @edit="handleTabsEdit" type="card">
      <el-tab-pane
        v-for="(item, index) in _data"
        :key="index"
        :label="tabs_label + (index + 1)"
        :name="index"
      >
        <template v-if="formField.children">
          <el-card :style="style">
            <DynamicsForm
              :style="formStyle"
              :view="view"
              ref="ceFormRef"
              v-model="_data[index]"
              :model="_data[index]"
              :other-params="other"
              :render-data="getChildFields()"
              v-bind="attr"
              :parent-field="formField.field + '.' + index"
              label-position="top"
              require-asterisk-position="right"
            ></DynamicsForm>
          </el-card>
        </template>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
