<template>
  <div class="w-full">
    <div class="flex-between mb-2">
      <span>
        拆分变量
        <span class="ml-1 text-danger">*</span>
      </span>
      <el-button link type="primary" @click="openAddDialog()">
        <MkIcon name="icon_add_outlined" class="mr-1" />
        添加
      </el-button>
    </div>

    <MkTable size="small" v-if="inputFieldList.length > 0" :data="inputFieldList" row-key="field">
      <el-table-column prop="field" label="变量" width="100" show-overflow-tooltip>
        <template #default="{ row }">
          <span :title="row.field" class="block truncate">{{ row.field }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="label" label="显示名称" min-width="90">
        <template #default="{ row }">
          <span :title="row.label" class="block truncate">{{ row.label }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="72">
        <template #default="{ row, $index }">
          <el-button text class="h-6! w-6! p-0!" aria-label="编辑" @click="openAddDialog(row, $index)">
            <MkIcon name="icon_edit_outlined" />
          </el-button>
          <el-button text class="ml-0! h-6! w-6! p-0!" aria-label="删除" @click="deleteField($index)">
            <MkIcon name="icon_delete-trash_outlined" />
          </el-button>
        </template>
      </el-table-column>
    </MkTable>
    <MkEmpty v-else description="暂无变量，请点击添加" :image-size="60" />

    <VariableFieldDialog ref="VariableFieldDialogRef" @refresh="refreshFieldList" />
  </div>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import { cloneDeep } from 'lodash'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'

import VariableFieldDialog from './VariableFieldDialog.vue'
import { MsgError } from '@/utils/message'

defineOptions({ name: 'WorkflowVariableSplittingFieldTable' })

const props = defineProps<{ nodeModel: WorkflowNodeModel }>()

const VariableFieldDialogRef = ref<InstanceType<typeof VariableFieldDialog>>()

const nodeProps = props.nodeModel.properties as unknown as {
  config: Record<string, unknown>
  node_data: Record<string, unknown>
}

if (!nodeProps.node_data) {
  nodeProps.node_data = {}
}
if (!Array.isArray(nodeProps.node_data.variable_list)) {
  nodeProps.node_data.variable_list = []
}

const inputFieldList = computed<Array<Record<string, unknown>>>({
  get: () => nodeProps.node_data.variable_list as Array<Record<string, unknown>>,
  set: (value) => {
    nodeProps.node_data.variable_list = value
  },
})

function syncConfig() {
  const fields = [{ label: '结果', value: 'result' }, ...inputFieldList.value.map((item) => ({ label: item.label, value: item.field }))]
  if (!nodeProps.config) {
    nodeProps.config = {}
  }
  nodeProps.config.fields = fields
  props.nodeModel.clearNextNodeField(false)
}

function openAddDialog(data?: Record<string, unknown>, index?: number) {
  VariableFieldDialogRef.value?.open(data as { field: string; label: string; expression: string }, index)
}

function deleteField(index: number) {
  const list = cloneDeep(inputFieldList.value)
  list.splice(index, 1)
  inputFieldList.value = list
  syncConfig()
}

function refreshFieldList(data: { field: string; label: string; expression: string }, index?: number) {
  for (let i = 0; i < inputFieldList.value.length; i++) {
    if ((inputFieldList.value[i] as { field: string }).field === data.field && i !== index) {
      MsgError(`变量 "${data.field}" 已存在`)
      return
    }
  }

  const list = cloneDeep(inputFieldList.value)
  if (index === undefined || index === null) {
    list.push(data)
  } else {
    list.splice(index, 1, data)
  }
  inputFieldList.value = list
  VariableFieldDialogRef.value?.close()
  syncConfig()
}
</script>
