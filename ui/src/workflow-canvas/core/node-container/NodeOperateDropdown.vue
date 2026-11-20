<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { BaseNodeModel } from '@logicflow/core'
import type { FormInstance } from 'element-plus'
import { WorkflowKind, WorkflowNodeType } from '@/workflow-canvas/types'
import { MsgConfirm, MsgError } from '@/utils/message'

defineOptions({ name: 'NodeOperateDropdown' })
const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ model: BaseNodeModel }>()
const emit = defineEmits<{
  'update:disabled': [disabled: boolean]
  'update:stepName': [stepName: string]
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
    emit('update:disabled', !value)
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
      MsgError(t('workflow.node.name.duplicateMessage'))
      return
    }

    emit('update:stepName', nodeNameForm.value.title)
    props.model.clearNextNodeField(true)
    nodeNameDialogVisible.value = false
    formInstance.resetFields()
  })
}

function copyNode() {
  props.model.graphModel.clearSelectElements()
  const cloneNode = props.model.graphModel.cloneNode(props.model.id)
  if (!cloneNode) return

  cloneNode.isSelected = true
  cloneNode.isHovered = true
  props.model.graphModel.toFront(cloneNode.id)
}

function deleteNode() {
  MsgConfirm(t('common.dialogs.notice'), t('workflow.node.delete.title', { name: nodeProperties.value.stepName || '-' }), {
    confirmButtonText: t('common.actions.comfirm'),
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
      <MkIcon name="icon_more_outlined" :size="20" />
    </el-button>
    <template #dropdown>
      <MkDropdownMenu class="min-w-36">
        <MkDropdownItem @click="renameNode">
          <template #icon><MkIcon name="icon_rename_outlined" /></template>
          {{ t('common.actions.rename') }}
        </MkDropdownItem>
        <MkDropdownItem @click="copyNode">
          <template #icon><MkIcon name="icon_copy_outlined" /></template>
          {{ t('common.actions.duplicate') }}
        </MkDropdownItem>
        <div v-if="canChangeEnabled" class="flex-between px-3 py-1" @click.stop>
          <span class="flex-align-center gap-2">
            <MkIcon name="icon_yes_outlined" class="text-N600!" />
            <span>{{ t('common.status.activeLabel') }}</span>
          </span>

          <el-switch v-model="nodeEnabled" size="small" />
        </div>
        <MkDropdownItem @click="deleteNode">
          <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
          {{ t('common.actions.delete') }}
        </MkDropdownItem>
        <div v-if="sourceName" class="border-t mt-1 px-3 py-2" @click.stop>
          <div class="text-sm text-N500">{{ t('workflow.node.source') }}</div>
          <div class="mt-1 break-all text-N600">{{ sourceName }}</div>
        </div>
      </MkDropdownMenu>
    </template>
  </MkDropdown>

  <MkDialog v-model="nodeNameDialogVisible" :title="t('workflow.node.name.label')" append-to-body>
    <el-form
      ref="titleFormRef"
      :model="nodeNameForm"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item prop="title" :rules="[{ whitespace: true, required: true, message: t('common.validation.inputRequired'), trigger: 'blur' }]">
        <el-input v-model="nodeNameForm.title" @blur="nodeNameForm.title = nodeNameForm.title.trim()" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button plain @click.prevent="nodeNameDialogVisible = false">{{ t('common.actions.cancel') }}</el-button>
      <el-button type="primary" @click="saveNodeName(titleFormRef)">{{ t('common.actions.save') }}</el-button>
    </template>
  </MkDialog>
</template>
