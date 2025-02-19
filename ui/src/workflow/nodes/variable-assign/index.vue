<template>
  <NodeContainer :nodeModel="nodeModel">
    <el-form
      @submit.prevent
      :model="form_data"
      label-position="top"
      require-asterisk-position="right"
      label-width="auto"
      ref="replyNodeFormRef"
    >
      <template v-for="(item, index) in form_data.variable_list" :key="item.id">
        <el-card
          shadow="never"
          class="card-never mb-8"
          style="--el-card-padding: 12px"
        >
          <el-form-item
            :label="$t('views.applicationWorkflow.nodes.variableAssignNode.variable.label')"
          >
            <template #label>
              <div class="flex-between">
                <div>
                  {{ $t('views.applicationWorkflow.nodes.variableAssignNode.variable.label') }}
                  <span class="danger">*</span>
                </div>
                <el-button text @click="deleteVariable(index)">
                  <el-icon>
                    <Delete />
                  </el-icon>
                </el-button>
              </div>
            </template>
            <NodeCascader
              ref="nodeCascaderRef"
              :nodeModel="nodeModel"
              class="w-full"
              :placeholder="
              $t('views.applicationWorkflow.nodes.variableAssignNode.variable.requiredMessage')
            "
              v-model="item.fields"
            />
          </el-form-item>
          <el-form-item>
            <template #label>
              <div class="flex-between">
                <div>
                  <span
                  >{{ $t('views.applicationWorkflow.nodes.variableAssignNode.value.label')
                    }}<span class="danger">*</span></span
                  >
                </div>
                <el-select v-model="item.source" type="small" style="width: 100px">
                  <el-option
                    :label="$t('views.applicationWorkflow.nodes.variableAssignNode.source.reference')"
                    value="reference"
                  />
                  <el-option
                    :label="$t('views.applicationWorkflow.nodes.variableAssignNode.source.custom')"
                    value="custom"
                  />
                </el-select>
              </div>
            </template>
            <div v-if="item.source === 'custom'">
              <el-select v-model="item.type">
                <el-option v-for="item in typeOptions" :key="item" :label="item" :value="item" />
              </el-select>
              <el-input
                v-model="item.value"
                placeholder="请输入"
                show-word-limit
                clearable
                @wheel="wheel"
              ></el-input>
            </div>
            <div v-else>
              <NodeCascader
                ref="nodeCascaderRef2"
                :nodeModel="nodeModel"
                class="w-full"
                :placeholder="
              $t('views.applicationWorkflow.nodes.variableAssignNode.variable.requiredMessage')
            "
                v-model="item.reference"
              />
            </div>
          </el-form-item>
        </el-card>
      </template>
      <el-button link type="primary" @click="addVariable">
        <el-icon class="mr-4">
          <Plus />
        </el-icon>
        {{ $t('views.applicationWorkflow.nodes.variableAssignNode.addVariable') }}
      </el-button>
    </el-form>
  </NodeContainer>
</template>
<script setup lang="ts">
import { cloneDeep, set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import { computed, onMounted, ref } from 'vue'
import { isLastNode } from '@/workflow/common/data'
import { randomId } from '@/utils/utils'


const props = defineProps<{ nodeModel: any }>()

const typeOptions = ['string', 'int', 'dict', 'array', 'float']

const wheel = (e: any) => {
  if (e.ctrlKey === true) {
    e.preventDefault()
    return true
  } else {
    e.stopPropagation()
    return true
  }
}
const form = {
  variable_list: [
    { id: randomId(), fields: [], value: null, reference: [], type: 'string', source: 'custom' }
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

function submitDialog(val: string) {
  set(props.nodeModel.properties.node_data, 'content', val)
}

const replyNodeFormRef = ref()
const nodeCascaderRef = ref()
const validate = async () => {
  return Promise.all([
    replyNodeFormRef.value?.validate()
  ]).catch((err: any) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}


function addVariable() {
  const list = cloneDeep(props.nodeModel.properties.node_data.variable_list)
  const obj = {
    id: randomId(),
    fields: [],
    value: null,
    reference: [],
    type: 'string',
    source: 'custom'
  }
  list.push(obj)
  console.log(list)
  set(props.nodeModel.properties.node_data, 'variable_list', list)
}

function deleteVariable(index: number) {
  const list = cloneDeep(props.nodeModel.properties.node_data.variable_list)
  list.splice(index, 1)
  set(props.nodeModel.properties.node_data, 'variable_list', list)
}

onMounted(() => {
  if (typeof props.nodeModel.properties.node_data?.is_result === 'undefined') {
    if (isLastNode(props.nodeModel)) {
      set(props.nodeModel.properties.node_data, 'is_result', true)
    }
  }

  set(props.nodeModel, 'validate', validate)
})
</script>
<style lang="scss" scoped></style>
