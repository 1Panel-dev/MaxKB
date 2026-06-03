<template>
  <div
    class="inline-form-item"
    v-loading="loading"
    :style="{
      width:
        formfield.input_type === 'SwitchInput' || formfield.input_type === 'DatePicker'
          ? 'auto'
          : formfield.input_type === 'Model' ? '165px' : '150px',
    }"
  >
    <div
      v-if="formfield.input_type === 'SwitchInput'"
      class="flex align-center border border-r-6"
      style="padding: 4px 10px"
    >
      <span :title="switchLabel" class="mr-4 lighter ellipsis" style="max-width: 75px;">
        {{ switchLabel }}
      </span>
      <component
        ref="componentFormRef"
        :view="view"
        v-model="itemValue"
        :is="formfield.input_type"
        :form-field="formfield"
        :other-params="otherParams"
        :field="formfield.field"
        v-bind="attrs"
        :formfield-list="formfieldList"
        size="small"
      ></component>
    </div>
    <component
      v-else
      ref="componentFormRef"
      :view="view"
      v-model="itemValue"
      :is="formfield.input_type"
      :form-field="formfield"
      :other-params="otherParams"
      :field="formfield.field"
      v-bind="attrs"
      :formfield-list="formfieldList"
    ></component>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted, type Ref } from 'vue'
import type { FormField } from '@/components/dynamics-form/type'
import type { Dict } from '@/api/type/common'
import bus from '@/utils/bus'
import { get } from 'lodash'

const props = defineProps<{
  modelValue: any
  formfield: FormField
  view: boolean
  otherParams: any
  trigger: (
    trigger_field: string,
    trigger_value: any,
    trigger_setting: any,
    self: any,
    loading: Ref<boolean>,
  ) => void
  initDefaultData: (formItem: FormField) => void
  defaultItemWidth: string
  formValue: Dict<any>
  formfieldList: Array<FormField>
  parent_field?: string
}>()

const emit = defineEmits(['change', 'changeLabel'])
const loading = ref<boolean>(false)
const componentFormRef = ref<any>()

const itemValue = computed({
  get: () => props.modelValue,
  set: (value: any) => {
    emit('change', value)
    if (props.parent_field) {
      bus.emit(props.parent_field + '.' + props.formfield.field, value)
    } else {
      bus.emit(props.formfield.field, value)
    }
  },
})

const attrs = computed(() => {
  const base = props.formfield.attrs || {}
  if (
    props.formfield.input_type === 'MultiSelect' ||
    props.formfield.input_type === 'Knowledge' ||
    (props.formfield.input_type === 'TreeSelect' && base.multiple)
  ) {
    return {
      ...base,
      'collapse-tags': true,
      'collapse-tags-tooltip': true,
      'max-collapse-tags': 1,
    }
  }
  return base
})

const switchLabel = computed(() => {
  const label =
    typeof props.formfield.label === 'string'
      ? props.formfield.label
      : props.formfield.label?.label || props.formfield.field
  return label
})

const initTrigger = (self: any, trigger_field_dict?: Dict<any>) => {
  if (trigger_field_dict) {
    Object.keys(trigger_field_dict).forEach((key) => {
      const setting = trigger_field_dict[key]
      const triggerValues = setting['values']
      const value = get(props.formValue, key)
      if (triggerValues && triggerValues.length > 0) {
        if (triggerValues.includes(value)) {
          props.trigger(key, value, setting, self, loading)
        }
      } else {
        props.trigger(key, value, setting, self, loading)
      }
    })
  }
}

const onTrigger = (self: any, trigger_field_dict?: Dict<any>) => {
  if (trigger_field_dict) {
    Object.keys(trigger_field_dict).forEach((key) => {
      const setting = trigger_field_dict[key]
      const values: Array<any> = setting.values
      bus.on(key, (v: any) => {
        if (values && values.length > 0) {
          if (values.includes(v)) {
            props.trigger(key, v, setting, self, loading)
          }
        } else {
          props.trigger(key, v, setting, self, loading)
        }
      })
    })
  }
}

onMounted(() => {
  props.initDefaultData(props.formfield)
  initTrigger(props.formfield, props.formfield.relation_trigger_field_dict)
  onTrigger(props.formfield, props.formfield.relation_trigger_field_dict)
})

defineExpose({
  validate: () => {
    if (props.formfield.trigger_type === 'CHILD_FORMS' && componentFormRef.value) {
      return componentFormRef.value.validate()
    }
    return Promise.resolve()
  },
})
</script>
<style lang="scss" scoped>
.inline-form-item {
  flex-shrink: 0;
}
</style>
