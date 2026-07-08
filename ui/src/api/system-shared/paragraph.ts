import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { pageRequest } from '@/api/type/common'
import type { Ref } from 'vue'
const prefix = '/system/shared/knowledge'

/**
 * 创建段落
 * @param 参数
 * knowledge_id, document_id
 * {
      "content": "string",
      "title": "string",
      "is_active": true,
      "problem_list": [
        {
          "content": "string"
        }
      ]
    }
 */
const postParagraph: (
  knowledge_id: string,
  document_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, document_id, data, loading) => {
  return post(
    `${prefix}/${knowledge_id}/document/${document_id}/paragraph`,
    data,
    undefined,
    loading,
  )
}

/**
 * 段落列表
 * @param 参数 knowledge_id document_id
 * param {
          "title": "string",
          "content": "string",
        }
 */
const getParagraphPage: (
  knowledge_id: string,
  document_id: string,
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, document_id, page, param, loading) => {
  return get(
    `${prefix}/${knowledge_id}/document/${document_id}/paragraph/${page.current_page}/${page.page_size}`,
    param,
    loading,
  )
}

/**
 * 修改段落
 * @param 参数
 * knowledge_id, document_id, paragraph_id
 * {
    "content": "string",
    "title": "string",
    "is_active": true,
      "problem_list": [
        {
          "content": "string"
        }
      ]
  }
 */
const putParagraph: (
  knowledge_id: string,
  document_id: string,
  paragraph_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, document_id, paragraph_id, data, loading) => {
  return put(
    `${prefix}/${knowledge_id}/document/${document_id}/paragraph/${paragraph_id}`,
    data,
    undefined,
    loading,
  )
}

/**
 * 删除段落
 * @param 参数 knowledge_id, document_id, paragraph_id
 */
const delParagraph: (
  knowledge_id: string,
  document_id: string,
  paragraph_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (knowledge_id, document_id, paragraph_id, loading) => {
  return del(
    `${prefix}/${knowledge_id}/document/${document_id}/paragraph/${paragraph_id}`,
    undefined,
    {},
    loading,
  )
}

/**
 * 某段落问题列表
 * @param 参数 knowledge_id，document_id，paragraph_id
 */
const getParagraphProblem: (
  knowledge_id: string,
  document_id: string,
  paragraph_id: string,
) => Promise<Result<any>> = (knowledge_id, document_id, paragraph_id: string) => {
  return get(`${prefix}/${knowledge_id}/document/${document_id}/paragraph/${paragraph_id}/problem`)
}

/**
 * 给某段落创建问题
 * @param 参数
 * knowledge_id, document_id, paragraph_id
 * {
      content": "string"
    }
 */
const postParagraphProblem: (
  knowledge_id: string,
  document_id: string,
  paragraph_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, document_id, paragraph_id, data: any, loading) => {
  return post(
    `${prefix}/${knowledge_id}/document/${document_id}/paragraph/${paragraph_id}/problem`,
    data,
    {},
    loading,
  )
}

/**
 * 段落调整顺序
 * @param knowledge_id 数据集id
 * @param document_id 文档id
 * @param loading 加载器
 * @query data {
 *              paragraph_id 段落id  new_position 新顺序
 *             }
 */
const putAdjustPosition: (
  knowledge_id: string,
  document_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, document_id, data, loading) => {
  return put(
    `${prefix}/${knowledge_id}/document/${document_id}/paragraph/adjust_position`,
    {},
    data,
    loading,
  )
}

/**
 * 添加某段落关联问题
 * @param knowledge_id 数据集id
 * @param document_id 文档id
 * @param loading 加载器
 * @query data {
 *              paragraph_id 段落id  problem_id 问题id
 *             }
 */
const putAssociationProblem: (
  knowledge_id: string,
  document_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, document_id, data, loading) => {
  return put(
    `${prefix}/${knowledge_id}/document/${document_id}/paragraph/association`,
    {},
    data,
    loading,
  )
}

/**
 * 批量删除段落
 * @param 参数 knowledge_id, document_id
 */
const putMulParagraph: (
  knowledge_id: string,
  document_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (knowledge_id, document_id, data, loading) => {
  return put(
    `${prefix}/${knowledge_id}/document/${document_id}/paragraph/batch_delete`,
    { id_list: data },
    undefined,
    loading,
  )
}

/**
 * 批量关联问题
 * @param 参数 knowledge_id, document_id
 * {
      "paragraph_id_list": [
        "3fa85f64-5717-4562-b3fc-2c963f66afa6"
      ],
      "model_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "prompt": "string",
      "document_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }
 */
const putBatchGenerateRelated: (
  knowledge_id: string,
  document_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (knowledge_id, document_id, data, loading) => {
  return put(
    `${prefix}/${knowledge_id}/document/${document_id}/paragraph/batch_generate_related`,
    data,
    undefined,
    loading,
  )
}

/**
 * 批量迁移段落
 * @param 参数 knowledge_id,target_knowledge_id,
 */
const putMigrateMulParagraph: (
  knowledge_id: string,
  document_id: string,
  target_knowledge_id: string,
  target_document_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (
  knowledge_id,
  document_id,
  target_knowledge_id,
  target_document_id,
  data,
  loading,
) => {
  return put(
    `${prefix}/${knowledge_id}/document/${document_id}/paragraph/migrate/knowledge/${target_knowledge_id}/document/${target_document_id}`,
    data,
    undefined,
    loading,
  )
}

/**
 * 解除某段落关联问题
 * @param 参数 knowledge_id, document_id,
 * @query data {
 *            paragraph_id 段落id  problem_id 问题id
 *         }
 */
const putDisassociationProblem: (
  knowledge_id: string,
  document_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (knowledge_id, document_id, data, loading) => {
  return put(
    `${prefix}/${knowledge_id}/document/${document_id}/paragraph/unassociation`,
    {},
    data,
    loading,
  )
}

export default {
  postParagraph,
  getParagraphPage,
  putParagraph,
  delParagraph,
  getParagraphProblem,
  postParagraphProblem,
  putAssociationProblem,
  putMulParagraph,
  putBatchGenerateRelated,
  putMigrateMulParagraph,
  putDisassociationProblem,
  putAdjustPosition,
}
