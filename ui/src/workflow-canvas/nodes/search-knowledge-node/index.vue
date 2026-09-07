<script setup lang="ts">
import type { KnowledgeItem } from '@/api/types'
import { computed, inject, onMounted, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import NodeSearchScope from '@/workflow-canvas/component/node-search-scope/index.vue'
import type { NodeSearchScopeData } from '@/workflow-canvas/component/node-search-scope/types'
import SearchSetting from './component/SearchSetting.vue'
import { defaultSearchSetting, searchModeOptions } from './constant.ts'
import type { SearchKnowledgeNodeForm } from './types'

defineOptions({ name: 'WorkflowSearchKnowledgeNode' })

const getModel = inject('getModel') as () => WorkflowNodeModel
const model = getModel()
const formRef = useTemplateRef<FormInstance>('formRef')
const questionReferenceRef = useTemplateRef<InstanceType<typeof NodeCascader>>('questionReferenceRef')

// 初始化时补齐旧工作流缺失的字段，读取表单时不再改写节点数据。
const defaultForm: SearchKnowledgeNodeForm = {
  knowledge_id_list: [],
  knowledge_list: [],
  knowledge_setting: cloneDeep(defaultSearchSetting),
  question_reference_address: [],
  show_knowledge: false,
  search_scope_type: 'custom',
  search_scope_source: 'knowledge',
  search_scope_reference: [],
}
const savedForm = model.properties.node_data as Partial<SearchKnowledgeNodeForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  knowledge_id_list: Array.isArray(savedForm?.knowledge_id_list) ? savedForm.knowledge_id_list : [],
  knowledge_list: Array.isArray(savedForm?.knowledge_list) ? savedForm.knowledge_list : [],
  knowledge_setting: { ...defaultForm.knowledge_setting, ...savedForm?.knowledge_setting },
  question_reference_address: Array.isArray(savedForm?.question_reference_address) ? savedForm.question_reference_address : [],
  show_knowledge: savedForm?.show_knowledge ?? false,
  search_scope_type: savedForm?.search_scope_type ?? defaultForm.search_scope_type,
  search_scope_source: savedForm?.search_scope_source ?? defaultForm.search_scope_source,
  search_scope_reference: Array.isArray(savedForm?.search_scope_reference) ? savedForm.search_scope_reference : [],
} satisfies SearchKnowledgeNodeForm

const formData = computed(() => model.properties.node_data as SearchKnowledgeNodeForm)
const selectedKnowledge = computed(() => {
  const knowledgeById = new Map(formData.value.knowledge_list.map((knowledge) => [knowledge.id, knowledge]))
  return formData.value.knowledge_id_list.map((id) => knowledgeById.get(id) ?? { id })
})

// 节点统一写回关联数据，并保留旧工作流移除知识库时的缓存清理。
function updateKnowledge(knowledge: (Partial<KnowledgeItem> & { id: string })[]) {
  const knowledgeIds = knowledge.map(({ id }) => id)
  const removedIds = new Set(formData.value.knowledge_id_list.filter((id) => !knowledgeIds.includes(id)))
  formData.value.knowledge_id_list = knowledgeIds
  formData.value.knowledge_list = cloneDeep(knowledge)
  if (formData.value.all_knowledge_id_list) {
    // 全量关联还包含当前用户不可见的知识库，只移除本次明确取消的 ID。
    formData.value.all_knowledge_id_list = formData.value.all_knowledge_id_list.filter((id) => !removedIds.has(id))
  }
}

function updateSearchScope(patch: Partial<NodeSearchScopeData>) {
  model.properties.node_data = { ...formData.value, ...patch }
}

// 检索参数由弹窗编辑，确认后统一写回。
const settingRows = computed(() => [
  {
    label: '检索模式',
    value:
      searchModeOptions.find(({ value }) => value === formData.value.knowledge_setting.search_mode)?.label ??
      formData.value.knowledge_setting.search_mode,
  },
  { label: '相似度高于', value: formData.value.knowledge_setting.similarity.toFixed(3) },
  { label: '引用分段数 TOP', value: formData.value.knowledge_setting.top_n },
  { label: '最多引用字符数', value: formData.value.knowledge_setting.max_paragraph_char_number },
])

// 检索范围由组件加入表单校验，检索问题保留原有引用有效性检查。
function validate() {
  return Promise.all([questionReferenceRef.value?.validate(), formRef.value?.validate()]).catch((error) =>
    Promise.reject({ node: model, errMessage: error }),
  )
}

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
        <!-- 检索参数 -->
        <el-form-item>
          <template #label>
            <div class="flex-between">
              <span>检索参数</span>
              <SearchSetting v-model="formData.knowledge_setting" />
            </div>
          </template>
          <div class="mk-white-card w-full">
            <ul class="space-y-2">
              <li v-for="row in settingRows" :key="row.label" class="flex gap-4">
                <span class="w-28 shrink-0 text-N600">{{ row.label }}</span>
                <span class="min-w-0 flex-1 truncate" :title="String(row.value)">
                  {{ row.value }}
                </span>
              </li>
            </ul>
          </div>
        </el-form-item>
        <!-- 检索问题 -->
        <el-form-item label="检索问题" prop="question_reference_address" :rules="{ required: true, message: '请选择检索问题', trigger: 'change' }">
          <NodeCascader ref="questionReferenceRef" v-model="formData.question_reference_address" :node-model="model" placeholder="请选择检索问题" />
        </el-form-item>
        <div class="flex-between">
          <span>结果显示在知识来源中</span>
          <el-switch v-model="formData.show_knowledge" size="small" />
        </div>
      </el-form>
    </div>
  </NodeContainer>
</template>
