<template>
  <div class="inline-params" v-if="fieldList.length > 0">
    <template v-for="item in exposedFields" :key="item.field">
      <InlineFormItem
        v-if="show(item)"
        v-bind:modelValue="formValue[item.field]"
        @change="change(item, $event)"
        :formfield="item"
        :trigger="trigger"
        :view="false"
        :initDefaultData="initDefaultData"
        defaultItemWidth="auto"
        :other-params="{}"
        :form-value="formValue"
        :formfield-list="fieldList"
      />
    </template>
    <el-button
      ref="triggerBtnRef"
      style="padding: 8px"
      v-if="dialogFields.length > 0"
      @click="emit('openDialog')"
    >
      <AppIcon iconName="app-all-menu"></AppIcon>
    </el-button>
  </div>
</template>
<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'
import type { FormField } from '@/components/dynamics-form/type'
import type { Dict } from '@/api/type/common'
import { computeVisibilityMap } from '@/components/dynamics-form/visibility'
import InlineFormItem from './InlineFormItem.vue'
import { t } from '@/locales'
import _ from 'lodash'
import { MsgWarning } from '@/utils/message'

const props = defineProps<{
  application: any
  formData: any
  maxExposed?: number
}>()

const emit = defineEmits(['update:formData', 'openDialog'])

const triggerBtnRef = ref()

const fieldList = ref<FormField[]>([])
const formValue = ref<Dict<any>>({})
const setting = ref<{ exposed_fields: string[]; menu_title: string }>({
  exposed_fields: [],
  menu_title: t('common.moreSettings'),
})

watch(
  formValue,
  () => {
    emit('update:formData', formValue.value)
  },
  { deep: true },
)

watch(
  () => props.formData,
  (val) => {
    if (val && JSON.stringify(val) !== JSON.stringify(formValue.value)) {
      formValue.value = val
      for (const field of fieldList.value) {
        if (
          field.default_value &&
          !formValue.value[field.field] &&
          formValue.value[field.field] !== false &&
          (field.show_default_value === true || field.show_default_value === undefined)
        ) {
          formValue.value[field.field] = field.default_value
        }
      }
    }
  },
  { immediate: true },
)

watch(
  () => props.application,
  () => {
    handleInputFieldList()
  },
)

function handleInputFieldList() {
  props.application?.work_flow?.nodes
    ?.filter((v: any) => v.id === 'base-node')
    .map((v: any) => {
      fieldList.value = v.properties.user_input_field_list
        ? v.properties.user_input_field_list.map((v: any) => {
            let field
            switch (v.type) {
              case 'input':
                field = {
                  field: v.variable,
                  input_type: 'TextInput',
                  label: v.name,
                  default_value: v.default_value,
                  required: v.is_required,
                }
                break
              case 'select':
                field = {
                  field: v.variable,
                  input_type: 'SingleSelect',
                  label: v.name,
                  default_value: v.default_value,
                  required: v.is_required,
                  option_list: v.optionList.map((o: any) => ({ key: o, value: o })),
                }
                break
              case 'date':
                field = {
                  field: v.variable,
                  input_type: 'DatePicker',
                  label: v.name,
                  default_value: v.default_value,
                  required: v.is_required,
                  attrs: {
                    format: 'YYYY-MM-DD HH:mm:ss',
                    'value-format': 'YYYY-MM-DD HH:mm:ss',
                    type: 'datetime',
                  },
                }
                break
              default:
                field = { ...v }
                break
            }
            const isEmpty =
              !field.default_value ||
              (Array.isArray(field.default_value) && field.default_value.length === 0) ||
              (typeof field.default_value === 'object' &&
                Object.keys(field.default_value).length === 0)
            if (isEmpty) {
              const label =
                typeof field.label === 'string' ? field.label : field.label?.label || field.field
              const truncated = label.length > 5 ? label.slice(0, 5) + '…' : label
              field.attrs = { ...field.attrs, placeholder: truncated }
            }
            field.attrs = {
              ...field.attrs,
              popperHeader: {
                label:
                  typeof field.label === 'string' ? field.label : field.label?.label || field.field,
                required: field.required,
                tooltip: typeof field.label === 'object' ? field.label?.attrs?.tooltip : undefined,
              },
            }
            return field
          })
        : []

      setting.value = v.properties.user_input_field_list_setting || {
        exposed_fields: [],
        menu_title: t('common.moreSettings'),
      }
    })
}

const exposedFields = computed(() => {
  if (setting.value.exposed_fields.length === 0) return []
  return setting.value.exposed_fields
    .map((field: string) => fieldList.value.find((f) => f.field === field))
    .filter(Boolean)
    .slice(0, props.maxExposed ?? 3) as FormField[]
})

const dialogFields = computed(() => {
  const inlineKeys = new Set(exposedFields.value.map((f) => f.field))
  return fieldList.value.filter((f) => !inlineKeys.has(f.field))
})

const visibilityMap = computed(() => computeVisibilityMap(fieldList.value, formValue.value))

const show = (field: FormField) => {
  if (field.relation_show_field_dict) {
    const keys = Object.keys(field.relation_show_field_dict)
    for (const index in keys) {
      const key = keys[index]
      const v = _.get(formValue.value, key)
      if (v && v !== undefined && v !== null) {
        const values = field.relation_show_field_dict[key]
        if (values && values.length > 0) {
          return values.includes(v)
        } else {
          return true
        }
      } else {
        return false
      }
    }
  }
  if (field.visibility_rules?.node_id) {
    return visibilityMap.value[field.field] ?? true
  }
  return true
}

defineExpose({
  triggerBtnRef,
  validate: () => {
    for (const field of fieldList.value) {
      if (!show(field)) {
        formValue.value[field.field] = null
      }
    }

    for (const item of exposedFields.value) {
      if (!show(item)) continue
      const isRequired = item.required ?? item.is_required
      if (isRequired) {
        const value = formValue.value[item.field]
        const isEmpty =
          value === undefined ||
          value === null ||
          value === '' ||
          (Array.isArray(value) && value.length === 0) ||
          (typeof value === 'object' && Object.keys(value).length === 0)
        if (isEmpty) {
          const name = typeof item.label === 'string' ? item.label : item.label?.label || item.field
          MsgWarning(`${name} 为必填属性`)
          return Promise.reject(false)
        }
      }
    }
    return Promise.resolve(true)
  },
})

const change = (field: FormField, value: any) => {
  formValue.value[field.field] = value
}

const trigger = (
  trigger_field: string,
  trigger_value: any,
  trigger_setting: any,
  self: any,
  loading: any,
) => {
  // 暂留空，后续按需补充
}

const initDefaultData = (formField: FormField) => {
  if (
    formField.default_value &&
    (formValue.value[formField.field] === undefined ||
      formValue.value[formField.field] === null ||
      !formValue.value[formField.field]) &&
    formValue.value[formField.field] != false
  ) {
    if (formField.show_default_value === true || formField.show_default_value === undefined) {
      formValue.value[formField.field] = formField.default_value
    }
  }
}

onMounted(() => {
  handleInputFieldList()
})
</script>
<style lang="scss" scoped>
.inline-params {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  padding: 4px 0;
}
</style>
