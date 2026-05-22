import { Result } from '@/request/Result'
import { get, post, del, put, exportFile } from '@/request/index'
import { type Ref } from 'vue'
import type { pageRequest } from '@/api/type/common'

import useStore from '@/stores'
const prefix: any = { _value: '/workspace/' }
Object.defineProperty(prefix, 'value', {
  get: function () {
    const { user } = useStore()
    return this._value + user.getWorkspaceId() + '/homepage'
  },
})

/**
 * 应用聚合
 * @params
 */
const getApplicationAggregation: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get(`${prefix.value}/application/aggregation`, undefined, loading)
}
/**
 * 知识库聚合
 * @params
 */
const getKnowledgeAggregation: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get(`${prefix.value}/knowledge/aggregation`, undefined, loading)
}
/**
 * 工具聚合
 * @params
 */
const getToolAggregation: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get(`${prefix.value}/tool/aggregation`, undefined, loading)
}
/**
 * 模型聚合
 * @params
 */
const getModelAggregation: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get(`${prefix.value}/model/aggregation`, undefined, loading)
}

/**
 * Tokens 消耗
 * @params
 */
const getTokensRanking: (page: pageRequest, loading?: Ref<boolean>) => Promise<Result<any>> = (
  page,
  loading,
) => {
  return get(
    `${prefix.value}/application/tokens_ranking/${page.current_page}/${page.page_size}`,
    undefined,
    loading,
  )
}
/**
 * 提问次数
 * @params
 */
const getQuestionsRanking: (page: pageRequest, loading?: Ref<boolean>) => Promise<Result<any>> = (
  page,
  loading,
) => {
  return get(
    `${prefix.value}/application/question_ranking/${page.current_page}/${page.page_size}`,
    undefined,
    loading,
  )
}
/**
 * 用户消耗token
 * @params
 */
const getUserTokensRanking: (page: pageRequest, loading?: Ref<boolean>) => Promise<Result<any>> = (
  page,
  loading,
) => {
  return get(
    `${prefix.value}/application/user_tokens_ranking/${page.current_page}/${page.page_size}`,
    undefined,
    loading,
  )
}

/**
 * 与对话有关的统计趋势
 * @params
 */
const getMonitorAggregation: (page: pageRequest, loading?: Ref<boolean>) => Promise<Result<any>> = (
  page,
  loading,
) => {
  return get(
    `${prefix.value}/monitor_aggregation/${page.current_page}/${page.page_size}`,
    undefined,
    loading,
  )
}

export default {
  getApplicationAggregation,
  getKnowledgeAggregation,
  getToolAggregation,
  getModelAggregation,
  getTokensRanking,
  getQuestionsRanking,
  getUserTokensRanking,
}
