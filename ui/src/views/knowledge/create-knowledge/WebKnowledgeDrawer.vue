<script setup lang="ts">
import { computed, reactive, ref, useTemplateRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type SystemSharedKnowledgeApi from '@/api/admin/system/shared-resources/knowledge/knowledge'
import type { FormInstance, FormRules } from 'element-plus'
import { KNOWLEDGE_TYPE } from '@/api/enums'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import DocumentStrategyForm from './components/DocumentStrategyForm.vue'
import KnowledgeBaseForm from './components/KnowledgeBaseForm.vue'
import { KNOWLEDGE_TYPE_MAP } from '@/constants/knowledge'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'CreateWebKnowledgeDrawer' })
const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{ api: typeof KnowledgeApi | typeof SystemSharedKnowledgeApi; folderId: string }>()
const emit = defineEmits<{ refresh: [] }>()
const { auth } = useStore()
const route = useRoute()
const router = useRouter()

/* 创建表单 */
const baseFormRef = useTemplateRef<InstanceType<typeof KnowledgeBaseForm>>('baseFormRef')
const drawerVisible = ref(false)
const loading = ref(false)
const activeStep = ref(0)
const strategyFormRef = useTemplateRef<InstanceType<typeof DocumentStrategyForm>>('strategyFormRef')
const knowledgeFormRef = ref<FormInstance>()
const knowledgeForm = reactive({ source_url: '', selector: '' })
const knowledgeFormRules = computed<FormRules<typeof knowledgeForm>>(() => ({
  source_url: [{ required: true, whitespace: true, message: t('knowledge.fields.webRootUrl.requiredMessage'), trigger: 'blur' }],
}))

function resetData() {
  baseFormRef.value?.reset()
  Object.assign(knowledgeForm, { source_url: '', selector: '' })
  knowledgeFormRef.value?.clearValidate()
  loading.value = false
  activeStep.value = 0
}

function open() {
  drawerVisible.value = true
}

function handleNext() {
  if (loading.value) return
  loading.value = true
  return Promise.all([baseFormRef.value?.validate(), knowledgeFormRef.value?.validate().catch(() => false)])
    .then((results) => {
      if (results.every(Boolean)) activeStep.value = 1
    })
    .finally(() => {
      loading.value = false
    })
}

/* 校验并创建，成功后刷新资料并进入文档列表 */
function submit() {
  if (loading.value) return
  loading.value = true
  return Promise.all([baseFormRef.value?.validate(), knowledgeFormRef.value?.validate().catch(() => false), strategyFormRef.value?.validate()])
    .then((validationResults) => {
      if (!validationResults.every(Boolean) || !baseFormRef.value) return
      const baseForm = baseFormRef.value.form
      return props.api
        .postWebKnowledge({
          name: baseForm.name.trim(),
          desc: baseForm.desc.trim(),
          embedding_model_id: baseForm.embedding_model_id,
          folder_id: props.folderId,
          type: KNOWLEDGE_TYPE.WEB,
          source_url: knowledgeForm.source_url.trim(),
          selector: knowledgeForm.selector.trim(),
          doc_strategy: strategyFormRef.value?.getStrategy(),
        })
        .then((knowledge) => {
          return auth.loadAuthBaseProfile().then(() => {
            MsgSuccess(t('common.messages.createSuccess'))
            drawerVisible.value = false
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
  <MkDrawer v-model="drawerVisible" direction="btt" @closed="resetData">
    <template #header>
      <div class="flex w-full">
        <h4>{{ t('knowledge.web.createTitle') }}</h4>
        <el-steps :active="activeStep" finish-status="success" class="absolute-center w-85!">
          <el-step :title="t('common.labels.basicInfo')" />
          <el-step :title="t('knowledge.documentStrategy.title')" />
        </el-steps>
      </div>
    </template>

    <div class="mx-auto w-full max-w-200" v-loading="loading">
      <section v-show="activeStep === 0">
        <h4 class="mb-4 mk-title-decoration">{{ t('common.labels.basicInfo') }}</h4>
        <KnowledgeBaseForm ref="baseFormRef" />
        <el-form
          class="mt-4"
          ref="knowledgeFormRef"
          :model="knowledgeForm"
          :rules="knowledgeFormRules"
          :validate-on-rule-change="false"
          label-position="top"
          require-asterisk-position="right"
          @submit.prevent
        >
          <el-form-item :label="t('knowledge.fields.webRootUrl.label')" prop="source_url">
            <el-input
              v-model="knowledgeForm.source_url"
              :placeholder="t('knowledge.fields.webRootUrl.placeholder')"
              @blur="knowledgeForm.source_url = knowledgeForm.source_url.trim()"
            />
          </el-form-item>
          <el-form-item :label="t('knowledge.fields.selector.label')" prop="selector">
            <el-input
              v-model="knowledgeForm.selector"
              :placeholder="t('knowledge.fields.selector.placeholder')"
              @blur="knowledgeForm.selector = knowledgeForm.selector.trim()"
            />
          </el-form-item>
        </el-form>
      </section>
      <section v-show="activeStep === 1">
        <h4 class="mb-5 mk-title-decoration">{{ t('knowledge.documentStrategy.title') }}</h4>
        <DocumentStrategyForm ref="strategyFormRef" />
      </section>
    </div>

    <template #footer>
      <!-- 取消创建 -->
      <el-button plain :disabled="loading" @click="drawerVisible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 返回基本信息 -->
      <el-button v-if="activeStep === 1" plain :disabled="loading" @click="activeStep = 0">{{ t('common.actions.previous') }}</el-button>
      <!-- 校验基本信息并进入策略配置 -->
      <el-button v-if="activeStep === 0" type="primary" :loading="loading" @click="handleNext">{{ t('common.actions.next') }}</el-button>
      <!-- 创建知识库 -->
      <el-button v-else type="primary" :loading="loading" @click="submit">{{ t('common.actions.create') }}</el-button>
    </template>
  </MkDrawer>
</template>
