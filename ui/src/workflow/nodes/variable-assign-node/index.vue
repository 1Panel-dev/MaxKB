<template>
  <NodeContainer :nodeModel="nodeModel">
    <el-form
      @submit.prevent
      :model="form_data"
      label-position="top"
      require-asterisk-position="right"
      label-width="auto"
      ref="replyNodeFormRef"
      hide-required-asterisk
    >
      <template v-for="(item, index) in form_data.variable_list" :key="item.id">
        <el-card shadow="never" class="card-never mb-8" style="--el-card-padding: 12px">
          <el-form-item :label="$t('views.applicationWorkflow.variable.label')">
            <template #label>
              <div class="flex-between">
                <div>
                  {{ $t('views.applicationWorkflow.variable.label') }}
                  <span class="color-danger">*</span>
                </div>
                <el-button
                  text
                  @click="deleteVariable(index)"
                  v-if="form_data.variable_list.length > 1"
                >
                  <AppIcon iconName="app-delete"></AppIcon>
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
          <div class="flex-between mb-8">
            <span class="lighter"
              >{{ $t('views.applicationWorkflow.nodes.variableAssignNode.assign')
              }}<span class="color-danger">*</span></span
            >
            <el-select :teleported="false" v-model="item.source" size="small" style="width: 85px">
              <el-option
                :label="$t('views.applicationWorkflow.nodes.replyNode.replyContent.reference')"
                value="referencing"
              />
              <el-option :label="$t('common.custom')" value="custom" />
            </el-select>
          </div>

          <div v-if="item.source === 'custom'" class="flex w-full">
            <el-select
              v-model="item.type"
              style="max-width: 85px"
              class="mr-8"
              @change="
                (val: string) => {
                  if (val === 'bool') {
                    form_data.variable_list[index].value = true
                  } else {
                    form_data.variable_list[index].value = null
                  }
                }
              "
            >
              <el-option v-for="item in typeOptions" :key="item" :label="item" :value="item" />
            </el-select>

            <el-form-item
              v-if="item.type === 'string'"
              :prop="'variable_list.' + index + '.value'"
              :rules="{
                message: t('common.inputPlaceholder'),
                trigger: 'blur',
                required: true,
              }"
            >
              <el-input
                v-model="item.value"
                :placeholder="$t('common.inputPlaceholder')"
                show-word-limit
                clearable
                @wheel="wheel"
              ></el-input>
            </el-form-item>
            <el-form-item
              v-else-if="item.type === 'num'"
              :prop="'variable_list.' + index + '.value'"
              :rules="{
                message: $t('common.inputPlaceholder'),
                trigger: 'blur',
                required: true,
              }"
            >
              <el-input-number v-model="item.value"></el-input-number>
            </el-form-item>
            <el-form-item
              class="w-full"
              v-else-if="item.type === 'json'"
              :prop="'variable_list.' + index + '.value'"
              :rules="[
                {
                  message: $t('common.inputPlaceholder'),
                  trigger: 'blur',
                  required: true,
                },
                {
                  validator: (rule: any, value: any, callback: any) => {
                    try {
                      JSON.parse(value)
                      callback() // Valid JSON
                    } catch (e) {
                      callback(new Error('Invalid JSON format'))
                    }
                  },
                  trigger: 'blur',
                },
              ]"
            >
              <CodemirrorEditor
                title="JSON"
                v-model="item.value"
                :style="{
                  height: '100px',
                  width: '155px',
                }"
                @submitDialog="(val: string) => (form_data.variable_list[index].value = val)"
              />
            </el-form-item>
            <el-form-item
              v-else-if="item.type === 'bool'"
              :prop="'variable_list.' + index + '.value'"
              :rules="{
                message: $t('common.inputPlaceholder'),
                trigger: 'blur',
                required: true,
              }"
            >
              <el-select v-model="item.value" style="width: 155px">
                <el-option label="true" :value="true" />
                <el-option label="false" :value="false" />
              </el-select>
            </el-form-item>
          </div>
          <el-form-item v-else>
            <NodeCascader
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
        <AppIcon iconName="app-add-outlined" class="mr-4"></AppIcon>
        {{ $t('common.add') }}
      </el-button>
    </el-form>
  </NodeContainer>
</template>
<script setup lang="ts">
import { cloneDeep, set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import { computed, nextTick, onMounted, ref, inject } from 'vue'
import { isLastNode } from '@/workflow/common/data'
import { randomId } from '@/utils/common'
import { t } from '@/locales'
import { WorkflowMode } from '@/enums/application'
const workflowMode = inject('workflowMode') as WorkflowMode
const props = defineProps<{ nodeModel: any }>()

const typeOptions = ['string', 'num', 'json', 'bool']

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
      name: '',
    },
  ],
}
const boolValue = ref(1)

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

function submitDialog(val: string) {
  set(props.nodeModel.properties.node_data, 'content', val)
}

const replyNodeFormRef = ref()
const nodeCascaderRef = ref()
const nodeCascaderRef2 = ref()

const validate = async () => {
  // console.log(replyNodeFormRef.value.validate())
  let ps = [
    replyNodeFormRef.value?.validate(),
    ...nodeCascaderRef.value.map((item: any) => item.validate()),
  ]
  if (nodeCascaderRef2.value) {
    ps = [...ps, ...nodeCascaderRef.value.map((item: any) => item.validate())]
  }
  return Promise.all(ps).catch((err: any) => {
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
    name: '',
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
  ;(workflowMode == WorkflowMode.ApplicationLoop
    ? [...props.nodeModel.graphModel.nodes, ...props.nodeModel.graphModel.get_parent_nodes()]
    : props.nodeModel.graphModel.nodes
  ).map((node: any) => {
    if (node.id === 'start-node') {
      node.properties.config.globalFields.forEach((field: any) => {
        if (field.value === item.fields[1]) {
          item.name = field.label
        }
      })
      node.properties.config.chatFields.forEach((field: any) => {
        if (field.value === item.fields[1]) {
          item.name = field.label
        }
      })
    }
    if (node.id === 'loop-start-node') {
      node.properties.loop_input_field_list.forEach((field: any) => {
        if (field.field === item.fields[1]) {
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
