<template>
  <el-dialog
    title="模型参数设置"
    v-model="dialogVisible"
    width="800px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="close"
  >
    <el-button type="primary" @click="openAddDrawer()" class="mb-12"> 添加参数 </el-button>
    <el-table :data="modelParamsForm" class="mb-16">
      <el-table-column prop="label" label="显示名称" show-overflow-tooltip>
        <template #default="{ row }">
          <span v-if="row.label && row.label.input_type === 'TooltipLabel'">{{
            row.label.label
          }}</span>
          <span v-else>{{ row.label }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="field" label="参数" show-overflow-tooltip />
      <el-table-column label="组件类型" width="110px">
        <template #default="{ row }">
          <el-tag type="info" class="info-tag">{{
            input_type_list.find((item) => item.value === row.input_type)?.label
          }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="default_value" label="默认值" show-overflow-tooltip />
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
import { MsgError, MsgSuccess } from '@/utils/message'
import ModelApi from '@/api/model'
import { input_type_list } from '@/components/dynamics-form/constructor/data'

const props = defineProps<{
  model: Model
}>()

const loading = ref<boolean>(false)
const dialogVisible = ref<boolean>(false)
const modelParamsForm = ref<any[]>([])
const AddParamRef = ref()

const open = () => {
  dialogVisible.value = true
  loading.value = true
  ModelApi.getModelParamsForm(props.model.id, loading)
    .then((ok) => {
      loading.value = false
      modelParamsForm.value = ok.data
    })
    .catch(() => {
      loading.value = false
    })
}

const close = () => {
  dialogVisible.value = false
}

function openAddDrawer(data?: any, index?: any) {
  AddParamRef.value?.open(data, index)
}

function deleteParam(index: any) {
  modelParamsForm.value.splice(index, 1)
}

function refresh(data: any, index: any) {
  for (let i = 0; i < modelParamsForm.value.length; i++) {
    let field = modelParamsForm.value[i].field
    let label = modelParamsForm.value[i].label
    if (label && label.input_type === 'TooltipLabel') {
      label = label.label
    }
    let label2 = data.label
    if (label2 && label2.input_type === 'TooltipLabel') {
      label2 = label2.label
    }

    if (field === data.field && index !== i) {
      MsgError('变量已存在: ' + data.field)
      return
    }
    if (label === label2 && index !== i) {
      MsgError('变量已存在: ' + label)
      return
    }
  }
  if (index !== null) {
    modelParamsForm.value.splice(index, 1, data)
  } else {
    modelParamsForm.value.push(data)
  }
}

function submit() {
  ModelApi.updateModelParamsForm(props.model.id, modelParamsForm.value, loading).then((ok) => {
    MsgSuccess('模型参数保存成功')
    close()
    // emit('submit')
  })
}

defineExpose({ open, close })
</script>

<style scoped lang="scss"></style>
