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
          :label="$t('views.workflow.nodes.rerankerNode.rerankerContent.label')"
          prop="reranker_reference_list"
          :rules="{
            type: 'array',
            message: $t(
              'views.workflow.nodes.rerankerNode.rerankerContent.requiredMessage',
            ),
            trigger: 'change',
            required: true,
          }"
        >
          <template #label>
            <div class="flex-between">
              <span
                >{{ $t('views.workflow.nodes.rerankerNode.rerankerContent.label')
                }}<span class="color-danger">*</span></span
              >
              <el-button @click="add_reranker_reference" link type="primary">
                <AppIcon iconName="app-add-outlined"></AppIcon>
              </el-button>
            </div>
          </template>
          <el-row
            :gutter="8"
            style="margin-bottom: 8px"
            v-for="(reranker_reference, index) in form_data.reranker_reference_list"
            :key="index"
            class="w-full"
          >
            <el-col :span="22">
              <el-form-item
                :prop="'reranker_reference_list.' + index"
                :rules="{
                  type: 'array',
                  required: true,
                  message: $t('views.workflow.variable.placeholder'),
                  trigger: 'change',
                }"
              >
                <NodeCascader
                  :key="index"
                  :nodeModel="nodeModel"
                  class="w-full"
                  :placeholder="
                    $t(
                      'views.workflow.nodes.rerankerNode.rerankerContent.requiredMessage',
                    )
                  "
                  v-model="form_data.reranker_reference_list[index]"
                />
              </el-form-item>
            </el-col>
            <el-col :span="2">
              <el-button link type="info" @click="deleteCondition(index)">
                <AppIcon iconName="app-delete"></AppIcon>
              </el-button>
            </el-col>
          </el-row>
        </el-form-item>
        <el-form-item
          :label="$t('views.workflow.nodes.searchKnowledgeNode.searchParam')"
        >
          <template #label>
            <div class="flex-between">
              <span>{{
                $t('views.workflow.nodes.searchKnowledgeNode.searchParam')
              }}</span>
              <el-button type="primary" link @click="openParamSettingDialog">
                <AppIcon iconName="app-setting"></AppIcon>
              </el-button>
            </div>
          </template>
          <div class="w-full">
            <el-row>
              <el-col :span="12" class="color-secondary lighter">
                Score
                {{ $t('views.workflow.nodes.rerankerNode.higher') }}</el-col
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
                  $t('views.workflow.nodes.rerankerNode.max_paragraph_char_number')
                }}</el-col
              >
              <el-col :span="12" class="lighter">
                {{ form_data.reranker_setting.max_paragraph_char_number }}</el-col
              >
            </el-row>
          </div>
        </el-form-item>
        <el-form-item
          :label="$t('views.workflow.nodes.searchKnowledgeNode.searchQuestion.label')"
          prop="question_reference_address"
          :rules="{
            message: $t(
              'views.workflow.nodes.searchKnowledgeNode.searchQuestion.requiredMessage',
            ),
            trigger: 'blur',
            required: true,
          }"
        >
          <template #label>
            <div class="flex-between">
              <span
                >{{ $t('views.workflow.nodes.searchKnowledgeNode.searchQuestion.label')
                }}<span class="color-danger">*</span></span
              >
            </div>
          </template>
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            :placeholder="
              $t('views.workflow.nodes.searchKnowledgeNode.searchQuestion.label')
            "
            v-model="form_data.question_reference_address"
          />
        </el-form-item>
        <el-form-item
          :label="$t('views.workflow.nodes.rerankerNode.reranker_model.label')"
          prop="reranker_model_id"
          :rules="{
            required: true,
            message: $t('views.workflow.nodes.rerankerNode.reranker_model.placeholder'),
            trigger: 'change',
          }"
        >
          <template #label>
            <div class="flex-between">
              <span
                >{{ $t('views.workflow.nodes.rerankerNode.reranker_model.label')
                }}<span class="color-danger">*</span></span
              >
            </div>
          </template>
          <ModelSelect
            @wheel="wheel"
            :teleported="false"
            v-model="form_data.reranker_model_id"
            :placeholder="
              $t('views.workflow.nodes.rerankerNode.reranker_model.placeholder')
            "
            :options="modelOptions"
            @submitModel="getSelectModel"
            showFooter
            :model-type="'RERANKER'"
          ></ModelSelect>
        </el-form-item>
        <el-form-item
          :label="$t('views.workflow.nodes.searchKnowledgeNode.showKnowledge.label')"
          prop="show_knowledge"
          required
          @click.prevent
        >
          <el-switch size="small" v-model="form_data.show_knowledge" />
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
import { ref, computed, onMounted, inject } from 'vue'
import { useRoute } from 'vue-router'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
const getResourceDetail = inject('getResourceDetail') as any
const route = useRoute()

const {
  params: { id },
} = route as any

const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const props = defineProps<{ nodeModel: any }>()

const ParamSettingDialogRef = ref<InstanceType<typeof ParamSettingDialog>>()

const form = {
  reranker_reference_list: [[]],
  reranker_model_id: '',
  question_reference_address: [],
  reranker_setting: {
    top_n: 3,
    similarity: 0,
    max_paragraph_char_number: 5000,
  },
  show_knowledge: false,
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
  },
})
function refreshParam(data: any) {
  set(props.nodeModel.properties.node_data, 'reranker_setting', data)
}

const resource = getResourceDetail()
function getSelectModel() {
  const obj =
    apiType.value === 'systemManage'
      ? {
          model_type: 'RERANKER',
          workspace_id: resource.value?.workspace_id,
        }
      : {
          model_type: 'RERANKER',
        }
  loadSharedApi({ type: 'model', systemType: apiType.value })
    .getSelectModelList(obj)
    .then((res: any) => {
      modelOptions.value = groupBy(res?.data, 'provider')
    })
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
    rerankerNodeFormRef.value?.validate(),
  ]).catch((err: any) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

onMounted(() => {
  getSelectModel()
  form_data.value.show_knowledge = form_data.value.show_knowledge
    ? form_data.value.show_knowledge
    : false
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
