<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ChatApplicationProfile } from '@/api/types'
import PortalApplicationCards from '../../components/portal-application-cards/index.vue'
import { usePortalConversationListStore } from './index'

defineOptions({ name: 'SelectApplicationDrawer' })

const { t } = useI18n({ useScope: 'global' })

// 没有当前智能体时新建对话：选择智能体后进入其新建对话。搜索条件与结果独立于全部智能体页。
const { fetchApplications, openApplication } = usePortalConversationListStore()

const visible = ref(false)
const applications = ref<ChatApplicationProfile[]>([])
const applicationKeyword = ref('')
const isLoading = ref(false)

const loadApplications = () => {
  isLoading.value = true
  fetchApplications(applicationKeyword.value)
    .then((records) => {
      applications.value = records
    })
    .finally(() => {
      isLoading.value = false
    })
}

// 每次打开清空搜索条件并重新查询
const open = () => {
  applicationKeyword.value = ''
  loadApplications()
  visible.value = true
}

const handleSelect = (applicationId: string) => {
  visible.value = false
  openApplication(applicationId)
}

defineExpose({ open })
</script>

<template>
  <MkDrawer
    v-model="visible"
    direction="btt"
    class="select-application-drawer"
    content-class="max-md:pt-0"
    :close-on-click-modal="true"
    :close-on-press-escape="true"
  >
    <template #header>
      <div class="flex w-full flex-col gap-4 md:flex-row">
        <h4>{{ t('portal.selectApplicationTitle') }}</h4>
        <div class="w-full md:absolute-center md:w-85">
          <!-- 搜索智能体 -->
          <MkSearchInput v-model="applicationKeyword" @change="loadApplications" />
        </div>
      </div>
    </template>

    <div v-loading="isLoading">
      <MkEmpty
        v-if="!isLoading && applications.length === 0"
        :type="applicationKeyword ? 'search' : 'default'"
        :description="applicationKeyword ? t('portal.noMatchingApplications') : t('portal.noAvailableApplications')"
        class="mt-10"
      />
      <PortalApplicationCards v-else :applications="applications" @select="handleSelect" />
    </div>
  </MkDrawer>
</template>

<style lang="scss" scoped>
/* 移动端选择智能体标题栏 */
@media (width < 768px) {
  :global(.select-application-drawer .el-drawer__header) {
    align-items: flex-start;
    border-bottom: none;
  }
}
</style>
