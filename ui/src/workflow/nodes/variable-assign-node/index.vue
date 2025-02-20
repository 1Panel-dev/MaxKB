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
        <el-card shadow="never" class="card-never mb-8" style="--el-card-padding: 12px">
          <el-form-item :label="$t('views.applicationWorkflow.variable.label')">
            <template #label>
              <div class="flex-between">
                <div>
                  {{ $t('views.applicationWorkflow.variable.label') }}
                  <span class="danger">*</span>
                </div>
                <el-button text @click="deleteVariable(index)" v-if="index !== 0">
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
              :placeholder="$t('views.applicationWorkflow.variable.placeholder')"
              v-model="item.fields"
              :global="true"
              @change="variableChange(item)"
            />
          </el-form-item>
          <el-form-item>
            <template #label>
              <div class="flex-between">
                <div>
                  <span
                  >{{ $t('views.applicationWorkflow.nodes.variableAssignNode.assign')
                    }}<span class="danger">*</span></span
                  >
                </div>
                <el-select
                  :teleported="false"
                  v-model="item.source"
                  size="small"
                  style="width: 85px"
                >
                  <el-option
                    :label="$t('views.applicationWorkflow.nodes.replyNode.replyContent.reference')"
                    value="referencing"
                  />
                  <el-option
                    :label="$t('views.applicationWorkflow.nodes.replyNode.replyContent.custom')"
                    value="custom"
                  />
                </el-select>
              </div>
            </template>
            <div v-if="item.source === 'custom'" class="flex">
              <el-select v-model="item.type" style="width: 130px;">
                <el-option v-for="item in typeOptions" :key="item" :label="item" :value="item" />
              </el-select>
              <el-input
                class="ml-4"
                v-model="item.value"
                :placeholder="$t('common.inputPlaceholder')"
                show-word-limit
                clearable
                @wheel="wheel"
              ></el-input>
            </div>

            <NodeCascader
              v-else
              ref="nodeCascaderRef2"
              :nodeModel="nodeModel"
              class="w-full"
              :placeholder="$t('views.applicationWorkflow.variable.placeholder')"
              v-model="item.reference"
            />
          </el-form-item>
        </el-card>
      </template>
      <el-button link type="primary" @click="addVariable">
        <el-icon class="mr-4">
          <Plus />
        </el-icon>
        {{ $t('common.add') }}
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
    {
      id: randomId(),
      fields: [],
      value: null,
      reference: [],
      type: 'string',
      source: 'custom',
      name: ''
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

function submitDialog(val: string) {
  set(props.nodeModel.properties.node_data, 'content', val)
}

const replyNodeFormRef = ref()
const nodeCascaderRef = ref()
const validate = async () => {
  return Promise.all([replyNodeFormRef.value?.validate()]).catch((err: any) => {
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
    source: 'custom',
    name: ''
  }
  list.push(obj)
  set(props.nodeModel.properties.node_data, 'variable_list', list)
}

function deleteVariable(index: number) {
  const list = cloneDeep(props.nodeModel.properties.node_data.variable_list)
  list.splice(index, 1)
  set(props.nodeModel.properties.node_data, 'variable_list', list)
}

function variableChange(item: any) {
  props.nodeModel.graphModel.nodes.map((node: any) => {
    if (node.id === 'start-node') {
      node.properties.config.globalFields.forEach((field: any) => {
        if (field.value === item.fields[1]) {
          item.name = field.label
        }
      })
    }
  })
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
