<template>
  <h4 class="title-decoration-1 mb-8">上传文档</h4>
  <el-form ref="FormRef" :model="form" :rules="rules" label-position="top">
    <el-form-item prop="fileList">
      <el-upload
        class="w-full"
        drag
        multiple
        v-model:file-list="form.fileList"
        action="#"
        :auto-upload="false"
      >
        <div class="el-upload__text">
          <p>
            拖拽文件到此上传或
            <em>
              选择文件
              <el-icon style="font-size: 25px"><upload-filled /></el-icon>
            </em>
          </p>
          <div class="upload__decoration">
            <p>1. 当前支持TXT、Markdown文本文件。</p>
            <p>2. 每次最多上传50个文档，每个文档最大不能超过10MB。</p>
            <p>3. 系统会对文档进行分段处理，若使用【高级分段】建议上传文档前规范文档的分段标识。</p>
          </div>
        </div>
      </el-upload>
    </el-form-item>
  </el-form>
  <p>文档列表</p>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
const form = reactive({
  fileList: []
})

const rules = reactive({
  fileList: [{ required: true, message: '请上传文件', trigger: 'change' }]
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
<style scoped lang="scss">
.upload__decoration {
  font-size: 12px;
  line-height: 20px;
  color: var(--el-text-color-secondary);
}
</style>
