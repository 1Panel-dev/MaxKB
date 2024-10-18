<template>
  <div class="flex-between mb-16">
    <h5 class="lighter">{{ '用户输入' }}</h5>
    <el-button link type="primary" @click="openAddDialog()">
      <el-icon class="mr-4">
        <Plus />
      </el-icon>
      添加
    </el-button>
  </div>
  <el-table
    v-if="props.nodeModel.properties.user_input_field_list?.length > 0"
    :data="props.nodeModel.properties.user_input_field_list"
    class="mb-16"
  >
    <el-table-column prop="variable" label="参数" />
    <el-table-column prop="name" label="显示名称" />
    <el-table-column label="输入类型">
      <template #default="{ row }">
        <el-tag type="info" class="info-tag" v-if="row.type === 'input'">文本框</el-tag>
        <el-tag type="info" class="info-tag" v-if="row.type === 'date'">日期</el-tag>
        <el-tag type="info" class="info-tag" v-if="row.type === 'select'">下拉选项</el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="default_value" label="默认值" />
    <el-table-column label="必填">
      <template #default="{ row }">
        <div @click.stop>
          <el-switch disabled size="small" v-model="row.is_required" />
        </div>
      </template>
    </el-table-column>
    <el-table-column label="操作" align="left" width="80">
      <template #default="{ row, $index }">
            <span class="mr-4">
              <el-tooltip effect="dark" content="修改" placement="top">
                <el-button type="primary" text @click.stop="openAddDialog(row, $index)">
                  <el-icon><EditPen /></el-icon>
                </el-button>
              </el-tooltip>
            </span>
        <el-tooltip effect="dark" content="删除" placement="top">
          <el-button type="primary" text @click="deleteField($index)">
            <el-icon>
              <Delete />
            </el-icon>
          </el-button>
        </el-tooltip>
      </template>
    </el-table-column>
  </el-table>

  <UserFieldFormDialog ref="UserFieldFormDialogRef" @refresh="refreshFieldList" />

</template>

<script setup lang="ts">

import { onMounted, ref } from 'vue'
import { set } from 'lodash'
import UserFieldFormDialog from './UserFieldFormDialog.vue'
import { MsgError } from '@/utils/message'

const props = defineProps<{ nodeModel: any }>()

const currentIndex = ref(null)
const UserFieldFormDialogRef = ref()
const inputFieldList = ref<any[]>([])

function openAddDialog(data?: any, index?: any) {
  if (typeof index !== 'undefined') {
    currentIndex.value = index
  }
  UserFieldFormDialogRef.value.open(data)
}

function deleteField(index: any) {
  inputFieldList.value.splice(index, 1)
  props.nodeModel.graphModel.eventCenter.emit('refreshFieldList')
}


function refreshFieldList(data: any) {
  for (let i = 0; i < inputFieldList.value.length; i++) {
    if (inputFieldList.value[i].variable === data.variable && currentIndex.value !== i) {
      MsgError('参数已存在: ' + data.variable)
      return
    }
  }
  // 查看另一个list又没有重复的
  let arr = props.nodeModel.properties.api_input_field_list
  for (let i = 0; i < arr.length; i++) {
    if (arr[i].variable === data.variable) {
      MsgError('参数已存在: ' + data.variable)
      return
    }
  }
  if (currentIndex.value !== null) {
    inputFieldList.value.splice(currentIndex.value, 1, data)
  } else {
    inputFieldList.value.push(data)
  }
  currentIndex.value = null
  UserFieldFormDialogRef.value.close()
  props.nodeModel.graphModel.eventCenter.emit('refreshFieldList')
}

onMounted(() => {
  if (!props.nodeModel.properties.user_input_field_list) {
    if (props.nodeModel.properties.input_field_list) {
      props.nodeModel.properties.input_field_list
        .filter((item: any) => {
          return item.assignment_method === 'user_input'
        })
        .forEach((item: any) => {
          inputFieldList.value.push(item)
        })
    }
  } else {
    inputFieldList.value.push(...props.nodeModel.properties.user_input_field_list)
  }
  set(props.nodeModel.properties, 'user_input_field_list', inputFieldList)
})

</script>


<style scoped lang="scss">

</style>