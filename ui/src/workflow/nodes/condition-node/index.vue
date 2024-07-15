<template>
  <NodeContainer :nodeModel="nodeModel">
    <el-form
      :model="form_data"
      label-position="top"
      require-asterisk-position="right"
      label-width="auto"
      ref="ConditionNodeFormRef"
      @keydown.stop
      @submit.prevent
      @click.stop
      @mousedown.stop
      @mousemove.stop
    >
      <template v-for="(item, index) in form_data.branch" :key="item.id">
        <el-card
          v-resize="(wh: any) => resizeCondition(wh, item, index)"
          shadow="never"
          class="card-never mb-8"
          style="--el-card-padding: 12px"
        >
          <div class="flex-between lighter">
            {{ item.type }}
            <div class="info" v-if="item.conditions.length > 1">
              <span>符合以下</span>
              <el-select
                :teleported="false"
                v-model="item.condition"
                size="small"
                style="width: 60px; margin: 0 8px"
              >
                <el-option label="所有" value="and" />
                <el-option label="任一" value="or" />
              </el-select>
              <span>条件</span>
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
                      message: '请选择变量',
                      trigger: 'change'
                    }"
                  >
                    <NodeCascader
                      ref="nodeCascaderRef"
                      :nodeModel="nodeModel"
                      class="w-full"
                      placeholder="请选择变量"
                      v-model="condition.field"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-form-item
                    :prop="'branch.' + index + '.conditions.' + cIndex + '.compare'"
                    :rules="{
                      required: true,
                      message: '请选择条件',
                      trigger: 'change'
                    }"
                  >
                    <el-select
                      @wheel="wheel"
                      @keydown="isKeyDown = true"
                      @keyup="isKeyDown = false"
                      :teleported="false"
                      v-model="condition.compare"
                      placeholder="请选择条件"
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
                    v-if="condition.compare !== 'is_null' && condition.compare !== 'is_not_null'"
                    :prop="'branch.' + index + '.conditions.' + cIndex + '.value'"
                    :rules="{
                      required: true,
                      message: '请输入值',
                      trigger: 'blur'
                    }"
                  >
                    <el-input v-model="condition.value" placeholder="请输入值" />
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
                    <el-icon><Delete /></el-icon>
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
            <el-icon class="mr-4"><Plus /></el-icon> 添加条件
          </el-button>
        </el-card>
      </template>
      <el-button link type="primary" @click="addBranch">
        <el-icon class="mr-4"><Plus /></el-icon> 添加分支
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
import { randomId } from '@/utils/utils'
import { compareList } from '@/workflow/common/data'

const props = defineProps<{ nodeModel: any }>()
const form = {
  branch: [
    {
      conditions: [
        {
          field: [],
          compare: '',
          value: ''
        }
      ],
      id: randomId(),
      type: 'IF',
      condition: 'and'
    },
    {
      conditions: [],
      id: randomId(),
      type: 'ELSE',
      condition: 'and'
    }
  ]
}
const isKeyDown = ref(false)
const wheel = (e: any) => {
  if (isKeyDown.value) {
    e.preventDefault()
  } else {
    e.stopPropagation()
    return true
  }
}

const resizeCondition = (wh: any, row: any, index: number) => {
  const branch_condition_list = cloneDeep(
    props.nodeModel.properties.branch_condition_list
      ? props.nodeModel.properties.branch_condition_list
      : []
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
  }
})

const ConditionNodeFormRef = ref<FormInstance>()
const nodeCascaderRef = ref()
const validate = () => {
  const v_list = [
    ConditionNodeFormRef.value?.validate(),
    ...nodeCascaderRef.value.map((item: any) => item.validate())
  ]
  return Promise.all(v_list).catch((err) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

function addBranch() {
  const list = cloneDeep(props.nodeModel.properties.node_data.branch)
  const obj = {
    conditions: [
      {
        field: [],
        compare: '',
        value: ''
      }
    ],
    type: 'ELSE IF ' + (list.length - 1),
    id: randomId(),
    condition: 'and'
  }
  list.splice(list.length - 1, 0, obj)
  refreshBranchAnchor(list, true)
  set(props.nodeModel.properties.node_data, 'branch', list)
}
function refreshBranchAnchor(list: Array<any>, is_add: boolean) {
  const branch_condition_list = cloneDeep(
    props.nodeModel.properties.branch_condition_list
      ? props.nodeModel.properties.branch_condition_list
      : []
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
    value: ''
  })
  set(props.nodeModel.properties.node_data, 'branch', list)
}

function deleteCondition(index: number, cIndex: number) {
  const list = cloneDeep(props.nodeModel.properties.node_data.branch)
  list[index]['conditions'].splice(cIndex, 1)
  if (list[index]['conditions'].length === 0) {
    const delete_edge = list.splice(index, 1)
    const delete_target_anchor_id_list = delete_edge.map(
      (item: any) => props.nodeModel.id + '_' + item.id + '_right'
    )

    props.nodeModel.graphModel.eventCenter.emit(
      'delete_edge',
      props.nodeModel.outgoing.edges
        .filter((item: any) => delete_target_anchor_id_list.includes(item.sourceAnchorId))
        .map((item: any) => item.id)
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
  if (val === 'is_null' || val === 'is_not_null') {
    const list = cloneDeep(props.nodeModel.properties.node_data.branch)
    list[index]['conditions'][cIndex].value = 1
    set(props.nodeModel.properties.node_data, 'branch', list)
  }
}

onMounted(() => {
  set(props.nodeModel, 'validate', validate)
})
</script>
<style lang="scss" scoped></style>
