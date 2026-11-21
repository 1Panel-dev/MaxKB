<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import workflowDemo from '@/assets/workflow/workflow-demo.png'
import { knowledgeTemplate } from '@/views/knowledge/template'
import { useKnowledgeDetailContext } from '../context'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { isWorkspaceSharedResource } from '@/utils/resource-context'

defineOptions({ name: 'KnowledgeWorkflowTransformView' })
defineProps<ResourceDetailPageProps>()
defineExpose({ hideHeader: true })

const route = useRoute()
const router = useRouter()
const { t } = useI18n({ useScope: 'global' })
const { knowledgeId, resourceApi, routeNames, routeParams } = useKnowledgeDetailContext()

/* 转换成功后进入全屏画布。 */
function enterWorkflow() {
  return router.replace({
    name: routeNames.value.workflow,
    params: routeParams.value,
    query: route.query,
  })
}

const loading = ref(false)
function handleTransformWorkflow() {
  const knowledgeApi = resourceApi.knowledge
  if (loading.value || isWorkspaceSharedResource() || !('postTransformWorkflow' in knowledgeApi)) return
  return MsgConfirm(t('knowledge.workflow.transform.title'), t('knowledge.workflow.transform.confirmMessage'), {
    confirmButtonText: t('knowledge.workflow.transform.action'),
    confirmButtonType: 'primary',
  })
    .then(() => {
      loading.value = true
      return knowledgeApi.postTransformWorkflow(knowledgeId.value, { work_flow: cloneDeep(knowledgeTemplate.default) }).then(() => {
        MsgSuccess(t('knowledge.workflow.transform.successMessage'))
        return enterWorkflow()
      })
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}
</script>

<template>
  <div class="flex-1 flex-center gap-6" v-loading="loading">
    <div class="w-full max-w-80 shrink-0">
      <h1 class="mb-3">{{ t('knowledge.workflow.transform.title') }}</h1>
      <div class="text-N600">
        {{ t('knowledge.workflow.transform.description') }}
        <br />
        {{ t('knowledge.workflow.transform.futureDocumentsHint') }}
      </div>
      <p class="mt-6 mb-2 text-warning">{{ t('knowledge.workflow.transform.irreversibleMessage') }}</p>
      <!-- 转换为工作流知识库 -->
      <el-button v-if="!isWorkspaceSharedResource()" type="primary" :loading="loading" @click="handleTransformWorkflow">
        {{ t('knowledge.workflow.transform.action') }}
      </el-button>
    </div>
    <img :src="workflowDemo" class="w-full min-w-0" />
  </div>
</template>
