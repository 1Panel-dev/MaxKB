<script setup lang="ts">
import { computed, provide, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ApplicationApi from '@/api/admin/workspace/application/application'
import type { ApplicationDetail } from '@/api/types'
import ResourceDetailLayout from '@/layout/ResourceDetailLayout.vue'
import { applicationDetailContextKey } from './context'

defineOptions({ name: 'WorkspaceApplicationDetail' })
/**
 * Workspace 智能体详情路由容器。
 * 容器随 applicationId 加载并持有共享详情，切换二级子路由时保持挂载；子页面保存后通过上下文
 * 直接替换完整接口响应，或在响应不完整时主动刷新详情。页面框架和二级导航由 ResourceDetailLayout 负责。
 */
provide(applicationDetailContextKey, {
  application: computed(() => application.value),
  refreshApplicationDetail,
  replaceApplicationDetail,
})

const route = useRoute()
const router = useRouter()
const application = ref<ApplicationDetail>()
const loading = ref(false)
const applicationId = computed(() => String(route.params.applicationId ?? ''))

function navigateToApplicationList() {
  void router.push({
    name: 'workspace-application-list',
    params: { workspaceId: route.params.workspaceId },
    query: route.query,
  })
}

function replaceApplicationDetail(applicationDetail: ApplicationDetail) {
  application.value = applicationDetail
}

function refreshApplicationDetail() {
  const currentApplicationId = applicationId.value
  if (!currentApplicationId) return Promise.resolve()

  loading.value = true
  return ApplicationApi.getApplicationDetail(currentApplicationId)
    .then((applicationDetail) => {
      replaceApplicationDetail(applicationDetail)
    })
    .finally(() => {
      loading.value = false
    })
}

watch(
  applicationId,
  () => {
    void refreshApplicationDetail()
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
