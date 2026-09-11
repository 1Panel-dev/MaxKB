<script setup lang="ts">
import { computed, ref, watch, provide } from 'vue'
import type { FormRules } from 'element-plus'
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

const baseFormRules: FormRules = {
  node_id: { required: true, trigger: 'change', message: '请选择数据源' },
}

const isLocalSource = (node: WorkflowNode) => [WorkflowNodeType.DataSourceLocalNode, WorkflowNodeType.DataSourceWebNode].includes(node.type)
const extra = ref<any>({
  current_tool_id: undefined,
})
const get_extra = () => {
  return extra.value
}
provide('get_extra', get_extra)

function sourceChange(nodeId: string) {
  baseFormData.value.node_id = nodeId
  const node = sourceNodeList.value.find((item) => item.id === nodeId)
  if (!node) return
  if (node.properties.node_data && node.properties.node_data.tool_lib_id) {
    extra.value.current_tool_id = node.properties.node_data.tool_lib_id
  }
  const type = isLocalSource(node) ? 'local' : 'tool'
  const id = isLocalSource(node) ? node.type : (node.properties.node_data?.tool_lib_id ?? node.type)
  KnowledgeWorkflowApi.getKnowledgeWorkflowFormList(props.knowledgeId, type, id, node as unknown as Dict<unknown>, loading).then((fields) => {
    dynamicsFormRef.value?.render(fields as unknown as FormField[])
  })
}

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

watch(
  sourceNodeList,
  () => {
    const firstNode = sourceNodeList.value[0]
    if (!baseFormData.value.node_id && firstNode) {
      sourceChange(firstNode.id)
    }
  },
  { immediate: true },
)

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
      <h4 class="mb-4 mt-1">选择数据源</h4>
      <el-form-item label="数据源" prop="node_id" :rules="baseFormRules.node_id">
        <el-row class="w-full" :gutter="8">
          <el-col v-for="node in sourceNodeList" :key="node.id" :span="8">
            <el-card
              shadow="never"
              class="mb-2 w-full cursor-pointer"
              :class="baseFormData.node_id === node.id ? 'border-primary!' : ''"
              style="--el-card-padding: 4px 12px"
              @click="sourceChange(node.id)"
            >
              <div class="flex items-center gap-2">
                <component :is="iconComponent(`${node.type}-icon`)" class="size-5" />
                <span class="min-w-0 truncate">{{ node.properties.stepName }}</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-form-item>
    </template>
  </MkDynamicsForm>
</template>
