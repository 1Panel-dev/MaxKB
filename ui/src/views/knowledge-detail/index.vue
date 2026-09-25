<script setup lang="ts">
import { computed, provide, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import SharedKnowledgeApi from '@/api/admin/workspace/shared/knowledge/knowledge'
import { FOLDER_ENTRY_ID } from '@/constants'
import { isWorkspaceSharedResource } from '@/utils/resource-context'
import type { KnowledgeDetail } from '@/api/types'
import ResourceDetailLayout from '@/layout/ResourceDetailLayout.vue'
import { knowledgeDetailContextKey } from './context'

defineOptions({ name: 'WorkspaceKnowledgeDetailView' })

/* 知识库详情与目录 */
const route = useRoute()
const router = useRouter()
const knowledge = ref<KnowledgeDetail>()
const loading = ref(false)
const knowledgeId = computed(() => String(route.params.knowledgeId ?? ''))
const requestApi = computed(() => (isWorkspaceSharedResource() ? SharedKnowledgeApi : KnowledgeApi))

function replaceKnowledgeDetail(detail: KnowledgeDetail) {
  knowledge.value = detail
}

provide(knowledgeDetailContextKey, {
  knowledge: computed(() => knowledge.value),
  replaceKnowledgeDetail,
})

function loadKnowledgeDetail() {
  knowledge.value = undefined
  loading.value = true
  return requestApi.value
    .getKnowledgeDetail(knowledgeId.value)
    .then((detail) => {
      knowledge.value = detail
    })
    .finally(() => {
      loading.value = false
    })
}

function handleBack() {
  const folderId = isWorkspaceSharedResource() ? FOLDER_ENTRY_ID.SHARED : knowledge.value?.folder_id
  void router.push({
    name: 'workspace-knowledge-list',
    params: { workspaceId: route.params.workspaceId },
    query: folderId ? { folderId } : {},
  })
}

watch(
  [() => route.params.workspaceId, knowledgeId, () => route.meta.resourceScope],
  () => {
    void loadKnowledgeDetail().catch(() => {})
  },
  { immediate: true },
)
</script>

<template>
  <ResourceDetailLayout :loading="loading" @back="handleBack">
    <template #resource-header>
      <KnowledgeIcon :type="knowledge?.type" />
      <h6 class="min-w-0 truncate" :title="knowledge?.name">{{ knowledge?.name }}</h6>
    </template>
  </ResourceDetailLayout>
</template>
