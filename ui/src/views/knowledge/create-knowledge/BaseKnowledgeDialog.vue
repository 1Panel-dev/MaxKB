<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type SystemSharedKnowledgeApi from '@/api/admin/system/shared-resources/knowledge/knowledge'
import { KNOWLEDGE_TYPE } from '@/api/enums'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import KnowledgeBaseForm from './components/KnowledgeBaseForm.vue'
import { KNOWLEDGE_TYPE_MAP } from '@/constants/knowledge'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'CreateBaseKnowledgeDialog' })
const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{ api: typeof KnowledgeApi | typeof SystemSharedKnowledgeApi; folderId: string }>()
const emit = defineEmits<{ refresh: [] }>()
const { auth } = useStore()
const route = useRoute()
const router = useRouter()

/* 创建表单 */
const baseFormRef = useTemplateRef<InstanceType<typeof KnowledgeBaseForm>>('baseFormRef')
const dialogVisible = ref(false)
const loading = ref(false)

function resetData() {
  baseFormRef.value?.reset()
  loading.value = false
}

function open() {
  dialogVisible.value = true
}

/* 校验并创建，成功后刷新资料并进入文档列表 */
function submit() {
  if (loading.value) return
  loading.value = true
  return Promise.all([baseFormRef.value?.validate()])
    .then((validationResults) => {
      if (!validationResults.every(Boolean) || !baseFormRef.value) return
      const baseForm = baseFormRef.value.form
      return props.api
        .postKnowledge({
          name: baseForm.name.trim(),
          desc: baseForm.desc.trim(),
          embedding_model_id: baseForm.embedding_model_id,
          folder_id: props.folderId,
          type: KNOWLEDGE_TYPE.BASE,
        })
        .then((knowledge) => {
          return auth.loadAuthBaseProfile().then(() => {
            MsgSuccess(t('common.messages.createSuccess'))
            dialogVisible.value = false
            emit('refresh')
            return router.push({
              name: 'workspace-knowledge-document-list',
              params: { knowledgeId: knowledge.id, type: KNOWLEDGE_TYPE_MAP[knowledge.type], workspaceId: route.params.workspaceId },
            })
          })
        })
    })
    .finally(() => {
      loading.value = false
    })
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="dialogVisible" :title="t('knowledge.base.createTitle')" @closed="resetData">
    <KnowledgeBaseForm ref="baseFormRef" v-loading="loading" />
    <template #footer>
      <!-- 取消创建 -->
      <el-button plain :disabled="loading" @click="dialogVisible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 创建知识库 -->
      <el-button type="primary" :loading="loading" @click="submit">{{ t('common.actions.create') }}</el-button>
    </template>
  </MkDialog>
</template>
