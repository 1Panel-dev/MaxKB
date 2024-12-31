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
    <el-table-column prop="field" label="参数">
      <template #default="{ row }">
        <span :title="row.field" class="ellipsis-1">{{ row.field }}</span>
      </template>
    </el-table-column>

    <el-table-column prop="label" label="显示名称">
      <template #default="{ row }">
        <span v-if="row.label && row.label.input_type === 'TooltipLabel'">
          <span :title="row.label.label" class="ellipsis-1">
            {{ row.label.label }}
          </span>
        </span>
        <span v-else>
          <span :title="row.label" class="ellipsis-1">
            {{ row.label }}
          </span></span
        >
      </template>
    </el-table-column>
    <el-table-column label="组件类型">
      <template #default="{ row }">
        <el-tag type="info" class="info-tag" v-if="row.input_type === 'TextInput'">文本框</el-tag>
        <el-tag type="info" class="info-tag" v-if="row.input_type === 'Slider'">滑块</el-tag>
        <el-tag type="info" class="info-tag" v-if="row.input_type === 'SwitchInput'">开关</el-tag>
        <el-tag type="info" class="info-tag" v-if="row.input_type === 'SingleSelect'"
          >单选框</el-tag
        >
        <el-tag type="info" class="info-tag" v-if="row.input_type === 'MultiSelect'">多选框</el-tag>
        <el-tag type="info" class="info-tag" v-if="row.input_type === 'RadioCard'">选项卡</el-tag>
        <el-tag type="info" class="info-tag" v-if="row.input_type === 'DatePicker'">日期</el-tag>
      </template>
    </el-table-column>

    <el-table-column prop="default_value" label="默认值">
      <template #default="{ row }">
        <span :title="row.default_value" class="ellipsis-1">{{ getDefaultValue(row) }}</span>
      </template>
    </el-table-column>
    <el-table-column label="必填">
      <template #default="{ row }">
        <div @click.stop>
          <el-switch disabled size="small" v-model="row.required" />
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

const UserFieldFormDialogRef = ref()
const inputFieldList = ref<any[]>([])

function openAddDialog(data?: any, index?: any) {
  UserFieldFormDialogRef.value.open(data, index)
}

function deleteField(index: any) {
  inputFieldList.value.splice(index, 1)
  props.nodeModel.graphModel.eventCenter.emit('refreshFieldList')
}

function refreshFieldList(data: any, index: any) {
  for (let i = 0; i < inputFieldList.value.length; i++) {
    if (inputFieldList.value[i].field === data.field && index !== i) {
      MsgError('参数已存在: ' + data.field)
      return
    }
  }
  // 查看另一个list又没有重复的
  let arr = props.nodeModel.properties.api_input_field_list
  for (let i = 0; i < arr.length; i++) {
    if (arr[i].variable === data.field) {
      MsgError('参数已存在: ' + data.field)
      return
    }
  }
  if (index !== null) {
    inputFieldList.value.splice(index, 1, data)
  } else {
    inputFieldList.value.push(data)
  }
  UserFieldFormDialogRef.value.close()
  props.nodeModel.graphModel.eventCenter.emit('refreshFieldList')
}

const getDefaultValue = (row: any) => {
  if (row.default_value) {
    const default_value = row.option_list
      ?.filter((v: any) => row.default_value.indexOf(v.value) > -1)
      .map((v: any) => v.label)
      .join(',')
    if (default_value) {
      return default_value
    }
    return row.default_value
  }
  if (row.default_value !== undefined) {
    return row.default_value
  }
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
  // 兼容旧数据
  inputFieldList.value.forEach((item, index) => {
    item.label = item.label || item.name
    item.field = item.field || item.variable
    item.required = item.required || item.is_required
    switch (item.type) {
      case 'input':
        item.input_type = 'TextInput'
        break
      case 'select':
        item.input_type = 'SingleSelect'
        break
      case 'date':
        item.input_type = 'DatePicker'
        break
    }
  })
  set(props.nodeModel.properties, 'user_input_field_list', inputFieldList)
})
</script>

<style scoped lang="scss"></style>
