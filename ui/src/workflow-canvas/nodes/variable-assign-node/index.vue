<script setup lang="ts">
import { computed, inject, onBeforeUnmount, onMounted, ref } from 'vue'
import { cloneDeep } from 'lodash'
import type { BaseNodeModel } from '@logicflow/core'
import type { FormInstance } from 'element-plus'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { createAnchorGuard, handleNodeWheel, isLastNode } from '@/workflow-canvas/core/utils'
import type { WorkflowNodeField } from '@/workflow-canvas/types'
import JsonInput from '@/components/codemirror-editor/Json.vue'
import { randomId } from '@/utils/common'

defineOptions({ name: 'WorkflowVariableAssignNode' })
const getModel = inject('getModel') as () => BaseNodeModel
const model = getModel()

interface VariableItem {
  fields: string[]
  id: string
  name: string
  reference: string[]
  source: 'custom' | 'referencing' | 'null'
  type: string
  value: unknown
}

interface VariableAssignNodeForm {
  variable_list: VariableItem[]
  is_result?: boolean
}

// 变量配置与表单校验。
const typeOptions = ['string', 'num', 'json', 'bool']

const createVariable = (): VariableItem => ({ id: randomId(), fields: [], value: null, reference: [], type: 'string', source: 'custom', name: '' })

const defaultForm: VariableAssignNodeForm = {
  variable_list: [createVariable()],
}
const savedForm = model.properties.node_data as Partial<VariableAssignNodeForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  variable_list: Array.isArray(savedForm?.variable_list) ? savedForm.variable_list : defaultForm.variable_list,
}

const formData = computed<VariableAssignNodeForm>({
  get: () => model.properties.node_data as VariableAssignNodeForm,
  set: (value) => (model.properties.node_data = value),
})

const variableAssignNodeFormRef = ref<FormInstance>()

// 变量增删与赋值类型切换。
function addVariable() {
  const variables = cloneDeep(formData.value.variable_list)
  variables.push(createVariable())
  formData.value.variable_list = variables
}

function changeType(index: number) {
  const item = formData.value.variable_list[index]
  if (!item) return
  item.value = item.type === 'bool' ? true : null
}

function deleteVariable(index: number) {
  const variables = cloneDeep(formData.value.variable_list)
  variables.splice(index, 1)
  formData.value.variable_list = variables
}

function variableChange(item: VariableItem) {
  if (item.fields.length < 2) return
  const nodeFieldList: WorkflowNodeField[] = model.getUpNodeFieldList(true, false)
  const fieldGroup = nodeFieldList.find((field) => field.value === item.fields[0])
  const child = fieldGroup?.children?.find((field) => field.value === item.fields[1])
  if (child) item.name = child.label
}

async function validate() {
  return variableAssignNodeFormRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error }))
}

const anchorGuard = createAnchorGuard(model)
onBeforeUnmount(() => anchorGuard.reset())

onMounted(() => {
  if (formData.value.is_result === undefined && isLastNode(model)) {
    formData.value.is_result = true
  }
  model.validate = validate
})
</script>

<template>
  <NodeContainer :node-model="model">
    <el-form ref="variableAssignNodeFormRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
      <template v-for="(item, index) in formData.variable_list" :key="item.id">
        <div class="mb-2 flex items-center gap-1">
          <div class="mk-gray-card flex-1">
            <!-- 变量 -->
            <el-form-item
              label="变量"
              :prop="'variable_list.' + index + '.fields'"
              :rules="{ required: true, message: '请选择变量', trigger: 'change' }"
            >
              <NodeCascader
                :node-model="model"
                placeholder="请选择变量"
                v-model="item.fields"
                :global="true"
                @change="variableChange(item)"
              />
            </el-form-item>
            <!-- 赋值 -->
            <div class="flex-between">
              <span :class="item.source !== 'null' ? 'mk-required' : ''">赋值</span>
              <el-select
                :teleported="false"
                v-model="item.source"
                size="small"
                class="w-21!"
                @visible-change="anchorGuard.setOverlayVisible(`${item.id}:source`, $event)"
                @wheel="handleNodeWheel"
              >
                <el-option label="引用变量" value="referencing" />
                <el-option label="自定义" value="custom" />
                <el-option label="null" value="null" />
              </el-select>
            </div>

            <div v-if="item.source === 'custom'">
              <el-radio-group v-model="item.type" @change="changeType(index)" class="mb-1">
                <template v-for="variableType in typeOptions" :key="variableType">
                  <el-radio :value="variableType">{{ variableType }}</el-radio>
                </template>
              </el-radio-group>
              <!-- string -->
              <el-form-item
                v-if="item.type === 'string'"
                :prop="'variable_list.' + index + '.value'"
                :rules="{ message: '请输入', trigger: 'blur', required: true }"
              >
                <el-input v-model="item.value" placeholder="请输入内容" clearable @wheel="handleNodeWheel"></el-input>
              </el-form-item>
              <!-- num -->
              <el-form-item
                v-else-if="item.type === 'num'"
                :prop="'variable_list.' + index + '.value'"
                :rules="{ message: '请输入', trigger: ['blur', 'change'], required: true }"
              >
                <el-input-number v-model="item.value" controls-position="right" align="left" />
              </el-form-item>
              <!-- json -->
              <el-form-item
                v-else-if="item.type === 'json'"
                :prop="'variable_list.' + index + '.value'"
                :rules="[
                  { message: '请输入', trigger: 'blur', required: true },
                  {
                    validator: (rule: any, value: any, callback: any) => {
                      try {
                        JSON.parse(value)
                        callback()
                      } catch (e) {
                        callback(new Error('Invalid JSON format'))
                      }
                    },
                    trigger: 'blur',
                  },
                ]"
                class="small min-w-0 flex-1"
              >
                <JsonInput v-model="item.value" title="JSON" class="w-full" />
              </el-form-item>
              <!-- bool -->
              <el-form-item
                v-else-if="item.type === 'bool'"
                :prop="'variable_list.' + index + '.value'"
                :rules="{ message: '请输入', trigger: 'change', required: true }"
              >
                <el-select v-model="item.value" class="w-full" :teleported="false" @wheel="handleNodeWheel">
                  <el-option label="true" :value="true" />
                  <el-option label="false" :value="false" />
                </el-select>
              </el-form-item>
            </div>
            <el-form-item
              v-else-if="item.source === 'referencing'"
              :prop="'variable_list.' + index + '.reference'"
              :rules="{ required: true, message: '请选择变量', trigger: 'change' }"
            >
              <NodeCascader v-model="item.reference" :node-model="model" placeholder="请选择变量" />
            </el-form-item>
          </div>
          <!-- 删除变量 -->
          <el-button
            v-if="formData.variable_list.length > 1"
            text
            class="h-6! w-6! shrink-0 p-0!"
            aria-label="删除变量"
            @click="deleteVariable(index)"
          >
            <MkIcon name="icon_delete-trash_outlined" />
          </el-button>
        </div>
      </template>

      <el-button link type="primary" @click="addVariable">
        <MkIcon name="icon_add_outlined" />
        <span>添加</span>
      </el-button>
    </el-form>
  </NodeContainer>
</template>
