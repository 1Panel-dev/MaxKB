<script setup lang="ts">
import type { ChatContent } from '@/api/types'
import ContentList from '../content-list/index.vue'
import ReverseInfiniteScroll from '../../core/reverse-infinite-scroll/index.vue'
import { useShareMessageListStore } from './index'
import { copyText } from '@/utils/clipboard'

defineOptions({ name: 'ShareMessageList' })

const { messages, loading, failed, load } = useShareMessageListStore()

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
    content-class="mk-conversation-content p-4"
    :loading="loading"
    :has-more="false"
    :count="messages.length"
    :load-more="async () => false"
  >
    <template v-for="msg in messages" :key="msg.id">
      <div>
        <ContentList :content-list="msg.content" />
        <!-- 回答底部操作栏，与对话消息底部的操作行一致 -->
        <div v-if="msg.role === 'ASSISTANT'" class="mk-conversation-message-footer mt-3">
          <div class="flex-align-center flex-wrap gap-2">
            <!-- 复制回答正文 -->
            <MkTooltip content="复制">
              <el-button text class="-ml-1" :disabled="!collectAnswerText(msg.content)" @click="copyText(collectAnswerText(msg.content))">
                <MkIcon name="icon_copy_outlined" />
              </el-button>
            </MkTooltip>
          </div>
        </div>
      </div>
    </template>
    <template #empty>
      <MkEmpty :description="failed ? '分享内容加载失败' : '暂无可分享的对话'" class="mt-20">
        <!-- 重新加载分享内容 -->
        <el-button v-if="failed" type="primary" @click="load()">重试</el-button>
      </MkEmpty>
    </template>
  </ReverseInfiniteScroll>
</template>
