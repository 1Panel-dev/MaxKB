<script setup lang="ts">
import { ref, useTemplateRef, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import { KNOWLEDGE_TYPE } from '@/api/enums'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'
import KnowledgeBaseForm from './components/KnowledgeBaseForm.vue'

defineOptions({ name: 'CreateLarkKnowledgeDialog' })
const props = defineProps<{ folderId: string }>()
const emit = defineEmits<{ refresh: [] }>()
const { auth } = useStore()
const route = useRoute()
const router = useRouter()

/* 创建表单 */
const baseFormRef = useTemplateRef<InstanceType<typeof KnowledgeBaseForm>>('baseFormRef')
const dialogVisible = ref(false)
const loading = ref(false)
const knowledgeFormRef = ref<FormInstance>()
const knowledgeForm = reactive({ app_id: '', app_secret: '', folder_token: '' })
const knowledgeFormRules: FormRules<typeof knowledgeForm> = {
  app_id: [{ required: true, whitespace: true, message: '请输入 App ID', trigger: 'blur' }],
  app_secret: [{ required: true, whitespace: true, message: '请输入 App Secret', trigger: 'blur' }],
  folder_token: [{ required: true, whitespace: true, message: '请输入 Folder Token', trigger: 'blur' }],
}

function resetData() {
  baseFormRef.value?.reset()
  Object.assign(knowledgeForm, { app_id: '', app_secret: '', folder_token: '' })
  knowledgeFormRef.value?.clearValidate()
  loading.value = false
}

function open() {
  resetData()
  dialogVisible.value = true
}

/* 校验并创建，成功后刷新资料并进入文档列表 */
function submit() {
  if (loading.value) return
  loading.value = true
  return Promise.all([baseFormRef.value?.validate(), knowledgeFormRef.value?.validate().catch(() => false)])
    .then((validationResults) => {
      if (!validationResults.every(Boolean) || !baseFormRef.value) return
      const baseForm = baseFormRef.value.form
      return KnowledgeApi.postLarkKnowledge({
        name: baseForm.name.trim(),
        desc: baseForm.desc.trim(),
        embedding_model_id: baseForm.embedding_model_id,
        folder_id: props.folderId,
        type: KNOWLEDGE_TYPE.LARK,
        app_id: knowledgeForm.app_id.trim(),
        app_secret: knowledgeForm.app_secret,
        folder_token: knowledgeForm.folder_token.trim(),
      }).then((knowledge) => {
        return auth.loadAuthBaseProfile().then(() => {
          MsgSuccess('创建成功')
          dialogVisible.value = false
          emit('refresh')
          return router.push({
            name: 'workspace-knowledge-document-list',
            params: { knowledgeId: knowledge.id, workspaceId: route.params.workspaceId },
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
  <MkDialog v-model="dialogVisible" title="创建飞书知识库" width="720" align-center :show-close="!loading" @closed="resetData">
    <KnowledgeBaseForm ref="baseFormRef" :disabled="loading" />
    <el-form
      ref="knowledgeFormRef"
      :model="knowledgeForm"
      :rules="knowledgeFormRules"
      :disabled="loading"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item label="App ID" prop="app_id">
        <el-input v-model="knowledgeForm.app_id" placeholder="请输入 App ID" @blur="knowledgeForm.app_id = knowledgeForm.app_id.trim()" />
      </el-form-item>
      <el-form-item label="App Secret" prop="app_secret">
        <el-input v-model="knowledgeForm.app_secret" placeholder="请输入 App Secret" type="password" show-password />
      </el-form-item>
      <el-form-item label="Folder Token" prop="folder_token">
        <el-input
          v-model="knowledgeForm.folder_token"
          placeholder="请输入 Folder Token"
          @blur="knowledgeForm.folder_token = knowledgeForm.folder_token.trim()"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消创建 -->
      <el-button plain :disabled="loading" @click="dialogVisible = false">取消</el-button>
      <!-- 创建知识库 -->
      <el-button type="primary" :loading="loading" @click="submit">创建</el-button>
    </template>
  </MkDialog>
</template>
