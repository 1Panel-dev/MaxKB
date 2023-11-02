<template>
  <h4 class="title-decoration-1 mb-10">基本信息</h4>
  <el-form ref="FormRef" :model="form" :rules="rules" label-position="top">
    <el-form-item label="数据集名称" prop="name">
      <el-input
        v-model.trim="form.name"
        placeholder="请输入数据集名称"
        maxlength="64"
        show-word-limit
      />
    </el-form-item>
    <el-form-item label="数据集描述" prop="desc">
      <el-input
        v-model.trim="form.desc"
        type="textarea"
        placeholder="描述数据集的内容，详尽的描述将帮助AI能深入理解该数据集的内容，能更准确的检索到内容，提高该数据集的命中率。"
        maxlength="500"
        show-word-limit
        :autosize="{ minRows: 3 }"
      />
    </el-form-item>
  </el-form>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
const form = reactive({
  name: '',
  desc: ''
})

const rules = reactive({
  name: [{ required: true, message: '请输入数据集名称', trigger: 'blur' }],
  desc: [{ required: true, message: '请输入数据集描述', trigger: 'blur' }]
})
const FormRef = ref()
// 表单校验
function validate() {
  if (!FormRef.value) return
  return FormRef.value.validate((valid: any) => {
    return valid
  })
}

onMounted(() => {})

defineExpose({
  validate,
  form
})
</script>
<style scoped lang="scss"></style>
