<template>
  <NodeContainer :node-model="model">
    <el-form
      ref="variableAssignNodeFormRef"
      :model="form_data"
      label-position="top"
      require-asterisk-position="right"
      label-width="auto"
      hide-required-asterisk
      @submit.prevent
    >
      <template v-for="(item, index) in form_data.variable_list" :key="item.id">
        <el-card shadow="never" class="card-never mb-8" style="--el-card-padding: 12px">
          <el-form-item>
            <template #label>
              <div class="flex-between">
                <div>
                  变量<span class="color-danger">*</span>
                </div>
                <el-button v-if="form_data.variable_list.length > 1" text @click="deleteVariable(index)">
                  <MkIcon name="icon_delete-trash_outlined" />
                </el-button>
              </div>
            </template>
            <NodeCascader
              :ref="setCascaderRef"
              :node-model="model"
              class="w-full"
              placeholder="请选择变量"
              v-model="item.fields"
              :global="true"
              @change="variableChange(item)"
            />
          </el-form-item>
          <div class="flex-between mb-8">
            <span class="lighter">赋值<span class="color-danger">*</span></span>
            <el-select :teleported="false" v-model="item.source" size="small" style="width: 85px">
              <el-option label="引用变量" value="referencing" />
              <el-option label="自定义" value="custom" />
              <el-option label="null" value="null" />
            </el-select>
          </div>

          <div v-if="item.source === 'custom'" class="flex w-full">
            <el-select v-model="item.type" style="max-width: 85px" class="mr-8" @change="changeType(index)">
              <el-option v-for="item in typeOptions" :key="item" :label="item" :value="item" />
            </el-select>

            <el-form-item
              v-if="item.type === 'string'"
              :prop="'variable_list.' + index + '.value'"
              :rules="{ message: '请输入内容', trigger: 'blur', required: true }"
              class="w-full"
            >
              <el-input v-model="item.value" placeholder="请输入内容" clearable @wheel="handleNodeWheel"></el-input>
            </el-form-item>
            <el-form-item v-else-if="item.type === 'num'" :prop="'variable_list.' + index + '.value'" class="w-full">
              <el-input-number v-model="item.value" controls-position="right" class="w-full" />
            </el-form-item>
            <el-form-item
              v-else-if="item.type === 'json'"
              :prop="'variable_list.' + index + '.value'"
              :rules="[
                { message: '请输入内容', trigger: 'blur', required: true },
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
              class="w-full"
            >
              <JsonInput v-model="item.value" title="JSON" class="w-full" />
            </el-form-item>
            <el-form-item
              v-else-if="item.type === 'bool'"
              :prop="'variable_list.' + index + '.value'"
              :rules="{ message: '请输入内容', trigger: 'blur', required: true }"
            >
              <el-select v-model="item.value" style="width: 155px" :teleported="false">
                <el-option label="true" :value="true" />
                <el-option label="false" :value="false" />
              </el-select>
            </el-form-item>
          </div>
          <el-form-item v-else-if="item.source === 'referencing'">
            <NodeCascader :ref="setCascaderRef2" :node-model="model" class="w-full" placeholder="请选择变量" v-model="item.reference" />
          </el-form-item>
        </el-card>
      </template>

      <el-button link type="primary" @click="addVariable">
        <MkIcon name="icon_add_outlined" class="mr-1" />
        添加变量
      </el-button>
    </el-form>
  </NodeContainer>
</template>
<script setup lang="ts">
import { cloneDeep } from 'lodash'
import type { BaseNodeModel } from '@logicflow/core'
import type { FormInstance } from 'element-plus'
import { inject, onMounted, ref, type Ref } from 'vue'

import JsonInput from '@/components/codemirror-editor/Json.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { handleNodeWheel, isLastNode } from '@/workflow-canvas/core/utils'
import type { WorkflowNodeField } from '@/workflow-canvas/types'
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

const typeOptions = ['string', 'num', 'json', 'bool']

const defaultVariable = (): VariableItem => ({ id: randomId(), fields: [], value: null, reference: [], type: 'string', source: 'custom', name: '' })

if (!model.properties.node_data) {
  model.properties.node_data = { variable_list: [defaultVariable()] }
}
const form_data = model.properties.node_data as { variable_list: VariableItem[] }

const variableAssignNodeFormRef = ref<FormInstance>()
const nodeCascaderRef: Ref<Array<{ validate: () => Promise<unknown> }>> = ref([])
const nodeCascaderRef2: Ref<Array<{ validate: () => Promise<unknown> }>> = ref([])

function setCascaderRef(el: unknown) {
  if (el && !nodeCascaderRef.value.includes(el as { validate: () => Promise<unknown> })) {
    nodeCascaderRef.value.push(el as { validate: () => Promise<unknown> })
  }
}
function setCascaderRef2(el: unknown) {
  if (el && !nodeCascaderRef2.value.includes(el as { validate: () => Promise<unknown> })) {
    nodeCascaderRef2.value.push(el as { validate: () => Promise<unknown> })
  }
}

const validate = () => {
  const ps = [variableAssignNodeFormRef.value?.validate(), ...nodeCascaderRef.value.map((item) => item.validate())]
  if (nodeCascaderRef2.value.length) {
    ps.push(...nodeCascaderRef2.value.map((item) => item.validate()))
  }
  return Promise.all(ps).catch((err: unknown) => Promise.reject({ node: model, errMessage: err }))
}

function addVariable() {
  const list = cloneDeep(form_data.variable_list)
  list.push(defaultVariable())
  model.properties.node_data.variable_list = list
}

function changeType(index: number) {
  const item = form_data.variable_list[index]
  if (!item) return
  item.value = item.type === 'bool' ? true : null
}

function deleteVariable(index: number) {
  const list = cloneDeep(form_data.variable_list)
  list.splice(index, 1)
  model.properties.node_data.variable_list = list
}

function variableChange(item: VariableItem) {
  if (item.fields.length < 2) return
  const nodeFieldList: WorkflowNodeField[] = model.getUpNodeFieldList(true, false)
  const fieldGroup = nodeFieldList.find((field) => field.value === item.fields[0])
  const child = fieldGroup?.children?.find((field) => field.value === item.fields[1])
  if (child) item.name = child.label
}

onMounted(() => {
  if (model.properties.node_data?.is_result === undefined && isLastNode(model)) {
    model.properties.node_data.is_result = true
  }
  model.validate = validate
})
</script>
<style lang="scss" scoped></style>
