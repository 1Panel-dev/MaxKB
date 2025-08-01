<template>
  <NodeContainer :nodeModel="nodeModel">
    <el-form
      :model="form_data"
      label-position="top"
      require-asterisk-position="right"
      label-width="auto"
      ref="ConditionNodeFormRef"
      @submit.prevent
    >
      <VueDraggable
        ref="el"
        v-bind:modelValue="form_data.branch"
        :disabled="form_data.branch === 2"
        handle=".handle"
        :animation="150"
        ghostClass="ghost"
        @end="onEnd"
      >
        <template v-for="(item, index) in form_data.branch" :key="item.id">
          <el-card
            v-resize="(wh: any) => resizeCondition(wh, item, index)"
            shadow="never"
            class="drag-card card-never mb-8"
            :class="{
              'no-drag': index === form_data.branch.length - 1 || form_data.branch.length === 2,
            }"
            style="--el-card-padding: 12px"
          >
            <div class="handle flex-between lighter">
              <span class="flex align-center">
                <img src="@/assets/sort.svg" alt="" height="15" class="handle-img mr-4" />
                {{ item.type }}
              </span>
              <div class="info" v-if="item.conditions.length > 1">
                <span>{{
                  $t('views.applicationWorkflow.nodes.conditionNode.conditions.info')
                }}</span>
                <el-select
                  :teleported="false"
                  v-model="item.condition"
                  size="small"
                  style="width: 60px; margin: 0 8px"
                >
                  <el-option :label="$t('views.applicationWorkflow.condition.AND')" value="and" />
                  <el-option :label="$t('views.applicationWorkflow.condition.OR')" value="or" />
                </el-select>
                <span>{{
                  $t('views.applicationWorkflow.nodes.conditionNode.conditions.label')
                }}</span>
              </div>
            </div>
            <div v-if="index !== form_data.branch.length - 1" class="mt-8">
              <template v-for="(condition, cIndex) in item.conditions" :key="cIndex">
                <el-row :gutter="8">
                  <el-col :span="11">
                    <el-form-item
                      :prop="'branch.' + index + '.conditions.' + cIndex + '.field'"
                      :rules="{
                        type: 'array',
                        required: true,
                        message: $t('views.applicationWorkflow.variable.placeholder'),
                        trigger: 'change',
                      }"
                    >
                      <NodeCascader
                        ref="nodeCascaderRef"
                        :nodeModel="nodeModel"
                        class="w-full"
                        :placeholder="$t('views.applicationWorkflow.variable.placeholder')"
                        v-model="condition.field"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="6">
                    <el-form-item
                      :prop="'branch.' + index + '.conditions.' + cIndex + '.compare'"
                      :rules="{
                        required: true,
                        message: $t(
                          'views.applicationWorkflow.nodes.conditionNode.conditions.requiredMessage',
                        ),
                        trigger: 'change',
                      }"
                    >
                      <el-select
                        @wheel="wheel"
                        :teleported="false"
                        v-model="condition.compare"
                        :placeholder="
                          $t(
                            'views.applicationWorkflow.nodes.conditionNode.conditions.requiredMessage',
                          )
                        "
                        clearable
                        @change="changeCondition($event, index, cIndex)"
                      >
                        <template v-for="(item, index) in compareList" :key="index">
                          <el-option :label="item.label" :value="item.value" />
                        </template>
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="6">
                    <el-form-item
                      v-if="
                        !['is_null', 'is_not_null', 'is_true', 'is_not_true'].includes(
                          condition.compare,
                        )
                      "
                      :prop="'branch.' + index + '.conditions.' + cIndex + '.value'"
                      :rules="{
                        required: true,
                        message: $t('views.applicationWorkflow.nodes.conditionNode.valueMessage'),
                        trigger: 'blur',
                      }"
                    >
                      <el-input
                        v-model="condition.value"
                        :placeholder="
                          $t('views.applicationWorkflow.nodes.conditionNode.valueMessage')
                        "
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="1">
                    <el-button
                      :disabled="index === 0 && cIndex === 0"
                      link
                      type="info"
                      class="mt-4"
                      @click="deleteCondition(index, cIndex)"
                    >
                      <AppIcon iconName="app-delete"></AppIcon>
                    </el-button>
                  </el-col>
                </el-row>
              </template>
            </div>

            <el-button
              link
              type="primary"
              @click="addCondition(index)"
              v-if="index !== form_data.branch.length - 1"
            >
              <el-icon class="mr-4"><Plus /></el-icon>
              {{ $t('views.applicationWorkflow.nodes.conditionNode.addCondition') }}
            </el-button>
          </el-card>
        </template>
      </VueDraggable>
      <el-button link type="primary" @click="addBranch">
        <el-icon class="mr-4"><Plus /></el-icon>
        {{ $t('views.applicationWorkflow.nodes.conditionNode.addBranch') }}
      </el-button>
    </el-form>
  </NodeContainer>
</template>
<script setup lang="ts">
import { cloneDeep, set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted, nextTick } from 'vue'
import { randomId } from '@/utils/common'
import { compareList } from '@/workflow/common/data'
import { VueDraggable } from 'vue-draggable-plus'

const props = defineProps<{ nodeModel: any }>()

const form = {
  branch: [
    {
      conditions: [
        {
          field: [],
          compare: '',
          value: '',
        },
      ],
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
}

const wheel = (e: any) => {
  if (e.ctrlKey === true) {
    e.preventDefault()
    return true
  } else {
    e.stopPropagation()
    return true
  }
}
const resizeCondition = (wh: any, row: any, index: number) => {
  const branch_condition_list = cloneDeep(
    props.nodeModel.properties.branch_condition_list
      ? props.nodeModel.properties.branch_condition_list
      : [],
  )
  const new_branch_condition_list = branch_condition_list.map((item: any) => {
    if (item.id === row.id) {
      return { ...item, height: wh.height, index: index }
    }
    return item
  })
  set(props.nodeModel.properties, 'branch_condition_list', new_branch_condition_list)
  refreshBranchAnchor(props.nodeModel.properties.node_data.branch, true)
}
const form_data = computed({
  get: () => {
    if (props.nodeModel.properties.node_data) {
      return props.nodeModel.properties.node_data
    } else {
      set(props.nodeModel.properties, 'node_data', form)
      refreshBranchAnchor(form.branch, true)
    }
    return props.nodeModel.properties.node_data
  },
  set: (value) => {
    set(props.nodeModel.properties, 'node_data', value)
  },
})

const ConditionNodeFormRef = ref<FormInstance>()
const nodeCascaderRef = ref()
const validate = () => {
  const v_list = [
    ConditionNodeFormRef.value?.validate(),
    ...nodeCascaderRef.value.map((item: any) => item.validate()),
  ]
  return Promise.all(v_list).catch((err) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

function onEnd(event?: any) {
  const { oldIndex, newIndex } = event
  if (oldIndex === undefined || newIndex === undefined) return
  const list = cloneDeep(props.nodeModel.properties.node_data.branch)
  if (oldIndex === list.length - 1 || newIndex === list.length - 1) {
    return
  }
  const newInstance = { ...list[oldIndex], type: list[newIndex].type, id: list[newIndex].id }
  const oldInstance = { ...list[newIndex], type: list[oldIndex].type, id: list[oldIndex].id }
  list[newIndex] = newInstance
  list[oldIndex] = oldInstance
  set(props.nodeModel.properties.node_data, 'branch', list)
}

function addBranch() {
  const list = cloneDeep(props.nodeModel.properties.node_data.branch)
  const obj = {
    conditions: [
      {
        field: [],
        compare: '',
        value: '',
      },
    ],
    type: 'ELSE IF ' + (list.length - 1),
    id: randomId(),
    condition: 'and',
  }
  list.splice(list.length - 1, 0, obj)
  refreshBranchAnchor(list, true)
  set(props.nodeModel.properties.node_data, 'branch', list)
}
function refreshBranchAnchor(list: Array<any>, is_add: boolean) {
  const branch_condition_list = cloneDeep(
    props.nodeModel.properties.branch_condition_list
      ? props.nodeModel.properties.branch_condition_list
      : [],
  )
  const new_branch_condition_list = list
    .map((item, index) => {
      const find = branch_condition_list.find((b: any) => b.id === item.id)
      if (find) {
        return { index: index, height: find.height, id: item.id }
      } else {
        if (is_add) {
          return { index: index, height: 12, id: item.id }
        }
      }
    })
    .filter((item) => item)

  set(props.nodeModel.properties, 'branch_condition_list', new_branch_condition_list)
  props.nodeModel.refreshBranch()
}

function addCondition(index: number) {
  const list = cloneDeep(props.nodeModel.properties.node_data.branch)
  list[index]['conditions'].push({
    field: [],
    compare: '',
    value: '',
  })
  set(props.nodeModel.properties.node_data, 'branch', list)
}

function deleteCondition(index: number, cIndex: number) {
  const list = cloneDeep(props.nodeModel.properties.node_data.branch)
  list[index]['conditions'].splice(cIndex, 1)
  if (list[index]['conditions'].length === 0) {
    const delete_edge = list.splice(index, 1)
    const delete_target_anchor_id_list = delete_edge.map(
      (item: any) => props.nodeModel.id + '_' + item.id + '_right',
    )

    props.nodeModel.graphModel.eventCenter.emit(
      'delete_edge',
      props.nodeModel.outgoing.edges
        .filter((item: any) => delete_target_anchor_id_list.includes(item.sourceAnchorId))
        .map((item: any) => item.id),
    )
    refreshBranchAnchor(list, false)

    list.forEach((item: any, index: number) => {
      if (item.type === 'ELSE IF ' + (index + 1)) {
        item.type = 'ELSE IF ' + index
      }
    })
  }
  set(props.nodeModel.properties.node_data, 'branch', list)
}

function changeCondition(val: string, index: number, cIndex: number) {
  if (['is_null', 'is_not_null', 'is_true', 'is_not_true'].includes(val)) {
    const list = cloneDeep(props.nodeModel.properties.node_data.branch)
    list[index]['conditions'][cIndex].value = 1
    set(props.nodeModel.properties.node_data, 'branch', list)
  }
}

onMounted(() => {
  set(props.nodeModel, 'validate', validate)
})
</script>
<style lang="scss" scoped>
.drag-card.no-drag {
  .handle {
    .handle-img {
      display: none;
    }
  }
}
.drag-card:not(.no-drag) {
  .handle {
    .handle-img {
      display: none;
    }
    &:hover {
      .handle-img {
        display: block;
      }
    }
  }
}
</style>
