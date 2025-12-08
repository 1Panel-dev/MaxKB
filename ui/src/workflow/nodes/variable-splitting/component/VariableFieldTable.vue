<template>
  <div class="flex-between w-full">
    <h5 class="break-all lighter">
      {{ $t('views.applicationWorkflow.nodes.variableSplittingNode.splitVariables') }}
      <span class="color-danger">*</span>
    </h5>
    <span class="ml-4" style="margin-top: -4px">
      <el-button link type="primary" @click="openAddDialog()">
        <AppIcon iconName="app-add-outlined"></AppIcon>
      </el-button>
    </span>
  </div>
  <el-table
    v-if="props.nodeModel.properties.node_data.variable_list?.length > 0"
    :data="props.nodeModel.properties.node_data.variable_list"
    ref="tableRef"
    row-key="field"
    class="border-l border-r"
  >
    <el-table-column prop="field" :label="$t('common.variable')" width="95">
      <template #default="{ row }">
        <span :title="row.field" class="ellipsis-1">{{ row.field }}</span>
      </template>
    </el-table-column>

    <el-table-column prop="label" :label="$t('dynamicsForm.paramForm.name.label')">
      <template #default="{ row }">
        <span :title="row.label" class="ellipsis-1">
          {{ row.label }}
        </span>
      </template>
    </el-table-column>
    <el-table-column :label="$t('common.operation')" align="left" width="90">
      <template #default="{ row, $index }">
        <span class="mr-4">
          <el-tooltip effect="dark" :content="$t('common.modify')" placement="top">
            <el-button type="primary" text @click.stop="openAddDialog(row, $index)">
              <AppIcon iconName="app-edit"></AppIcon>
            </el-button>
          </el-tooltip>
        </span>
        <el-tooltip effect="dark" :content="$t('common.delete')" placement="top">
          <el-button type="primary" text @click="deleteField($index)">
            <AppIcon iconName="app-delete"></AppIcon>
          </el-button>
        </el-tooltip>
      </template>
    </el-table-column>
  </el-table>
  <VariableFieldDialog
    ref="VariableFieldDialogRef"
    @refresh="refreshFieldList"
  ></VariableFieldDialog>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { set, cloneDeep } from 'lodash'
import VariableFieldDialog from './VariableFieldDialog.vue'
import { MsgError } from '@/utils/message'
import { t } from '@/locales'
const props = defineProps<{ nodeModel: any }>()

const tableRef = ref()
const VariableFieldDialogRef = ref()

const inputFieldList = ref<any[]>([])

function openAddDialog(data?: any, index?: any) {
  VariableFieldDialogRef.value.open(data, index)
}

function deleteField(index: any) {
  inputFieldList.value.splice(index, 1)
  const fields = [
    {
      label: t('common.result'),
      value: 'result',
    },
    ...inputFieldList.value.map((item) => ({ label: item.label, value: item.field })),
  ]
  set(props.nodeModel.properties.config, 'fields', fields)
  props.nodeModel.clear_next_node_field(false)
}

function refreshFieldList(data: any, index: any) {
  for (let i = 0; i < inputFieldList.value.length; i++) {
    if (inputFieldList.value[i].field === data.field && index !== i) {
      MsgError(t('views.applicationWorkflow.tip.paramErrorMessage') + data.field)
      return
    }
  }
  if ([undefined, null].includes(index)) {
    inputFieldList.value.push(data)
  } else {
    inputFieldList.value.splice(index, 1, data)
  }
  VariableFieldDialogRef.value.close()
  const fields = [
    {
      label: t('common.result'),
      value: 'result',
    },
    ...inputFieldList.value.map((item) => ({ label: item.label, value: item.field })),
  ]
  set(props.nodeModel.properties.config, 'fields', fields)
  props.nodeModel.clear_next_node_field(false)
}

onMounted(() => {
  if (props.nodeModel.properties.node_data.variable_list) {
    inputFieldList.value = cloneDeep(props.nodeModel.properties.node_data.variable_list)
  }
  set(props.nodeModel.properties.node_data, 'variable_list', inputFieldList)
  const fields = [
    {
      label: t('common.result'),
      value: 'result',
    },
    ...inputFieldList.value.map((item) => ({ label: item.label, value: item.field })),
  ]
  set(props.nodeModel.properties.config, 'fields', fields)
})
</script>

<style scoped lang="scss"></style>
