<script setup lang="ts">
import { computed, provide, ref, watch } from 'vue'
import { MkDynamicsForm, type DynamicFormValue, type FormField } from '@/components/mk-dynamics-form'
import type { Dict } from '@/api/types'
import KnowledgeWorkflowApi from '@/api/admin/workspace/knowledge/workflow'
import { getWorkspaceId } from '@/utils/resource-context'
import { iconComponent } from '@/workflow-canvas/icons/utils'
import { WorkflowKind, WorkflowNodeType } from '@/workflow-canvas/types'

defineOptions({ name: 'DataSource' })

interface WorkflowNode {
  id: string
  type: WorkflowNodeType
  properties: {
    kind?: string
    stepName?: string
    node_data?: { tool_lib_id?: string } & Dict<unknown>
  } & Dict<unknown>
}

const props = defineProps<{
  workflow: { nodes?: WorkflowNode[] } | null
  knowledgeId: string
}>()

const loading = defineModel<boolean>('loading', { default: false })

// 数据源选择与动态表单。
const dynamicsFormRef = ref<InstanceType<typeof MkDynamicsForm>>()
const baseFormData = ref<{ node_id: string }>({ node_id: '' })
const dynamicsFormData = ref<Dict<DynamicFormValue>>({})

const formData = computed<Dict<DynamicFormValue>>({
  get: () => ({ ...dynamicsFormData.value, ...baseFormData.value }),
  set: (value: Dict<DynamicFormValue>) => {
    dynamicsFormData.value = value
  },
})

const sourceNodeList = computed(() => props.workflow?.nodes?.filter((node) => node.properties?.kind === WorkflowKind.DataSource) ?? [])
const hasKnowledgeBaseInput = computed(() => {
  const node = props.workflow?.nodes?.find((node) => node.type === WorkflowNodeType.KnowledgeBase)
  return ((node?.properties?.user_input_field_list as FormField[] | undefined)?.length ?? 0) > 0
})

const isLocalSource = (node: WorkflowNode) => [WorkflowNodeType.DataSourceLocalNode, WorkflowNodeType.DataSourceWebNode].includes(node.type)
const sourceContext = ref<{ current_tool_id?: string }>({
  current_tool_id: undefined,
})
// 动态目录字段沿用 get_extra 注入协议，读取当前工具上下文。
provide('get_extra', () => sourceContext.value)

function handleSourceChange(nodeId: string) {
  baseFormData.value.node_id = nodeId
  const node = sourceNodeList.value.find((sourceNode) => sourceNode.id === nodeId)
  if (!node) return
  if (node.properties.node_data?.tool_lib_id) {
    sourceContext.value.current_tool_id = node.properties.node_data.tool_lib_id
  }
  const localSource = isLocalSource(node)
  const sourceType = localSource ? 'local' : 'tool'
  const sourceId = localSource ? node.type : (node.properties.node_data?.tool_lib_id ?? node.type)
  loading.value = true
  return KnowledgeWorkflowApi.getKnowledgeWorkflowFormList(props.knowledgeId, sourceType, sourceId, node as unknown as Dict<unknown>)
    .then((fields) => dynamicsFormRef.value?.render(fields as unknown as FormField[]))
    .finally(() => {
      loading.value = false
    })
}

watch(
  sourceNodeList,
  () => {
    const firstNode = sourceNodeList.value[0]
    if (!baseFormData.value.node_id && firstNode) {
      handleSourceChange(firstNode.id)
    }
  },
  { immediate: true },
)

// 表单校验与调试载荷。
function validate() {
  return dynamicsFormRef.value?.validate() ?? Promise.resolve()
}

// 仅提交上传成功的文件，避免把上传中/失败的文件带入调试请求。
function getData() {
  const data = formData.value
  return {
    ...data,
    file_list:
      (data.file_list as DynamicFormValue[] | undefined)?.filter((file) => file.status !== 'uploading' && file.status !== 'fail') ?? data.file_list,
  }
}

defineExpose({ validate, getData })
</script>

<template>
  <MkDynamicsForm
    ref="dynamicsFormRef"
    v-model="formData"
    :render-data="[]"
    :other-params="{ current_workspace_id: getWorkspaceId(), current_knowledge_id: knowledgeId }"
    label-position="top"
    require-asterisk-position="right"
  >
    <template #default>
      <h4 v-if="hasKnowledgeBaseInput" class="mb-4 mk-title-decoration">选择数据源</h4>
      <el-form-item label="数据源类型">
        <div class="grid w-full grid-cols-3 gap-2">
          <template v-for="node in sourceNodeList" :key="node.id">
            <el-card
              shadow="never"
              class="small min-w-0 cursor-pointer"
              :class="baseFormData.node_id === node.id ? 'border-primary!' : ''"
              @click="handleSourceChange(node.id)"
            >
              <div class="flex-align-center gap-2">
                <component :is="iconComponent(`${node.type}-icon`)" class="size-5!" />
                <span class="min-w-0 truncate">{{ node.properties.stepName }}</span>
              </div>
            </el-card>
          </template>
        </div>
      </el-form-item>
    </template>
  </MkDynamicsForm>
</template>
