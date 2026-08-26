
<script setup lang="ts">
import { onMounted, ref, nextTick } from 'vue'
import { dynamicFormTypeOptions} from '@/components/mk-dynamics-form/constant'
import VisibilityConstructor from './visibility/index.vue'
import BasicInfoConstructor from './BasicInfoConstructor.vue'
import { type LeftOptions } from './type.ts'

// $attrs（label-position 等）显式透传给 BasicInfoConstructor 的 el-form
defineOptions({ inheritAttrs: false })
// 声明 v-model 事件，避免其监听器漏入 $attrs 透传到子表单
defineEmits(['update:modelValue'])

const props = withDefaults(
  defineProps<{
    modelValue?: any
    input_type_list?: Array<{ label: string; value: string }>
    enableVisibility?: boolean
    leftOptions?: Array<LeftOptions>
  }>(),
  {
    enableVisibility: false,
    input_type_list: () =>
      dynamicFormTypeOptions.map((item) => ({
        label: item.label,
        value: item.value + 'Constructor',
      })),
  },
)

const activeTab = ref('basic')
const basicRef = ref<any>()
const visibilityRef = ref()
const visibility_rules = ref<any>(null)

const form_data = ref<any>({
  label: '',
  field: '',
  tooltip: '',
  required: false,
  input_type: '',
})

const getData = () => ({
  ...basicRef.value.getData(),
  visibility_rules: visibilityRef.value?.getData() ?? null,
})

const validate = () => {
  const promises = []
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
    rander(props.modelValue)
  }
})

const rander = (data: any) => {
  visibility_rules.value = data.visibility_rules ?? null
  nextTick(() => {
    basicRef.value?.rander(data)
    visibilityRef.value?.rander(data.visibility_rules)
  })
}

defineExpose({ getData, validate, rander })
</script>

<template>
  <el-tabs v-if="enableVisibility" v-model="activeTab">
    <el-tab-pane label="基本信息" name="basic">
      <BasicInfoConstructor
        ref="basicRef"
        v-model="form_data"
        :input-type-list="input_type_list"
        v-bind="$attrs"
      />
    </el-tab-pane>
    <el-tab-pane label="显隐设置" name="visibility">
      <VisibilityConstructor
        ref="visibilityRef"
        :initialValue="visibility_rules"
        :leftOptions="leftOptions"
      />
    </el-tab-pane>
  </el-tabs>

  <BasicInfoConstructor
    v-else
    ref="basicRef"
    v-model="form_data"
    :input-type-list="input_type_list"
    v-bind="$attrs"
  />
</template>
