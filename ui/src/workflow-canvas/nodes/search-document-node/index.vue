<script setup lang="ts">
import { computed, inject, onBeforeUnmount, onMounted, ref, useTemplateRef, watch } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import type { KnowledgeItem, KnowledgeTagGroup } from '@/api/types'
import SelectKnowledgeDialog from '@/components/business/select-knowledge-dialog/index.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { createAnchorGuard, handleNodeWheel } from '@/workflow-canvas/core/utils'

defineOptions({ name: 'WorkflowSearchDocumentNode' })
const getModel = inject('getModel') as () => WorkflowNodeModel
const getKnowledgeTags = inject('getKnowledgeTags') as (knowledgeIds: string[]) => Promise<KnowledgeTagGroup[]>
const model = getModel()
const formRef = useTemplateRef<FormInstance>('formRef')
const scopeCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('scopeCascaderRef')
const questionCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('questionCascaderRef')
const knowledgeDialogRef = useTemplateRef<InstanceType<typeof SelectKnowledgeDialog>>('knowledgeDialogRef')

interface SearchCondition {
  key: string
  compare: 'contain' | 'not_contain' | 'eq'
  value: string
}
interface SearchDocumentForm {
  knowledge_id_list: string[]
  knowledge_list: (Partial<KnowledgeItem> & { id: string })[]
  search_scope_type: 'custom' | 'referencing'
  search_scope_source: 'knowledge' | 'document'
  search_scope_reference: string[]
  search_mode: 'auto' | 'custom'
  question_reference: string[]
  search_condition_type: 'AND' | 'OR'
  search_condition_list: SearchCondition[]
  knowledge_tags: KnowledgeTagGroup[]
}
const compareOptions = [
  { value: 'contain', label: '包含' },
  { value: 'not_contain', label: '不包含' },
  { value: 'eq', label: '等于' },
]
const scopeExample = '示例：\n["019d8ac3-e2c6-7ff2-8956-c9c98f0e11f4", "019d8ac3-e2c6-7ff2-8956-c9c98f0e11f3"]'

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
function openKnowledgeDialog() {
  knowledgeDialogRef.value?.open(selectedKnowledge.value)
}
function updateKnowledge(knowledge: (Partial<KnowledgeItem> & { id: string })[]) {
  formData.value.knowledge_id_list = knowledge.map(({ id }) => id)
  formData.value.knowledge_list = cloneDeep(knowledge)
}
function removeKnowledge(knowledgeId: string) {
  updateKnowledge(selectedKnowledge.value.filter(({ id }) => id !== knowledgeId))
}
function changeScopeSource() {
  formData.value.search_scope_reference = []
}

// 标签选项随关联知识库刷新；请求过期或节点卸载后不再回写。
const allKnowledgeTags = ref<KnowledgeTagGroup[]>([])
let tagRequestVersion = 0
watch(
  () => formData.value.knowledge_id_list,
  (knowledgeIds) => {
    const version = ++tagRequestVersion
    allKnowledgeTags.value = []
    formData.value.knowledge_tags = []
    if (!knowledgeIds.length) return
    getKnowledgeTags(knowledgeIds)
      .then((tags) => {
        if (version !== tagRequestVersion) return
        allKnowledgeTags.value = tags
        formData.value.knowledge_tags = tags.slice(0, 100)
      })
      .catch(() => {
        if (version !== tagRequestVersion) return
        allKnowledgeTags.value = []
        formData.value.knowledge_tags = []
      })
  },
  { immediate: true, deep: true },
)
function filterTags(keyword: string) {
  formData.value.knowledge_tags = allKnowledgeTags.value.filter((tag) => tag.key.includes(keyword)).slice(0, 100)
}
function addCondition() {
  formData.value.search_condition_list = [...cloneDeep(formData.value.search_condition_list), { key: '', compare: 'contain', value: '' }]
}
function removeCondition(index: number) {
  formData.value.search_condition_list = cloneDeep(formData.value.search_condition_list.filter((_, conditionIndex) => conditionIndex !== index))
}

function validate() {
  return Promise.all([scopeCascaderRef.value?.validate(), questionCascaderRef.value?.validate(), formRef.value?.validate()]).catch((error) =>
    Promise.reject({ node: model, errMessage: error }),
  )
}
const anchorGuard = createAnchorGuard(model)
onBeforeUnmount(() => {
  tagRequestVersion++
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
        <el-form-item>
          <template #label>
            <div class="flex-between">
              <span>检索范围</span>
              <div class="flex items-center gap-2">
                <el-button v-if="formData.search_scope_type === 'custom'" link type="primary" title="添加关联知识库" @click="openKnowledgeDialog"
                  ><MkIcon name="icon_add_outlined"
                /></el-button>
                <el-select
                  v-model="formData.search_scope_type"
                  :teleported="false"
                  size="small"
                  class="w-22!"
                  @visible-change="anchorGuard.setOverlayVisible('scope-type', $event)"
                  @wheel="handleNodeWheel"
                >
                  <el-option label="引用变量" value="referencing" /><el-option label="自定义" value="custom" />
                </el-select>
              </div>
            </div>
          </template>
          <div v-if="formData.search_scope_type === 'custom'" class="w-full">
            <span v-if="!selectedKnowledge.length" class="text-N600">请选择关联知识库</span>
            <div v-else class="flex flex-col gap-2">
              <div v-for="knowledge in selectedKnowledge" :key="knowledge.id" class="flex-between rounded-md border bg-white px-2 py-1">
                <span class="flex min-w-0 items-center gap-2">
                  <KnowledgeIcon :type="knowledge.type" :size="20" class="shrink-0" />
                  <span class="truncate" :title="knowledge.name || knowledge.id">{{ knowledge.name || knowledge.id }}</span>
                </span>
                <el-button text title="移除知识库" @click="removeKnowledge(knowledge.id)"><MkIcon name="icon_close_outlined" /></el-button>
              </div>
            </div>
          </div>
          <el-form-item
            v-else
            class="mk-hide-asterisk w-full"
            prop="search_scope_reference"
            :rules="{ required: true, message: '请选择引用变量', trigger: 'change' }"
          >
            <template #label>
              <div class="flex-between">
                <span class="flex items-center gap-1">
                  <span class="mk-required">选择变量</span>
                  <el-tooltip placement="right">
                    <template #content
                      ><div class="font-mono whitespace-pre-wrap">{{ scopeExample }}</div></template
                    >
                    <MkIcon name="icon_info_outlined" class="text-N600!" />
                  </el-tooltip>
                </span>
                <el-select
                  v-model="formData.search_scope_source"
                  :teleported="false"
                  size="small"
                  class="w-26!"
                  @change="changeScopeSource"
                  @visible-change="anchorGuard.setOverlayVisible('scope-source', $event)"
                  @wheel="handleNodeWheel"
                >
                  <el-option label="知识库列表" value="knowledge" /><el-option label="文档列表" value="document" />
                </el-select>
              </div>
            </template>
            <NodeCascader ref="scopeCascaderRef" v-model="formData.search_scope_reference" :node-model="model" placeholder="请选择引用变量" />
          </el-form-item>
        </el-form-item>
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
          <div class="mb-2 flex items-center gap-2 text-sm text-N600">
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
          <div class="flex flex-col gap-2">
            <div v-for="(condition, index) in formData.search_condition_list" :key="index" class="flex items-start gap-2">
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
              <el-select
                v-model="condition.compare"
                :teleported="false"
                class="w-24!"
                @visible-change="anchorGuard.setOverlayVisible(`compare-${index}`, $event)"
                @wheel="handleNodeWheel"
              >
                <el-option v-for="option in compareOptions" :key="option.value" :value="option.value" :label="option.label" />
              </el-select>
              <el-input v-model="condition.value" placeholder="值或变量" class="min-w-0 flex-1" />
              <el-button text title="删除条件" @click="removeCondition(index)"
                ><MkIcon name="icon_delete-trash_outlined" class="text-N600"
              /></el-button>
            </div>
          </div>
          <el-button link type="primary" class="mt-2" @click="addCondition"><MkIcon name="icon_add_outlined" />添加条件</el-button>
        </template>
      </el-form>
    </div>
    <SelectKnowledgeDialog ref="knowledgeDialogRef" @submit="updateKnowledge" />
  </NodeContainer>
</template>
