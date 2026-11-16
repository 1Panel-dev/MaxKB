<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { MkDynamicsFormConstructor, type FormField } from '@/components/mk-dynamics-form'

defineOptions({ name: 'ModelParamDialog' })

const { t } = useI18n({ useScope: 'global' })

const emit = defineEmits<{ submit: [field: FormField] }>()

const visible = ref(false)
const editing = ref(false)
const currentField = ref<Partial<FormField>>({})
const constructorRef = useTemplateRef<InstanceType<typeof MkDynamicsFormConstructor>>('constructorRef')

function resetData() {
  editing.value = false
  currentField.value = {}
}

function open(field?: FormField) {
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
  })
}

function close() {
  visible.value = false
}

defineExpose({ close, open })
</script>

<template>
  <MkDialog v-model="visible" :title="editing ? t('dynamicForm.editTitle') : t('dynamicForm.addTitle')" @closed="resetData">
    <MkDynamicsFormConstructor ref="constructorRef" v-model="currentField" />

    <template #footer>
      <el-button plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <el-button type="primary" @click="handleSubmit">
        {{ editing ? t('common.actions.save') : t('common.actions.add') }}
      </el-button>
    </template>
  </MkDialog>
</template>
