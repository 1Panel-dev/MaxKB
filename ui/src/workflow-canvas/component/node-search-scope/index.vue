<script setup lang="ts">
import type { KnowledgeItem } from '@/api/types'
import { nextTick, onBeforeUnmount, useTemplateRef } from 'vue'
import type { FormItemInstance } from 'element-plus'
import SelectKnowledgeDialog from '@/components/business/select-knowledge-dialog/index.vue'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { createAnchorGuard, handleNodeWheel } from '@/workflow-canvas/core/utils'
import type { NodeSearchScopeData } from './types'

defineOptions({ name: 'NodeSearchScope' })

const props = defineProps<{
  nodeModel: WorkflowNodeModel
  formData: NodeSearchScopeData
  selectedKnowledge: (Partial<KnowledgeItem> & { id: string })[]
}>()
const emit = defineEmits<{
  update: [patch: Partial<NodeSearchScopeData>]
  'update:knowledge': [knowledge: (Partial<KnowledgeItem> & { id: string })[]]
}>()
const selectionDialogRef = useTemplateRef<InstanceType<typeof SelectKnowledgeDialog>>('selectionDialogRef')
const scopeReferenceRef = useTemplateRef<InstanceType<typeof NodeCascader>>('scopeReferenceRef')
const referenceFormItemRef = useTemplateRef<FormItemInstance>('referenceFormItemRef')
const scopeExample = `示例：
[
  "019d8ac3-e2c6-7ff2-8956-c9c98f0e11f4",
  "019d8ac3-e2c6-7ff2-8956-c9c98f0e11f3"
]`

// 选择结果交给节点写回，节点保留快照与不可见知识库的清理规则。
function removeKnowledge(knowledgeId: string) {
  emit(
    'update:knowledge',
    props.selectedKnowledge.filter(({ id }) => id !== knowledgeId),
  )
}

// 切换范围保留已有配置；切换列表来源时清空不再适用的引用。
function changeScopeType(search_scope_type: NodeSearchScopeData['search_scope_type']) {
  emit('update', { search_scope_type })
  anchorGuard.setOverlayVisible('knowledge-help', false)
  anchorGuard.setOverlayVisible('document-help', false)
  nextTick(() => referenceFormItemRef.value?.clearValidate())
}
function changeScopeSource(search_scope_source: NodeSearchScopeData['search_scope_source']) {
  emit('update', { search_scope_source, search_scope_reference: [] })
  nextTick(() => referenceFormItemRef.value?.clearValidate())
}

// 引用范围加入节点外层表单，自定义范围不注册隐藏引用的规则。
async function validateReference() {
  if (props.formData.search_scope_type !== 'referencing') return
  if (!props.formData.search_scope_reference.length) throw new Error('请选择引用变量')
  await nextTick()
  if (!scopeReferenceRef.value) throw new Error('请选择引用变量')
  await scopeReferenceRef.value.validate().catch((error: unknown) => {
    throw error instanceof Error ? error : new Error(String(error))
  })
}

const anchorGuard = createAnchorGuard(props.nodeModel)
onBeforeUnmount(() => anchorGuard.reset())
</script>

<template>
  <el-form-item>
    <template #label>
      <div class="flex-between">
        <span>检索范围</span>
        <div class="flex items-center gap-2">
          <el-button
            v-if="formData.search_scope_type === 'custom'"
            link
            type="primary"
            title="添加关联知识库"
            @click="selectionDialogRef?.open(selectedKnowledge)"
          >
            <MkIcon name="icon_add_outlined" />
          </el-button>
          <el-select
            :model-value="formData.search_scope_type"
            :validate-event="false"
            :teleported="false"
            size="small"
            class="w-18!"
            @wheel="handleNodeWheel"
            @update:model-value="changeScopeType"
            @visible-change="anchorGuard.setOverlayVisible('scope-type', $event)"
          >
            <el-option label="引用" value="referencing" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </div>
      </div>
    </template>
    <div v-if="formData.search_scope_type === 'custom'" class="w-full">
      <span v-if="!selectedKnowledge.length" class="text-N600">请选择关联知识库</span>
      <div v-else class="flex flex-col gap-1">
        <template v-for="knowledge in selectedKnowledge" :key="knowledge.id">
          <el-card class="small" shadow="never">
            <div class="flex-between">
              <span class="flex min-w-0 items-center gap-2">
                <KnowledgeIcon :type="knowledge.type" :size="20" class="shrink-0 small" />
                <span class="truncate" :title="knowledge.name || knowledge.id">{{ knowledge.name || knowledge.id }}</span>
              </span>
              <!-- 移除知识库 -->
              <el-button text title="移除知识库" @click="removeKnowledge(knowledge.id)"><MkIcon name="icon_close_outlined" /></el-button>
            </div>
          </el-card>
        </template>
      </div>
    </div>
    <el-form-item
      v-else
      ref="referenceFormItemRef"
      class="mk-hide-asterisk w-full"
      prop="search_scope_reference"
      :rules="{ validator: validateReference, trigger: 'change' }"
    >
      <el-radio-group class="mb-1" :model-value="formData.search_scope_source" :validate-event="false" @update:model-value="changeScopeSource">
        <el-radio value="knowledge">
          <span class="flex items-center gap-1">
            <span>知识库列表</span>
            <span class="relative inline-flex">
              <el-tooltip
                :teleported="false"
                placement="right"
                @show="anchorGuard.setOverlayVisible('knowledge-help', true)"
                @hide="anchorGuard.setOverlayVisible('knowledge-help', false)"
              >
                <template #content>
                  <span class="whitespace-pre font-mono">{{ scopeExample }}</span>
                </template>
                <span class="inline-flex">
                  <MkIcon name="icon_info_outlined" class="text-N600!" />
                </span>
              </el-tooltip>
            </span>
          </span>
        </el-radio>
        <el-radio value="document">
          <span class="flex items-center gap-1">
            <span>文档列表</span>
            <span class="relative inline-flex">
              <el-tooltip
                :teleported="false"
                placement="right"
                @show="anchorGuard.setOverlayVisible('document-help', true)"
                @hide="anchorGuard.setOverlayVisible('document-help', false)"
              >
                <template #content>
                  <span class="whitespace-pre font-mono">{{ scopeExample }}</span>
                </template>
                <span class="inline-flex">
                  <MkIcon name="icon_info_outlined" class="text-N600!" />
                </span>
              </el-tooltip>
            </span>
          </span>
        </el-radio>
      </el-radio-group>

      <NodeCascader
        ref="scopeReferenceRef"
        :model-value="formData.search_scope_reference"
        @update:model-value="emit('update', { search_scope_reference: $event })"
        :node-model="nodeModel"
        placeholder="请选择引用变量"
      />
    </el-form-item>
  </el-form-item>
  <SelectKnowledgeDialog ref="selectionDialogRef" @submit="emit('update:knowledge', $event)" />
</template>
