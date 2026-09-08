<script setup lang="ts">
import { computed, inject, onMounted, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import type { ToolInputField } from '@/api/types'
import PythonCodeEditor from '@/components/codemirror-editor/python.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { handleNodeWheel, isLastNode } from '@/workflow-canvas/core/utils'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { WorkflowMode } from '@/workflow-canvas/types'
import FieldSetting from './component/FieldSetting.vue'

defineOptions({ name: 'WorkflowToolCustomNode' })

type ToolNodeInputField =
  | (Omit<ToolInputField, 'source'> & { source: 'reference'; value: string[] })
  | (Omit<ToolInputField, 'source'> & { source: 'custom'; value: string })

interface ToolCustomNodeForm {
  code: string
  input_field_list: ToolNodeInputField[]
  is_result?: boolean
}

const getModel = inject('getModel') as () => WorkflowNodeModel
const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
const model = getModel()

const formRef = useTemplateRef<FormInstance>('formRef')
const inputFieldDialogRef = useTemplateRef<InstanceType<typeof InputFieldDialog>>('inputFieldDialogRef')

// 初始化节点配置，保留旧节点缺少返回内容开关时的兼容逻辑。
const defaultForm: ToolCustomNodeForm = { code: '', input_field_list: [], is_result: false }
const savedForm = model.properties.node_data as Partial<ToolCustomNodeForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  code: savedForm?.code ?? defaultForm.code,
  input_field_list: Array.isArray(savedForm?.input_field_list) ? savedForm.input_field_list : defaultForm.input_field_list,
  is_result: savedForm ? savedForm.is_result : defaultForm.is_result,
}

const formData = computed<ToolCustomNodeForm>({
  get: () => model.properties.node_data as ToolCustomNodeForm,
  set: (value) => (model.properties.node_data = value),
})

const showReturnContent = computed(() =>
  [WorkflowMode.Application, WorkflowMode.ApplicationLoop, WorkflowMode.Tool, WorkflowMode.ToolLoop].includes(workflowMode),
)

// 参数配置由弹窗提交，节点入口统一写回；编辑后沿用原有的值重置行为。
function handleOpenInputField(field?: ToolNodeInputField, index?: number) {
  inputFieldDialogRef.value?.open(field, index)
}

function handleDeleteInputField(index: number) {
  const inputFields = cloneDeep(formData.value.input_field_list)
  inputFields.splice(index, 1)
  formData.value = { ...formData.value, input_field_list: inputFields }
}

function handleInputFieldSubmit(field: ToolInputField, index?: number) {
  const inputField: ToolNodeInputField =
    field.source === 'reference' ? { ...field, source: 'reference', value: [] } : { ...field, source: 'custom', value: '' }
  const inputFields = cloneDeep(formData.value.input_field_list)

  if (index === undefined) {
    inputFields.push(inputField)
  } else {
    inputFields.splice(index, 1, inputField)
  }
  formData.value = { ...formData.value, input_field_list: inputFields }
  inputFieldDialogRef.value?.close()
}

function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error })) ?? Promise.resolve()
}

onMounted(() => {
  if (formData.value.is_result === undefined && isLastNode(model)) formData.value.is_result = true
  model.validate = validate
})
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">节点设置</h6>

    <el-form ref="formRef" :model="formData" label-position="top" hide-required-asterisk @submit.prevent>
      <div class="mk-gray-card">
        <!-- 输入参数 -->
        <div class="flex-between mb-2">
          <p>输入参数</p>
          <FieldSetting ref="inputFieldDialogRef" @submit="handleInputFieldSubmit" />
        </div>

        <template v-if="formData.input_field_list.length">
          <div class="mk-white-card">
            <el-form-item
              v-for="(field, index) in formData.input_field_list"
              :key="`${field.name}-${index}`"
              :prop="`input_field_list.${index}.value`"
              :rules="{
                required: field.is_required,
                message: field.source === 'reference' ? '请选择参数' : '请输入参数',
                trigger: field.source === 'reference' ? 'change' : 'blur',
              }"
            >
              <template #label>
                <div class="flex w-full items-center justify-between gap-2">
                  <div class="flex min-w-0 items-center gap-1">
                    <span class="max-w-32 truncate" :class="{ 'mk-required': field.is_required }" :title="field.name">{{ field.name }}</span>
                    <el-tooltip v-if="field.desc" :content="field.desc" effect="dark" placement="right">
                      <MkIcon name="icon_info_outlined" class="text-N600!" />
                    </el-tooltip>
                    <el-tag size="small" type="info">{{ field.type }}</el-tag>
                  </div>

                  <div class="flex shrink-0 items-center">
                    <el-button text type="primary" @click.stop="handleOpenInputField(field, index)">
                      <MkIcon name="icon_edit_outlined" />
                    </el-button>
                    <el-button text type="primary" @click="handleDeleteInputField(index)">
                      <MkIcon name="icon_delete-trash_outlined" />
                    </el-button>
                  </div>
                </div>
              </template>

              <NodeCascader v-if="field.source === 'reference'" v-model="field.value" :node-model="model" placeholder="请选择参数" />
              <el-input v-else v-model="field.value" placeholder="请输入参数" />
            </el-form-item>
          </div>
        </template>
        <!-- 输入参数 -->
        <el-form-item label="工具内容（Python）" class="mt-4">
          <PythonCodeEditor v-model="formData.code" title="工具内容（Python）" @wheel="handleNodeWheel" />
        </el-form-item>
        <!-- 返回内容 -->
        <div class="flex-between w-full" v-if="showReturnContent">
          <span class="flex items-center gap-1">
            返回内容
            <el-tooltip content="关闭后该节点的内容则不输出给用户。如果你想让用户看到该节点的输出内容，请打开开关。" placement="right">
              <MkIcon name="icon_info_outlined" class="text-N600!" />
            </el-tooltip>
          </span>
          <span>
            <el-switch v-model="formData.is_result" size="small" />
          </span>
        </div>
      </div>
    </el-form>
  </NodeContainer>
</template>
