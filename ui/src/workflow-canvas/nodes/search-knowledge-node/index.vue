<script setup lang="ts">
import { computed, inject, onMounted, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import type { KnowledgeSelection } from '@/components/business/knowledge-selection-dialog/types'
import SearchScope from './component/search-scope/index.vue'
import SearchSetting from './component/search-setting/index.vue'
import { defaultSearchSetting } from './config'
import type { SearchKnowledgeNodeForm } from './types'

defineOptions({ name: 'WorkflowSearchKnowledgeNode' })

const getModel = inject('getModel') as () => WorkflowNodeModel
const model = getModel()
const formRef = useTemplateRef<FormInstance>('formRef')
const searchScopeRef = useTemplateRef<InstanceType<typeof SearchScope>>('searchScopeRef')
const questionReferenceRef = useTemplateRef<InstanceType<typeof NodeCascader>>('questionReferenceRef')

// 初始化时补齐旧工作流缺失的字段，读取表单时不再改写节点数据。
const savedData = (model.properties.node_data ?? {}) as Partial<SearchKnowledgeNodeForm>
model.properties.node_data = {
  ...savedData,
  knowledge_id_list: savedData.knowledge_id_list ?? [],
  knowledge_list: savedData.knowledge_list ?? [],
  knowledge_setting: { ...cloneDeep(defaultSearchSetting), ...savedData.knowledge_setting },
  question_reference_address: savedData.question_reference_address ?? [],
  show_knowledge: savedData.show_knowledge ?? false,
  search_scope_type: savedData.search_scope_type ?? 'custom',
  search_scope_source: savedData.search_scope_source ?? 'knowledge',
  search_scope_reference: savedData.search_scope_reference ?? [],
} satisfies SearchKnowledgeNodeForm

const formData = computed(() => model.properties.node_data as SearchKnowledgeNodeForm)
const selectedKnowledge = computed(() => {
  const knowledgeById = new Map(formData.value.knowledge_list.map((knowledge) => [knowledge.id, knowledge]))
  return formData.value.knowledge_id_list.map((id) => knowledgeById.get(id) ?? { id })
})

// 节点统一写回关联数据，并保留旧工作流移除知识库时的缓存清理。
function updateKnowledge(knowledge: KnowledgeSelection[]) {
  const knowledgeIds = knowledge.map(({ id }) => id)
  const removedIds = new Set(formData.value.knowledge_id_list.filter((id) => !knowledgeIds.includes(id)))
  formData.value.knowledge_id_list = knowledgeIds
  formData.value.knowledge_list = cloneDeep(knowledge)
  if (formData.value.all_knowledge_id_list) {
    // 全量关联还包含当前用户不可见的知识库，只移除本次明确取消的 ID。
    formData.value.all_knowledge_id_list = formData.value.all_knowledge_id_list.filter((id) => !removedIds.has(id))
  }
}

function updateScopeSource(source: SearchKnowledgeNodeForm['search_scope_source']) {
  formData.value.search_scope_source = source
  formData.value.search_scope_reference = []
}

// 两个变量选择器独立校验；自定义范围不校验隐藏的引用变量。
function validate() {
  return Promise.all([searchScopeRef.value?.validate(), questionReferenceRef.value?.validate(), formRef.value?.validate()]).catch((error) =>
    Promise.reject({ node: model, errMessage: error }),
  )
}

onMounted(() => {
  model.validate = validate
})
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mb-3">节点设置</h6>
    <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
      <SearchScope
        ref="searchScopeRef"
        :node-model="model"
        :knowledge="selectedKnowledge"
        :scope-type="formData.search_scope_type"
        :scope-source="formData.search_scope_source"
        :scope-reference="formData.search_scope_reference"
        @update:knowledge="updateKnowledge"
        @update:scope-type="formData.search_scope_type = $event"
        @update:scope-source="updateScopeSource"
        @update:scope-reference="formData.search_scope_reference = $event"
      />
      <SearchSetting :setting="formData.knowledge_setting" @update="formData.knowledge_setting = $event" />
      <el-form-item label="检索问题" prop="question_reference_address" :rules="{ required: true, message: '请选择检索问题', trigger: 'change' }">
        <NodeCascader
          ref="questionReferenceRef"
          v-model="formData.question_reference_address"
          :node-model="model"
          class="w-full"
          placeholder="请选择检索问题"
        />
      </el-form-item>
      <el-form-item label="结果显示在知识来源中" prop="show_knowledge" :rules="{ required: true, message: '请设置参数', trigger: 'change' }">
        <el-switch v-model="formData.show_knowledge" size="small" />
      </el-form-item>
    </el-form>
  </NodeContainer>
</template>
