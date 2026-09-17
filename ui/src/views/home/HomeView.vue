<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import HomepageApi from '@/api/admin/workspace/homepage'
import ApplicationApi from '@/api/admin/workspace/application/application'
import type { ApplicationDetail } from '@/api/types'
import HomeQuickCreate from './components/HomeQuickCreate.vue'
import HomeResourceOverview from './components/HomeResourceOverview.vue'
import HomeStatistics from './components/HomeStatistics.vue'
import HomeRankings from './components/ranking/HomeRankings.vue'
const route = useRoute()
const workspaceId = computed(() => String(route.params.workspaceId))

/* 监控智能体筛选 */
const applicationId = ref('all')
const applications = ref<ApplicationDetail[]>([])
const applicationsLoading = ref(false)
const selectedApplication = ref<ApplicationDetail>()
function loadApplications(query = '') {
  applicationsLoading.value = true
  return ApplicationApi.getApplicationPage({ currentPage: 1, pageSize: 200 }, { name: query })
    .then((result) => {
      applications.value = result.records
    })
    .finally(() => {
      applicationsLoading.value = false
    })
}
function handleApplicationChange(value: string) {
  selectedApplication.value = applications.value.find((application) => application.id === value)
}
watch(
  workspaceId,
  () => {
    applicationId.value = 'all'
    applications.value = []
    selectedApplication.value = undefined
    loadApplications()
  },
  { immediate: true },
)
</script>
<template>
  <el-scrollbar class="h-full">
    <div class="px-6 py-4">
      <!-- 快捷创建 -->
      <h4 class="mb-4">快捷创建</h4>
      <HomeQuickCreate :workspace-id="workspaceId" />
      <!-- 资源 -->
      <h4 class="mb-4 mt-4">资源</h4>
      <HomeResourceOverview :api="HomepageApi" :workspace-id="workspaceId" />
      <!-- 监控 -->
      <HomeStatistics class="mt-4" :workspace-id="workspaceId" :application-id="applicationId" :api="HomepageApi">
        <template #application="{ loading }">
          <el-select
            v-model="applicationId"
            filterable
            remote
            fit-input-width
            class="w-55!"
            :remote-method="loadApplications"
            :loading="applicationsLoading"
            :disabled="loading"
            @change="handleApplicationChange"
          >
            <el-option label="全部智能体" value="all">
              <div class="flex items-center gap-2">
                <MkIcon name="icon_card_outlined" :size="20" class="shrink-0 text-N600" />
                <span>全部智能体</span>
              </div>
            </el-option>
            <template v-for="application in applications" :key="application.id">
              <el-option :label="application.name" :value="application.id">
                <div class="flex items-center gap-2">
                  <ApplicationIcon :icon="application.icon" :size="20" class="shrink-0" />
                  <span class="truncate" :title="application.name">{{ application.name }}</span>
                </div>
              </el-option>
            </template>
            <template #label="{ label, value }">
              <div class="flex items-center gap-2">
                <MkIcon v-if="value === 'all'" name="icon_card_outlined" :size="18" class="shrink-0" />
                <ApplicationIcon v-else :icon="selectedApplication?.icon" :size="18" class="shrink-0" />
                <span class="truncate" :title="label">{{ label }}</span>
              </div>
            </template>
          </el-select>
        </template>
      </HomeStatistics>
      <!-- 排行榜 TOP5 -->
      <HomeRankings class="mt-4" :workspace-id="workspaceId" :api="HomepageApi" />
    </div>
  </el-scrollbar>
</template>
