<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useApplicationDetailContext } from '../context'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import HomeStatistics from '@/views/home/components/HomeStatistics.vue'
import ApplicationRanking from './components/ApplicationRanking.vue'

defineOptions({ name: 'ApplicationOverviewView' })
defineProps<ResourceDetailPageProps>()
defineExpose({ hideHeader: true })

/* 当前智能体的监控与用户排行 */
const route = useRoute()
const workspaceId = computed(() => String(route.params.workspaceId ?? ''))
const { applicationId, resourceApi } = useApplicationDetailContext()
</script>

<template>
  <HomeStatistics :key="applicationId" :workspace-id="workspaceId" :application-id="applicationId" :api="resourceApi.overview" />
  <ApplicationRanking :key="applicationId" class="mt-4" :application-id="applicationId" />
</template>
