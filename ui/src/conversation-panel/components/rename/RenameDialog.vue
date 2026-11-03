<script setup lang="ts">
import { inject, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import ConversationApi from '@/api/chat/conversation'
import { PORTAL_CONVERSATION_LIST_KEY } from '../../left-sidebar/portal-conversation-list/index'
import type { Conversation } from '../../core/types'
import { useConversationListStore } from '../../left-sidebar/conversation-list/index'

defineOptions({ name: 'RenameDialog' })

const props = defineProps<{ conversation: Conversation; applicationId?: string }>()
const conversationList = useConversationListStore()
const portalList = inject(PORTAL_CONVERSATION_LIST_KEY, null)
const emit = defineEmits<{ renamed: [title: string]; closed: [] }>()

// 重命名会话：回填标题，校验并去除首尾空格后提交。
const renameDialogVisible = ref(true)
const renameSubmitting = ref(false)
const renameConversationId = props.conversation.id
const renameFormRef = ref<FormInstance>()
const renameForm = reactive({ abstract: props.conversation.abstract || '' })
const renameRules: FormRules<typeof renameForm> = {
  abstract: [{ required: true, whitespace: true, message: '请输入', trigger: 'blur' }],
}

function submitRename() {
  if (renameSubmitting.value) return
  renameFormRef.value?.validate((valid) => {
    if (!valid) return
    renameSubmitting.value = true
    const title = renameForm.abstract.trim()
    const conversationId = renameConversationId
    const applicationId = props.applicationId
    const request = applicationId
      ? ConversationApi.putConversation(applicationId, conversationId, { abstract: title })
      : conversationList.renameChat(conversationId, title)
    return request
      .then(() => {
        if (applicationId && portalList) {
          const group = portalList.applicationGroups.value.find((group) => group.id === applicationId)
          const groupConversation = group?.conversations.find((conversation) => conversation.id === conversationId)
          if (groupConversation) groupConversation.abstract = title
          if (portalList.currentApplicationId.value === applicationId) {
            const currentConversation = conversationList.conversations.value.find((conversation) => conversation.id === conversationId)
            if (currentConversation) currentConversation.abstract = title
          }
        }
        emit('renamed', title)
        renameDialogVisible.value = false
      })
      .catch(() => {})
      .finally(() => {
        renameSubmitting.value = false
      })
  })
}
</script>

<template>
  <MkDialog v-model="renameDialogVisible" title="重命名" @closed="emit('closed')">
    <el-form ref="renameFormRef" :model="renameForm" :rules="renameRules" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="会话标题" prop="abstract">
        <el-input v-model="renameForm.abstract" placeholder="请输入" />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消重命名 -->
      <el-button plain @click="renameDialogVisible = false">取消</el-button>
      <!-- 保存会话标题 -->
      <el-button type="primary" :loading="renameSubmitting" @click="submitRename">保存</el-button>
    </template>
  </MkDialog>
</template>
