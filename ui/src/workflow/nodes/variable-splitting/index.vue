<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">{{ $t('views.applicationWorkflow.nodeSetting') }}</h5>
    <el-card shadow="never" class="card-never" style="--el-card-padding: 12px">
      <el-form
        @submit.prevent
        :model="form_data"
        label-position="top"
        require-asterisk-position="right"
        label-width="auto"
        ref="VariableSplittingRef"
        hide-required-asterisk
      >
        <el-form-item
          prop="input_variable"
          :rules="{
            message: $t('views.applicationWorkflow.variable.placeholder'),
            trigger: 'blur',
            required: true,
          }"
        >
          <template #label>
            <div class="flex-between">
              <div>
                {{ $t('views.applicationWorkflow.nodes.variableSplittingNode.inputVariables') }}
                <span class="color-danger">*</span>
              </div>
            </div>
          </template>
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            :placeholder="$t('views.applicationWorkflow.variable.placeholder')"
            v-model="form_data.input_variable"
          />
        </el-form-item>

        <el-form-item
          prop="variable_list"
          :rules="{
            message: $t(
              'views.applicationWorkflow.nodes.variableSplittingNode.variableListPlaceholder',
            ),
            trigger: 'blur',
            required: true,
          }"
        >
          <VariableFieldTable
            ref="VariableFieldTableRef"
            :node-model="nodeModel"
          ></VariableFieldTable>
        </el-form-item>
      </el-form>
    </el-card>
  </NodeContainer>
</template>
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import VariableFieldTable from '@/workflow/nodes/variable-splitting/component/VariableFieldTable.vue'
import { set } from 'lodash'
const props = defineProps<{ nodeModel: any }>()

const form = {
  input_variable: [],
  variable_list: [],
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
const VariableSplittingRef = ref()
const validate = async () => {
  return VariableSplittingRef.value.validate().catch((err: any) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}
onMounted(() => {
  set(props.nodeModel, 'validate', validate)
})
</script>
<style lang="scss" scoped></style>
