<template>
  <DynamicsForm
    v-loading="loading"
    v-model="form_data"
    :render_data="base_form_list"
    :model="form_data"
    ref="dynamicsFormRef"
    label-position="top"
    require-asterisk-position="right"
  >
    <template #default>
      <h4 class="title-decoration-1 mb-16 mt-4">
        {{ $t('chat.userInput') }}
      </h4>
    </template>
  </DynamicsForm>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue'
import DynamicsForm from '@/components/dynamics-form/index.vue'
import { WorkflowType } from '@/enums/application'
const props = defineProps<{ workflow: any }>()
const loading = ref<boolean>()
const form_data = ref<any>({})
const dynamicsFormRef = ref<InstanceType<typeof DynamicsForm>>()
const validate = () => {
  return dynamicsFormRef.value?.validate()
}
const base_form_list = computed(() => {
  const kBase = props.workflow?.nodes?.find((n: any) => n.type === WorkflowType.KnowledgeBase)
  if (kBase) {
    return kBase.properties.user_input_field_list
  }
  return []
})
const get_data = () => {
  return form_data.value
}

defineExpose({ validate, get_data })
</script>
<style lang="scss" scoped></style>
