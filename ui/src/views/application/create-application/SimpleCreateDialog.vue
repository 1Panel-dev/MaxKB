<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'

defineOptions({ name: 'SimpleCreateDialog' })

interface SimpleApplicationDraft {
  desc: string
  name: string
}

const emit = defineEmits<{ submit: [draft: SimpleApplicationDraft] }>()

const dialogVisible = ref(false)
const applicationFormRef = ref<FormInstance>()
const applicationForm = reactive<SimpleApplicationDraft>({ desc: '', name: '' })
const applicationFormRules: FormRules<SimpleApplicationDraft> = {
  name: [{ required: true, message: '请输入智能体名称', trigger: 'blur' }],
}
const createDisabled = computed(() => !applicationForm.name.trim())

function open() {
  resetData()
  dialogVisible.value = true
}

function submit() {
  applicationFormRef.value?.validate((valid) => {
    if (!valid) return

    emit('submit', { desc: applicationForm.desc.trim(), name: applicationForm.name.trim() })
    dialogVisible.value = false
  })
}

function resetData() {
  Object.assign(applicationForm, { desc: '', name: '' })
  applicationFormRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="dialogVisible" title="创建简易智能体" width="600" align-center @closed="resetData">
    <el-form
      ref="applicationFormRef"
      :model="applicationForm"
      :rules="applicationFormRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent="submit"
    >
      <el-form-item label="名称" prop="name">
        <el-input
          v-model="applicationForm.name"
          maxlength="64"
          placeholder="请输入智能体名称"
          show-word-limit
          @blur="applicationForm.name = applicationForm.name.trim()"
        />
      </el-form-item>

      <el-form-item label="描述">
        <el-input
          v-model="applicationForm.desc"
          maxlength="128"
          placeholder="描述该智能体的应用场景及用途，如：XXX 小助手回答用户提出的 XXX 产品使用问题"
          :rows="4"
          show-word-limit
          type="textarea"
          @blur="applicationForm.desc = applicationForm.desc.trim()"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button class="w-20!" plain @click="dialogVisible = false">取消</el-button>
      <el-button class="w-20!" type="primary" :disabled="createDisabled" @click="submit">创建</el-button>
    </template>
  </MkDialog>
</template>
