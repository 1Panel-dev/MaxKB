<script setup lang="ts">
import { computed, nextTick, provide, ref, useTemplateRef, type Component, type Ref } from 'vue'
import type LogicFlow from '@logicflow/core'
import KnowledgeWorkflowApi from '@/api/admin/workspace/knowledge/workflow'
import type { LoadingTarget } from '@/api/admin/core/types'
import type { Dict } from '@/api/types'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import type { FormField } from '@/components/mk-dynamics-form'
import DataSource from './action/DataSource.vue'
import KnowledgeBase from './action/KnowledgeBase.vue'
import Result from './action/Result.vue'

defineOptions({ name: 'KnowledgeWorkflowDebugDrawer' })

const props = defineProps<{ knowledgeId: string }>()

type ActionStep = 'data_source' | 'knowledge_base' | 'result'

const actionComponents: Record<ActionStep, Component> = { data_source: DataSource, knowledge_base: KnowledgeBase, result: Result }

// mk-dynamics-form 的上传项通过 inject('upload') 获取上传函数；返回值的 data 为文件地址（末段即 file_id）。
provide('upload', (file: File, loading?: Ref<boolean>) =>
  KnowledgeWorkflowApi.postKnowledgeUploadFile(props.knowledgeId, file, loading as LoadingTarget).then((url) => ({ data: url })),
)

const visible = ref(false)
const loading = ref(false)
const active = ref<ActionStep>('data_source')
const actionKey = ref(0)
const actionId = ref<string>()
const currentWorkflow = ref<LogicFlow.GraphConfigData | null>(null)
const formPayload = ref<{ data_source: Dict<unknown>; knowledge_base: Dict<unknown> }>({ data_source: {}, knowledge_base: {} })

const actionRef = useTemplateRef<{ validate: () => Promise<unknown>; getData: () => Dict<unknown> }>('actionRef')

// 知识库节点存在用户输入字段时，才需要「数据源 → 知识库输入」两步。
const hasKnowledgeBaseInput = computed(() => {
  const node = currentWorkflow.value?.nodes?.find((item) => item.type === WorkflowNodeType.KnowledgeBase)
  return ((node?.properties?.user_input_field_list as FormField[] | undefined)?.length ?? 0) > 0
})

const showNext = computed(() => hasKnowledgeBaseInput.value && active.value === 'data_source')
const showPrev = computed(() => hasKnowledgeBaseInput.value && active.value === 'knowledge_base')
const showImport = computed(() => (hasKnowledgeBaseInput.value ? active.value === 'knowledge_base' : active.value === 'data_source'))

function next() {
  actionRef.value?.validate().then(() => {
    formPayload.value.data_source = actionRef.value?.getData() ?? {}
    active.value = 'knowledge_base'
  })
}

function prev() {
  formPayload.value.knowledge_base = actionRef.value?.getData() ?? {}
  active.value = 'data_source'
}

function submit() {
  actionRef.value?.validate().then(() => {
    formPayload.value[active.value as 'data_source' | 'knowledge_base'] = actionRef.value?.getData() ?? {}
    KnowledgeWorkflowApi.postKnowledgeWorkflowDebug(
      props.knowledgeId,
      { data_source: formPayload.value.data_source, knowledge_base: formPayload.value.knowledge_base },
      loading,
    ).then((action) => {
      actionId.value = action.id
      active.value = 'result'
    })
  })
}

// 继续导入：重置表单并强制重建动作组件，保留当前工作流。
function continueImporting() {
  const workflow = currentWorkflow.value
  currentWorkflow.value = null
  actionId.value = undefined
  formPayload.value = { data_source: {}, knowledge_base: {} }
  active.value = 'data_source'
  actionKey.value += 1
  nextTick(() => {
    currentWorkflow.value = workflow
  })
}

function open(workflow: LogicFlow.GraphConfigData) {
  currentWorkflow.value = workflow
  active.value = 'data_source'
  actionId.value = undefined
  formPayload.value = { data_source: {}, knowledge_base: {} }
  actionKey.value += 1
  visible.value = true
}

function close() {
  visible.value = false
  currentWorkflow.value = null
  active.value = 'data_source'
  actionId.value = undefined
}

defineExpose({ open, close })
</script>

<template>
  <MkDrawer v-model="visible" title="调试" size="800" :close-on-click-modal="false" :close-on-press-escape="false" @closed="close">
    <div v-loading="loading" class="h-full">
      <keep-alive :include="['DataSource', 'KnowledgeBase']">
        <component
          :is="actionComponents[active]"
          :key="actionKey"
          ref="actionRef"
          v-model:loading="loading"
          :workflow="currentWorkflow"
          :knowledge-id="knowledgeId"
          :action-id="actionId"
        />
      </keep-alive>
    </div>

    <template #footer>
      <div class="flex justify-end gap-3">
        <el-button v-if="active === 'result'" @click="continueImporting">继续导入</el-button>
        <el-button v-if="showPrev" :disabled="loading" @click="prev">上一步</el-button>
        <el-button v-if="showNext" :disabled="loading" @click="next">下一步</el-button>
        <el-button v-if="showImport" type="primary" :loading="loading" @click="submit">导入</el-button>
        <el-button v-if="active === 'result'" type="primary" @click="close">完成</el-button>
      </div>
    </template>
  </MkDrawer>
</template>
