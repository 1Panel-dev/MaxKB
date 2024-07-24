<template>
  <el-dialog title="修改标注" v-model="dialogVisible" width="600" class="edit-mark-dialog">
    <template #header="{ titleId, titleClass }">
      <div class="flex-between">
        <h4 :id="titleId" :class="titleClass">修改标注</h4>
        <div class="text-right">
          <el-button text @click="isEdit = true" v-if="!isEdit">
            <el-icon><EditPen /></el-icon>
          </el-button>
          <el-button text style="margin-left: 4px" @click="deleteMark">
            <el-icon><Delete /></el-icon>
          </el-button>
          <el-divider direction="vertical" />
        </div>
      </div>
    </template>

    <el-scrollbar>
      <div style="min-height: 250px; max-height: 350px" v-loading="loading">
        <el-form
          v-if="isEdit"
          ref="formRef"
          :model="form"
          label-position="top"
          require-asterisk-position="right"
          :rules="rules"
          @submit.prevent
        >
          <el-form-item prop="content">
            <el-input
              v-model="form.content"
              placeholder="请输入分段内容"
              maxlength="100000"
              show-word-limit
              :rows="15"
              type="textarea"
            >
            </el-input>
          </el-form-item>
        </el-form>
        <span v-else class="pre-line">{{ form?.content }}</span>
      </div>
    </el-scrollbar>

    <template #footer>
      <span class="dialog-footer" v-if="isEdit">
        <el-button @click.prevent="isEdit = false"> 取消 </el-button>
        <el-button type="primary" @click="submit(formRef)" :loading="loading"> 保存 </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, reactive } from 'vue'
import { useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import logApi from '@/api/log'
import useStore from '@/stores'
import { MsgSuccess, MsgConfirm } from '@/utils/message'

const route = useRoute()
const {
  params: { id }
} = route as any

const { paragraph } = useStore()

const emit = defineEmits(['refresh'])

const formRef = ref()

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

const form = ref<any>({})
const isEdit = ref(false)
const detail = ref<any>({})

const rules = reactive<FormRules>({
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
})

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {}
    isEdit.value = false
  }
})

function deleteMark() {
  logApi
    .delMarkRecord(
      id as string,
      detail.value.chat_id,
      detail.value.id,
      form.value.dataset,
      form.value.document,
      form.value.id,
      loading
    )
    .then(() => {
      emit('refresh')
      MsgSuccess('删除成功')
      dialogVisible.value = false
    })
}

function getMark(data: any) {
  logApi.getMarkRecord(id as string, data.chat_id, data.id, loading).then((res: any) => {
    if (res.data.length > 0) {
      form.value = res.data[0]
    }
  })
}

const open = (data: any) => {
  detail.value = data
  getMark(data)
  dialogVisible.value = true
}
const submit = async (formEl: FormInstance) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      paragraph
        .asyncPutParagraph(
          form.value.dataset,
          form.value.document,
          form.value.id,
          {
            content: form.value.content
          },
          loading
        )
        .then((res) => {
          dialogVisible.value = false
        })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scope>
.edit-mark-dialog {
  .el-dialog__header.show-close {
    padding-right: 15px;
  }
  .el-dialog__headerbtn {
    top: 13px;
  }
}
</style>
