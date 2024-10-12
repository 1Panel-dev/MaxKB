<template>
  <el-dialog
    title="模型参数设置"
    v-model="dialogVisible"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="close"
  >
    <el-button type="primary" @click="openAddDrawer()" class="mb-12">
      添加参数
    </el-button>
    <el-table
      :data="modelParams"
      class="mb-16"
    >
      <el-table-column prop="label" label="参数">
        <template #default="{ row }">
          <span v-if="row.label && row.label.input_type === 'TooltipLabel'">{{ row.label.label }}</span>
          <span v-else>{{ row.label }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="field" label="显示名称" />
      <el-table-column label="组件类型">
        <template #default="{ row }">
          <el-tag type="info" class="info-tag" v-if="row.input_type === 'TextInput'">文本框</el-tag>
          <el-tag type="info" class="info-tag" v-if="row.input_type === 'Slider'">滑块</el-tag>
          <el-tag type="info" class="info-tag" v-if="row.input_type === 'SwitchInput'">开关</el-tag>
          <el-tag type="info" class="info-tag" v-if="row.input_type === 'SingleSelect'">单选框</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="default_value" label="默认值" />
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
                <el-button type="primary" text @click.stop="openAddDrawer(row, $index)">
                  <el-icon><EditPen /></el-icon>
                </el-button>
              </el-tooltip>
            </span>
          <el-tooltip effect="dark" content="删除" placement="top">
            <el-button type="primary" text @click="deleteParam($index)">
              <el-icon>
                <Delete />
              </el-icon>
            </el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="close">取消</el-button>
        <el-button type="primary" @click="submit" :loading="loading"> 保存 </el-button>
      </span>
    </template>
  </el-dialog>
  <AddParamDrawer ref="AddParamRef" @refresh="refresh" />
</template>

<script setup lang="ts">
import type { Model } from '@/api/type/model'
import { ref } from 'vue'
import AddParamDrawer from './AddParamDrawer.vue'
import { MsgError } from '@/utils/message'

const loading = ref<boolean>(false)
const dialogVisible = ref<boolean>(false)
const modelParams = ref<any[]>([])
const AddParamRef = ref()

const open = (model: Model) => {
  dialogVisible.value = true
}

const close = () => {
  dialogVisible.value = false
}


function openAddDrawer(data?: any, index?: any) {
  AddParamRef.value?.open(data, index)
}

function deleteParam(index: any) {
  modelParams.value.splice(index, 1)
}

function refresh(data: any, index: any) {
  // console.log(data, index)
  for (let i = 0; i < modelParams.value.length; i++) {
    if (modelParams.value[i].field === data.field && index !== i) {
      MsgError('变量已存在: ' + data.field)
      return
    }
  }
  if (index !== null) {
    modelParams.value.splice(index, 1, data)
  } else {
    modelParams.value.push(data)
  }
  console.log(modelParams.value)
}

function submit() {
  console.log('submit')
}

defineExpose({ open, close })
</script>

<style scoped lang="scss">

</style>