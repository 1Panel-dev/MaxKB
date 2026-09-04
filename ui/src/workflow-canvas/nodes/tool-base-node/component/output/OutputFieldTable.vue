<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { cloneDeep, set } from 'lodash'
import { MsgError } from '@/utils/message'
import OutputFieldFormDialog from './OutputFieldFormDialog.vue'
import OutputTitleDialog from './OutputTitleDialog.vue'

const props = defineProps<{ nodeModel: any }>()
const outputFieldFormDialogRef = ref<InstanceType<typeof OutputFieldFormDialog>>()
const outputTitleDialogRef = ref<InstanceType<typeof OutputTitleDialog>>()
const outputFieldList = ref<any[]>([])
const outputFieldConfig = ref({ title: '输出参数' })

function openAddDialog(data?: any, index?: any) {
  if (index !== undefined) {
    currentIndex.value = index
  }
  outputFieldFormDialogRef.value?.open(data)
}

function openChangeTitleDialog() {
  outputTitleDialogRef.value?.open(outputFieldConfig.value)
}

function deleteField(index: any) {
  outputFieldList.value = outputFieldList.value.filter((item, i) => i !== index)
  set(props.nodeModel.properties, 'user_output_field_list', outputFieldList.value)
}

const currentIndex = ref<number | null>(null)
function refreshFieldList(data: any) {
  if (currentIndex.value !== null) {
    if (
      outputFieldList.value
        .filter((item, index) => index != currentIndex.value)
        .some((field) => field.field == data.field)
    ) {
      MsgError('参数名已存在：' + data.field)
      return
    }
    outputFieldList.value?.splice(currentIndex.value, 1, data)
  } else {
    if (outputFieldList.value.some((field) => field.field == data.field)) {
      MsgError('参数名已存在：' + data.field)
      return
    }
    outputFieldList.value?.push(data)
  }
  set(props.nodeModel.properties, 'user_output_field_list', cloneDeep(outputFieldList.value))
  outputFieldFormDialogRef.value?.close()
  props.nodeModel.graphModel.getNodeModelById('tool-start-node')?.clearNextNodeField(true)
  currentIndex.value = null
}

function refreshFieldTitle(data: any) {
  outputFieldConfig.value = data
  outputTitleDialogRef.value?.close()
}

onMounted(() => {
  if (props.nodeModel.properties.user_output_config) {
    outputFieldConfig.value = cloneDeep(props.nodeModel.properties.user_output_config)
  }
  if (props.nodeModel.properties.user_output_field_list) {
    outputFieldList.value = cloneDeep(props.nodeModel.properties.user_output_field_list)
  }
})
</script>

<template>
  <div class="flex-between mb-4">
    <h6 class="break-all ellipsis lighter" style="max-width: 80%" :title="outputFieldConfig.title">
      {{ outputFieldConfig.title }}
    </h6>
    <div>
      <el-button type="primary" link @click="openChangeTitleDialog">
        <MkIcon name="icon_setting_outlined" />
      </el-button>
      <span class="ml-4">
        <el-button link type="primary" @click="openAddDialog()">
          <MkIcon name="icon_add_outlined" class="mr-4" />
          添加
        </el-button>
      </span>
    </div>
  </div>

  <el-table :data="outputFieldList" class="mb-4">
    <el-table-column prop="field" label="参数名" />
    <el-table-column prop="label" label="显示名" />
    <el-table-column label="操作" align="left" width="90">
      <template #default="{ row, $index }">
        <span class="mr-4">
          <el-tooltip effect="dark" content="编辑" placement="top">
            <el-button type="primary" text @click.stop="openAddDialog(row, $index)">
              <MkIcon name="icon_edit_outlined" />
            </el-button>
          </el-tooltip>
        </span>
        <el-tooltip effect="dark" content="删除" placement="top">
          <el-button type="primary" text @click="deleteField($index)">
            <MkIcon name="icon_delete_outlined" />
          </el-button>
        </el-tooltip>
      </template>
    </el-table-column>
  </el-table>
  <OutputFieldFormDialog ref="outputFieldFormDialogRef" @refresh="refreshFieldList" />
  <OutputTitleDialog ref="outputTitleDialogRef" @refresh="refreshFieldTitle" />
</template>