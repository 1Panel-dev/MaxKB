<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { FOLDER_ENTRY_ID } from '@/constants'
import type { KnowledgeDetail } from '@/api/types'
import ResourceDetailLayout from '@/layout/ResourceDetailLayout.vue'
import { provideKnowledgeDetailContext } from './context'
import { isWorkspaceResource, isSystemResource, isSystemSharedResource, isWorkspaceSharedResource } from '@/utils/resource-context'

defineOptions({ name: 'KnowledgeDetailView' })

/* 知识库详情与目录 */
const route = useRoute()
const router = useRouter()
const knowledge = ref<KnowledgeDetail>()
const loading = ref(false)
function replaceKnowledgeDetail(detail: KnowledgeDetail) {
  knowledge.value = detail
}

const { knowledgeId, resourceApi, listRouteName } = provideKnowledgeDetailContext({
  knowledge: computed(() => knowledge.value),
  replaceKnowledgeDetail,
})

const detailSection = computed(() => {
  if (!isSystemResource() && !isWorkspaceResource()) return undefined
  if (String(route.name).endsWith('document-strategy')) return 'document_strategy' as const
  if (String(route.name).endsWith('setting')) return 'setting' as const
  return undefined
})

function loadKnowledgeDetail() {
  knowledge.value = undefined
  loading.value = true
  return resourceApi.knowledge
    .getKnowledgeDetail(knowledgeId.value, detailSection.value)
    .then((detail) => {
      knowledge.value = detail
    })
    .finally(() => {
      loading.value = false
    })
}

function handleBack() {
  if (isSystemResource() || isSystemSharedResource()) {
    void router.push({ name: listRouteName.value })
    return
  }
  const folderId = isWorkspaceSharedResource() ? FOLDER_ENTRY_ID.SHARED : knowledge.value?.folder_id
  void router.push({
    name: listRouteName.value,
    params: { workspaceId: route.params.workspaceId },
    query: folderId ? { folderId } : {},
  })
}

watch(
  [() => route.params.workspaceId, knowledgeId, () => route.meta.resourceScope, detailSection],
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
