/** 沿用 v2 PROMPT_CACHE，按用户记忆最近提交的关联问题配置。 */
import { cloneDeep, isPlainObject } from 'lodash'
import type { RelatedQuestionsConfig } from '@/api/types'

const PROMPT_CACHE_KEY = 'PROMPT_CACHE'

interface PromptCacheEntry {
  user: string
  formValue: RelatedQuestionsConfig
}

function readPromptCache(): PromptCacheEntry[] {
  try {
    const saved = JSON.parse(localStorage.getItem(PROMPT_CACHE_KEY) || '[]')
    if (Array.isArray(saved)) {
      return saved.filter(
        (entry: PromptCacheEntry) =>
          typeof entry?.user === 'string' &&
          typeof entry.formValue?.model_id === 'string' &&
          typeof entry.formValue?.prompt === 'string' &&
          isPlainObject(entry.formValue?.model_params_setting),
      )
    }
  } catch {
    // 缓存损坏或浏览器禁止存储时使用默认表单。
  }
  return []
}

/** 每次打开读取当前用户配置，表单修改不影响已保存内容。 */
export function getPromptConfig(userId: string, defaultPrompt: string): RelatedQuestionsConfig {
  const saved = userId ? readPromptCache().find(({ user }) => user === userId) : undefined
  return saved ? cloneDeep(saved.formValue) : { model_id: '', model_params_setting: {}, prompt: defaultPrompt }
}

/** 提交时仅替换当前用户记录，保留其他用户的配置。 */
export function savePromptConfig(userId: string, config: RelatedQuestionsConfig) {
  if (!userId) return
  const configs = readPromptCache().filter(({ user }) => user !== userId)
  configs.push({ user: userId, formValue: cloneDeep(config) })
  try {
    localStorage.setItem(PROMPT_CACHE_KEY, JSON.stringify(configs))
  } catch {
    // 存储不可用时跳过记忆，不阻止任务提交或修改当前表单。
  }
}
