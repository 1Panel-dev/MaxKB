<script setup lang="ts">
import { cloneDeep } from 'lodash'
import type { BaseNodeModel } from '@logicflow/core'
import type { FormInstance } from 'element-plus'
import { computed, inject, nextTick, onBeforeUnmount, onMounted, ref, type Ref, useTemplateRef } from 'vue'
import Sortable from 'sortablejs'

import GroupFieldDialog from './component/GroupFieldDialog.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
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

const defaultForm = () =>
  ({
    strategy: 'first_non_null',
    group_list: [
      {
        id: randomId(),
        label: 'Group1',
        field: 'Group1',
        variable_list: [{ v_id: randomId(), variable: [] }],
      },
    ],
  }) as { strategy: string; group_list: GroupItem[] }

// 初始化时兼容旧聚合策略，表单读取不修改节点数据。
const savedForm = model.properties.node_data as { is_result?: boolean; strategy: string; group_list: GroupItem[] } | undefined
const initialForm = savedForm ?? defaultForm()
model.properties.node_data = {
  ...initialForm,
  strategy: initialForm.strategy === 'variable_to_json' ? 'variable_to_array' : initialForm.strategy,
}
const formData = computed<{ is_result?: boolean; strategy: string; group_list: GroupItem[] }>({
  get: () => model.properties.node_data as { is_result?: boolean; strategy: string; group_list: GroupItem[] },
  set: (value) => (model.properties.node_data = value),
})

const variableAggregationFormRef = useTemplateRef<FormInstance>('variableAggregationFormRef')
const groupFieldDialogRef = useTemplateRef<InstanceType<typeof GroupFieldDialog>>('groupFieldDialogRef')
const nodeCascaderRef: Ref<Array<{ validate: () => Promise<unknown> }>> = ref([])
const sortableInstances = new Map<number, Sortable>()

function setCascaderRef(el: unknown) {
  if (el && !nodeCascaderRef.value.includes(el as { validate: () => Promise<unknown> })) {
    nodeCascaderRef.value.push(el as { validate: () => Promise<unknown> })
  }
}

function initSortable(gIndex: number) {
  destroySortable(gIndex)
  const nodeRoot = document.querySelector(`[data-node-id="${model.id}"]`)
  const el = nodeRoot?.querySelector(`[data-group-index="${gIndex}"]`) as HTMLElement | undefined
  if (!el) {
    // 节点内容 Teleport 到 foreignObject 是异步的,未挂载时重试
    nextTick(() => initSortable(gIndex))
    return
  }
  sortableInstances.set(
    gIndex,
    Sortable.create(el, {
      animation: 150,
      ghostClass: 'ghost',
      handle: '.handle',
      onEnd: (evt: { oldIndex?: number; newIndex?: number }) => {
        if (evt.oldIndex === undefined || evt.newIndex === undefined) return
        if (evt.oldIndex === evt.newIndex) return
        const group = formData.value.group_list[gIndex]
        if (!group) return
        const list = cloneDeep(group.variable_list)
        const [moved] = list.splice(evt.oldIndex, 1)
        if (!moved) return
        list.splice(evt.newIndex, 0, moved)
        group.variable_list = list
        nextTick(() => initSortable(gIndex))
      },
    }),
  )
}

function destroySortable(gIndex: number) {
  sortableInstances.get(gIndex)?.destroy()
  sortableInstances.delete(gIndex)
}

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

function refreshFieldList(data: { field: string; label: string }, index?: number) {
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
  nextTick(() => initSortable(list.length - 1))
  syncFieldList()
}

function deleteGroup(gIndex: number) {
  const list = cloneDeep(formData.value.group_list)
  list.splice(gIndex, 1)
  formData.value.group_list = list
  destroySortable(gIndex)
  syncFieldList()
}

function addVariable(gIndex: number) {
  const list = cloneDeep(formData.value.group_list)
  const target = list[gIndex]
  if (!target) return
  target.variable_list.push({ v_id: randomId(), variable: [] })
  formData.value.group_list = list
  nextTick(() => initSortable(gIndex))
}

function deleteVariable(gIndex: number, vIndex: number) {
  const list = cloneDeep(formData.value.group_list)
  const target = list[gIndex]
  if (!target) return
  target.variable_list.splice(vIndex, 1)
  formData.value.group_list = list
  nextTick(() => initSortable(gIndex))
}

function openAddOrEditDialog(group?: GroupItem, index?: number) {
  const data = group ? { field: group.field, label: group.label } : undefined
  groupFieldDialogRef.value?.open(data, index)
}

const validate = () => {
  const vList = [variableAggregationFormRef.value?.validate(), ...nodeCascaderRef.value.map((item) => item.validate())]
  return Promise.all(vList).catch((err) => Promise.reject({ node: model, errMessage: err }))
}

const anchorGuard = createAnchorGuard(model)

onMounted(() => {
  if (formData.value.is_result === undefined && isLastNode(model)) {
    formData.value.is_result = true
  }
  model.validate = validate
  nextTick(() => {
    formData.value.group_list.forEach((_, index) => initSortable(index))
  })
  syncFieldList()
})

onBeforeUnmount(() => {
  anchorGuard.reset()
  Array.from(sortableInstances.keys()).forEach(destroySortable)
})
</script>

<template>
  <NodeContainer :node-model="model">
    <el-form
      ref="variableAggregationFormRef"
      :model="formData"
      label-position="top"
      require-asterisk-position="right"
      label-width="auto"
      hide-required-asterisk
      @submit.prevent
    >
      <el-form-item :rules="{ required: true, trigger: 'change' }">
        <template #label>
          <div class="flex-between">
            <div>
              <span>聚合策略<span class="ml-1 text-danger">*</span></span>
            </div>
          </div>
        </template>
        <el-select
          v-model="formData.strategy"
          :teleported="false"
          @change="onStrategyChange"
          @visible-change="anchorGuard.setOverlayVisible('strategy', $event)"
          @wheel="handleNodeWheel"
        >
          <el-option label="返回每组的第一个非空值" value="first_non_null" />
          <el-option label="返回每组变量的数组（Array）" value="variable_to_array" />
          <el-option label="返回每组变量的字典（Dict）" value="variable_to_dict" />
        </el-select>
      </el-form-item>

      <div v-for="(group, gIndex) in formData.group_list" :key="group.id" class="mk-gray-card mb-2">
        <div class="flex-between mb-2 gap-2">
          <span class="min-w-0 truncate" :title="group.label">{{ group.label }}</span>
          <div class="flex shrink-0 items-center gap-1">
            <el-button @click="openAddOrEditDialog(group, gIndex)" text class="h-6! w-6! p-0!" aria-label="编辑分组">
              <MkIcon name="icon_edit_outlined" />
            </el-button>
            <el-button
              @click="deleteGroup(gIndex)"
              text
              class="ml-0! h-6! w-6! p-0!"
              aria-label="删除分组"
              :disabled="formData.group_list.length <= 1"
            >
              <MkIcon name="icon_delete-trash_outlined" />
            </el-button>
          </div>
        </div>

        <div :data-group-index="gIndex">
          <div v-for="(item, vIndex) in group.variable_list" :key="item.v_id" class="mb-2">
            <div class="handle flex cursor-move items-center gap-2">
              <span class="flex h-8 shrink-0 items-center text-N600">
                <MkIcon name="icon_move2_outlined" />
              </span>
              <div class="min-w-0 flex-1">
                <el-form-item
                  :prop="`group_list.${gIndex}.variable_list.${vIndex}.variable`"
                  :rules="{ type: 'array', required: true, message: '请选择变量', trigger: 'change' }"
                  class="mb-0! w-full"
                >
                  <el-input
                    v-if="formData.strategy === 'variable_to_dict'"
                    v-model="item.key"
                    placeholder="变量键"
                    class="mr-2 w-25! shrink-0"
                    maxlength="256"
                  />
                  <NodeCascader :ref="setCascaderRef" :node-model="model" class="min-w-0 flex-1" placeholder="请选择变量" v-model="item.variable" />
                </el-form-item>
              </div>
              <el-button
                text
                class="h-6! w-6! shrink-0 p-0!"
                aria-label="删除变量"
                :disabled="group.variable_list.length <= 1"
                @click="deleteVariable(gIndex, vIndex)"
              >
                <MkIcon name="icon_delete-trash_outlined" />
              </el-button>
            </div>
          </div>
        </div>

        <el-button @click="addVariable(gIndex)" type="primary" link>
          <MkIcon name="icon_add_outlined" class="mr-1" />
          添加
        </el-button>
      </div>

      <el-button @click="openAddOrEditDialog()" type="primary" link>
        <MkIcon name="icon_add_outlined" class="mr-1" />
        添加分组
      </el-button>
    </el-form>
    <GroupFieldDialog ref="groupFieldDialogRef" @refresh="refreshFieldList" />
  </NodeContainer>
</template>
