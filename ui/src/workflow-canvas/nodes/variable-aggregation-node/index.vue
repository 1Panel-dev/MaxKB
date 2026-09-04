<template>
  <NodeContainer :node-model="model">
    <h5 class="title-decoration-1 mb-4">节点设置</h5>
    <el-form
      ref="variableAggregationFormRef"
      :model="form_data"
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
              <span>聚合策略<span class="text-danger">*</span></span>
            </div>
          </div>
        </template>
        <el-select v-model="form_data.strategy" :teleported="false" @change="onStrategyChange">
          <el-option label="返回每组的第一个非空值" value="first_non_null" />
          <el-option label="返回每组变量的数组（Array）" value="variable_to_array" />
          <el-option label="返回每组变量的字典（Dict）" value="variable_to_dict" />
        </el-select>
      </el-form-item>

      <div v-for="(group, gIndex) in form_data.group_list" :key="group.id" class="mb-4">
        <el-card shadow="never" class="card-never" style="--el-card-padding: 12px">
          <div class="flex-between mb-4">
            <span class="ellipsis" :title="group.label">{{ group.label }}</span>
            <div class="flex items-center">
              <el-button @click="openAddOrEditDialog(group, gIndex)" link>
                <MkIcon name="icon_edit_outlined" />
              </el-button>
              <el-button @click="deleteGroup(gIndex)" link :disabled="form_data.group_list.length <= 1">
                <MkIcon name="icon_delete-trash_outlined" />
              </el-button>
            </div>
          </div>

          <div :data-group-index="gIndex">
            <div v-for="(item, vIndex) in group.variable_list" :key="item.v_id" class="drag-card mb-2">
              <el-row class="handle" align="middle">
                <span class="drag-handle flex items-center mr-4">
                  <MkIcon name="icon_move2_outlined" color="#909399" />
                </span>
                <div class="flex flex-1 items-center">
                  <el-form-item
                    :prop="`group_list.${gIndex}.variable_list.${vIndex}.variable`"
                    :rules="{ type: 'array', required: true, message: '请选择变量', trigger: 'change' }"
                    class="mb-0"
                  >
                    <el-input
                      v-if="form_data.strategy === 'variable_to_dict'"
                      v-model="item.key"
                      placeholder="变量键"
                      style="width: 100px; margin-right: 8px"
                      maxlength="256"
                    />
                    <NodeCascader
                      :ref="setCascaderRef"
                      :node-model="model"
                      :style="{ width: form_data.strategy === 'variable_to_dict' ? '200px' : '308px' }"
                      placeholder="请选择变量"
                      v-model="item.variable"
                    />
                  </el-form-item>
                </div>
                <el-button
                  link
                  :disabled="group.variable_list.length <= 1"
                  @click="deleteVariable(gIndex, vIndex)"
                >
                  <MkIcon name="icon_delete-trash_outlined" />
                </el-button>
              </el-row>
            </div>
          </div>

          <el-button @click="addVariable(gIndex)" type="primary" size="large" link>
            <MkIcon name="icon_add_outlined" class="mr-1" />
            添加
          </el-button>
        </el-card>
      </div>

      <el-button @click="openAddOrEditDialog()" type="primary" size="large" link>
        <MkIcon name="icon_add_outlined" class="mr-1" />
        添加分组
      </el-button>
    </el-form>
    <GroupFieldDialog ref="groupFieldDialogRef" @refresh="refreshFieldList" />
  </NodeContainer>
</template>
<script setup lang="ts">
import { cloneDeep, set } from 'lodash'
import type { BaseNodeModel } from '@logicflow/core'
import type { FormInstance } from 'element-plus'
import { computed, inject, nextTick, onBeforeUnmount, onMounted, ref, type Ref, useTemplateRef } from 'vue'
import Sortable from 'sortablejs'

import GroupFieldDialog from './component/GroupFieldDialog.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { isLastNode } from '@/workflow-canvas/core/utils'
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

const form_data = computed<{ is_result?: boolean; strategy: string; group_list: GroupItem[] }>({
  get: () => {
    if (!model.properties.node_data) {
      set(model.properties, 'node_data', defaultForm())
    }
    // 向下兼容 variable_to_json -> variable_to_array
    const data = model.properties.node_data as { is_result?: boolean; strategy: string; group_list: GroupItem[] }
    if (data.strategy === 'variable_to_json') {
      data.strategy = 'variable_to_array'
    }
    return data
  },
  set: (value) => {
    set(model.properties, 'node_data', value)
  },
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
        const group = form_data.value.group_list[gIndex]
        if (!group) return
        const list = cloneDeep(group.variable_list)
        const [moved] = list.splice(evt.oldIndex, 1)
        if (!moved) return
        list.splice(evt.newIndex, 0, moved)
        set(group, 'variable_list', list)
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
  if (form_data.value.strategy !== 'variable_to_dict') {
    form_data.value.group_list.forEach((group) => {
      group.variable_list.forEach((item) => {
        if (item.key !== undefined) set(item, 'key', undefined)
      })
    })
  }
}

function syncFieldList() {
  const fields = form_data.value.group_list.map((item) => ({ label: item.label, value: item.field }))
  if (!model.properties.config) {
    set(model.properties, 'config', {})
  }
  set(model.properties.config!, 'fields', fields)
  model.clearNextNodeField(true)
}

function refreshFieldList(data: { field: string; label: string }, index?: number) {
  for (let i = 0; i < form_data.value.group_list.length; i++) {
    const group = form_data.value.group_list[i]
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
  const list = cloneDeep(form_data.value.group_list)
  const target = list[gIndex]
  if (!target) return
  target.field = data.field
  target.label = data.label
  set(form_data.value, 'group_list', list)
  syncFieldList()
}

function addGroup(data: { field: string; label: string }) {
  const list = cloneDeep(form_data.value.group_list)
  list.push({ id: randomId(), field: data.field, label: data.label, variable_list: [{ v_id: randomId(), variable: [] }] })
  set(form_data.value, 'group_list', list)
  nextTick(() => initSortable(list.length - 1))
  syncFieldList()
}

function deleteGroup(gIndex: number) {
  const list = cloneDeep(form_data.value.group_list)
  list.splice(gIndex, 1)
  set(form_data.value, 'group_list', list)
  destroySortable(gIndex)
  syncFieldList()
}

function addVariable(gIndex: number) {
  const list = cloneDeep(form_data.value.group_list)
  const target = list[gIndex]
  if (!target) return
  target.variable_list.push({ v_id: randomId(), variable: [] })
  set(form_data.value, 'group_list', list)
  nextTick(() => initSortable(gIndex))
}

function deleteVariable(gIndex: number, vIndex: number) {
  const list = cloneDeep(form_data.value.group_list)
  const target = list[gIndex]
  if (!target) return
  target.variable_list.splice(vIndex, 1)
  set(form_data.value, 'group_list', list)
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

onMounted(() => {
  if (form_data.value.is_result === undefined && isLastNode(model)) {
    set(form_data.value, 'is_result', true)
  }
  set(model, 'validate', validate)
  nextTick(() => {
    form_data.value.group_list.forEach((_, index) => initSortable(index))
  })
  syncFieldList()
})

onBeforeUnmount(() => {
  Array.from(sortableInstances.keys()).forEach(destroySortable)
})
</script>
<style lang="scss" scoped>
.drag-card {
  :deep(.el-form-item) {
    margin-bottom: 0;
  }
}

.handle {
  cursor: move;
}

.drag-handle {
  height: 32px;
}
</style>
