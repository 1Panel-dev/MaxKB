<template>
  <el-dialog title="编辑分段" v-model="dialogVisible" width="600">
    <el-form
      ref="segmentFormRef"
      :model="segmentForm"
      label-position="top"
      :rules="rules"
      @submit.prevent
    >
      <el-form-item label="分段标题">
        <el-input v-model="segmentForm.title" placeholder="请输入分段标题"> </el-input>
      </el-form-item>
      <el-form-item label="分段内容" prop="content">
        <el-input
          v-model="segmentForm.content"
          placeholder="请输入分段内容"
          maxlength="500"
          show-word-limit
          :autosize="{ minRows: 3, maxRow: 8 }"
          type="textarea"
        >
        </el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button type="primary" @click="submitHandle(segmentFormRef)"> 保存 </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { cloneDeep } from 'lodash';

const emit = defineEmits(['updateContent'])

const dialogVisible = ref<boolean>(false)

const segmentForm = ref({
  title: '',
  content: ''
})

const segmentFormRef = ref<FormInstance>()

const rules = ref<FormRules>({
  content: [{ required: true, message: '请输入分段内容', trigger: 'blur' }]
})

watch(dialogVisible, (bool) => {
  if (!bool) {
    segmentForm.value = {
      title: '',
      content: ''
    }
  }
})

const open = (data: any) => {
  segmentForm.value = cloneDeep(data)
  dialogVisible.value = true
}
const submitHandle = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      emit('updateContent', segmentForm.value)
      dialogVisible.value = false
    } else {
      console.log('error submit!')
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scope></style>
