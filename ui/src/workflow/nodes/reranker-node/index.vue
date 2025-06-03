<template>
  <NodeContainer :nodeModel="nodeModel">
    <el-card shadow="never" class="card-never" style="--el-card-padding: 12px">
      <el-form
        @submit.prevent
        :model="form_data"
        label-position="top"
        require-asterisk-position="right"
        label-width="auto"
        ref="rerankerNodeFormRef"
        hide-required-asterisk
      >
        <el-form-item
          :label="$t('views.applicationWorkflow.nodes.rerankerNode.rerankerContent.label')"
          prop="reranker_reference_list"
          :rules="{
            type: 'array',
            message: $t(
              'views.applicationWorkflow.nodes.rerankerNode.rerankerContent.requiredMessage'
            ),
            trigger: 'change',
            required: true
          }"
        >
          <template #label>
            <div class="flex-between">
              <span
                >{{ $t('views.applicationWorkflow.nodes.rerankerNode.rerankerContent.label')
                }}<span class="danger">*</span></span
              >
              <el-button @click="add_reranker_reference" link type="primary">
                <el-icon class="mr-4"><Plus /></el-icon>
              </el-button>
            </div>
          </template>
          <el-row
            :gutter="8"
            style="margin-bottom: 8px"
            v-for="(reranker_reference, index) in form_data.reranker_reference_list"
            :key="index"
          >
            <el-col :span="22">
              <el-form-item
                :prop="'reranker_reference_list.' + index"
                :rules="{
                  type: 'array',
                  required: true,
                  message: $t('views.applicationWorkflow.variable.placeholder'),
                  trigger: 'change'
                }"
              >
                <NodeCascader
                  :key="index"
                  :nodeModel="nodeModel"
                  class="w-full"
                  :placeholder="
                    $t(
                      'views.applicationWorkflow.nodes.rerankerNode.rerankerContent.requiredMessage'
                    )
                  "
                  v-model="form_data.reranker_reference_list[index]"
                />
              </el-form-item>
            </el-col>
            <el-col :span="1">
              <el-button link type="info" class="mt-4" @click="deleteCondition(index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-col>
          </el-row>
        </el-form-item>
        <el-form-item :label="$t('views.applicationWorkflow.nodes.searchDatasetNode.searchParam')">
          <template #label>
            <div class="flex-between">
              <span>{{ $t('views.applicationWorkflow.nodes.searchDatasetNode.searchParam') }}</span>
              <el-button type="primary" link @click="openParamSettingDialog">
                <el-icon><Setting /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="w-full">
            <el-row>
              <el-col :span="12" class="color-secondary lighter">
                Score
                {{ $t('views.applicationWorkflow.nodes.rerankerNode.higher') }}</el-col
              >
              <el-col :span="12" class="lighter">
                {{ form_data.reranker_setting.similarity?.toFixed(3) }}</el-col
              >
              <el-col :span="12" class="color-secondary lighter">
                {{ $t('chat.KnowledgeSource.referenceParagraph') }} Top</el-col
              >
              <el-col :span="12" class="lighter"> {{ form_data.reranker_setting.top_n }}</el-col>
              <el-col :span="12" class="color-secondary lighter">
                {{
                  $t('views.applicationWorkflow.nodes.rerankerNode.max_paragraph_char_number')
                }}</el-col
              >
              <el-col :span="12" class="lighter">
                {{ form_data.reranker_setting.max_paragraph_char_number }}</el-col
              >
            </el-row>
          </div>
        </el-form-item>
        <el-form-item
          :label="$t('views.applicationWorkflow.nodes.searchDatasetNode.searchQuestion.label')"
          prop="question_reference_address"
          :rules="{
            message: $t(
              'views.applicationWorkflow.nodes.searchDatasetNode.searchQuestion.requiredMessage'
            ),
            trigger: 'blur',
            required: true
          }"
        >
          <template #label>
            <div class="flex-between">
              <span
                >{{ $t('views.applicationWorkflow.nodes.searchDatasetNode.searchQuestion.label')
                }}<span class="danger">*</span></span
              >
            </div>
          </template>
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            :placeholder="
              $t('views.applicationWorkflow.nodes.searchDatasetNode.searchQuestion.label')
            "
            v-model="form_data.question_reference_address"
          />
        </el-form-item>
        <el-form-item
          :label="$t('views.applicationWorkflow.nodes.rerankerNode.reranker_model.label')"
          prop="reranker_model_id"
          :rules="{
            required: true,
            message: $t('views.applicationWorkflow.nodes.rerankerNode.reranker_model.placeholder'),
            trigger: 'change'
          }"
        >
          <template #label>
            <div class="flex-between">
              <span
                >{{ $t('views.applicationWorkflow.nodes.rerankerNode.reranker_model.label')
                }}<span class="danger">*</span></span
              >
            </div>
          </template>
          <ModelSelect
            @wheel="wheel"
            :teleported="false"
            v-model="form_data.reranker_model_id"
            :placeholder="
              $t('views.applicationWorkflow.nodes.rerankerNode.reranker_model.placeholder')
            "
            :options="modelOptions"
            @submitModel="getModel"
            showFooter
            :model-type="'RERANKER'"
          ></ModelSelect>
        </el-form-item>
      </el-form>
    </el-card>
    <ParamSettingDialog ref="ParamSettingDialogRef" @refresh="refreshParam" />
  </NodeContainer>
</template>
<script setup lang="ts">
import { set, cloneDeep, groupBy } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import ParamSettingDialog from './ParamSettingDialog.vue'
import { ref, computed, onMounted } from 'vue'

import applicationApi from '@/api/application'
import useStore from '@/stores'
import { app } from '@/main'

const { model } = useStore()
const props = defineProps<{ nodeModel: any }>()

const ParamSettingDialogRef = ref<InstanceType<typeof ParamSettingDialog>>()
const {
  params: { id }
} = app.config.globalProperties.$route as any
const form = {
  reranker_reference_list: [[]],
  reranker_model_id: '',
  question_reference_address: [],
  reranker_setting: {
    top_n: 3,
    similarity: 0,
    max_paragraph_char_number: 5000
  }
}

const modelOptions = ref<any>(null)
const openParamSettingDialog = () => {
  ParamSettingDialogRef.value?.open(form_data.value.reranker_setting)
}
const deleteCondition = (index: number) => {
  const list = cloneDeep(props.nodeModel.properties.node_data.reranker_reference_list)
  list.splice(index, 1)
  set(props.nodeModel.properties.node_data, 'reranker_reference_list', list)
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
  }
})
function refreshParam(data: any) {
  set(props.nodeModel.properties.node_data, 'reranker_setting', data)
}
function getModel() {
  if (id) {
    applicationApi.getApplicationRerankerModel(id).then((res: any) => {
      modelOptions.value = groupBy(res?.data, 'provider')
    })
  } else {
    model.asyncGetModel({ model_type: 'RERANKER' }).then((res: any) => {
      modelOptions.value = groupBy(res?.data, 'provider')
    })
  }
}

const add_reranker_reference = () => {
  const list = cloneDeep(props.nodeModel.properties.node_data.reranker_reference_list)
  list.push([])
  set(props.nodeModel.properties.node_data, 'reranker_reference_list', list)
}
const rerankerNodeFormRef = ref()
const nodeCascaderRef = ref()
const validate = () => {
  return Promise.all([
    nodeCascaderRef.value ? nodeCascaderRef.value.validate() : Promise.resolve(''),
    rerankerNodeFormRef.value?.validate()
  ]).catch((err: any) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

onMounted(() => {
  getModel()
  set(props.nodeModel, 'validate', validate)
})
</script>
<style lang="scss" scoped>
.reply-node-editor {
  :deep(.md-editor-footer) {
    border: none !important;
  }
}
</style>
