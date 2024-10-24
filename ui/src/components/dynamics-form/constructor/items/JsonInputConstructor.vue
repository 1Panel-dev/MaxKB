<template>
  <el-form-item
    label="默认值"
    :required="formValue.required"
    prop="default_value"
    :rules="[default_value_rule]"
  >
    <JsonInput v-model="formValue.default_value"> </JsonInput>
  </el-form-item>
</template>
<script setup lang="ts">
import { computed, onMounted } from 'vue'
import JsonInput from '@/components/dynamics-form/items/JsonInput.vue'
const props = defineProps<{
  modelValue: any
}>()
const emit = defineEmits(['update:modelValue'])
const formValue = computed({
  set: (item) => {
    emit('update:modelValue', item)
  },
  get: () => {
    return props.modelValue
  }
})

const getData = () => {
  return {
    input_type: 'JsonInput',
    attrs: {},
    props_info: {
      rules: [
        {
          required: true,
          validator: `validator = (rule, value, callback) => {
  try {
    JSON.parse(value)
  } catch (e) {
    callback(new Error('JSON格式不正确'))
  }
}`,
          trigger: 'blur'
        }
      ]
    },
    default_value: formValue.value.default_value
  }
}

const default_value_rule = {
  required: true,
  validator: (rule: any, value: any, callback: any) => {
    try {
      JSON.parse(value)
    } catch (e) {
      callback(new Error('JSON格式不正确'))
    }
    return true
  },
  trigger: 'blur'
}

const rander = (form_data: any) => {
  formValue.value.default_value = form_data.default_value
}
defineExpose({ getData, rander })
onMounted(() => {
  formValue.value.default_value = '{}'
})
</script>
<style lang="scss"></style>
