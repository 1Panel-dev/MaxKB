<script setup lang="ts">
import { cloneDeep } from 'lodash'
import { computed, inject, onBeforeUnmount, onMounted, useTemplateRef, type Directive } from 'vue'
import type { FormInstance } from 'element-plus'
import type { BaseNodeModel } from '@logicflow/core'

import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { createAnchorGuard, handleNodeWheel } from '@/workflow-canvas/core/utils'
import { compareList } from '@/workflow-canvas/config/constants'
import { randomId } from '@/utils/common'

defineOptions({ name: 'WorkflowConditionNode' })
const getModel = inject('getModel') as () => BaseNodeModel
const model = getModel() as BaseNodeModel & { refreshBranch: () => void }

interface ConditionItem {
  field: string[]
  compare: string
  value: string | number
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

// 表单初始化与条件校验。
const valueLessComparisons = new Set(['is_null', 'is_not_null', 'is_true', 'is_not_true'])
const createCondition = (): ConditionItem => ({ field: [], compare: '', value: '' })

if (!model.properties.node_data) {
  model.properties.node_data = {
    branch: [
      { conditions: [createCondition()], id: randomId(), type: 'IF', condition: 'and' },
      { conditions: [], id: randomId(), type: 'ELSE', condition: 'and' },
    ],
  }
}
const formData = computed(() => model.properties.node_data as { branch: BranchItem[] })
const conditionNodeFormRef = useTemplateRef<FormInstance>('conditionNodeFormRef')
const nodeCascaderRefs = useTemplateRef<InstanceType<typeof NodeCascader>[]>('nodeCascaderRefs')

function validate() {
  return Promise.all([conditionNodeFormRef.value?.validate(), ...(nodeCascaderRefs.value ?? []).map((cascader) => cascader.validate())]).catch(
    (error) => Promise.reject({ node: model, errMessage: error }),
  )
}

// 分支增删保留原有锚点 ID，删除空分支时同步清理连线。
function addBranch() {
  const branches = cloneDeep(formData.value.branch)
  branches.splice(branches.length - 1, 0, {
    conditions: [createCondition()],
    type: `ELSE IF ${branches.length - 1}`,
    id: randomId(),
    condition: 'and',
  })
  formData.value.branch = branches
  refreshBranchAnchors()
}

function addCondition(branch: BranchItem) {
  branch.conditions.push(createCondition())
}

function deleteCondition(branchIndex: number, conditionIndex: number) {
  const branches = cloneDeep(formData.value.branch)
  const branch = branches[branchIndex]
  if (!branch || (branches.length === 2 && branch.conditions.length === 1)) return

  branch.conditions.splice(conditionIndex, 1)
  if (branch.conditions.length === 0) {
    branches.splice(branchIndex, 1)
    const anchorId = `${model.id}_${branch.id}_right`
    const edgeIds = model.outgoing.edges.filter((edge) => edge.sourceAnchorId === anchorId).map((edge) => edge.id)
    model.graphModel.eventCenter.emit('delete_edge', edgeIds)
    branches.forEach((remainingBranch, index) => {
      if (remainingBranch.type === `ELSE IF ${index + 1}`) {
        remainingBranch.type = `ELSE IF ${index}`
      }
    })
  }
  formData.value.branch = branches
  refreshBranchAnchors()
}

function changeComparison(condition: ConditionItem) {
  // 无比较值的运算仍按现有节点协议写入占位值。
  if (valueLessComparisons.has(condition.compare)) condition.value = 1
}

// 根据卡片实际高度刷新分支锚点；通过 ID 查找当前顺序，避免删除后沿用旧索引。
function refreshBranchAnchors(branchId?: string, height?: number) {
  const previousBranches = (model.properties.branch_condition_list as BranchConditionListItem[] | undefined) ?? []
  model.properties.branch_condition_list = formData.value.branch.map((branch, index) => ({
    id: branch.id,
    index,
    height: branch.id === branchId && height !== undefined ? height : (previousBranches.find((previous) => previous.id === branch.id)?.height ?? 12),
  }))
  model.refreshBranch()
}

const branchObservers = new Map<HTMLElement, ResizeObserver>()
const vBranchResize: Directive<HTMLElement, string> = {
  mounted(element, { value: branchId }) {
    const observer = new ResizeObserver(() => {
      // 折叠时保留展开高度，避免隐藏卡片把锚点高度覆盖为 0。
      if (element.offsetHeight > 0) refreshBranchAnchors(branchId, element.offsetHeight)
    })
    branchObservers.set(element, observer)
    observer.observe(element)
  },
  unmounted(element) {
    branchObservers.get(element)?.disconnect()
    branchObservers.delete(element)
  },
}

const anchorGuard = createAnchorGuard(model)
onMounted(() => {
  model.validate = validate
  refreshBranchAnchors()
})
onBeforeUnmount(() => {
  branchObservers.forEach((observer) => observer.disconnect())
  branchObservers.clear()
  anchorGuard.reset()
})
</script>

<template>
  <NodeContainer :node-model="model">
    <el-form ref="conditionNodeFormRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
      <div v-for="(branch, branchIndex) in formData.branch" :key="branch.id" v-branch-resize="branch.id" class="mk-gray-card mb-2">
        <div class="flex-between min-h-6">
          <span>{{ branch.type }}</span>
          <div v-if="branch.conditions.length > 1" class="flex items-center gap-2 text-N600">
            <span>符合以下</span>
            <el-select
              v-model="branch.condition"
              :teleported="false"
              size="small"
              class="w-15!"
              @visible-change="anchorGuard.setOverlayVisible(`${branch.id}:condition`, $event)"
              @wheel="handleNodeWheel"
            >
              <el-option label="所有" value="and" />
              <el-option label="任一" value="or" />
            </el-select>
            <span>条件</span>
          </div>
        </div>

        <template v-if="branchIndex !== formData.branch.length - 1">
          <div class="mt-2 space-y-2">
            <div v-for="(condition, conditionIndex) in branch.conditions" :key="conditionIndex" class="flex items-start gap-2">
              <el-form-item
                class="mb-0! min-w-0 flex-2"
                :prop="`branch.${branchIndex}.conditions.${conditionIndex}.field`"
                :rules="{ type: 'array', required: true, message: '请选择变量', trigger: 'change' }"
              >
                <NodeCascader ref="nodeCascaderRefs" v-model="condition.field" :node-model="model" class="w-full" placeholder="请选择变量" />
              </el-form-item>
              <el-form-item
                class="mb-0! min-w-0 flex-1"
                :prop="`branch.${branchIndex}.conditions.${conditionIndex}.compare`"
                :rules="{ required: true, message: '请选择比较符', trigger: 'change' }"
              >
                <el-select
                  v-model="condition.compare"
                  :teleported="false"
                  placeholder="请选择比较符"
                  clearable
                  @change="changeComparison(condition)"
                  @visible-change="anchorGuard.setOverlayVisible(`${branch.id}:${conditionIndex}:compare`, $event)"
                  @wheel="handleNodeWheel"
                >
                  <el-option v-for="comparison in compareList" :key="comparison.value" :label="comparison.label" :value="comparison.value" />
                </el-select>
              </el-form-item>
              <div class="min-w-0 flex-1">
                <el-form-item
                  v-if="!valueLessComparisons.has(condition.compare)"
                  class="mb-0!"
                  :prop="`branch.${branchIndex}.conditions.${conditionIndex}.value`"
                  :rules="{ required: true, message: '请输入比较值', trigger: 'blur' }"
                >
                  <el-input v-model="condition.value" placeholder="请输入比较值" />
                </el-form-item>
              </div>
              <el-button
                :disabled="formData.branch.length === 2 && branch.conditions.length === 1"
                link
                type="info"
                class="mt-2 shrink-0"
                aria-label="删除条件"
                @click="deleteCondition(branchIndex, conditionIndex)"
              >
                <MkIcon name="icon_delete-trash_outlined" />
              </el-button>
            </div>
          </div>
          <el-button class="mt-2" link type="primary" @click="addCondition(branch)">
            <MkIcon name="icon_add_outlined" class="mr-1" />
            添加条件
          </el-button>
        </template>
      </div>
      <el-button link type="primary" @click="addBranch">
        <MkIcon name="icon_add_outlined" class="mr-1" />
        添加分支
      </el-button>
    </el-form>
  </NodeContainer>
</template>
