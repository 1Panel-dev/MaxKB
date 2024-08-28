<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-16">节点设置</h5>
    <div class="flex-between">
      <h5 class="lighter mb-8">输入变量</h5>
      <el-button link type="primary" @click="openAddDialog()">
        <el-icon class="mr-4"><Plus /></el-icon> 添加
      </el-button>
    </div>
    <el-form
      @submit.prevent
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
                  <div class="flex">
                    <span class="flex">
                      <auto-tooltip :content="item.name" style="max-width: 130px">
                        {{ item.name }}
                      </auto-tooltip>
                      <span class="danger" v-if="item.is_required">*</span>
                    </span>
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
                :width="100"
              />
              <el-input v-else v-model="item.value" placeholder="请输入变量值" />
            </el-form-item>
          </template>
        </div>

        <el-text type="info" v-else> 暂无数据 </el-text>
      </el-card>

      <h5 class="lighter mb-8">Python 代码</h5>
      <div class="function-CodemirrorEditor mb-8" v-if="showEditor">
        <CodemirrorEditor
          v-model="chat_data.code"
          @wheel="wheel"
          style="height: 130px !important"
        />
        <div class="function-CodemirrorEditor__footer">
          <el-button text type="info" @click="openCodemirrorDialog" class="magnify">
            <AppIcon iconName="app-magnify" style="font-size: 16px"></AppIcon>
          </el-button>
        </div>
      </div>

      <el-form-item label="返回内容" @click.prevent>
        <template #label>
          <div class="flex align-center">
            <div class="mr-4">
              <span>返回内容<span class="danger">*</span></span>
            </div>
            <el-tooltip effect="dark" placement="right" popper-class="max-w-200">
              <template #content>
                关闭后该节点的内容则不输出给用户。 如果你想让用户看到该节点的输出内容，请打开开关。
              </template>
              <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
            </el-tooltip>
          </div>
        </template>
        <el-switch size="small" v-model="chat_data.is_result" />
      </el-form-item>
    </el-form>
    <FieldFormDialog ref="FieldFormDialogRef" @refresh="refreshFieldList" />
    <!-- Codemirror 弹出层 -->
    <el-dialog v-model="dialogVisible" title="Python 代码" append-to-body>
      <CodemirrorEditor
        v-model="cloneContent"
        style="height: 300px !important; border: 1px solid #bbbfc4; border-radius: 4px"
      />
      <template #footer>
        <div class="dialog-footer mt-24">
          <el-button type="primary" @click="submitDialog"> 确认</el-button>
        </div>
      </template>
    </el-dialog>
  </NodeContainer>
</template>
<script setup lang="ts">
import { cloneDeep, set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted } from 'vue'
import FieldFormDialog from '@/views/function-lib/component/FieldFormDialog.vue'
import { isLastNode } from '@/workflow/common/data'

const props = defineProps<{ nodeModel: any }>()

const wheel = (e: any) => {
  if (e.ctrlKey === true) {
    e.preventDefault()
    return true
  } else {
    e.stopPropagation()
    return true
  }
}
const FieldFormDialogRef = ref()
const nodeCascaderRef = ref()

const form = {
  code: '',
  input_field_list: [],
  is_result: false
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

const dialogVisible = ref(false)
const cloneContent = ref('')

function openCodemirrorDialog() {
  cloneContent.value = chat_data.value.code
  dialogVisible.value = true
}

function submitDialog() {
  set(props.nodeModel.properties.node_data, 'code', cloneContent.value)
  dialogVisible.value = false
}

function openAddDialog(data?: any, index?: any) {
  if (typeof index !== 'undefined') {
    currentIndex.value = index
  }

  FieldFormDialogRef.value.open(data)
}

function deleteField(index: any) {
  const list: any = cloneDeep(props.nodeModel.properties.node_data.input_field_list)
  list.splice(index, 1)
  set(props.nodeModel.properties.node_data, 'input_field_list', list)
}

function refreshFieldList(data: any) {
  const list = cloneDeep(props.nodeModel.properties.node_data.input_field_list)
  const obj = {
    value: data.source === 'reference' ? [] : '',
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
  if (typeof props.nodeModel.properties.node_data?.is_result === 'undefined') {
    if (isLastNode(props.nodeModel)) {
      set(props.nodeModel.properties.node_data, 'is_result', true)
    }
  }
  set(props.nodeModel, 'validate', validate)
  setTimeout(() => {
    showEditor.value = true
  }, 100)
})
</script>
<style lang="scss"></style>
