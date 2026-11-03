<script setup lang="ts">
import { onMounted } from 'vue'
import { useConversationListStore } from '../../left-sidebar/conversation-list/index'
import { usePortalConversationListStore } from '../../left-sidebar/portal-conversation-list/index'
import PortalApplicationCards from '../../components/portal-application-cards/index.vue'

defineOptions({ name: 'PortalApplicationPanel' })

const { leftSideOpen, toggleLeftSide } = useConversationListStore()
const portalList = usePortalConversationListStore()
const { applications, applicationKeyword, isApplicationsLoading, loadApplications, openApplication } = portalList

onMounted(() => {
  loadApplications()
})
</script>

<template>
  <!-- 全部智能体主面板:头部 + 智能体卡片列表 -->
  <main class="mk-conversation-main">
    <header class="flex-align-center shrink-0 gap-2 px-4 py-3 max-md:flex-wrap max-md:gap-y-4">
      <!-- 左侧收起时才在顶部显示:展开左侧 + 新建对话(展开时它们在侧栏内) -->
      <template v-if="!leftSideOpen">
        <!-- 展开左侧 -->
        <MkTooltip content="展开侧边栏">
          <el-button text @click="toggleLeftSide()">
            <MkIcon name="icon_sidebar_outlined" :size="18" class="text-N900!" />
          </el-button>
        </MkTooltip>

        <el-divider direction="vertical" />
      </template>
      <h4 class="min-w-0 flex-1 truncate">智能体</h4>
      <!-- 搜索智能体 -->
      <MkSearchInput v-model="applicationKeyword" class="w-full! md:w-50!" placeholder="搜索" @change="loadApplications" />
    </header>

    <el-scrollbar v-loading="isApplicationsLoading" class="min-h-0 flex-1 p-4 pt-0!">
      <MkEmpty
        v-if="!isApplicationsLoading && applications.length === 0"
        :type="applicationKeyword ? 'search' : 'default'"
        :description="applicationKeyword ? '没有匹配的智能体' : '暂无可用智能体'"
        class="mt-20"
      />
      <PortalApplicationCards v-else :applications="applications" @select="openApplication" />
    </el-scrollbar>
  </main>
</template>
