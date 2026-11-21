<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ChatContent } from '@/api/types'
import ReverseInfiniteScroll from '../../core/reverse-infinite-scroll/index.vue'
import ContentList from '../content-list/index.vue'
import { useShareMessageListStore } from './index'
import { copyText } from '@/utils/clipboard'
import { resetUrl } from '@/utils/icon'

defineOptions({ name: 'ShareMessageList' })

const { t } = useI18n({ useScope: 'global' })
const { appInfo, messages, loading, failed, load } = useShareMessageListStore()
const avatar = computed(() => appInfo.value?.avatar)
const userAvatar = computed(() => appInfo.value?.user_avatar)
const showAvatar = computed(() => appInfo.value?.show_avatar)
const showUserAvatar = computed(() => appInfo.value?.show_user_avatar)

// 仅复制回答正文，按展示顺序收集分组内的文本，不包含思考与工具参数。
function collectAnswerText(contents: ChatContent[]): string {
  return [...contents]
    .sort((left, right) => (left.id || '').localeCompare(right.id || ''))
    .flatMap((content) => {
      if (content.type === 'GROUP') return collectAnswerText(content.children ?? [])
      return content.type === 'TEXT' ? content.content || '' : []
    })
    .filter(Boolean)
    .join('\n\n')
}
</script>

<template>
  <!-- 分享消息列表：只读展示公开分享接口返回的问答 -->
  <ReverseInfiniteScroll
    content-class="mk-conversation-content space-y-2 p-4"
    :loading="loading"
    :has-more="false"
    :count="messages.length"
    :load-more="async () => false"
  >
    <template v-for="msg in messages" :key="msg.id">
      <div v-if="msg.role === 'USER'">
        <div v-if="showUserAvatar" class="text-right mb-2">
          <el-avatar v-if="userAvatar" class="bg-transparent!" shape="square" :size="24">
            <img :src="resetUrl(userAvatar)" alt="" />
          </el-avatar>
          <el-avatar v-else :size="24" :style="{ background: appInfo?.custom_theme?.theme_color || 'var(--mk-primary-gradient)' }">
            <img src="@/assets/mk_icon_user_gradient.svg" alt="" style="width: 50%" />
          </el-avatar>
        </div>
        <ContentList :content-list="msg.content" />
      </div>
      <div v-else>
        <ApplicationIcon v-if="showAvatar" :icon="avatar" :size="24" class="shrink-0 mb-3" />
        <ContentList :content-list="msg.content" />
        <!-- 回答底部操作栏，与对话消息底部的操作行一致 -->
        <div class="mk-conversation-message-footer mt-3">
          <div class="flex-align-center flex-wrap gap-2">
            <!-- 复制回答正文 -->
            <MkTooltip :content="t('common.actions.copy')">
              <el-button
                text
                class="-ml-1"
                :disabled="!collectAnswerText(msg.content)"
                @click="copyText(collectAnswerText(msg.content), t('common.messages.copied'))"
              >
                <MkIcon name="icon_copy_outlined" />
              </el-button>
            </MkTooltip>
          </div>
        </div>
      </div>
    </template>
    <template #empty>
      <MkEmpty :description="failed ? t('chat.share.loadFailedMessage') : t('chat.share.empty')" class="mt-20">
        <!-- 重新加载分享内容 -->
        <el-button v-if="failed" type="primary" @click="load()">{{ t('common.actions.retry') }}</el-button>
      </MkEmpty>
    </template>
  </ReverseInfiniteScroll>
</template>
