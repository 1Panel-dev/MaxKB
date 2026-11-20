<template>
  <div class="w-full">
    <div class="flex-between">
      <span>{{ t('workflow.loopStart.variables.label') }}</span>
      <div class="flex-align-center">
        <!-- 添加循环变量 -->
        <el-button text type="primary" @click="openAddDialog()">
          <MkIcon name="icon_add_outlined" />
        </el-button>
      </div>
    </div>
    <MkTable class="mt-2 border" size="small" v-if="loopInputFieldList.length > 0" :data="loopInputFieldList" row-key="field">
      <el-table-column prop="field" :label="t('dynamicForm.fields.parameter.label')">
        <template #default="{ row }">
          <span :title="row.field" class="truncate">{{ row.field }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="label" :label="t('dynamicForm.fields.displayName.label')">
        <template #default="{ row }">
          <span :title="row.label" class="truncate">{{ row.label }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.labels.operation')" align="left" width="80">
        <template #default="{ row, $index }">
          <!-- 编辑循环变量 -->
          <el-button type="primary" text @click.stop="openAddDialog(row, $index)">
            <template #icon><MkIcon name="icon_edit_outlined" /></template>
          </el-button>
          <!-- 删除循环变量 -->
          <el-button type="primary" text @click="deleteField($index)">
            <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
          </el-button>
        </template>
      </el-table-column>
    </MkTable>
    <LoopFieldDialog ref="fieldDialogRef" @submit="submitField" />
  </div>
</template>
<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { cloneDeep, set } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { BaseNodeModel } from '@logicflow/core'
import { isLoopBuiltinField } from '../constant'
import LoopFieldDialog from './LoopFieldDialog.vue'
import { MsgError } from '@/utils/message'

defineOptions({ name: 'LoopFieldTable' })
const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{ nodeModel: BaseNodeModel }>()

type WorkflowGraphModel = BaseNodeModel['graphModel'] & { refresh_loop_fields?: (fields: Array<{ label: string; value: string }>) => void }
type LoopInputField = { field: string; label: string }

const fieldDialogRef = ref<InstanceType<typeof LoopFieldDialog>>()
const loopInputFieldList = ref<LoopInputField[]>([])

function openAddDialog(data?: LoopInputField, index?: number) {
  fieldDialogRef.value?.open(data, index)
}

function deleteField(index: number) {
  loopInputFieldList.value.splice(index, 1)
  sync()
}

function submitField(data: LoopInputField, index?: number) {
  if (loopInputFieldList.value.some((item, i) => index !== i && item.field === data.field)) {
    MsgError(`${t('workflow.parameters.duplicateMessage')}：${data.field}`)
    return
  }
  if (index === undefined) {
    loopInputFieldList.value.push(data)
  } else {
    loopInputFieldList.value.splice(index, 1, data)
  }
  sync()
  fieldDialogRef.value?.close()
}

function sync() {
  set(props.nodeModel.properties, 'loop_input_field_list', cloneDeep(loopInputFieldList.value))
  const graphModel = props.nodeModel.graphModel as WorkflowGraphModel
  graphModel.refresh_loop_fields?.(loopInputFieldList.value.map((item) => ({ label: item.label, value: item.field })))
  // 循环变量变化后清空循环体内下游节点的字段字典缓存，使其能读到最新的 loop 分组变量
  ;(props.nodeModel as { clearNextNodeField?: (containSelf: boolean) => void }).clearNextNodeField?.(true)
}

/* 内置参数（index/item）由循环引擎提供，作为只读输出参数展示，不进入用户可配置的循环变量列表 */
function readFields(): LoopInputField[] {
  const properties = props.nodeModel.properties as { loop_input_field_list?: LoopInputField[] }
  return (Array.isArray(properties.loop_input_field_list) ? cloneDeep(properties.loop_input_field_list) : []).filter(
    (item) => !isLoopBuiltinField(item.field),
  )
}

onMounted(() => {
  loopInputFieldList.value = readFields()
  sync()
})
// 节点属性被外部改写（如 AI 生成写入循环变量）时同步表格，避免后续编辑覆盖掉外部写入
watch(
  () => (props.nodeModel.properties as { loop_input_field_list?: LoopInputField[] }).loop_input_field_list,
  () => {
    loopInputFieldList.value = readFields()
  },
  { deep: true },
)
</script>
