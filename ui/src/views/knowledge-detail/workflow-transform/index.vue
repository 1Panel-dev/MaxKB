<script setup lang="ts">
import { useKnowledgeNavigationContext } from '@/views/knowledge-detail/context'
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { cloneDeep } from 'lodash'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { knowledgeTemplate } from '@/views/knowledge/template'
import workflowDemo from '@/assets/workflow/workflow-demo.png'
import { useKnowledgeSettingContext } from '../context'

const { routeNames, routeParams } = useKnowledgeNavigationContext()

defineOptions({ name: 'KnowledgeWorkflowTransformView' })
defineProps<ResourceDetailPageProps>()
defineExpose({ hideHeader: true })

const route = useRoute()
const router = useRouter()
const { knowledgeId, resourceApi } = useKnowledgeSettingContext()

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
  return MsgConfirm('转换为工作流知识库', '转换后无法回退，请谨慎操作。', {
    confirmButtonText: '转换',
    confirmButtonType: 'primary',
  })
    .then(() => {
      loading.value = true
      return resourceApi.knowledge.postTransformWorkflow(knowledgeId.value, { work_flow: cloneDeep(knowledgeTemplate.default) }).then(() => {
        MsgSuccess('转换成功')
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
      <h1 class="mb-3">转换为工作流知识库</h1>
      <div class="text-N600">
        您现在可以将现有知识库转换为工作流知识库 ——这是一种更开放、更灵活的知识库，通过拖拽节点的方式自主编排从不同数据源到知识库写入的全流程，满足企业个性化知识管理需求。可以使用我们工具中的数据源和工具。
        <br />
        新的处理方式将应用到后续导入的所有文档。
      </div>
      <p class="mt-6 mb-2 text-warning">注意：转换后不可撤回。</p>
      <!-- 转换为工作流知识库 -->
      <el-button type="primary" :loading="loading" @click="handleTransformWorkflow">转换</el-button>
    </div>
    <img :src="workflowDemo" class="w-full min-w-0" />
  </div>
</template>
