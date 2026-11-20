import { computed, reactive } from 'vue'
import { t } from '@/locales'

// 回复格式展示文案，配置选项与执行详情共用。
export const REPLY_CONTENT_TYPE_LABELS: Readonly<Record<string, string>> = reactive({
  TEXT: computed(() => t('workflow.reply.format.text')),
  HTML: 'HTML',
  TOOL: computed(() => t('workflow.reply.format.tool')),
})
