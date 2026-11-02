<script setup lang="ts">
import { ref } from 'vue'
import { debounce } from 'lodash'
import type { ChatApplicationProfile } from '@/api/types'
import PortalApplicationCards from '../../components/portal-application-cards/index.vue'
import { usePortalConversationListStore } from './index'

defineOptions({ name: 'SelectApplicationDrawer' })

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

// 输入名称时延迟搜索，避免每个字符都发起请求
const handleKeywordInput = debounce(loadApplications, 300)

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
      <div class="flex w-full">
        <h4>选择智能体</h4>
        <div class="absolute-center hidden w-85 md:block">
          <!-- 搜索智能体 -->
          <MkSearchInput v-model="applicationKeyword" @input="handleKeywordInput" />
        </div>
      </div>
    </template>

    <div class="mb-4 md:hidden">
      <!-- 移动端搜索智能体 -->
      <MkSearchInput v-model="applicationKeyword" @input="handleKeywordInput" />
    </div>

    <div v-loading="isLoading">
      <MkEmpty
        v-if="!isLoading && applications.length === 0"
        :type="applicationKeyword ? 'search' : 'default'"
        :description="applicationKeyword ? '没有匹配的智能体' : '暂无可用智能体'"
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
    border-bottom: none;
  }
}
</style>
