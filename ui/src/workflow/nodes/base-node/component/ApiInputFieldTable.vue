<template>
  <div class="flex-between mb-16">
    <h5 class="lighter">{{ $t('views.template.templateForm.title.apiParamPassing') }}</h5>
    <el-button link type="primary" @click="openAddDialog()">
      <el-icon class="mr-4">
        <Plus />
      </el-icon>
      {{ $t('common.add') }}
    </el-button>
  </div>
  <el-table
    v-if="props.nodeModel.properties.api_input_field_list?.length > 0"
    :data="props.nodeModel.properties.api_input_field_list"
    class="mb-16"
    ref="tableRef"
    row-key="field"
  >
    <el-table-column prop="variable" :label="$t('dynamicsForm.paramForm.field.label')">
      <template #default="{ row }">
        <span class="ellipsis-1" :title="row.variable">
          {{ row.variable }}
        </span>
      </template>
    </el-table-column>
    <el-table-column prop="default_value" :label="$t('dynamicsForm.default.label')">
      <template #default="{ row }">
        <span class="ellipsis-1" :title="row.default_value">
          {{ row.default_value }}
        </span>
      </template>
    </el-table-column>
    <el-table-column :label="$t('common.required')">
      <template #default="{ row }">
        <div @click.stop>
          <el-switch disabled size="small" v-model="row.is_required" />
        </div>
      </template>
    </el-table-column>
    <el-table-column :label="$t('common.operation')" align="left" width="90">
      <template #default="{ row, $index }">
        <span class="mr-4">
          <el-tooltip effect="dark" :content="$t('common.modify')" placement="top">
            <el-button type="primary" text @click.stop="openAddDialog(row, $index)">
              <el-icon><EditPen /></el-icon>
            </el-button>
          </el-tooltip>
        </span>
        <el-tooltip effect="dark" :content="$t('common.delete')" placement="top">
          <el-button type="primary" text @click="deleteField($index)">
            <el-icon>
              <Delete />
            </el-icon>
          </el-button>
        </el-tooltip>
      </template>
    </el-table-column>
  </el-table>

  <ApiFieldFormDialog ref="ApiFieldFormDialogRef" @refresh="refreshFieldList" />
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { set } from 'lodash'
import Sortable from 'sortablejs'
import ApiFieldFormDialog from './ApiFieldFormDialog.vue'
import { MsgError } from '@/utils/message'
import { t } from '@/locales'

const props = defineProps<{ nodeModel: any }>()
const tableRef = ref()
const currentIndex = ref(null)
const ApiFieldFormDialogRef = ref()
const inputFieldList = ref<any[]>([])

function openAddDialog(data?: any, index?: any) {
  if (typeof index !== 'undefined') {
    currentIndex.value = index
  }
  ApiFieldFormDialogRef.value.open(data)
}

function deleteField(index: any) {
  inputFieldList.value.splice(index, 1)
  props.nodeModel.graphModel.eventCenter.emit('refreshFieldList')
  onDragHandle()
}

function refreshFieldList(data: any) {
  for (let i = 0; i < inputFieldList.value.length; i++) {
    if (inputFieldList.value[i].variable === data.variable && currentIndex.value !== i) {
      MsgError(t('views.applicationWorkflow.tip.paramErrorMessage') + data.variable)
      return
    }
  }
  // 查看另一个list又没有重复的
  let arr = props.nodeModel.properties.user_input_field_list
  for (let i = 0; i < arr.length; i++) {
    if (arr[i].field === data.variable) {
      MsgError(t('views.applicationWorkflow.tip.paramErrorMessage') + data.variable)
      return
    }
  }
  if (currentIndex.value !== null) {
    inputFieldList.value.splice(currentIndex.value, 1, data)
  } else {
    inputFieldList.value.push(data)
  }
  currentIndex.value = null
  ApiFieldFormDialogRef.value.close()
  props.nodeModel.graphModel.eventCenter.emit('refreshFieldList')
  onDragHandle()
}

// 表格排序拖拽
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
      const items = [...inputFieldList.value]
      const [movedItem] = items.splice(evt.oldIndex, 1)
      items.splice(evt.newIndex, 0, movedItem)
      inputFieldList.value = items
      props.nodeModel.graphModel.eventCenter.emit('refreshFieldList')
    }
  })
}

onMounted(() => {
  if (!props.nodeModel.properties.api_input_field_list) {
    if (props.nodeModel.properties.input_field_list) {
      props.nodeModel.properties.input_field_list
        .filter((item: any) => {
          return item.assignment_method === 'api_input'
        })
        .forEach((item: any) => {
          inputFieldList.value.push(item)
        })
    }
  } else {
    inputFieldList.value.push(...props.nodeModel.properties.api_input_field_list)
  }
  set(props.nodeModel.properties, 'api_input_field_list', inputFieldList)
})
</script>

<style scoped lang="scss"></style>
