import { computed, reactive } from 'vue'
import { t } from '@/locales'

// 分段策略展示文案，配置选项与执行详情共用。
export const DOCUMENT_SPLIT_STRATEGY_LABELS: Readonly<Record<string, string>> = reactive({
  auto: computed(() => t('knowledge.documentStrategy.smart.label')),
  custom: computed(() => t('knowledge.documentStrategy.advanced.label')),
  qa: computed(() => t('knowledge.document.upload.qaLabel')),
})
