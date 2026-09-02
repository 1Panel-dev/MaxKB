<script setup lang="ts">
import type { BaseNodeModel } from '@logicflow/core'
import type { FormInstance } from 'element-plus'
import { computed, ref, useTemplateRef } from 'vue'
import { set } from 'lodash'

import { WorkflowKind, WorkflowNodeType } from '@/workflow-canvas/types'
import { MsgConfirm, MsgError } from '@/utils/message'

defineOptions({ name: 'NodeOperateDropdown' })

const props = defineProps<{ model: BaseNodeModel }>()
const emit = defineEmits<{
  'visible-change': [visible: boolean]
}>()

interface NodeNameForm {
  title: string
}

interface NodeOperateProperties {
  disabled?: boolean
  kind?: WorkflowKind
  node_data?: { name?: string }
  stepName?: string
}

const nodeProperties = computed(() => props.model.properties as unknown as NodeOperateProperties)
const visible = computed(() => {
  return ![
    WorkflowNodeType.Start,
    WorkflowNodeType.Base,
    WorkflowNodeType.KnowledgeBase,
    WorkflowNodeType.LoopStartNode.toString(),
    WorkflowNodeType.ToolBaseNode,
    WorkflowNodeType.ToolStartNode,
  ].includes(String(props.model.type))
})
const canChangeEnabled = computed(() => {
  return !(
    (String(props.model.type) === WorkflowNodeType.ToolLib && nodeProperties.value.kind === WorkflowKind.DataSource) ||
    String(props.model.type) === WorkflowNodeType.DataSourceLocalNode ||
    String(props.model.type) === WorkflowNodeType.DataSourceWebNode
  )
})
const nodeEnabled = computed({
  get: () => !nodeProperties.value.disabled,
  set: (value: boolean) => {
    set(props.model.properties, 'disabled', !value)
  },
})
const sourceName = computed(() => {
  if ([WorkflowNodeType.Application, WorkflowNodeType.ToolLib].includes(String(props.model.type) as WorkflowNodeType)) {
    return nodeProperties.value.node_data?.name ?? ''
  }
  return ''
})

const titleFormRef = useTemplateRef<FormInstance>('titleFormRef')
const nodeNameDialogVisible = ref(false)
const nodeNameForm = ref<NodeNameForm>({ title: '' })

function renameNode() {
  nodeNameForm.value.title = String(nodeProperties.value.stepName ?? '')
  nodeNameDialogVisible.value = true
}

async function saveNodeName(formInstance: FormInstance | null | undefined) {
  if (!formInstance) return

  await formInstance.validate((valid) => {
    if (!valid) return

    const nameExists = props.model.graphModel.nodes
      .filter((node) => node.id !== props.model.id)
      .some((node) => node.properties.stepName === nodeNameForm.value.title)
    if (nameExists) {
      MsgError('节点名称已存在！')
      return
    }

    set(props.model.properties, 'stepName', nodeNameForm.value.title)
    props.model.clearNextNodeField(true)
    nodeNameDialogVisible.value = false
    formInstance.resetFields()
  })
}

function copyNode() {
  props.model.graphModel.clearSelectElements()
  const cloneNode = props.model.graphModel.cloneNode(props.model.id)
  if (!cloneNode) return

  set(cloneNode, 'isSelected', true)
  set(cloneNode, 'isHovered', true)
  props.model.graphModel.toFront(cloneNode.id)
}

function deleteNode() {
  MsgConfirm('提示', '确定删除当前节点吗？', {
    confirmButtonText: '确定',
    confirmButtonClass: 'danger',
  }).then(() => {
    if (String(props.model.type) === WorkflowNodeType.LoopNode) {
      const outgoingNodes = props.model.graphModel.getNodeOutgoingNode(props.model.id)
      outgoingNodes.forEach((outgoingNode) => {
        if (String(outgoingNode.type) === WorkflowNodeType.LoopBodyNode) {
          props.model.graphModel.deleteNode(outgoingNode.id)
        }
      })
    }
    props.model.graphModel.deleteNode(props.model.id)
  })
  props.model.graphModel.eventCenter.emit('delete_node', undefined)
}
</script>

<template>
  <MkDropdown v-if="visible" :teleported="false" trigger="click" @visible-change="emit('visible-change', $event)">
    <el-button text>
      <MkIcon name="icon_more_outlined" />
    </el-button>
    <template #dropdown>
      <MkDropdownMenu class="min-w-36">
        <MkDropdownItem @click="renameNode">
          <template #icon><MkIcon name="icon_rename_outlined" /></template>
          重命名
        </MkDropdownItem>
        <MkDropdownItem @click="copyNode">
          <template #icon><MkIcon name="icon_copy_outlined" /></template>
          复制
        </MkDropdownItem>
        <div v-if="canChangeEnabled" class="flex-between px-3 py-1" @click.stop>
          <span class="flex items-center gap-2">
            <MkIcon name="icon_yes_outlined" class="text-N600!" />
            <span>启用状态</span>
          </span>

          <el-switch v-model="nodeEnabled" size="small" />
        </div>
        <MkDropdownItem divided @click="deleteNode">
          <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
          删除
        </MkDropdownItem>
        <div v-if="sourceName" class="border-t mt-1 px-3 py-2" @click.stop>
          <div class="text-sm text-N600">来源</div>
          <div class="mt-1 break-all text-N600">{{ sourceName }}</div>
        </div>
      </MkDropdownMenu>
    </template>
  </MkDropdown>

  <MkDialog v-model="nodeNameDialogVisible" title="节点名称" append-to-body @submit.prevent>
    <el-form ref="titleFormRef" :model="nodeNameForm" label-position="top">
      <el-form-item prop="title" :rules="[{ required: true, message: '请输入', trigger: 'blur' }]">
        <el-input v-model="nodeNameForm.title" @blur="nodeNameForm.title = nodeNameForm.title.trim()" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click.prevent="nodeNameDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="saveNodeName(titleFormRef)">保存</el-button>
    </template>
  </MkDialog>
</template>
