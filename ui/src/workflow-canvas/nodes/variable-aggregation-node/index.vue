<script setup lang="ts">
import { computed, inject, onBeforeUnmount, onMounted, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { BaseNodeModel } from '@logicflow/core'
import type { FormInstance } from 'element-plus'

import GroupFieldDialog from './component/GroupFieldDialog.vue'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { createAnchorGuard, handleNodeWheel, isLastNode } from '@/workflow-canvas/core/utils'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { randomId } from '@/utils/common'
import { MsgError } from '@/utils/message'

defineOptions({ name: 'WorkflowVariableAggregationNode' })
const getModel = inject('getModel') as () => BaseNodeModel
const model = getModel() as WorkflowNodeModel

interface VariableItem {
  v_id: string
  variable: string[]
  key?: string
}
interface GroupItem {
  id: string
  label: string
  field: string
  variable_list: VariableItem[]
}

interface VariableAggregationNodeForm {
  strategy: string
  group_list: GroupItem[]
  is_result?: boolean
}

const defaultForm: VariableAggregationNodeForm = {
  strategy: 'first_non_null',
  group_list: [
    {
      id: randomId(),
      label: 'Group1',
      field: 'Group1',
      variable_list: [{ v_id: randomId(), variable: [] }],
    },
  ],
}

// 初始化时兼容旧聚合策略，表单读取不修改节点数据。
const savedForm = model.properties.node_data as Partial<VariableAggregationNodeForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  strategy: savedForm?.strategy === 'variable_to_json' ? 'variable_to_array' : (savedForm?.strategy ?? defaultForm.strategy),
  group_list: Array.isArray(savedForm?.group_list) ? savedForm.group_list : defaultForm.group_list,
}
const formData = computed<VariableAggregationNodeForm>({
  get: () => model.properties.node_data as VariableAggregationNodeForm,
  set: (value) => (model.properties.node_data = value),
})

const variableAggregationFormRef = useTemplateRef<FormInstance>('variableAggregationFormRef')
const groupFieldDialogRef = useTemplateRef<InstanceType<typeof GroupFieldDialog>>('groupFieldDialogRef')
const defaultVariable = (): VariableItem => ({ v_id: randomId(), variable: [] })

function onStrategyChange() {
  if (formData.value.strategy !== 'variable_to_dict') {
    formData.value.group_list.forEach((group) => {
      group.variable_list.forEach((item) => {
        if (item.key !== undefined) item.key = undefined
      })
    })
  }
}

function syncFieldList() {
  const fields = formData.value.group_list.map((item) => ({ label: item.label, value: item.field }))
  if (!model.properties.config) {
    model.properties.config = {}
  }
  model.properties.config!.fields = fields
  model.clearNextNodeField(true)
}

/* 添加编辑组 */
function handleGroupSubmit(data: { field: string; label: string }, index?: number) {
  for (let i = 0; i < formData.value.group_list.length; i++) {
    const group = formData.value.group_list[i]
    if (group && group.field === data.field && i !== index) {
      MsgError(`变量 "${data.field}" 已存在`)
      return
    }
  }
  if (index === undefined || index === null) {
    addGroup(data)
  } else {
    editGroupName(data, index)
  }
  groupFieldDialogRef.value?.close()
}

function editGroupName(data: { field: string; label: string }, gIndex: number) {
  const list = cloneDeep(formData.value.group_list)
  const target = list[gIndex]
  if (!target) return
  target.field = data.field
  target.label = data.label
  formData.value.group_list = list
  syncFieldList()
}

function addGroup(data: { field: string; label: string }) {
  const list = cloneDeep(formData.value.group_list)
  list.push({ id: randomId(), field: data.field, label: data.label, variable_list: [{ v_id: randomId(), variable: [] }] })
  formData.value.group_list = list
  syncFieldList()
}

function deleteGroup(gIndex: number) {
  const list = cloneDeep(formData.value.group_list)
  list.splice(gIndex, 1)
  formData.value.group_list = list
  syncFieldList()
}

function openAddOrEditDialog(group?: GroupItem, index?: number) {
  const data = group ? { field: group.field, label: group.label } : undefined
  groupFieldDialogRef.value?.open(data, index)
}

async function validate() {
  return variableAggregationFormRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error }))
}
const anchorGuard = createAnchorGuard(model)

onMounted(() => {
  if (formData.value.is_result === undefined && isLastNode(model)) {
    formData.value.is_result = true
  }
  model.validate = validate
  syncFieldList()
})

onBeforeUnmount(() => {
  anchorGuard.reset()
})
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">节点设置</h6>
    <div class="mk-gray-card">
      <el-form ref="variableAggregationFormRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
        <!-- 聚合策略 -->
        <el-form-item label="聚合策略" :rules="{ required: true, message: '请选择聚合策略', trigger: 'change' }">
          <el-select v-model="formData.strategy" :teleported="false" @change="onStrategyChange" @wheel="handleNodeWheel">
            <el-option label="返回每组的第一个非空值" value="first_non_null" />
            <el-option label="返回每组变量的数组（Array）" value="variable_to_array" />
            <el-option label="返回每组变量的字典（Dict）" value="variable_to_dict" />
          </el-select>
        </el-form-item>
        <template v-for="(group, gIndex) in formData.group_list" :key="group.id">
          <div class="mk-white-card mb-2">
            <div class="flex-between mb-2 gap-2">
              <span class="min-w-0 truncate" :title="group.label">{{ group.label }}</span>
              <div class="flex shrink-0 items-center gap-1">
                <!-- 编辑组 -->
                <el-button text @click="openAddOrEditDialog(group, gIndex)">
                  <MkIcon name="icon_edit_outlined" />
                </el-button>
                <!-- 删除组 -->
                <el-button text @click="deleteGroup(gIndex)" :disabled="formData.group_list.length <= 1">
                  <MkIcon name="icon_delete-trash_outlined" />
                </el-button>
              </div>
            </div>

            <MkFormList v-model="group.variable_list" :default-item="defaultVariable" :first-row-has-label="false" sortable item-key="v_id">
              <template #default="{ item, index: vIndex }">
                <el-form-item
                  v-if="formData.strategy === 'variable_to_dict'"
                  class="small w-25 shrink-0"
                  :prop="`group_list.${gIndex}.variable_list.${vIndex}.key`"
                  :rules="{ required: true, message: '请输入键名', trigger: 'blur' }"
                >
                  <el-input v-model="item.key" placeholder="请输入键名" maxlength="256" />
                </el-form-item>
                <el-form-item
                  class="small min-w-0 flex-1"
                  :prop="`group_list.${gIndex}.variable_list.${vIndex}.variable`"
                  :rules="{ type: 'array', required: true, message: '请选择变量', trigger: 'change' }"
                >
                  <NodeCascader v-model="item.variable" :node-model="model" placeholder="请选择变量" />
                </el-form-item>
              </template>
            </MkFormList>
          </div>
        </template>

        <el-button @click="openAddOrEditDialog()" type="primary" link>
          <MkIcon name="icon_add_outlined" class="mr-1" />
          添加分组
        </el-button>
      </el-form>
    </div>
    <GroupFieldDialog ref="groupFieldDialogRef" @submit="handleGroupSubmit" />
  </NodeContainer>
</template>
