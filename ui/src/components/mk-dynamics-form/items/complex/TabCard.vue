<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { computed, ref } from 'vue'
import type { DynamicFormResponse, FormField } from '../../type'
import DynamicsForm from '../../index.vue'
import type { TabPaneName } from 'element-plus'

const props = defineProps<{
  modelValue?: DynamicFormValue[]
  formValue?: DynamicFormValue
  formfieldList?: FormField[]
  field: string
  otherParams: DynamicFormValue
  formField: FormField
  view?: boolean
}>()

const getChildFields = () => {
  return Promise.resolve({
    data: props.formField.children as FormField[],
  } satisfies DynamicFormResponse<FormField[]>)
}

const emit = defineEmits(['update:modelValue', 'change'])

// 校验实例对象
const dynamicsFormRef = ref<InstanceType<typeof DynamicsForm>[]>([])

const localValue = computed<DynamicFormValue[]>({
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

const fieldProps = computed(() => {
  return props.formField.props_info ? props.formField.props_info : {}
})

const tabsLabel = computed(() => {
  return fieldProps.value.tabs_label ? fieldProps.value.tabs_label : 'label'
})
/**
 * 组件样式
 */
const formStyle = computed(() => {
  return fieldProps.value.form_style ? fieldProps.value.form_style : {}
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
  return fieldProps.value.style ? fieldProps.value.style : {}
})

const handleTabsEdit = (targetName: TabPaneName | undefined, action: 'remove' | 'add') => {
  if (action === 'add') {
    localValue.value = [...localValue.value, {}]
    activeTab.value = localValue.value.length
  } else if (action === 'remove') {
    const updatedValue = localValue.value.filter((item, index) => index !== targetName)
    localValue.value = updatedValue
    activeTab.value = updatedValue.length - 1
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
        v-for="(item, index) in localValue"
        :key="index"
        :label="tabsLabel + (index + 1)"
        :name="index"
      >
        <template v-if="formField.children">
          <el-card :style="style">
            <DynamicsForm
              :style="formStyle"
              :view="view"
              ref="ceFormRef"
              v-model="localValue[index]"
              :model="localValue[index]"
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
