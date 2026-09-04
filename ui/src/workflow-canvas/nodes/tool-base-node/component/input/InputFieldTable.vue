<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { cloneDeep, set } from 'lodash'
import { MsgError } from '@/utils/message'
import InputFieldFormDialog from './InputFieldFormDialog.vue'
import InputTitleDialog from './InputTitleDialog.vue'

const props = defineProps<{ nodeModel: any }>()
const inputFieldFormDialogRef = ref<InstanceType<typeof InputFieldFormDialog>>()
const inputTitleDialogRef = ref<InstanceType<typeof InputTitleDialog>>()
const inputFieldList = ref<any[]>([])
const inputFieldConfig = ref({ title: '用户输入' })

function openAddDialog(data?: any, index?: any) {
  if (index !== undefined) {
    currentIndex.value = index
  }
  inputFieldFormDialogRef.value?.open(data)
}

function openChangeTitleDialog() {
  inputTitleDialogRef.value?.open(inputFieldConfig.value)
}

function deleteField(index: any) {
  inputFieldList.value.splice(index, 1)
  set(props.nodeModel.properties, 'user_input_field_list', cloneDeep(inputFieldList.value))
  props.nodeModel.graphModel.eventCenter.emit('refreshFieldList')
}

const currentIndex = ref<number | null>(null)
function refreshFieldList(data: any) {
  if (currentIndex.value !== null) {
    if (
      inputFieldList.value
        .filter((item, index) => index != currentIndex.value)
        .some((field) => field.field == data.field)
    ) {
      MsgError('参数名已存在：' + data.field)
      return
    }
    inputFieldList.value?.splice(currentIndex.value, 1, data)
  } else {
    if (inputFieldList.value.some((field) => field.field == data.field)) {
      MsgError('参数名已存在：' + data.field)
      return
    }
    inputFieldList.value?.push(data)
  }
  set(props.nodeModel.properties, 'user_input_field_list', cloneDeep(inputFieldList.value))
  props.nodeModel.graphModel.eventCenter.emit('refreshFieldList')
  props.nodeModel.graphModel.getNodeModelById('tool-start-node')?.clearNextNodeField(true)
  inputFieldFormDialogRef.value?.close()
  currentIndex.value = null
}

function refreshFieldTitle(data: any) {
  inputFieldConfig.value = data
  inputTitleDialogRef.value?.close()
}

onMounted(() => {
  if (props.nodeModel.properties.user_input_config) {
    inputFieldConfig.value = cloneDeep(props.nodeModel.properties.user_input_config)
  }
  if (props.nodeModel.properties.user_input_field_list) {
    inputFieldList.value = cloneDeep(props.nodeModel.properties.user_input_field_list)
  }
  props.nodeModel.graphModel.eventCenter.emit('refreshFieldList')
})
</script>

<template>
  <div class="flex-between mb-4">
    <h6 class="break-all ellipsis lighter" style="max-width: 80%" :title="inputFieldConfig.title">
      {{ inputFieldConfig.title }}
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

  <el-table :data="inputFieldList" class="mb-4">
    <el-table-column prop="field" label="参数名">
      <template #default="{ row }">
        <span class="ellipsis-1" :title="row.field">
          {{ row.field }}
        </span>
      </template>
    </el-table-column>
    <el-table-column prop="label" label="显示名">
      <template #default="{ row }">
        <span class="ellipsis-1" :title="row.label">
          {{ row.label }}
        </span>
      </template>
    </el-table-column>
    <el-table-column label="数据类型">
      <template #default="{ row }">
        <el-tag type="info" class="info-tag">{{ row.type }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column label="必填">
      <template #default="{ row }">
        <div @click.stop>
          <el-switch disabled size="small" v-model="row.is_required" />
        </div>
      </template>
    </el-table-column>
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
  <InputFieldFormDialog ref="inputFieldFormDialogRef" @refresh="refreshFieldList" />
  <InputTitleDialog ref="inputTitleDialogRef" @refresh="refreshFieldTitle" />
</template>