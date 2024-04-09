<template>
  <el-dialog
    title="创建问题"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
  >
    <el-form
      label-position="top"
      ref="problemFormRef"
      :rules="rules"
      :model="form"
      require-asterisk-position="right"
    >
      <el-form-item label="问题" prop="data">
        <el-input
          v-model="form.data"
          placeholder="请输入问题，支持输入多个，一行一个。"
          :rows="10"
          type="textarea"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button type="primary" @click="submit(problemFormRef)" :loading="loading">
          确定
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { MsgSuccess } from '@/utils/message'
import useStore from '@/stores'

const route = useRoute()
const {
  params: { id }
} = route as any
const { problem } = useStore()

const emit = defineEmits(['refresh'])
const problemFormRef = ref()
const loading = ref<boolean>(false)

const form = ref<any>({
  data: ''
})

const rules = reactive({
  data: [{ required: true, message: '请输入问题', trigger: 'blur' }]
})

const dialogVisible = ref<boolean>(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      data: ''
    }
  }
})

const open = () => {
  dialogVisible.value = true
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      const arr = form.value.data.split('\n').filter(function (item: string) {
        return item !== ''
      })
      problem.asyncPostProblem(id, arr, loading).then((res: any) => {
        MsgSuccess('创建成功')
        emit('refresh')
        dialogVisible.value = false
      })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
