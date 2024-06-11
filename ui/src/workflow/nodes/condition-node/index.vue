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
    >
      <template v-for="(item, index) in form_data.branch" :key="index">
        <el-card shadow="never" class="card-never mb-8" style="--el-card-padding: 12px">
          <p class="lighter">{{ judgeLabel(index) }}</p>
          <div v-if="index !== form_data.branch.length - 1" class="mt-8">
            <template v-for="(condition, cIndex) in item.conditions" :key="cIndex">
              <el-row :gutter="8">
                <el-col :span="11">
                  <el-form-item
                    :prop="'branch.' + index + '.conditions' + cIndex + '.field'"
                    :rules="{
                      type: Array,
                      required: true,
                      message: '请选择变量',
                      trigger: 'change'
                    }"
                  >
                    <NodeCascader
                      :nodeModel="nodeModel"
                      class="w-full"
                      placeholder="请选择变量"
                      v-model="condition.field"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-form-item
                    :prop="'branch.' + index + '.conditions' + cIndex + '.compare'"
                    :rules="{
                      required: true,
                      message: '请选择条件',
                      trigger: 'change'
                    }"
                  >
                    <el-select v-model="condition.compare" placeholder="请选择条件" clearable>
                      <el-option label="Zone one" value="shanghai" />
                      <el-option label="Zone two" value="beijing" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-form-item
                    :prop="'branch.' + index + '.conditions' + cIndex + '.value'"
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
                  <el-button link type="info" class="mt-4" @click="deleteCondition(index, cIndex)">
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
import { ref, computed, onMounted } from 'vue'
import { randomId } from '@/utils/utils'
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
      condition: 'and'
    },
    {
      conditions: [],
      id: randomId(),
      condition: 'and'
    }
  ]
}

const form_data = computed({
  get: () => {
    if (props.nodeModel.properties.node_data) {
      return props.nodeModel.properties.node_data
    } else {
      set(props.nodeModel.properties, 'node_data', form)
    }
    return props.nodeModel.properties.node_data
  },
  set: (value) => {
    set(props.nodeModel.properties, 'node_data', value)
  }
})

const ConditionNodeFormRef = ref<FormInstance>()

const validate = () => {
  ConditionNodeFormRef.value?.validate()
}

const judgeLabel = (index: number) => {
  if (index === 0) {
    return 'IF'
  } else if (index === form_data.value.branch.length - 1) {
    return 'ELSE'
  } else {
    return 'ELSE IF ' + index
  }
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
    id: randomId(),
    condition: 'and'
  }
  list.splice(list.length - 1, 0, obj)
  props.nodeModel.addField({ key: obj.id })
  set(props.nodeModel.properties.node_data, 'branch', list)
}

function addCondition(index: number) {
  const list = cloneDeep(props.nodeModel.properties.node_data.branch)
  list[index]['conditions'].push({
    field: { node_id: 'xxx', fields: '' },
    compare: '',
    value: ''
  })
  set(props.nodeModel.properties.node_data, 'branch', list)
}

function deleteCondition(index: number, cIndex: number) {
  const list = cloneDeep(props.nodeModel.properties.node_data.branch)
  list[index]['conditions'].splice(cIndex, 1)
  if (list[index]['conditions'].length === 0) {
    list.splice(index, 1)
  }
  set(props.nodeModel.properties.node_data, 'branch', list)
}

onMounted(() => {
  set(props.nodeModel, 'validate', validate)
})
</script>
<style lang="scss" scoped></style>
