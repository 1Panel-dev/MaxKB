<template>
  <NodeContainer :nodeModel="nodeModel">
    <div class="flex-between">
      <h5 class="title-decoration-1 mb-8">输入变量</h5>
      <el-button link type="primary" @click="openAddDialog()">
        <el-icon class="mr-4"><Plus /></el-icon> 添加
      </el-button>
    </div>
    <el-form
      @submit.prevent
      @mousemove.stop
      @mousedown.stop
      @keydown.stop
      @click.stop
      ref="FunctionNodeFormRef"
      :model="chat_data"
      label-position="top"
      require-asterisk-position="right"
      hide-required-asterisk
    >
      <el-card shadow="never" class="card-never mb-16" style="--el-card-padding: 12px">
        <div v-if="chat_data.input_field_list?.length > 0">
          <template v-for="(item, index) in chat_data.input_field_list" :key="index">
            <el-form-item
              :label="item.name"
              :prop="'input_field_list.' + index + '.value'"
              :rules="{
                required: item.is_required,
                message: '请输入变量值',
                trigger: 'blur'
              }"
            >
              <template #label>
                <div class="flex-between">
                  <div>
                    <span
                      >{{ item.name }} <span class="danger" v-if="item.is_required">*</span></span
                    >
                    <el-tag type="info" class="info-tag ml-4">{{ item.type }}</el-tag>
                  </div>
                  <div>
                    <el-button text @click.stop="openAddDialog(item, index)">
                      <el-icon><EditPen /></el-icon>
                    </el-button>
                    <el-button text @click="deleteField(index)" style="margin-left: 4px !important">
                      <el-icon>
                        <Delete />
                      </el-icon>
                    </el-button>
                  </div>
                </div>
              </template>
              <NodeCascader
                v-if="item.source === 'reference'"
                ref="nodeCascaderRef"
                :nodeModel="nodeModel"
                class="w-full"
                placeholder="请选择变量"
                v-model="item.value"
              />
              <el-input v-else v-model="item.value" placeholder="请输入变量值" />
            </el-form-item>
          </template>
        </div>

        <el-text type="info" v-else> 暂无数据 </el-text>
      </el-card>

      <h5 class="title-decoration-1 mb-16">Python 代码</h5>

      <CodemirrorEditor
        v-model:value="chat_data.code"
        v-if="showEditor"
        @change="changeCode"
        @wheel="wheel"
        @keydown="isKeyDown = true"
        @keyup="isKeyDown = false"
      />
    </el-form>
    <FieldFormDialog ref="FieldFormDialogRef" @refresh="refreshFieldList" />
  </NodeContainer>
</template>
<script setup lang="ts">
import { cloneDeep, set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted } from 'vue'
import FieldFormDialog from '@/views/function-lib/component/FieldFormDialog.vue'

const props = defineProps<{ nodeModel: any }>()

const isKeyDown = ref(false)
const wheel = (e: any) => {
  if (isKeyDown.value) {
    e.preventDefault()
  } else {
    e.stopPropagation()
    return true
  }
}

const FieldFormDialogRef = ref()
const nodeCascaderRef = ref()

const form = {
  code: '',
  input_field_list: []
}

const currentIndex = ref<any>(null)
const showEditor = ref(false)

const chat_data = computed({
  get: () => {
    if (props.nodeModel.properties.node_data) {
      return props.nodeModel.properties.node_data
    } else {
      set(props.nodeModel.properties, 'node_data', form)
    }
    return props.nodeModel.properties.node_data
  },
  set: (value) => {
    set(props.nodeModel.properties, 'node_data', value)
  }
})

const FunctionNodeFormRef = ref<FormInstance>()

const validate = () => {
  return FunctionNodeFormRef.value?.validate().catch((err) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

function changeCode(value: string) {
  set(props.nodeModel.properties.node_data, 'code', value)
}

function openAddDialog(data?: any, index?: any) {
  if (typeof index !== 'undefined') {
    currentIndex.value = index
  }

  FieldFormDialogRef.value.open(data)
}

function deleteField(index: any) {
  const list = cloneDeep(props.nodeModel.properties.node_data.input_field_list)
  list.splice(index, 1)
  set(props.nodeModel.properties.node_data, 'input_field_list', list)
}

function refreshFieldList(data: any) {
  const list = cloneDeep(props.nodeModel.properties.node_data.input_field_list)
  const obj = {
    value: '',
    ...data
  }
  if (currentIndex.value !== null) {
    list.splice(currentIndex.value, 1, obj)
  } else {
    list.push(obj)
  }
  set(props.nodeModel.properties.node_data, 'input_field_list', list)
  currentIndex.value = null
}

onMounted(() => {
  set(props.nodeModel, 'validate', validate)
  setTimeout(() => {
    showEditor.value = true
  }, 100)
})
</script>
<style lang="scss" scoped></style>
