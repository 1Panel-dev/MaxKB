<template>
  <NodeContainer :nodeModel="nodeModel">
    <el-card shadow="never" class="card-never" style="--el-card-padding: 12px">
      <el-form
        :model="form_data"
        label-position="top"
        require-asterisk-position="right"
        label-width="auto"
        ref="ContinueFromRef"
        @submit.prevent
      >
        <div class="handle flex-between lighter mb-8">
          <div class="info" v-if="form_data.condition_list.length > 1">
            <span>{{ $t('views.applicationWorkflow.nodes.conditionNode.conditions.info') }}</span>
            <el-select
              :teleported="false"
              v-model="form_data.condition"
              size="small"
              style="width: 60px; margin: 0 8px"
            >
              <el-option :label="$t('views.applicationWorkflow.condition.AND')" value="and" />
              <el-option :label="$t('views.applicationWorkflow.condition.OR')" value="or" />
            </el-select>
            <span>{{ $t('views.applicationWorkflow.nodes.conditionNode.conditions.label') }}</span>
          </div>
        </div>
        <template v-for="(condition, index) in form_data.condition_list" :key="index">
          <el-row :gutter="8">
            <el-col :span="11">
              <el-form-item
                :prop="'condition_list.' + index + '.field'"
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
                :prop="'condition_list.' + index + '.compare'"
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
                    $t('views.applicationWorkflow.nodes.conditionNode.conditions.requiredMessage')
                  "
                  clearable
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
                  !['is_null', 'is_not_null', 'is_true', 'is_not_true'].includes(condition.compare)
                "
                :prop="'condition_list.' + index + '.value'"
                :rules="{
                  required: true,
                  message: $t('views.applicationWorkflow.nodes.conditionNode.valueMessage'),
                  trigger: 'blur',
                }"
              >
                <el-input
                  v-model="condition.value"
                  :placeholder="$t('views.applicationWorkflow.nodes.conditionNode.valueMessage')"
                />
              </el-form-item>
            </el-col>
            <el-col :span="1">
              <el-button link type="info" class="mt-4" @click="deleteCondition(index)">
                <AppIcon iconName="app-delete"></AppIcon>
              </el-button>
            </el-col>
          </el-row>
        </template>
      </el-form>

      <el-button link type="primary" @click="addCondition()">
        <AppIcon iconName="app-add-outlined" class="mr-4"></AppIcon>
        {{ $t('views.applicationWorkflow.nodes.conditionNode.addCondition') }}
      </el-button>
    </el-card>
  </NodeContainer>
</template>

<script setup lang="ts">
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import { computed, ref, onMounted } from 'vue'
import { set, cloneDeep } from 'lodash'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import { compareList } from '@/workflow/common/data'
import type { FormInstance } from 'element-plus'
const props = defineProps<{ nodeModel: any }>()

const form = {
  condition_list: [],
  condition: 'and',
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
  },
})
const addCondition = () => {
  const condition_list = cloneDeep(form_data.value?.condition_list || [])
  condition_list.push({
    field: [],
    compare: '',
    value: '',
  })
  set(props.nodeModel.properties.node_data, 'condition_list', condition_list)
}
const deleteCondition = (index: number) => {
  const condition_list = cloneDeep(form_data.value?.condition_list || [])
  condition_list.splice(index, 1)
  set(props.nodeModel.properties.node_data, 'condition_list', condition_list)
}
const ContinueFromRef = ref<FormInstance>()
const validate = () => {
  const v_list = [ContinueFromRef.value?.validate()]
  return Promise.all(v_list).catch((err) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}
onMounted(() => {
  set(props.nodeModel, 'validate', validate)
})
</script>

<style lang="scss" scoped></style>
