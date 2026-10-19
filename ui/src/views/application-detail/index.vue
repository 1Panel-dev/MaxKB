<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { ApplicationDetail } from '@/api/types'
import ResourceDetailLayout from '@/layout/ResourceDetailLayout.vue'
import { provideApplicationDetailContext } from './context'
import { isWorkspaceResource } from '@/utils/resource-context'

defineOptions({ name: 'ApplicationDetailView' })
/**
 * 智能体详情路由容器。
 * 容器随 applicationId 加载并持有共享详情，切换二级子路由时保持挂载；子页面保存后通过上下文
 * 直接替换完整接口响应，或在响应不完整时主动刷新详情。页面框架和二级导航由 ResourceDetailLayout 负责。
 */
const route = useRoute()
const router = useRouter()
const application = ref<ApplicationDetail>()
const loading = ref(false)
const { applicationId, resourceApi, listRouteName, routeParams } = provideApplicationDetailContext({
  application: computed(() => application.value),
  refreshApplicationDetail,
  replaceApplicationDetail,
})

function navigateToApplicationList() {
  void router.push({
    name: listRouteName.value,
    params: isWorkspaceResource() ? { workspaceId: routeParams.value.workspaceId } : {},
    query: isWorkspaceResource() && application.value?.folder ? { folderId: application.value.folder } : {},
  })
}

function replaceApplicationDetail(applicationDetail: ApplicationDetail) {
  application.value = applicationDetail
}

function refreshApplicationDetail(showLoading = true) {
  const currentApplicationId = applicationId.value
  const requestApi = resourceApi.application
  if (!currentApplicationId || !requestApi.getApplicationDetail) return Promise.resolve()

  if (showLoading) loading.value = true
  return requestApi
    .getApplicationDetail(currentApplicationId)
    .then((applicationDetail) => {
      replaceApplicationDetail(applicationDetail)
    })
    .finally(() => {
      if (showLoading) loading.value = false
    })
}

watch(
  [() => route.params.workspaceId, applicationId, () => route.meta.resourceScope],
  () => {
    application.value = undefined
    void refreshApplicationDetail().catch(() => {})
  },
  { immediate: true },
)
</script>

<template>
  <ResourceDetailLayout :loading="loading" @back="navigateToApplicationList">
    <template #resource-header>
      <ApplicationIcon :icon="application?.icon" />
      <h6 class="min-w-0 truncate" :title="application?.name">{{ application?.name }}</h6>
    </template>
  </ResourceDetailLayout>
</template>
