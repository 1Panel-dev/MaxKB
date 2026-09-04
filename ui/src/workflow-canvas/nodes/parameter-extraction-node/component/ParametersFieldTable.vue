<template>
  <div class="w-full">
    <div class="flex w-full items-center justify-between">
      <h6 class="font-medium">
        提取参数
        <span class="text-danger">*</span>
      </h6>
      <el-button link type="primary" @click="openAddDialog()">
        <MkIcon name="icon_add_outlined" class="mr-1" />
        添加
      </el-button>
    </div>

    <el-table v-if="inputFieldList.length > 0" :data="inputFieldList" row-key="field" class="border">
      <el-table-column prop="field" label="参数" width="100" show-overflow-tooltip>
        <template #default="{ row }">
          <span :title="row.field" class="ellipsis-1">{{ row.field }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="label" label="显示名称">
        <template #default="{ row }">
          <span :title="row.label" class="ellipsis-1">{{ row.label }}</span>
        </template>
      </el-table-column>
      <el-table-column label="参数类型">
        <template #default="{ row }">
          <el-tag size="small" type="info" class="info-tag">{{ row.parameter_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="90">
        <template #default="{ row, $index }">
          <el-button link type="primary" @click="openAddDialog(row, $index)">
            <MkIcon name="icon_edit_outlined" />
          </el-button>
          <el-button link type="info" @click="deleteField($index)">
            <MkIcon name="icon_delete-trash_outlined" />
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-else description="暂无参数，请点击添加" :image-size="60" />

    <ParametersFieldDialog ref="ParamsFieldDialogRef" @refresh="refreshFieldList" />
  </div>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import { cloneDeep } from 'lodash'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'

import ParametersFieldDialog from './ParametersFieldDialog.vue'

defineOptions({ name: 'WorkflowParameterExtractionFieldTable' })

const props = defineProps<{ nodeModel: WorkflowNodeModel }>()

const ParamsFieldDialogRef = ref<InstanceType<typeof ParametersFieldDialog>>()

const nodeProps = props.nodeModel.properties as unknown as {
  config: Record<string, unknown>
  node_data: Record<string, unknown>
}

const inputFieldList = computed<Array<Record<string, unknown>>>({
  get: () => {
    if (!nodeProps.node_data) {
      nodeProps.node_data = {}
    }
    if (!Array.isArray(nodeProps.node_data.variable_list)) {
      nodeProps.node_data.variable_list = []
    }
    return nodeProps.node_data.variable_list as Array<Record<string, unknown>>
  },
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
  ParamsFieldDialogRef.value?.open(data, index)
}

function deleteField(index: number) {
  const list = cloneDeep(inputFieldList.value)
  list.splice(index, 1)
  inputFieldList.value = list
  syncConfig()
}

function refreshFieldList(data: Record<string, unknown>, index?: number) {
  const field = data as { field: string }
  for (let i = 0; i < inputFieldList.value.length; i++) {
    if ((inputFieldList.value[i] as { field: string }).field === field.field && index !== i) {
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
  ParamsFieldDialogRef.value?.close()
  syncConfig()
}
</script>
