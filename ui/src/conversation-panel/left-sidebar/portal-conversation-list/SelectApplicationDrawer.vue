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
    size="88%"
    :close-on-click-modal="true"
    :close-on-press-escape="true"
    content-class="p-4"
  >
    <template #header>
      <div class="flex-align-center gap-4">
        <h4 class="flex-1">选择智能体</h4>
        <MkSearchInput v-model="applicationKeyword" class="w-60!" placeholder="搜索" @input="handleKeywordInput" />
        <div class="flex-1" />
      </div>
    </template>

    <div v-loading="isLoading" class="min-h-40">
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
