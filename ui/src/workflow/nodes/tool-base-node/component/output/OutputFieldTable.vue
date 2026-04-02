<template>
  <div class="flex-between mb-16">
    <h5 class="break-all ellipsis lighter" style="max-width: 80%" :title="outputFieldConfig.title">
      {{ outputFieldConfig.title }}
    </h5>
    <div>
      <el-button type="primary" link @click="openChangeTitleDialog">
        <AppIcon iconName="app-setting"></AppIcon>
      </el-button>
      <span class="ml-4">
        <el-button link type="primary" @click="openAddDialog()">
          <AppIcon iconName="app-add-outlined" class="mr-4"></AppIcon>
          {{ $t('common.add') }}
        </el-button>
      </span>
    </div>
  </div>

  <el-table ref="inputFieldTableRef" :data="inputFieldList" class="mb-16">
    <el-table-column prop="field" :label="$t('views.tool.form.paramName.label')" />
    <el-table-column prop="label" :label="$t('dynamicsForm.paramForm.name.label')" />
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
  <InputFieldFormDialog ref="inputFieldFormDialogRef" @refresh="refreshFieldList" />
  <OutputTitleDialog ref="outputTitleDialogRef" @refresh="refreshFieldTitle" />
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { set, cloneDeep } from 'lodash'
import Sortable from 'sortablejs'
import { MsgError } from '@/utils/message'
import InputFieldFormDialog from './OutputFieldFormDialog.vue'
import { t } from '@/locales'
import OutputTitleDialog from '@/workflow/nodes/tool-base-node/component/output/OutputTitleDialog.vue'
const props = defineProps<{ nodeModel: any }>()
const tableRef = ref()
const inputFieldFormDialogRef = ref<InstanceType<typeof InputFieldFormDialog>>()
const outputTitleDialogRef = ref<InstanceType<typeof OutputTitleDialog>>()
const inputFieldList = ref<any[]>([])
const outputFieldConfig = ref({ title: t('chat.userOutput', '输出参数') })

function openAddDialog(data?: any, index?: any) {
  if (index !== undefined) {
    currentIndex.value = index
  }
  inputFieldFormDialogRef.value?.open(data)
}

function openChangeTitleDialog() {
  outputTitleDialogRef.value?.open(outputFieldConfig.value)
}

function deleteField(index: any) {
  inputFieldList.value = inputFieldList.value.filter((item, i) => i !== index)
  set(props.nodeModel.properties, 'user_output_field_list', inputFieldList.value)
}
const currentIndex = ref<number | null>(null)
function refreshFieldList(data: any) {
  if (currentIndex.value !== null) {
    if (
      inputFieldList.value
        .filter((item, index) => index != currentIndex.value)
        .some((field) => field.field == data.field)
    ) {
      MsgError(t('workflow.tip.paramErrorMessage') + data.field)
      return
    }
    inputFieldList.value?.splice(currentIndex.value, 1, data)
  } else {
    if (inputFieldList.value.some((field) => field.field == data.field)) {
      MsgError(t('workflow.tip.paramErrorMessage') + data.field)
      return
    }
    inputFieldList.value?.push(data)
  }
  set(props.nodeModel.properties, 'user_output_field_list', cloneDeep(inputFieldList.value))
  inputFieldFormDialogRef.value?.close()
  props.nodeModel.graphModel.getNodeModelById('tool-start-node').clear_next_node_field(true)
  currentIndex.value = null
}

function refreshFieldTitle(data: any) {
  outputFieldConfig.value = data
  outputTitleDialogRef.value?.close()
}

function onDragHandle() {
  if (!tableRef.value) return

  // 获取表格的 tbody DOM 元素
  const wrapper = tableRef.value.$el as HTMLElement
  const tbody = wrapper.querySelector('.el-table__body-wrapper tbody')
  if (!tbody) return
  // 初始化 Sortable
  Sortable.create(tbody as HTMLElement, {
    animation: 150,
    ghostClass: 'ghost-row',
    onEnd: (evt) => {
      if (evt.oldIndex === undefined || evt.newIndex === undefined) return
      // 更新数据顺序
      const items = cloneDeep([...inputFieldList.value])
      const [movedItem] = items.splice(evt.oldIndex, 1)
      items.splice(evt.newIndex, 0, movedItem)
      inputFieldList.value = items
      props.nodeModel.graphModel.eventCenter.emit('refreshFieldList')
    },
  })
}

onMounted(() => {
  if (props.nodeModel.properties.user_output_config) {
    outputFieldConfig.value = cloneDeep(props.nodeModel.properties.user_output_config)
  }
  if (props.nodeModel.properties.user_output_field_list) {
    inputFieldList.value = cloneDeep(props.nodeModel.properties.user_output_field_list)
  }
  onDragHandle()
})
</script>

<style scoped lang="scss"></style>
