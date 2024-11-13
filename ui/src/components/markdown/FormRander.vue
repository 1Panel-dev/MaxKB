<template>
  <div>
    <DynamicsForm
      :disabled="is_submit"
      label-position="top"
      require-asterisk-position="right"
      ref="dynamicsFormRef"
      :render_data="form_field_list"
      label-suffix=":"
      v-model="form_data"
      :model="form_data"
    ></DynamicsForm>
    <el-button :type="is_submit ? 'info' : 'primary'" :disabled="is_submit" @click="submit"
      >提交</el-button
    >
  </div>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import DynamicsForm from '@/components/dynamics-form/index.vue'
const props = defineProps<{
  form_setting: string
  sendMessage?: (question: string, type: 'old' | 'new', other_params_data?: any) => void
}>()
const form_setting_data = computed(() => {
  if (props.form_setting) {
    return JSON.parse(props.form_setting)
  } else {
    return {}
  }
})
const _submit = ref<boolean>(false)
/**
 * 表单字段列表
 */
const form_field_list = computed(() => {
  if (form_setting_data.value.form_field_list) {
    return form_setting_data.value.form_field_list
  }
  return []
})
const is_submit = computed(() => {
  if (_submit.value) {
    return true
  }
  if (form_setting_data.value.is_submit) {
    return form_setting_data.value.is_submit
  } else {
    return false
  }
})
const _form_data = ref<any>({})
const form_data = computed({
  get: () => {
    console.log(form_setting_data.value)
    if (form_setting_data.value.is_submit) {
      return form_setting_data.value.form_data
    } else {
      return _form_data.value
    }
  },
  set: (v) => {
    _form_data.value = v
  }
})
const dynamicsFormRef = ref<InstanceType<typeof DynamicsForm>>()
const submit = () => {
  dynamicsFormRef.value?.validate().then(() => {
    _submit.value = true
    const setting = JSON.parse(props.form_setting)
    if (props.sendMessage) {
      props.sendMessage('', 'old', {
        runtime_node_id: setting.runtime_node_id,
        chat_record_id: setting.chat_record_id,
        node_data: form_data.value
      })
    }
  })
}
</script>
<style lang="scss" scoped></style>
