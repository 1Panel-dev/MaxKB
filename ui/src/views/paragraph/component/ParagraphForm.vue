<template>
  <el-form
    ref="paragraphFormRef"
    :model="form"
    label-position="top"
    require-asterisk-position="right"
    :rules="rules"
    @submit.prevent
  >
    <el-form-item label="分段标题">
      <el-input v-if="isEdit" v-model="form.title" placeholder="请输入分段标题"> </el-input>
      <span v-else>{{ form.title || '-' }}</span>
    </el-form-item>
    <el-form-item label="分段内容" prop="content">
      <el-input
        v-if="isEdit"
        v-model="form.content"
        placeholder="请输入分段内容"
        maxlength="1024"
        show-word-limit
        :rows="8"
        type="textarea"
      >
      </el-input>
      <span v-else>{{ form.content }}</span>
    </el-form-item>
  </el-form>
</template>
<script setup lang="ts">
import { ref, reactive, onUnmounted, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'

const props = defineProps({
  data: {
    type: Object,
    default: () => {}
  },
  isEdit: Boolean
})

const form = ref<any>({
  title: '',
  content: ''
})

const rules = reactive<FormRules>({
  content: [{ required: true, message: '请输入分段内容', trigger: 'blur' }]
})

const paragraphFormRef = ref<FormInstance>()

watch(
  () => props.data,
  (value) => {
    if (value && JSON.stringify(value) !== '{}') {
      form.value.title = value.title
      form.value.content = value.content
    }
  },
  {
    immediate: true
  }
)

/*
  表单校验
*/
function validate() {
  if (!paragraphFormRef.value) return
  return paragraphFormRef.value.validate((valid: any) => {
    return valid
  })
}

onUnmounted(() => {
  form.value = {
    title: '',
    content: ''
  }
})

defineExpose({
  validate,
  form
})
</script>
<style scoped lang="scss"></style>
