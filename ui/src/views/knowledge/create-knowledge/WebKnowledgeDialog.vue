<script setup lang="ts">
import { ref, useTemplateRef, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import { KNOWLEDGE_TYPE } from '@/api/enums'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'
import KnowledgeBaseForm from './components/KnowledgeBaseForm.vue'

defineOptions({ name: 'CreateWebKnowledgeDialog' })
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
const knowledgeForm = reactive({ source_url: '', selector: '' })
const knowledgeFormRules: FormRules<typeof knowledgeForm> = {
  source_url: [{ required: true, whitespace: true, message: '请输入 Web 站点 URL', trigger: 'blur' }],
}

function resetData() {
  baseFormRef.value?.reset()
  Object.assign(knowledgeForm, { source_url: '', selector: '' })
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
      return KnowledgeApi.postWebKnowledge({
        name: baseForm.name.trim(),
        desc: baseForm.desc.trim(),
        embedding_model_id: baseForm.embedding_model_id,
        folder_id: props.folderId,
        type: KNOWLEDGE_TYPE.WEB,
        source_url: knowledgeForm.source_url.trim(),
        selector: knowledgeForm.selector.trim(),
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
  <MkDialog v-model="dialogVisible" title="创建 Web 知识库" align-center @closed="resetData">
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
      <el-form-item label="Web 站点 URL" prop="source_url">
        <el-input
          v-model="knowledgeForm.source_url"
          placeholder="请输入 Web 站点 URL"
          @blur="knowledgeForm.source_url = knowledgeForm.source_url.trim()"
        />
      </el-form-item>
      <el-form-item label="选择器" prop="selector">
        <el-input
          v-model="knowledgeForm.selector"
          placeholder="请输入 CSS 选择器，默认 body"
          @blur="knowledgeForm.selector = knowledgeForm.selector.trim()"
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
