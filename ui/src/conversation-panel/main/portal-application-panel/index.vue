<script setup lang="ts">
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import PortalApplicationCards from '../../components/portal-application-cards/index.vue'
import { useConversationListStore } from '../../left-sidebar/conversation-list/index'
import { usePortalConversationListStore } from '../../left-sidebar/portal-conversation-list/index'

defineOptions({ name: 'PortalApplicationPanel' })

const { t } = useI18n({ useScope: 'global' })

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
        <MkTooltip :content="t('chat.actions.expandSidebar')">
          <el-button text @click="toggleLeftSide()">
            <MkIcon name="icon_sidebar_outlined" :size="18" class="text-N900!" />
          </el-button>
        </MkTooltip>

        <el-divider direction="vertical" />
      </template>
      <h4 class="min-w-0 flex-1 truncate">{{ t('application.title') }}</h4>
      <!-- 搜索智能体 -->
      <MkSearchInput
        v-model="applicationKeyword"
        class="w-full! md:w-50!"
        :placeholder="t('common.placeholders.search')"
        @change="loadApplications"
      />
    </header>

    <el-scrollbar class="min-h-0 flex-1 p-4 pt-0!">
      <el-skeleton v-if="isApplicationsLoading" animated />
      <MkEmpty
        v-else-if="applications.length === 0"
        :type="applicationKeyword ? 'search' : 'default'"
        :description="applicationKeyword ? t('portal.noMatchingApplications') : t('portal.noAvailableApplications')"
        class="mt-20"
      />
      <PortalApplicationCards v-else :applications="applications" @select="openApplication" />
    </el-scrollbar>
  </main>
</template>
