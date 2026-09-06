<script setup lang="ts">
import { onMounted, ref, nextTick } from 'vue'
import { dynamicFormTypeOptions } from '@/components/mk-dynamics-form/constant'
import VisibilityConstructor from './visibility/index.vue'
import BasicInfoConstructor from './BasicInfoConstructor.vue'
import type {
  DynamicFormConstructorExpose,
  DynamicFormConstructorOption,
  DynamicFormConstructorState,
  FormField,
  VisibilityFieldOption,
  VisibilityRules,
} from '../type'

interface VisibilityConstructorExpose {
  getData: () => VisibilityRules | null
  render: (rules: VisibilityRules | null) => void
  validate: () => Promise<void>
}

// $attrs（label-position 等）显式透传给 BasicInfoConstructor 的 el-form
defineOptions({ name: 'MkDynamicsFormConstructor', inheritAttrs: false })
// 声明 v-model 事件，避免其监听器漏入 $attrs 透传到子表单
defineEmits<{ (event: 'update:modelValue', value: Partial<FormField>): void }>()

const props = withDefaults(
  defineProps<{
    modelValue?: Partial<FormField>
    // “基本信息”中可选的组件类型；不传时使用全部默认类型，value 使用带 Constructor 后缀的配置器名称。
    fieldTypeOptions?: DynamicFormConstructorOption[]
    // 是否展示“显隐设置”页签，默认关闭。
    enableVisibility?: boolean
    // “显隐设置”中条件左侧可引用的变量，启用显隐设置时使用；变量类型和选项用于匹配比较方式及值输入控件。
    // 由调用方提供可引用范围，例如上游节点字段、当前字段之前的表单字段，不控制可选的组件类型。
    leftOptions?: VisibilityFieldOption[]
  }>(),
  {
    enableVisibility: false,
    fieldTypeOptions: () => dynamicFormTypeOptions.map((item) => ({ label: item.label, value: `${item.value}Constructor` })),
  },
)

const activeTab = ref('basic')
const basicRef = ref<DynamicFormConstructorExpose>()
const visibilityRef = ref<VisibilityConstructorExpose>()
const visibilityRules = ref<VisibilityRules | null>(null)

const formData = ref<DynamicFormConstructorState>({ label: '', field: '', tooltip: '', required: false, input_type: '' })

const getData = (): FormField => {
  const fieldData = basicRef.value?.getData() ?? {}
  return {
    ...fieldData,
    field: fieldData.field ?? formData.value.field,
    input_type: fieldData.input_type ?? formData.value.input_type.replace(/Constructor$/, ''),
    visibility_rules: visibilityRef.value?.getData() ?? null,
  }
}

const validate = () => {
  const promises: Promise<unknown>[] = []
  if (basicRef.value?.validate) {
    promises.push(basicRef.value.validate())
  }
  if (visibilityRef.value?.validate) {
    promises.push(visibilityRef.value.validate())
  }
  return Promise.all(promises)
}

onMounted(() => {
  if (props.modelValue) {
    render(props.modelValue)
  }
})

const render = (data: Partial<FormField>) => {
  const fieldData: FormField = { ...data, field: data.field ?? '', input_type: data.input_type ?? '' }
  visibilityRules.value = fieldData.visibility_rules ?? null
  nextTick(() => {
    basicRef.value?.render(fieldData)
    visibilityRef.value?.render(fieldData.visibility_rules ?? null)
  })
}

defineExpose({ getData, validate, render })
</script>

<template>
  <div v-if="enableVisibility" class="flex max-h-[inherit] min-h-0 flex-col">
    <el-tabs v-model="activeTab" class="shrink-0">
      <el-tab-pane label="基本信息" name="basic" />
      <el-tab-pane label="显隐设置" name="visibility" />
    </el-tabs>

    <!-- 导航固定，内容独立滚动；两个表单保持挂载，供统一回填、取值和校验。 -->
    <el-scrollbar class="mk-scrollbar-right mt-4 flex h-auto! min-h-0 flex-auto flex-col" wrap-class="h-auto! min-h-0 flex-auto">
      <BasicInfoConstructor v-show="activeTab === 'basic'" ref="basicRef" v-model="formData" :input-type-list="fieldTypeOptions" v-bind="$attrs" />
      <VisibilityConstructor v-show="activeTab === 'visibility'" ref="visibilityRef" :initial-value="visibilityRules" :left-options="leftOptions" />
    </el-scrollbar>
  </div>

  <BasicInfoConstructor v-else ref="basicRef" v-model="formData" :input-type-list="fieldTypeOptions" v-bind="$attrs" />
</template>
