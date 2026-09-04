<script setup lang="ts">
import { onBeforeUnmount, useTemplateRef } from 'vue'
import { Close, Plus, Warning } from '@element-plus/icons-vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { createAnchorGuard } from '@/workflow-canvas/core/utils'
import KnowledgeSelectionDialog from '@/components/business/knowledge-selection-dialog/index.vue'
import type { KnowledgeSelection } from '@/components/business/knowledge-selection-dialog/types'
import type { SearchKnowledgeNodeForm } from '../../types'

defineOptions({ name: 'SearchKnowledgeNodeScope' })

const props = defineProps<{
  nodeModel: WorkflowNodeModel
  knowledge: KnowledgeSelection[]
  scopeType: SearchKnowledgeNodeForm['search_scope_type']
  scopeSource: SearchKnowledgeNodeForm['search_scope_source']
  scopeReference: string[]
}>()
const emit = defineEmits<{
  'update:knowledge': [knowledge: KnowledgeSelection[]]
  'update:scopeType': [value: SearchKnowledgeNodeForm['search_scope_type']]
  'update:scopeSource': [value: SearchKnowledgeNodeForm['search_scope_source']]
  'update:scopeReference': [value: string[]]
}>()

const selectionDialogRef = useTemplateRef<InstanceType<typeof KnowledgeSelectionDialog>>('selectionDialogRef')
const referenceRef = useTemplateRef<InstanceType<typeof NodeCascader>>('referenceRef')
const anchorGuard = createAnchorGuard(props.nodeModel)

function removeKnowledge(knowledgeId: string) {
  emit(
    'update:knowledge',
    props.knowledge.filter(({ id }) => id !== knowledgeId),
  )
}

function changeScopeType(value: SearchKnowledgeNodeForm['search_scope_type']) {
  anchorGuard.setOverlayVisible('reference', false)
  anchorGuard.setOverlayVisible('source', false)
  anchorGuard.setOverlayVisible('help', false)
  emit('update:scopeType', value)
}

function validate() {
  return props.scopeType === 'referencing' ? referenceRef.value?.validate() : Promise.resolve()
}

onBeforeUnmount(anchorGuard.reset)
defineExpose({ validate })
</script>

<template>
  <el-form-item>
    <template #label>
      <div class="flex-between w-full">
        <span>检索范围</span>
        <div class="flex items-center gap-2">
          <el-button v-if="scopeType === 'custom'" link type="primary" title="添加关联知识库" @click="selectionDialogRef?.open(knowledge)">
            <MkIcon :icon="Plus" />
          </el-button>
          <el-select
            :model-value="scopeType"
            :teleported="false"
            size="small"
            class="w-24!"
            @change="changeScopeType"
            @visible-change="anchorGuard.setOverlayVisible('type', $event)"
          >
            <el-option label="引用" value="referencing" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </div>
      </div>
    </template>
    <div v-if="scopeType === 'custom'" class="w-full">
      <span v-if="!knowledge.length" class="text-N600">请选择关联知识库</span>
      <div v-else class="flex flex-col gap-1">
        <div v-for="resource in knowledge" :key="resource.id" class="flex-between rounded-md border bg-white px-2 py-1">
          <span class="flex min-w-0 items-center gap-2">
            <KnowledgeIcon :type="resource.type" :size="20" class="shrink-0" />
            <span class="truncate" :title="resource.name || resource.id">{{ resource.name || resource.id }}</span>
          </span>
          <el-button text title="移除知识库" @click="removeKnowledge(resource.id)"><MkIcon :icon="Close" /></el-button>
        </div>
      </div>
    </div>
    <el-form-item v-else class="w-full" prop="search_scope_reference" :rules="{ required: true, message: '请选择引用变量', trigger: 'change' }">
      <template #label>
        <div class="flex-between w-full">
          <span class="flex items-center gap-1">
            选择变量
            <el-tooltip
              :teleported="false"
              placement="right"
              @show="anchorGuard.setOverlayVisible('help', true)"
              @hide="anchorGuard.setOverlayVisible('help', false)"
            >
              <template #content
                ><span class="whitespace-pre-wrap font-mono">{{
                  '["019d8ac3-e2c6-7ff2-8956-c9c98f0e11f4", "019d8ac3-e2c6-7ff2-8956-c9c98f0e11f3"]'
                }}</span></template
              >
              <MkIcon :icon="Warning" class="text-N600" />
            </el-tooltip>
          </span>
          <el-select
            :model-value="scopeSource"
            :teleported="false"
            size="small"
            class="w-28!"
            @change="emit('update:scopeSource', $event)"
            @visible-change="anchorGuard.setOverlayVisible('source', $event)"
          >
            <el-option label="知识库列表" value="knowledge" />
            <el-option label="文档列表" value="document" />
          </el-select>
        </div>
      </template>
      <NodeCascader
        ref="referenceRef"
        :model-value="scopeReference"
        :node-model="nodeModel"
        class="w-full"
        placeholder="请选择引用变量"
        @update:model-value="emit('update:scopeReference', $event)"
        @visible-change="anchorGuard.setOverlayVisible('reference', $event)"
      />
    </el-form-item>
  </el-form-item>
  <KnowledgeSelectionDialog ref="selectionDialogRef" @submit="emit('update:knowledge', $event)" />
</template>
