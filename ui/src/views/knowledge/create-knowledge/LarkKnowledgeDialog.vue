<script setup lang="ts">
import { computed, reactive, ref, useTemplateRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type SystemSharedKnowledgeApi from '@/api/admin/system/shared-resources/knowledge/knowledge'
import type { FormInstance, FormRules } from 'element-plus'
import { KNOWLEDGE_TYPE } from '@/api/enums'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import KnowledgeBaseForm from './components/KnowledgeBaseForm.vue'
import { KNOWLEDGE_TYPE_MAP } from '@/constants/knowledge'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'CreateLarkKnowledgeDialog' })
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
const knowledgeFormRef = ref<FormInstance>()
const knowledgeForm = reactive({ app_id: '', app_secret: '', folder_token: '' })
const larkFieldLabels = { app_id: 'App ID', app_secret: 'App Secret', folder_token: 'Folder Token' } as const
const knowledgeFormRules = computed<FormRules<typeof knowledgeForm>>(() => ({
  app_id: [
    { required: true, whitespace: true, message: t('common.validation.inputFieldRequired', { label: larkFieldLabels.app_id }), trigger: 'blur' },
  ],
  app_secret: [
    { required: true, whitespace: true, message: t('common.validation.inputFieldRequired', { label: larkFieldLabels.app_secret }), trigger: 'blur' },
  ],
  folder_token: [
    {
      required: true,
      whitespace: true,
      message: t('common.validation.inputFieldRequired', { label: larkFieldLabels.folder_token }),
      trigger: 'blur',
    },
  ],
}))

function resetData() {
  baseFormRef.value?.reset()
  Object.assign(knowledgeForm, { app_id: '', app_secret: '', folder_token: '' })
  knowledgeFormRef.value?.clearValidate()
  loading.value = false
}

function open() {
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
      return props.api
        .postLarkKnowledge({
          name: baseForm.name.trim(),
          desc: baseForm.desc.trim(),
          embedding_model_id: baseForm.embedding_model_id,
          folder_id: props.folderId,
          type: KNOWLEDGE_TYPE.LARK,
          app_id: knowledgeForm.app_id.trim(),
          app_secret: knowledgeForm.app_secret,
          folder_token: knowledgeForm.folder_token.trim(),
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
  <MkDialog v-model="dialogVisible" :title="t('knowledge.lark.createTitle')" @closed="resetData">
    <KnowledgeBaseForm ref="baseFormRef" v-loading="loading" />
    <el-form
      class="mt-4"
      ref="knowledgeFormRef"
      :model="knowledgeForm"
      :rules="knowledgeFormRules"
      :validate-on-rule-change="false"
      v-loading="loading"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="larkFieldLabels.app_id" prop="app_id">
        <el-input
          v-model="knowledgeForm.app_id"
          :placeholder="t('common.placeholders.inputField', { label: larkFieldLabels.app_id })"
          @blur="knowledgeForm.app_id = knowledgeForm.app_id.trim()"
        />
      </el-form-item>
      <el-form-item :label="larkFieldLabels.app_secret" prop="app_secret">
        <el-input
          v-model="knowledgeForm.app_secret"
          :placeholder="t('common.placeholders.inputField', { label: larkFieldLabels.app_secret })"
          type="password"
          autocomplete="new-password"
          show-password
        />
      </el-form-item>
      <el-form-item :label="larkFieldLabels.folder_token" prop="folder_token">
        <el-input
          v-model="knowledgeForm.folder_token"
          :placeholder="t('common.placeholders.inputField', { label: larkFieldLabels.folder_token })"
          @blur="knowledgeForm.folder_token = knowledgeForm.folder_token.trim()"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消创建 -->
      <el-button plain :disabled="loading" @click="dialogVisible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 创建知识库 -->
      <el-button type="primary" :loading="loading" @click="submit">{{ t('common.actions.create') }}</el-button>
    </template>
  </MkDialog>
</template>
