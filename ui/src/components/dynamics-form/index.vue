<template>
  <el-form
    @submit.prevent
    ref="ruleFormRef"
    label-width="130px"
    label-suffix=":"
    v-loading="loading"
    v-bind="$attrs"
    label-position="top"
    require-asterisk-position="right"
  >
    <slot :form_value="formValue"></slot>
    <template v-for="item in formFieldList" :key="item.field">
      <FormItem
        ref="formFieldRef"
        :key="item.field"
        v-if="show(item)"
        @change="change(item, $event)"
        @changeLabel="changeLabel(item, $event)"
        v-bind:modelValue="formValue[item.field]"
        :formfield="item"
        :trigger="trigger"
        :view="view"
        :initDefaultData="initDefaultData"
        :defaultItemWidth="defaultItemWidth"
        :other-params="otherParams"
        :form-value="formValue"
        :formfield-list="formFieldList"
        :parent_field="parent_field"
      >
      </FormItem>
    </template>
  </el-form>
</template>
<script lang="ts" setup>
import type { Dict } from '@/api/type/common'
import FormItem from '@/components/dynamics-form/FormItem.vue'
import type { FormField } from '@/components/dynamics-form/type'
import { ref, onBeforeMount, watch, type Ref, computed } from 'vue'
import type { FormInstance } from 'element-plus'
import type Result from '@/request/Result'
import _ from 'lodash'
import { get, post, put, del } from '@/request/index'
const request = {
  get,
  post,
  put,
  del,
}
defineOptions({ name: 'dynamicsForm' })

const props = withDefaults(
  defineProps<{
    // 页面渲染数据
    render_data:
      | Promise<Result<Array<FormField>>>
      | string
      | Array<FormField>
      | (() => Promise<Result<Array<FormField>>>)
    // 调用接口所需要的其他参数
    otherParams?: any
    // 是否只读
    view?: boolean
    // 默认每个宽度
    defaultItemWidth?: string

    parent_field?: string

    modelValue?: Dict<any>
  }>(),
  { view: false, defaultItemWidth: '75%', otherParams: () => {} },
)

const formValue = ref<Dict<any>>({})

const loading = ref<boolean>(false)

const formFieldList = ref<Array<FormField>>([])

const ruleFormRef = ref<FormInstance>()

const formFieldRef = ref<Array<InstanceType<typeof FormItem>>>([])
/**
 * 当前 field是否展示
 * @param field
 */
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
  return true
}

const emit = defineEmits(['update:modelValue'])
/**
 * 表单字段修改
 * @param field
 * @param value
 */
const change = (field: FormField, value: any) => {
  formValue.value[field.field] = value
}

/**
 * 表单字段修改
 * @param field
 * @param value
 */
const changeLabel = (field: FormField, value: any) => {
  formValue.value[field.label.field] = value
}

watch(
  formValue,
  () => {
    emit('update:modelValue', formValue.value)
  },
  { deep: true },
)
function renderTemplate(template: string, data: any) {
  return template.replace(/\$\{(\w+)\}/g, (match, key) => {
    return data[key] !== undefined ? data[key] : match
  })
}
/**
 * 触发器,用户获取子表单 或者 下拉选项
 * @param field
 * @param loading
 */
const trigger = (
  trigger_field: string,
  trigger_value: any,
  trigger_setting: any,
  self: any,
  loading: Ref<boolean>,
) => {
  const request_call = new Function(
    'self',
    'trigger_setting',
    'request',
    'extra',
    trigger_setting.request
      ? trigger_setting.request
      : 'return  request.get(extra.renderTemplate(trigger_setting.url));',
  )(self, trigger_setting, request, {
    renderTemplate: (url: string) =>
      renderTemplate(url, {
        trigger_value: trigger_value,
        ...props.otherParams,
      }),
  })

  if (!trigger_setting.change && !trigger_setting.change_field) {
    return
  }
  request_call.then((ok: any) => {
    new Function(
      'self',
      'trigger_setting',
      'response',
      'extra',
      trigger_setting.change
        ? trigger_setting.change
        : `self[trigger_setting.change_field]=[
        ...response.data.shared_model.map((m) => {
          return { ...m, type: 'share' }
        }),
        ...response.data.model.map((m) => {
          return { ...m, type: 'workspace' }
        })
      ];`,
    )(self, trigger_setting, ok, { form_data: formValue, getDefault: getFormDefaultValue })
  })
}
/**
 * 初始化默认数据
 */
const initDefaultData = (formField: FormField) => {
  if (
    formField.default_value &&
    (formValue.value[formField.field] === undefined ||
      formValue.value[formField.field] === null ||
      !formValue.value[formField.field]) &&
    formValue.value[formField.field] != false
  ) {
    if (formField.show_default_value === true) {
      formValue.value[formField.field] = formField.default_value
    }
  }
}

onBeforeMount(() => {
  render(props.render_data, props.modelValue)
})

const render = (
  render_data:
    | string
    | Array<FormField>
    | Promise<Result<Array<FormField>>>
    | (() => Promise<Result<Array<FormField>>>),
  data?: Dict<any>,
) => {
  if (typeof render_data == 'string') {
    get(render_data, {}, loading).then((ok) => {
      formFieldList.value = ok.data
    })
  } else if (render_data instanceof Array) {
    formFieldList.value = render_data
  } else if (typeof render_data === 'function') {
    render_data().then((ok: any) => {
      formFieldList.value = ok.data
      const form_data = data ? data : {}
      if (form_data) {
        const value = getFormDefaultValue(formFieldList.value, form_data)
        formValue.value = _.cloneDeep(value)
      }
    })
  } else {
    render_data.then((ok) => {
      formFieldList.value = ok.data
    })
  }
  const form_data = data ? data : {}
  if (form_data) {
    const value = getFormDefaultValue(formFieldList.value, form_data)
    formValue.value = _.cloneDeep(value)
  }
}
const getFormDefaultValue = (fieldList: Array<any>, form_data?: any) => {
  form_data = form_data ? form_data : {}
  const value = fieldList
    .map((item) => {
      if (form_data[item.field] !== undefined) {
        if (item.value_field && item.option_list && item.option_list.length > 0) {
          const value_field = item.value_field
          const find = item.option_list?.find((i: any) => {
            if (typeof form_data[item.field] === 'string') {
              return i[value_field] === form_data[item.field]
            } else {
              return form_data[item.field].indexOf([value_field]) === -1
            }
          })
          if (find) {
            return { [item.field]: form_data[item.field] }
          }
          if (item.show_default_value === true || item.show_default_value === undefined) {
            return { [item.field]: item.default_value }
          }
        } else {
          return { [item.field]: form_data[item.field] }
        }
      }
      if (item.show_default_value === true || item.show_default_value === undefined) {
        return { [item.field]: item.default_value }
      }
      return {}
    })
    .reduce((x, y) => ({ ...x, ...y }), {})
  return value
}
/**
 * 校验函数
 */
const validate = () => {
  return Promise.all([
    ...formFieldRef.value.map((item) => item.validate()),
    ruleFormRef.value ? ruleFormRef.value.validate() : Promise.resolve(),
  ])
}

// 暴露获取当前表单数据函数
defineExpose({
  initDefaultData,
  validate,
  render,
  ruleFormRef,
})
</script>
<style lang="scss" scoped></style>
