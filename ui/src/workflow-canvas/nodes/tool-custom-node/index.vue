<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'
import { QuestionFilled } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import type { ToolInputField } from '@/api/types'
import PythonCodeEditor from '@/components/codemirror-editor/python.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { handleNodeWheel, isLastNode } from '@/workflow-canvas/core/utils'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { WorkflowMode } from '@/workflow-canvas/types'
import InputFieldDialog from './InputFieldDialog.vue'

defineOptions({ name: 'WorkflowToolCustomNode' })

type ToolNodeInputField =
  | (Omit<ToolInputField, 'source'> & { source: 'reference'; value: string[] })
  | (Omit<ToolInputField, 'source'> & { source: 'custom'; value: string })

interface ToolCustomNodeForm {
  code: string
  input_field_list: ToolNodeInputField[]
  is_result: boolean
}

const getModel = inject('getModel') as () => WorkflowNodeModel
const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
const model = getModel()

const formRef = useTemplateRef<FormInstance>('formRef')
const inputFieldDialogRef = useTemplateRef<InstanceType<typeof InputFieldDialog>>('inputFieldDialogRef')
const currentFieldIndex = ref<number>()

const savedForm = model.properties.node_data as Partial<ToolCustomNodeForm> | undefined
model.properties.node_data = {
  code: savedForm?.code ?? '',
  input_field_list: Array.isArray(savedForm?.input_field_list) ? savedForm.input_field_list : [],
  is_result: savedForm ? savedForm.is_result : false,
}

const formData = computed<ToolCustomNodeForm>({
  get: () => model.properties.node_data as ToolCustomNodeForm,
  set: (value) => (model.properties.node_data = value),
})

const showReturnContent = computed(() =>
  [WorkflowMode.Application, WorkflowMode.ApplicationLoop, WorkflowMode.Tool, WorkflowMode.ToolLoop].includes(workflowMode),
)

function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error })) ?? Promise.resolve()
}

function handleOpenInputField(field?: ToolNodeInputField, index?: number) {
  currentFieldIndex.value = index
  inputFieldDialogRef.value?.open(field)
}

function handleDeleteInputField(index: number) {
  formData.value.input_field_list.splice(index, 1)
}

function handleInputFieldRefresh(field: ToolInputField) {
  const inputField: ToolNodeInputField =
    field.source === 'reference' ? { ...field, source: 'reference', value: [] } : { ...field, source: 'custom', value: '' }

  if (currentFieldIndex.value === undefined) {
    formData.value.input_field_list.push(inputField)
  } else {
    formData.value.input_field_list.splice(currentFieldIndex.value, 1, inputField)
  }
  currentFieldIndex.value = undefined
}

onMounted(() => {
  if (formData.value.is_result === undefined && isLastNode(model)) formData.value.is_result = true
  model.validate = validate
})
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mb-3">节点设置</h6>

    <el-form ref="formRef" :model="formData" label-position="top" hide-required-asterisk @submit.prevent>
      <div class="mb-2 flex-between">
        <h6>输入参数</h6>
        <el-button link type="primary" @click="handleOpenInputField()">
          <MkIcon name="icon_add_outlined" class="mr-1" />
          添加
        </el-button>
      </div>

      <el-card shadow="never" class="card-never mb-4" style="--el-card-padding: 12px">
        <template v-if="formData.input_field_list.length">
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
                  <span class="max-w-32 truncate" :title="field.name">{{ field.name }}</span>
                  <el-tooltip v-if="field.desc" :content="field.desc" effect="dark" placement="right">
                    <MkIcon :icon="QuestionFilled" class="cursor-help text-N600" />
                  </el-tooltip>
                  <span v-if="field.is_required" class="text-danger">*</span>
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

            <NodeCascader v-if="field.source === 'reference'" v-model="field.value" :node-model="model" class="w-full" placeholder="请选择参数" />
            <el-input v-else v-model="field.value" placeholder="请输入参数" />
          </el-form-item>
        </template>
        <MkEmpty v-else :image-size="60" />
      </el-card>

      <h6 class="mb-2">Python 代码</h6>
      <PythonCodeEditor v-model="formData.code" class="h-32" title="Python 代码" @wheel="handleNodeWheel" />

      <el-form-item v-if="showReturnContent" label="返回内容" class="mt-4" @click.prevent>
        <template #label>
          <div class="flex items-center gap-1">
            <span>返回内容</span>
            <el-tooltip content="开启后，该节点的输出会作为工作流的最终回复内容" effect="dark" placement="right">
              <MkIcon :icon="QuestionFilled" class="cursor-help text-N600" />
            </el-tooltip>
          </div>
        </template>
        <el-switch v-model="formData.is_result" size="small" />
      </el-form-item>
    </el-form>

    <InputFieldDialog ref="inputFieldDialogRef" @refresh="handleInputFieldRefresh" />
  </NodeContainer>
</template>
