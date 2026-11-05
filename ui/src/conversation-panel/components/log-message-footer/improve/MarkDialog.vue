<script setup lang="ts">
import { onMounted, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type ChatLogApi from '@/api/admin/workspace/application/chat-log'
import WorkspaceParagraphApi from '@/api/admin/workspace/knowledge/paragraph'
import SystemParagraphApi from '@/api/admin/system/resource-management/knowledge/paragraph'
import { isSystemResource } from '@/utils/resource-context'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'MarkDialog' })
const props = defineProps<{
  api: Pick<typeof ChatLogApi, 'getMarkChatRecord' | 'deleteMarkChatRecord'>
  applicationId: string
  chatId: string
  recordId: string
}>()
const emit = defineEmits<{ closed: []; refresh: [ids: string[]] }>()
const visible = ref(false)
const loading = ref(false)
const editing = ref(false)
const paragraph = ref<{ id: string; knowledge: string; document: string; content: string }>()
const contentForm = ref({ content: '' })
const formRef = useTemplateRef<FormInstance>('formRef')
const rules: FormRules = {
  content: [
    { required: true, whitespace: true, message: '请输入内容', trigger: 'blur' },
    { max: 100000, message: '内容不能超过100000个字符', trigger: 'blur' },
  ],
}
const markIds = ref<string[]>([])

// 与 V2 一致，展示并编辑首条标注。
onMounted(() => {
  visible.value = true
  loading.value = true
  props.api
    .getMarkChatRecord(props.applicationId, props.chatId, props.recordId)
    .then((paragraphs) => {
      markIds.value = paragraphs.map((mark) => String(mark.id))
      emit('refresh', markIds.value)
      const mark = paragraphs[0]
      if (!mark) return
      paragraph.value = {
        id: String(mark.id),
        knowledge: String(mark.knowledge),
        document: String(mark.document),
        content: String(mark.content || ''),
      }
      contentForm.value.content = paragraph.value.content
    })
    .catch(() => {
      /* 请求层统一提示错误。 */
    })
    .finally(() => {
      loading.value = false
    })
})

async function save() {
  if (loading.value || !paragraph.value) return
  if (!(await formRef.value?.validate().catch(() => false)) || loading.value) return
  loading.value = true
  const api = isSystemResource() ? SystemParagraphApi : WorkspaceParagraphApi
  const mark = paragraph.value
  return api
    .putParagraph(mark.knowledge, mark.document, mark.id, { content: contentForm.value.content.trim() })
    .then(() => {
      MsgSuccess('保存成功')
      visible.value = false
    })
    .catch(() => {
      /* 失败保留草稿。 */
    })
    .finally(() => {
      loading.value = false
    })
}

function deleteMark() {
  if (loading.value || !paragraph.value) return
  loading.value = true
  const mark = paragraph.value
  return props.api
    .deleteMarkChatRecord(props.applicationId, props.chatId, props.recordId, mark.knowledge, mark.document, mark.id)
    .then(() => {
      emit(
        'refresh',
        markIds.value.filter((id) => id !== mark.id),
      )
      MsgSuccess('删除成功')
      visible.value = false
    })
    .catch(() => {
      /* 请求层统一提示错误。 */
    })
    .finally(() => {
      loading.value = false
    })
}

function cancelEdit() {
  contentForm.value.content = paragraph.value?.content || ''
  editing.value = false
}
</script>

<template>
  <MkDialog v-model="visible" title="查看标注" @closed="emit('closed')">
    <div v-loading="loading" class="group relative">
      <el-card v-if="!editing" class="group-hover-visible absolute top-2 right-2 z-10" shadow="always" style="--el-card-padding: 4px">
        <div class="flex-align-center">
          <!-- 编辑已保存的标注 -->
          <el-button text size="small" :disabled="loading || !paragraph" @click="editing = true"><MkIcon name="icon_edit_outlined" /></el-button>
          <!-- 删除当前标注 -->
          <el-button text size="small" :disabled="loading || !paragraph" @click="deleteMark">
            <MkIcon name="icon_delete-trash_outlined" />
          </el-button>
        </div>
      </el-card>
      <el-form ref="formRef" :model="contentForm" :rules="rules" @submit.prevent>
        <el-form-item prop="content">
          <el-input v-model="contentForm.content" :rows="13" type="textarea" :readonly="!editing" maxlength="100000" placeholder="请输入内容" />
        </el-form-item>
      </el-form>
    </div>
    <template v-if="editing" #footer>
      <!-- 取消编辑标注 -->
      <el-button plain :disabled="loading" @click="cancelEdit">取消</el-button>
      <!-- 保存标注内容 -->
      <el-button type="primary" :loading="loading" @click="save">保存</el-button>
    </template>
  </MkDialog>
</template>

<style scoped lang="scss"></style>
