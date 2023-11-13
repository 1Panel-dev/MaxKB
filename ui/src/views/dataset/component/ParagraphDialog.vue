<template>
  <el-dialog :title="title" v-model="dialogVisible" width="800" class="paragraph-dialog">
    <el-row>
      <el-col :span="16" class="p-24">
        <div class="flex-between mb-16">
          <div class="bold title align-center">分段内容</div>
          <el-button text>
            <el-icon><EditPen /></el-icon>
          </el-button>
        </div>

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
              :rows="8"
              type="textarea"
            >
            </el-input>
          </el-form-item>
        </el-form>
        <div class="text-right">
          <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
          <el-button type="primary" @click="submitHandle(segmentFormRef)"> 保存 </el-button>
        </div>
      </el-col>
      <el-col :span="8" class="border-l p-24">
        <p class="bold title mb-16">
          关联问题 <el-divider direction="vertical" />
          <el-button text>
            <el-icon><Plus /></el-icon>
          </el-button>
        </p>
      </el-col>
    </el-row>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { cloneDeep } from 'lodash'

const props = defineProps({
  title: String
})

const emit = defineEmits(['updateContent'])

const segmentFormRef = ref<FormInstance>()

const dialogVisible = ref<boolean>(false)

const segmentForm = ref({
  title: '',
  content: ''
})

const rules = ref<FormRules>({
  content: [{ required: true, message: '请输入分段内容', trigger: 'blur' }]
})

const isEdit = ref(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    segmentForm.value = {
      title: '',
      content: ''
    }
    isEdit.value = false
  }
})

const open = (data: any) => {
  if (data) {
    segmentForm.value.title = data.title
    segmentForm.value.content = data.content
    isEdit.value = true
  }
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
<style lang="scss" scope>
.paragraph-dialog {
  .el-dialog__header {
    padding-bottom: 16px;
  }
  .el-dialog__body {
    border-top: 1px solid var(--el-border-color);
    padding: 0 !important;
  }
  .title {
    color: var(--app-text-color);
  }
}
</style>
