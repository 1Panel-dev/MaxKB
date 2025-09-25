<template>
  <div class="flex-between mb-16">
    <h5 class="break-all ellipsis lighter" style="max-width: 80%">
      {{ $t('views.applicationWorkflow.variable.loop', '循环变量') }}
    </h5>
    <div>
      <span class="ml-4">
        <el-button link type="primary" @click="openAddDialog()">
          <AppIcon iconName="app-add-outlined" class="mr-4"></AppIcon>
          {{ $t('common.add') }}
        </el-button>
      </span>
    </div>
  </div>
  <el-table
    v-if="props.nodeModel.properties.loop_input_field_list?.length > 0"
    :data="props.nodeModel.properties.loop_input_field_list"
    class="mb-16"
    ref="tableRef"
    row-key="field"
  >
    <el-table-column prop="field" :label="$t('dynamicsForm.paramForm.field.label')" width="95">
      <template #default="{ row }">
        <span :title="row.field" class="ellipsis-1">{{ row.field }}</span>
      </template>
    </el-table-column>

    <el-table-column prop="label" :label="$t('dynamicsForm.paramForm.name.label')">
      <template #default="{ row }">
        <span>
          <span :title="row.label" class="ellipsis-1">
            {{ row.label }}
          </span></span
        >
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
  <LoopFieldDialog ref="ChatFieldDialogRef" @refresh="refreshFieldList"></LoopFieldDialog>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { set, cloneDeep } from 'lodash'
import LoopFieldDialog from './LoopFieldDialog.vue'
import { MsgError } from '@/utils/message'
import { t } from '@/locales'

const props = defineProps<{ nodeModel: any }>()

const tableRef = ref()
const ChatFieldDialogRef = ref()

const inputFieldList = ref<any[]>([])

function openAddDialog(data?: any, index?: any) {
  ChatFieldDialogRef.value.open(data, index)
}

function deleteField(index: any) {
  inputFieldList.value.splice(index, 1)
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

  ChatFieldDialogRef.value.close()
}

onMounted(() => {
  if (props.nodeModel.properties.loop_input_field_list) {
    inputFieldList.value = cloneDeep(props.nodeModel.properties.loop_input_field_list)
  }
  set(props.nodeModel.properties, 'loop_input_field_list', inputFieldList)
})
</script>

<style scoped lang="scss"></style>
