<template>
  <div>
    <DynamicsForm
      label-position="top"
      require-asterisk-position="right"
      ref="dynamicsFormRef"
      :render_data="form_field_list"
      label-suffix=":"
      v-model="cc"
      :model="cc"
    ></DynamicsForm>
    <el-button @click="submit">提交</el-button>
  </div>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import DynamicsForm from '@/components/dynamics-form/index.vue'
const props = defineProps<{
  form_setting: string
  sendMessage: (val: string, other_params_data?: any) => void
}>()
const form_field_list = computed(() => {
  if (props.form_setting) {
    const result = JSON.parse(props.form_setting)
    return result.form_field_list
  } else {
    return []
  }
})
const cc = ref<any>({})
const form_data = computed(() => {
  if (props.form_setting) {
    const result = JSON.parse(props.form_setting)
    return result.form_data
  } else {
    return {}
  }
})
const dynamicsFormRef = ref<InstanceType<typeof DynamicsForm>>()
const submit = () => {
  dynamicsFormRef.value?.validate().then(() => {
    const setting = JSON.parse(props.form_setting)
    props.sendMessage('form_data', {
      runtime_node_id: setting.runtime_node_id,
      chat_record_id: setting.chat_record_id,
      node_data: cc.value
    })
  })
}
</script>
<style lang="scss" scoped></style>
