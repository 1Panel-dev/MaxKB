<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { MkDynamicsFormConstructor, type FormField } from '@/components/mk-dynamics-form'

defineOptions({ name: 'ModelParamDialog' })

const emit = defineEmits<{
  submit: [field: FormField]
}>()

const visible = ref(false)
const editing = ref(false)
const currentField = ref<Partial<FormField>>({})
const constructorRef =
  useTemplateRef<InstanceType<typeof MkDynamicsFormConstructor>>('constructorRef')

function resetData() {
  editing.value = false
  currentField.value = {}
}

function open(field?: FormField) {
  resetData()
  if (field) {
    editing.value = true
    currentField.value = cloneDeep(field)
  }
  visible.value = true
}

function handleSubmit() {
  constructorRef.value?.validate().then(() => {
    const field = constructorRef.value?.getData()
    if (!field) return

    emit('submit', field)
    visible.value = false
  })
}

defineExpose({ open })
</script>

<template>
  <MkDialog
    v-model="visible"
    :title="editing ? '编辑参数' : '添加参数'"
    @closed="resetData"
    align-center
  >
    <MkDynamicsFormConstructor ref="constructorRef" v-model="currentField" />

    <template #footer>
      <el-button plain @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">
        {{ editing ? '保存' : '添加' }}
      </el-button>
    </template>
  </MkDialog>
</template>
