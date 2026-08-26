<script lang="ts" setup>
import type { Dict } from '@/api/types/common'
import FormItem from '@/components/mk-dynamics-form/FormItem.vue'
import type { FormField } from '@/components/mk-dynamics-form/type'
import { ref, onBeforeMount, watch, type Ref, nextTick, computed } from 'vue'
import type { FormInstance } from 'element-plus'
import type { ApiResponse } from '@/api/admin/core/types'
import _ from 'lodash'
import { get, post, put, del } from '@/api/admin/core/request'
import type { CompareOptions, VisibilityCondition, VisibilityRules } from './type'
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
      | Promise<ApiResponse<Array<FormField>>>
      | string
      | Array<FormField>
      | (() => Promise<ApiResponse<Array<FormField>>>)
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

// ===== 显隐规则求值 =====
const containImpl = (source: any, target: any): boolean => {
  if (Array.isArray(target)) {
    return target.every((t) => containImpl(source, t))
  }
  const t = String(target)
  if (typeof source === 'string') return source.includes(t)
  if (Array.isArray(source)) return source.some((item) => String(item) === t)
  return String(source).includes(t)
}

const numOrStrCmp = (
  left: any,
  right: any,
  numFn: (a: number, b: number) => boolean,
  strFn: (a: string, b: string) => boolean,
): boolean => {
  const a = Number(left)
  const b = Number(right)
  if (!Number.isNaN(a) && !Number.isNaN(b)) return numFn(a, b)
  try {
    return strFn(String(left), String(right))
  } catch {
    return false
  }
}

const compareHandlers: Record<CompareOptions, (left: any, right: any) => boolean> = {
  eq: (l, r) => String(l) === String(r),
  not_eq: (l, r) => String(l) !== String(r),
  contain: (l, r) => containImpl(l, r),
  not_contain: (l, r) => !containImpl(l, r),
  is_true: (l) => l === true,
  is_not_true: (l) => l !== true,
  gt: (l, r) =>
    numOrStrCmp(
      l,
      r,
      (a, b) => a > b,
      (a, b) => a > b,
    ),
  ge: (l, r) =>
    numOrStrCmp(
      l,
      r,
      (a, b) => a >= b,
      (a, b) => a >= b,
    ),
  lt: (l, r) =>
    numOrStrCmp(
      l,
      r,
      (a, b) => a < b,
      (a, b) => a < b,
    ),
  le: (l, r) =>
    numOrStrCmp(
      l,
      r,
      (a, b) => a <= b,
      (a, b) => a <= b,
    ),
}

const compareByOp = (left: any, op: CompareOptions, right: any): boolean => {
  const fn = compareHandlers[op]
  if (!fn) throw new Error(`Unknown compare op: ${op}`)
  return fn(left, right)
}

/**
 * 取条件左值：self 为真时实时从本表单 formValue 取，否则用预填 leftValue。
 */
const lookupLeft = (cond: VisibilityCondition, values: Dict<any>): any => {
  if (cond.self) {
    return values?.[cond.field[1]]
  }
  return cond.leftValue
}

/**
 * 对单条 visibility_rules 求值，返回该字段是否可见。
 */
const evaluateVisibility = (
  rules: VisibilityRules | null | undefined,
  values: Dict<any>,
): boolean => {
  if (!rules || !rules.conditions || rules.conditions.length === 0) {
    return true
  }
  const results = rules.conditions.map((cond) => {
    const left = lookupLeft(cond, values)
    if (left == null && cond.compare !== 'is_true' && cond.compare !== 'is_not_true') {
      return false
    }
    return compareByOp(left, cond.compare as CompareOptions, cond.value)
  })
  const matched = rules.condition === 'or' ? results.some(Boolean) : results.every(Boolean)
  return rules.action === 'show' ? matched : !matched
}

/**
 * 单向扫描当前表单字段列表，计算显隐表。
 * 前面字段被隐藏后其值置空，级联影响后续字段判定。
 */
const visibilityMap = computed<Dict<boolean>>(() => {
  const copy: Dict<any> = { ...formValue.value }
  const map: Dict<boolean> = {}
  for (const field of formFieldList.value) {
    if (!field.visibility_rules?.conditions?.length) {
      map[field.field] = true
      continue
    }
    const visible = evaluateVisibility(field.visibility_rules, copy)
    map[field.field] = visible
    if (!visible) {
      copy[field.field] = null
    }
  }
  return map
})

/**
 * 当前 field是否展示
 * @param field
 */
const show = (field: FormField) => {
  if (field.visibility_rules?.conditions?.length) {
    return visibilityMap.value[field.field] ?? true
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

watch(
  () => props.modelValue,
  (val) => {
    if (!val) return
    if (_.isEqual(val, formValue.value)) return
    formValue.value = _.cloneDeep(val)
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
    | Promise<ApiResponse<Array<FormField>>>
    | (() => Promise<ApiResponse<Array<FormField>>>),
  data?: Dict<any>,
) => {
  formFieldList.value = []
  nextTick(() => {
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
  })
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
              return form_data[item.field]
                ? form_data[item.field].indexOf([value_field]) === -1
                : false
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
    .reduce((x, y) => ({ ...x, ...y }), { ...form_data })
  return value
}
/**
 * 校验函数
 */
const validate = () => {
  for (const field of formFieldList.value) {
    if (!show(field)) {
      formValue.value[field.field] = null
    }
  }
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
