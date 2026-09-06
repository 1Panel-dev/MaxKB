<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { MkDynamicsFormConstructor, type FormField, type VisibilityFieldOption } from '@/components/mk-dynamics-form'

defineOptions({ name: 'WorkflowFormFieldDialog' })

const props = defineProps<{ formFields: FormField[]; upstreamFieldOptions: VisibilityFieldOption[]; nodeId: string; nodeName: string }>()
const emit = defineEmits<{ submit: [data: FormField, index?: number] }>()
const dynamicsFormConstructorRef = useTemplateRef<InstanceType<typeof MkDynamicsFormConstructor>>('dynamicsFormConstructorRef')
const visible = ref(false)
const currentIndex = ref<number>()
const formData = ref<Partial<FormField>>({})

// 当前表单只能选择编辑字段之前的字段，上游变量由节点入口提供。
const visibilityFieldOptions = computed<VisibilityFieldOption[]>(() => {
  const selfFields = props.formFields
    .filter((_, index) => currentIndex.value === undefined || index < currentIndex.value)
    .map((field) => ({
      label: typeof field.label === 'string' ? field.label : (field.label?.label ?? ''),
      value: field.field,
      input_type: field.input_type,
      option_list: field.option_list,
      attrs: field.attrs,
    }))
  return [
    ...props.upstreamFieldOptions,
    ...(selfFields.length ? [{ label: props.nodeName, value: props.nodeId, self: true, children: selfFields }] : []),
  ]
})

function open(data?: FormField, index?: number) {
  if (data) {
    formData.value = cloneDeep(data)
    currentIndex.value = index
  }
  visible.value = true
}

function handleSubmit() {
  const dynamicsFormConstructor = dynamicsFormConstructorRef.value
  if (!dynamicsFormConstructor) return

  dynamicsFormConstructor
    .validate()
    .then(() => emit('submit', cloneDeep(dynamicsFormConstructor.getData()), currentIndex.value))
    .catch(() => {})
}

function close() {
  visible.value = false
}

function resetData() {
  currentIndex.value = undefined
  formData.value = {}
}

defineExpose({ close, open })
</script>

<template>
  <MkDialog v-model="visible" :title="currentIndex === undefined ? '添加参数' : '编辑参数'" @closed="resetData" align-center>
    <MkDynamicsFormConstructor ref="dynamicsFormConstructorRef" v-model="formData" enable-visibility :left-options="visibilityFieldOptions" />
    <template #footer>
      <el-button plain @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">{{ currentIndex === undefined ? '添加' : '保存' }}</el-button>
    </template>
  </MkDialog>
</template>
