<template>
  <NodeContainer :node-model="model">
    <el-form ref="conditionNodeFormRef" :model="form_data" label-position="top" require-asterisk-position="right" label-width="auto" @submit.prevent>
      <template v-for="(item, index) in form_data.branch" :key="item.id">
        <div v-branch-resize="{ item, index }">
          <el-card shadow="never" class="card-never drag-card mb-2" :class="{ 'drag-card-empty': index === form_data.branch.length - 1 }">
            <template #header>
              <div class="flex items-center justify-between">
                <span>{{ item.type }}</span>
                <div v-if="item.conditions.length > 1" class="flex items-center">
                  <span class="text-N600">满足</span>
                  <el-select :teleported="false" v-model="item.condition" size="small" style="width: 60px; margin: 0 8px">
                    <el-option label="且" value="and" />
                    <el-option label="或" value="or" />
                  </el-select>
                  <span class="text-N600">条件</span>
                </div>
              </div>
            </template>

            <div v-if="index !== form_data.branch.length - 1">
              <template v-for="(condition, cIndex) in item.conditions" :key="cIndex">
                <el-row :gutter="8">
                  <el-col :span="11">
                    <el-form-item
                      :prop="`branch.${index}.conditions.${cIndex}.field`"
                      :rules="{ type: 'array', required: true, message: '请选择变量', trigger: 'change' }"
                    >
                      <NodeCascader :ref="setCascaderRef" :node-model="model" class="w-full" placeholder="请选择变量" v-model="condition.field" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="6">
                    <el-form-item
                      :prop="`branch.${index}.conditions.${cIndex}.compare`"
                      :rules="{ required: true, message: '请选择比较符', trigger: 'change' }"
                    >
                      <el-select
                        :teleported="false"
                        v-model="condition.compare"
                        placeholder="请选择比较符"
                        clearable
                        @change="changeCondition($event, index, cIndex)"
                        @wheel="handleNodeWheel"
                      >
                        <template v-for="(item, index) in compareList" :key="index">
                          <el-option :label="item.label" :value="item.value" />
                        </template>
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="6">
                    <el-form-item
                      v-if="!['is_null', 'is_not_null', 'is_true', 'is_not_true'].includes(condition.compare)"
                      :prop="`branch.${index}.conditions.${cIndex}.value`"
                      :rules="{ required: true, message: '请输入比较值', trigger: 'blur' }"
                    >
                      <el-input v-model="condition.value" placeholder="请输入比较值" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="1">
                    <el-button
                      :disabled="form_data.branch.length === 2 && item.conditions.length === 1"
                      link
                      type="info"
                      class="mt-2"
                      @click="deleteCondition(index, cIndex)"
                    >
                      <MkIcon name="icon_delete-trash_outlined" />
                    </el-button>
                  </el-col>
                </el-row>
              </template>
            </div>

            <el-button v-if="index !== form_data.branch.length - 1" link type="primary" @click="addCondition(index)">
              <MkIcon name="icon_add_outlined" class="mr-1" />
              添加条件
            </el-button>
          </el-card>
        </div>
      </template>
      <el-button link type="primary" @click="addBranch">
        <MkIcon name="icon_add_outlined" class="mr-1" />
        添加分支
      </el-button>
    </el-form>
  </NodeContainer>
</template>
<script setup lang="ts">
import { cloneDeep, set } from 'lodash'
import { inject, onBeforeUnmount, onMounted, ref, type Directive, type DirectiveBinding, type Ref } from 'vue'
import type { FormInstance } from 'element-plus'
import type { BaseNodeModel } from '@logicflow/core'

import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { handleNodeWheel } from '@/workflow-canvas/core/utils'
import { compareList } from '@/workflow-canvas/config/constants'
import { randomId } from '@/utils/common'

defineOptions({ name: 'WorkflowConditionNode' })
const getModel = inject('getModel') as () => BaseNodeModel
const model = getModel() as BaseNodeModel & { refreshBranch: () => void }

interface ConditionItem {
  field: Array<string>
  compare: string
  value: string
}
interface BranchItem {
  conditions: ConditionItem[]
  id: string
  type: string
  condition: string
}
interface BranchConditionListItem {
  height: number
  id: string
  index: number
}

const defaultForm = () => ({
  branch: [
    {
      conditions: [{ field: [], compare: '', value: '' }],
      id: randomId(),
      type: 'IF',
      condition: 'and',
    },
    {
      conditions: [],
      id: randomId(),
      type: 'ELSE',
      condition: 'and',
    },
  ],
})

if (!model.properties.node_data) {
  set(model.properties, 'node_data', defaultForm())
}
const form_data = model.properties.node_data as { branch: BranchItem[] }

const conditionNodeFormRef = ref<FormInstance>()
const nodeCascaderRef: Ref<Array<{ validate: () => Promise<unknown> }>> = ref([])

function setCascaderRef(el: unknown) {
  if (el && !nodeCascaderRef.value.includes(el as { validate: () => Promise<unknown> })) {
    nodeCascaderRef.value.push(el as { validate: () => Promise<unknown> })
  }
}

const validate = () => {
  const vList = [conditionNodeFormRef.value?.validate(), ...nodeCascaderRef.value.map((item) => item.validate())]
  return Promise.all(vList).catch((err) => {
    return Promise.reject({ node: model, errMessage: err })
  })
}

function addBranch() {
  const list: BranchItem[] = cloneDeep(model.properties.node_data.branch)
  const obj: BranchItem = {
    conditions: [{ field: [], compare: '', value: '' }],
    type: 'ELSE IF ' + (list.length - 1),
    id: randomId(),
    condition: 'and',
  }
  list.splice(list.length - 1, 0, obj)
  refreshBranchAnchor(list, true)
  set(model.properties.node_data, 'branch', list)
}

function refreshBranchAnchor(list: BranchItem[], isAdd: boolean) {
  const branchConditionList = cloneDeep<BranchConditionListItem[]>((model.properties.branch_condition_list as BranchConditionListItem[]) ?? [])
  const newBranchConditionList = list
    .map((item, index) => {
      const find = branchConditionList.find((b) => b.id === item.id)
      if (find) {
        return { index, height: find.height, id: item.id }
      } else {
        if (isAdd) {
          return { index, height: 12, id: item.id }
        }
      }
    })
    .filter((item) => item)
  set(model.properties, 'branch_condition_list', newBranchConditionList)
  model.refreshBranch()
}

function addCondition(index: number) {
  const list = cloneDeep(model.properties.node_data.branch)
  list[index].conditions.push({ field: [], compare: '', value: '' })
  set(model.properties.node_data, 'branch', list)
}

function deleteCondition(index: number, cIndex: number) {
  const list: BranchItem[] = cloneDeep(model.properties.node_data.branch)
  const branch = list[index]
  if (!branch) return
  branch.conditions.splice(cIndex, 1)
  if (branch.conditions.length === 0) {
    const deleteEdge = list.splice(index, 1)
    const deleteTargetAnchorIdList = deleteEdge.map((item) => model.id + '_' + item.id + '_right')
    model.graphModel.eventCenter.emit(
      'delete_edge',
      model.outgoing.edges.filter((item) => item.sourceAnchorId && deleteTargetAnchorIdList.includes(item.sourceAnchorId)).map((item) => item.id),
    )
    refreshBranchAnchor(list, false)
    list.forEach((item, i) => {
      if (item.type === 'ELSE IF ' + (i + 1)) {
        item.type = 'ELSE IF ' + i
      }
    })
  }
  set(model.properties.node_data, 'branch', list)
}

function changeCondition(val: string, index: number, cIndex: number) {
  if (['is_null', 'is_not_null', 'is_true', 'is_not_true'].includes(val)) {
    const list = cloneDeep(model.properties.node_data.branch)
    list[index].conditions[cIndex].value = 1
    set(model.properties.node_data, 'branch', list)
  }
}

const branchCardRefs = new Map<HTMLElement, ResizeObserver>()

const vBranchResize: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding<{ item: BranchItem; index: number }>) {
    const { item, index } = binding.value
    const observer = new ResizeObserver(() => {
      resizeCondition(el, item, index)
    })
    branchCardRefs.set(el, observer)
    observer.observe(el)
  },
  unmounted(el: HTMLElement) {
    branchCardRefs.get(el)?.disconnect()
    branchCardRefs.delete(el)
  },
}

function resizeCondition(container: HTMLElement, row: BranchItem, index: number) {
  const branchConditionList = cloneDeep<BranchConditionListItem[]>((model.properties.branch_condition_list as BranchConditionListItem[]) ?? [])
  const newBranchConditionList = branchConditionList.map((item) => {
    if (item.id === row.id) {
      return { ...item, height: container.offsetHeight, index }
    }
    return item
  })
  set(model.properties, 'branch_condition_list', newBranchConditionList)
  refreshBranchAnchor(model.properties.node_data.branch, true)
}

onMounted(() => {
  set(model, 'validate', validate)
  if (!model.properties.branch_condition_list) {
    refreshBranchAnchor(form_data.branch, true)
  }
})

onBeforeUnmount(() => {
  Array.from(branchCardRefs.values()).forEach((observer: ResizeObserver) => observer.disconnect())
  branchCardRefs.clear()
})
</script>
<style lang="scss" scoped>
.drag-card {
  :deep(.el-card__body) {
    padding: 12px;
  }

  &.drag-card-empty {
    :deep(.el-card__body) {
      display: none;
    }
  }
}
</style>
