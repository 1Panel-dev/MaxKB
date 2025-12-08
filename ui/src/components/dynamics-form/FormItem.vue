<template>
  <el-form-item
    v-loading="loading"
    :style="formItemStyle"
    :prop="formfield.field"
    :key="formfield.field"
    :rules="rules"
    :class="formfield.required_asterisk ? 'hide-asterisk' : ''"
  >
    <template #label v-if="formfield.label">
      <FormItemLabel v-if="isString(formfield.label)" :form-field="formfield"></FormItemLabel>
      <component
        v-else
        :is="formfield.label.input_type"
        :label="formfield.label"
        v-model="labelValue"
        :form-value="formValue"
        v-bind="label_attrs"
      ></component>
    </template>
    <component
      ref="componentFormRef"
      :view="view"
      v-model="itemValue"
      :is="formfield.input_type"
      :form-field="formfield"
      :other-params="otherParams"
      :style="componentStyle"
      :field="formfield.field"
      v-bind="attrs"
      :formfield-list="formfieldList"
    ></component>
  </el-form-item>
</template>
<script setup lang="ts">
import { ref, computed, onMounted, type Ref } from 'vue'
import type { FormField } from '@/components/dynamics-form/type'
import FormItemLabel from './FormItemLabel.vue'
import type { Dict } from '@/api/type/common'
import bus from '@/utils/bus'
import { t } from '@/locales'
import { get } from 'lodash'
const props = defineProps<{
  // 双向绑定的值
  modelValue: any

  // 表单Item
  formfield: FormField
  // 是否只读
  view: boolean
  // 调用接口所需要的其他参数
  otherParams: any
  // 获取Options
  trigger: (
    trigger_field: string,
    trigger_value: any,
    trigger_setting: any,
    self: any,
    loading: Ref<boolean>,
  ) => void
  // 初始化默认数据
  initDefaultData: (formItem: FormField) => void
  // 默认每个宽度
  defaultItemWidth: string
  // 表单收集数据
  formValue: Dict<any>

  formfieldList: Array<FormField>

  parent_field?: string
}>()

const emit = defineEmits(['change', 'changeLabel'])

const loading = ref<boolean>(false)

const isString = (value: any) => {
  return typeof value === 'string'
}
const labelValue = computed({
  get: () => {
    return props.formValue[props.formfield.label.field]
  },
  set: (value: any) => {
    emit('changeLabel', value)
    bus.emit(props.formfield.label.field, value)
  },
})
const itemValue = computed({
  get: () => {
    return props.modelValue
  },
  set: (value: any) => {
    emit('change', value)
    if (props.parent_field) {
      bus.emit(props.parent_field + '.' + props.formfield.field, value)
    } else {
      bus.emit(props.formfield.field, value)
    }
  },
})
const componentFormRef = ref<any>()
const label_attrs = computed(() => {
  return props.formfield.label &&
    typeof props.formfield.label !== 'string' &&
    props.formfield.label.attrs
    ? props.formfield.label.attrs
    : {}
})
const props_info = computed(() => {
  return props.formfield.props_info ? props.formfield.props_info : {}
})
/**
 * 表单 item style
 */
const formItemStyle = computed(() => {
  return props_info.value.item_style ? props_info.value.item_style : {}
})

/**
 * 表单错误Msg
 */
const errMsg = computed(() => {
  return props_info.value.err_msg
    ? props_info.value.err_msg
    : isString(props.formfield.label)
      ? props.formfield.label + ' ' + t('dynamicsForm.tip.requiredMessage')
      : props.formfield.label.label + ' ' + t('dynamicsForm.tip.requiredMessage')
})
/**
 * 反序列化
 * @param rule
 */
const to_rule = (rule: any) => {
  if (rule.validator) {
    let validator = (rule: any, value: string, callback: any) => {}
    eval(rule.validator)
    return { ...rule, validator }
  }
  return rule
}

/**
 * 校验
 */
const rules = computed(() => {
  return props_info.value.rules
    ? props_info.value.rules.map(to_rule)
    : {
        message: errMsg.value,
        trigger: props.formfield.input_type === 'Slider' ? 'blur' : ['blur', 'change'],
        required: props.formfield.required === false ? false : true,
      }
})

/**
 * 组件样式
 */
const componentStyle = computed(() => {
  return props_info.value.style ? props_info.value.style : {}
})

/**
 * 组件attrs
 */
const attrs = computed(() => {
  return props.formfield.attrs ? props.formfield.attrs : {}
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
onMounted(() => {
  props.initDefaultData(props.formfield)
  initTrigger(props.formfield, props.formfield.relation_trigger_field_dict)
  initTrigger(props.formfield.label, props.formfield.label?.relation_trigger_field_dict)
  isString(props.formfield.label)
    ? undefined
    : onTrigger(props.formfield.label, props.formfield.label.relation_trigger_field_dict)
  onTrigger(props.formfield, props.formfield.relation_trigger_field_dict)
})
const onTrigger = (self: any, trigger_field_dict?: Dict<any>) => {
  if (trigger_field_dict) {
    const keys = Object.keys(trigger_field_dict)
    keys.forEach((key) => {
      const setting = trigger_field_dict[key]
      const values: Array<any> = setting.values
      // 添加关系
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
const validate = () => {
  if (props.formfield.trigger_type === 'CHILD_FORMS' && componentFormRef.value) {
    return componentFormRef.value.validate()
  }
  return Promise.resolve()
}
defineExpose({ validate })
</script>
<style lang="scss" scoped>
.hide-asterisk {
  ::after {
    display: none;
  }
}
</style>
