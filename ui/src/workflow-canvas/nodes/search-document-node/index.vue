<script setup lang="ts">
import { computed, inject, onBeforeUnmount, onMounted, ref, useTemplateRef, watch } from 'vue'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import type { KnowledgeItem, KnowledgeTagGroup } from '@/api/types'
import NodeSearchScope from '@/workflow-canvas/component/node-search-scope/index.vue'
import type { NodeSearchScopeData } from '@/workflow-canvas/component/node-search-scope/types'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { createAnchorGuard, handleNodeWheel } from '@/workflow-canvas/core/utils'

import { compareOptions, defaultSearchCondition } from './constant'
import type { SearchDocumentForm } from './types'

defineOptions({ name: 'WorkflowSearchDocumentNode' })
const getModel = inject('getModel') as () => WorkflowNodeModel
const apiType = (inject('apiType') as string) || 'workspace'
const store = useWorkflowStore(apiType)
const model = getModel()
const formRef = useTemplateRef<FormInstance>('formRef')
const questionCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('questionCascaderRef')

// 初始化只补齐缺失数据，保留已保存的检索范围与条件。
const defaultForm: SearchDocumentForm = {
  knowledge_id_list: [],
  knowledge_list: [],
  search_scope_type: 'custom',
  search_scope_source: 'knowledge',
  search_scope_reference: [],
  search_mode: 'auto',
  question_reference: [],
  search_condition_type: 'AND',
  search_condition_list: [],
  knowledge_tags: [],
}
const savedForm = model.properties.node_data as Partial<SearchDocumentForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  knowledge_id_list: Array.isArray(savedForm?.knowledge_id_list) ? savedForm.knowledge_id_list : [],
  knowledge_list: Array.isArray(savedForm?.knowledge_list) ? savedForm.knowledge_list : [],
  search_scope_reference: Array.isArray(savedForm?.search_scope_reference) ? savedForm.search_scope_reference : [],
  question_reference: Array.isArray(savedForm?.question_reference) ? savedForm.question_reference : [],
  search_condition_list: Array.isArray(savedForm?.search_condition_list) ? savedForm.search_condition_list : [],
  knowledge_tags: Array.isArray(savedForm?.knowledge_tags) ? savedForm.knowledge_tags : [],
}
const formData = computed(() => model.properties.node_data as SearchDocumentForm)

// 关联知识库保留快照，缺少详情时仍展示和保留原 ID。
const selectedKnowledge = computed(() => {
  const knowledgeById = new Map(formData.value.knowledge_list.map((knowledge) => [knowledge.id, knowledge]))
  return formData.value.knowledge_id_list.map((id) => knowledgeById.get(id) ?? { id })
})
function updateKnowledge(knowledge: (Partial<KnowledgeItem> & { id: string })[]) {
  formData.value.knowledge_id_list = knowledge.map(({ id }) => id)
  formData.value.knowledge_list = cloneDeep(knowledge)
}
function updateSearchScope(patch: Partial<NodeSearchScopeData>) {
  model.properties.node_data = { ...formData.value, ...patch }
}

// 标签选项随关联知识库刷新。
const allKnowledgeTags = ref<KnowledgeTagGroup[]>([])
watch(
  () => formData.value.knowledge_id_list,
  (knowledgeIds) => {
    allKnowledgeTags.value = []
    formData.value.knowledge_tags = []
    if (!knowledgeIds.length) return
    store
      .getKnowledgeTags(knowledgeIds)
      .then((tags) => {
        allKnowledgeTags.value = tags
        formData.value.knowledge_tags = tags.slice(0, 100)
      })
      .catch(() => {
        allKnowledgeTags.value = []
        formData.value.knowledge_tags = []
      })
  },
  { immediate: true, deep: true },
)
function filterTags(keyword: string) {
  formData.value.knowledge_tags = allKnowledgeTags.value.filter((tag) => tag.key.includes(keyword)).slice(0, 100)
}

// 范围引用由公共组件加入表单校验，自动检索保留问题引用有效性检查。
async function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error }))
}
const anchorGuard = createAnchorGuard(model)
onBeforeUnmount(() => {
  anchorGuard.reset()
})
onMounted(() => {
  model.validate = validate
})
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">节点设置</h6>
    <div class="mk-gray-card">
      <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
        <!-- 检索范围 -->
        <NodeSearchScope
          :node-model="model"
          :form-data="formData"
          :selected-knowledge="selectedKnowledge"
          @update="updateSearchScope"
          @update:knowledge="updateKnowledge"
        />
        <!-- 检索设置 -->
        <el-form-item label="检索设置">
          <el-radio-group v-model="formData.search_mode">
            <el-radio value="auto">
              <span class="flex items-center gap-1"
                >自动<el-tooltip content="根据检索问题自动匹配文档标签" placement="right"
                  ><MkIcon name="icon_info_outlined" class="text-N600!" /></el-tooltip
              ></span>
            </el-radio>
            <el-radio v-if="formData.search_scope_type === 'custom'" value="custom">
              <span class="flex items-center gap-1"
                >手动<el-tooltip content="手动设置标签过滤条件" placement="right"><MkIcon name="icon_info_outlined" class="text-N600!" /></el-tooltip
              ></span>
            </el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item
          v-if="formData.search_mode === 'auto'"
          label="检索问题"
          prop="question_reference"
          :rules="{ required: true, message: '请选择检索问题', trigger: 'change' }"
        >
          <NodeCascader ref="questionCascaderRef" v-model="formData.question_reference" :node-model="model" placeholder="请选择检索问题" />
        </el-form-item>
        <template v-else>
          <div class="-mt-2 mb-2 flex items-center gap-2 text-sm text-N600">
            满足以下
            <el-select
              v-model="formData.search_condition_type"
              :teleported="false"
              size="small"
              class="w-18!"
              @visible-change="anchorGuard.setOverlayVisible('condition-type', $event)"
              @wheel="handleNodeWheel"
            >
              <el-option label="所有" value="AND" /><el-option label="任一" value="OR" />
            </el-select>
            条件
          </div>
          <MkFormList
            v-model="formData.search_condition_list"
            :default-item="defaultSearchCondition"
            :min-rows="0"
            :first-row-has-label="false"
            add-text="添加条件"
          >
            <template #default="{ item: condition, index }">
              <el-form-item class="small min-w-0 flex-1">
                <el-select
                  v-model="condition.key"
                  filterable
                  :filter-method="filterTags"
                  :teleported="false"
                  class="min-w-0 flex-1"
                  placeholder="请选择标签"
                  @visible-change="anchorGuard.setOverlayVisible(`tag-${index}`, $event)"
                  @wheel="handleNodeWheel"
                >
                  <el-option v-for="tag in formData.knowledge_tags" :key="tag.key" :label="tag.key" :value="tag.key" />
                </el-select>
              </el-form-item>
              <el-form-item class="small w-24 shrink-0">
                <el-select
                  v-model="condition.compare"
                  :teleported="false"
                  @visible-change="anchorGuard.setOverlayVisible(`compare-${index}`, $event)"
                  @wheel="handleNodeWheel"
                >
                  <el-option v-for="option in compareOptions" :key="option.value" :value="option.value" :label="option.label" />
                </el-select>
              </el-form-item>
              <el-form-item class="small min-w-0 flex-1">
                <el-input v-model="condition.value" placeholder="值或变量" />
              </el-form-item>
            </template>
          </MkFormList>
        </template>
      </el-form>
    </div>
  </NodeContainer>
</template>
