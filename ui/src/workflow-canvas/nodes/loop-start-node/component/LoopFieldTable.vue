<template>
  <div>
    <div class="flex-between mb-2">
      <h6 class="mk-title-decoration">循环变量</h6>
      <el-button text type="primary" @click="openAddDialog()">
        <template #icon><MkIcon name="icon_add_outlined" /></template>
        添加
      </el-button>
    </div>
    <el-table v-if="loopInputFieldList.length > 0" :data="loopInputFieldList" row-key="field" border>
      <el-table-column prop="field" label="变量名">
        <template #default="{ row }">
          <span :title="row.field" class="truncate">{{ row.field }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="label" label="标签">
        <template #default="{ row }">
          <span :title="row.label" class="truncate">{{ row.label }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="left" width="90">
        <template #default="{ row, $index }">
          <el-button type="primary" text @click.stop="openAddDialog(row, $index)">
            <template #icon><MkIcon name="icon_edit_outlined" /></template>
          </el-button>
          <el-button type="primary" text @click="deleteField($index)">
            <template #icon><MkIcon name="icon_delete" /></template>
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <LoopFieldDialog ref="fieldDialogRef" @refresh="refreshFieldList" />
  </div>
</template>
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { cloneDeep, set } from 'lodash'
import type { BaseNodeModel } from '@logicflow/core'
import LoopFieldDialog from './LoopFieldDialog.vue'
import { MsgError } from '@/utils/message'

defineOptions({ name: 'LoopFieldTable' })
const props = defineProps<{ nodeModel: BaseNodeModel }>()

type WorkflowGraphModel = BaseNodeModel['graphModel'] & { refresh_loop_fields?: (fields: Array<{ label: string; value: string }>) => void }
type LoopInputField = { field: string; label: string }

const DEFAULT_FIELDS: LoopInputField[] = [
  { field: 'index', label: '下标' },
  { field: 'item', label: '循环元素' },
]

const fieldDialogRef = ref<InstanceType<typeof LoopFieldDialog>>()
const loopInputFieldList = ref<LoopInputField[]>([])

function openAddDialog(data?: LoopInputField, index?: number) {
  fieldDialogRef.value?.open(data, index)
}

function deleteField(index: number) {
  loopInputFieldList.value.splice(index, 1)
  sync()
}

function refreshFieldList(data: LoopInputField, index?: number) {
  if (loopInputFieldList.value.some((item, i) => index !== i && item.field === data.field)) {
    MsgError(`循环变量已存在：${data.field}`)
    return
  }
  if (index === undefined) {
    loopInputFieldList.value.push(data)
  } else {
    loopInputFieldList.value.splice(index, 1, data)
  }
  sync()
}

function sync() {
  set(props.nodeModel.properties, 'loop_input_field_list', cloneDeep(loopInputFieldList.value))
  const graphModel = props.nodeModel.graphModel as WorkflowGraphModel
  graphModel.refresh_loop_fields?.(loopInputFieldList.value.map((item) => ({ label: item.label, value: item.field })))
  // 循环变量变化后清空循环体内下游节点的字段字典缓存，使其能读到最新的 loop 分组变量
  ;(props.nodeModel as { clearNextNodeField?: (containSelf: boolean) => void }).clearNextNodeField?.(true)
}

onMounted(() => {
  const properties = props.nodeModel.properties as { loop_input_field_list?: LoopInputField[] }
  if (Array.isArray(properties.loop_input_field_list)) {
    loopInputFieldList.value = cloneDeep(properties.loop_input_field_list)
  } else {
    loopInputFieldList.value = cloneDeep(DEFAULT_FIELDS)
  }
  sync()
})
</script>
