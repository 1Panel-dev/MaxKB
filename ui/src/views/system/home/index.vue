<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import SystemHomepageApi from '@/api/admin/system/homepage'
import WorkspaceApi from '@/api/admin/system/workspace'
import ApplicationApi from '@/api/admin/workspace/application/application'
import type { ApplicationDetail, WorkspaceItem } from '@/api/types'
import WorkspaceDropdown from '@/components/business/workspace-dropdown/index.vue'
import { useStore } from '@/stores'
import HomeResourceOverview from '@/views/home/components/HomeResourceOverview.vue'
import HomeStatistics from '@/views/home/components/HomeStatistics.vue'
import HomeRankings from '@/views/home/components/ranking/HomeRankings.vue'

defineOptions({ name: 'SystemHomeView' })

const { auth } = useStore()

/* 工作空间筛选 */
const selectedWorkspaceId = ref('default')
const workspaceOptions = ref<WorkspaceItem[]>([])
function loadWorkspaceOptions() {
  return WorkspaceApi.getSystemWorkspaceList().then((workspaces) => {
    workspaceOptions.value = workspaces
    if (!workspaces.some(({ id }) => id === selectedWorkspaceId.value)) {
      selectedWorkspaceId.value = workspaces[0]?.id ?? 'default'
    }
  })
}
function handleWorkspaceSelect(workspace: WorkspaceItem) {
  selectedWorkspaceId.value = workspace.id ?? 'default'
}

/* 监控智能体筛选 */
const applicationId = ref('all')
const applications = ref<ApplicationDetail[]>([])
const applicationsLoading = ref(false)
const selectedApplication = ref<ApplicationDetail>()
function loadApplications(query = '') {
  applicationsLoading.value = true
  return ApplicationApi.getApplicationPage({ currentPage: 1, pageSize: 200 }, { name: query }, selectedWorkspaceId.value)
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
  selectedWorkspaceId,
  () => {
    applicationId.value = 'all'
    applications.value = []
    selectedApplication.value = undefined
    loadApplications()
  },
  { immediate: true },
)

onMounted(() => {
  if (auth.isEE) {
    loadWorkspaceOptions()
  }
})
</script>
<template>
  <el-scrollbar class="h-full">
    <!-- 切换工作空间 -->
    <div class="px-6 py-4">
      <WorkspaceDropdown v-model="selectedWorkspaceId" :options="workspaceOptions" @select="handleWorkspaceSelect" />
    </div>
    <el-divider />
    <!-- 资源 -->
    <div class="px-6 py-4">
      <h4 class="mb-4 mt-4">资源</h4>
      <HomeResourceOverview :key="selectedWorkspaceId" :api="SystemHomepageApi" :workspace-id="selectedWorkspaceId" />
      <!-- 监控 -->
      <HomeStatistics
        :key="selectedWorkspaceId"
        class="mt-4"
        :workspace-id="selectedWorkspaceId"
        :application-id="applicationId"
        :api="SystemHomepageApi"
      >
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
              <div class="flex-align-center gap-2">
                <MkIcon name="icon_card_outlined" :size="20" class="shrink-0 text-N600" />
                <span>全部智能体</span>
              </div>
            </el-option>
            <!--  TODO 全部智能体 -->
            <template v-for="application in applications" :key="application.id">
              <el-option :label="application.name" :value="application.id">
                <div class="flex-align-center gap-2">
                  <ApplicationIcon :icon="application.icon" :size="20" class="shrink-0" />
                  <span class="truncate" :title="application.name">{{ application.name }}</span>
                </div>
              </el-option>
            </template>
            <template #label="{ label, value }">
              <div class="flex-align-center gap-2">
                <MkIcon v-if="value === 'all'" name="icon_card_outlined" :size="18" class="shrink-0" />
                <ApplicationIcon v-else :icon="selectedApplication?.icon" :size="18" class="shrink-0" />
                <span class="truncate" :title="label">{{ label }}</span>
              </div>
            </template>
          </el-select>
        </template>
      </HomeStatistics>
      <!-- 排行榜 TOP5 -->
      <HomeRankings :key="selectedWorkspaceId" class="mt-4" :workspace-id="selectedWorkspaceId" :api="SystemHomepageApi" />
    </div>
  </el-scrollbar>
</template>
