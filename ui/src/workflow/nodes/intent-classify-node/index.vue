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
        ref="IntentClassifyNodeFormRef"
        hide-required-asterisk
      >
        <el-form-item
          :label="$t('views.application.form.aiModel.label')"
          prop="model_id"
          :rules="{
            required: true,
            message: $t('views.application.form.aiModel.placeholder'),
            trigger: 'change',
          }"
        >
          <template #label>
            <div class="flex-between">
              <div>
                <span
                  >{{ $t('views.application.form.aiModel.label')
                  }}<span class="color-danger">*</span></span
                >
              </div>
              <el-button
                type="primary"
                link
                :disabled="!form_data.model_id"
                @click="openAIParamSettingDialog(form_data.model_id)"
                @refreshForm="refreshParam"
              >
                <AppIcon iconName="app-setting"></AppIcon>
              </el-button>
            </div>
          </template>
          <ModelSelect
            @change="model_change"
            @wheel="wheel"
            :teleported="false"
            v-model="form_data.model_id"
            :placeholder="$t('views.application.form.aiModel.placeholder')"
            :options="modelOptions"
            @submitModel="getSelectModel"
            showFooter
            :model-type="'LLM'"
          ></ModelSelect>
        </el-form-item>
        <el-form-item
          prop="content_list"
          :label="$t('views.applicationWorkflow.nodes.intentNode.input.label')"
          :rules="{
            message: $t('views.applicationWorkflow.nodes.textToSpeechNode.content.label'),
            trigger: 'change',
            required: true,
          }"
        >
          <template #label>
            <div class="flex-between">
              <div>
                <span
                  >{{ $t('views.applicationWorkflow.nodes.intentNode.input.label')
                  }}<span class="color-danger">*</span></span
                >
              </div>
            </div>
          </template>
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            :placeholder="$t('views.applicationWorkflow.nodes.textToSpeechNode.content.label')"
            v-model="form_data.content_list"
          />
        </el-form-item>
        <el-form-item :label="$t('views.application.form.historyRecord.label')">
          <el-input-number
            v-model="form_data.dialogue_number"
            :min="0"
            :value-on-clear="0"
            controls-position="right"
            class="w-full"
            :step="1"
            :step-strictly="true"
          />
        </el-form-item>
        <el-form-item
        >
          <template #label>
            <div class="flex-between">
              <div>
                <span
                  >{{ $t('views.applicationWorkflow.nodes.intentNode.classify.label')
                  }}<span class="color-danger">*</span></span
                >
              </div>
              <el-button @click="addClassfiyBranch" type="primary" size="large" link>
                <el-icon><Plus /></el-icon>
              </el-button>
            </div>
          </template>
          <div>
            <div
              v-for="(item, index) in form_data.branch"
              :key="item.id"
            >
            <el-form-item
            :prop="`branch.${index}.content`"
            :rules="{
            message: $t('views.applicationWorkflow.nodes.intentNode.classify.placeholder'),
            trigger: 'change',
            required: true,
          }"
            >
              <el-row class="mb-8" :gutter="12" align="middle">
                <el-col :span="21">
                  <el-input
                    v-model="item.content"
                    style="width: 210px"
                    :disabled="item.isOther"
                    :placeholder="
                      $t('views.applicationWorkflow.nodes.intentNode.classify.placeholder')
                    "
                  />
                </el-col>
                <el-col :span="3">
                  <el-button
                    link
                    size="large"
                    v-if="!item.isOther"
                    :disabled="form_data.branch.filter((b: any) => !b.isOther).length <= 1"
                    @click="deleteClassifyBranch(item.id)"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-col>
              </el-row>
            </el-form-item>
            </div>
          </div>
        </el-form-item>
      </el-form>
    </el-card>

    <AIModeParamSettingDialog ref="AIModeParamSettingDialogRef" @refresh="refreshParam" />
  </NodeContainer>
</template>
<script setup lang="ts">
import { set, groupBy, cloneDeep } from 'lodash'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import AIModeParamSettingDialog from '@/views/application/component/AIModeParamSettingDialog.vue'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted, inject } from 'vue'
import { isLastNode } from '@/workflow/common/data'
import { t } from '@/locales'
import { useRoute } from 'vue-router'
import { randomId } from '@/utils/common'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
const getApplicationDetail = inject('getApplicationDetail') as any
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

const nodeCascaderRef = ref()
const AIModeParamSettingDialogRef = ref<InstanceType<typeof AIModeParamSettingDialog>>()

function addClassfiyBranch() {
  const list = cloneDeep(props.nodeModel.properties.node_data.branch)
  const obj = {
    id: randomId(),
    content: '',
    isOther: false,
  }
  list.splice(list.length - 1, 0, obj)
  refreshBranchAnchor(list, true)
  set(props.nodeModel.properties.node_data, 'branch', list)
  props.nodeModel.refreshBranch()
}

function deleteClassifyBranch(id: string) {
  const list = cloneDeep(props.nodeModel.properties.node_data.branch)

  const itemToDelete = list.find((item: any) => item.id === id)
  if (!itemToDelete || itemToDelete.isOther) {
    return
  }

  const commonItems = list.filter((item: any) => !item.isOther)
  if (commonItems.length <= 1) {
    return
  }
  // 删除连接线
  const delete_anchor_id = `${props.nodeModel.id}_${id}_right`
  const edgetToDelete = (props.nodeModel.outgoing?.edges || [])
    .filter((edge: any) => edge.sourceAnchorId === delete_anchor_id)
    .map((edge: any) => edge.id)

  if (edgetToDelete.length > 0) {
    props.nodeModel.graphModel.eventCenter.emit('delete_edge', edgetToDelete)
  }

  const newList = list.filter((item: any) => item.id !== id) // 删除分支

  set(props.nodeModel.properties.node_data, 'branch', newList) // 更新数据
  refreshBranchAnchor(newList, false) // 刷新锚点
}

function refreshBranchAnchor(list: Array<any>, is_add: boolean) {
  const branch_condition_list = cloneDeep(
    props.nodeModel.properties.branch_condition_list
      ? props.nodeModel.properties.branch_condition_list
      : [],
  )

  const new_branch_condition_list = list
    .map((item, index) => {
      const exist = branch_condition_list.find((b: any) => b.id === item.id)
      if (exist) {
        return { index: index, height: exist.height, id: item.id }
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

const resizeBranch = (wh: any, row: any, index: number) => {
  const branch_condition_list = cloneDeep(
    props.nodeModel.properties.branch_condition_list
      ? props.nodeModel.properties.branch_condition_list
      : [],
  )
  const new_branch_condition_list = branch_condition_list.map((item: any) => {
    if (item.id === row.id) {
      return {
        ...item,
        height: wh.height, //该分支高度
        index: index,
      }
    }
    return item
  })
  set(props.nodeModel.properties, 'branch_condition_list', new_branch_condition_list)
  refreshBranchAnchor(props.nodeModel.properties.node_data.branch, true)
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

const model_change = (model_id?: string) => {
  if (model_id) {
    AIModeParamSettingDialogRef.value?.reset_default(model_id, id)
  } else {
    refreshParam({})
  }
}

const form = {
  model_id: '',
  branch: [
    {
      id: randomId(),
      content: '',
      isOther: false,
    },
    {
      id: randomId(),
      content: t('views.applicationWorkflow.nodes.intentNode.other'),
      isOther: true,
    },
  ],
  dialogue_number: 1,
  content_list: [],
}

function refreshParam(data: any) {
  set(props.nodeModel.properties.node_data, 'model_params_setting', data)
}

const openAIParamSettingDialog = (modelId: string) => {
  if (modelId) {
    AIModeParamSettingDialogRef.value?.open(modelId, id, form_data.value.model_params_setting)
  }
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
const props = defineProps<{ nodeModel: any }>()

const IntentClassifyNodeFormRef = ref<FormInstance>()
const modelOptions = ref<any>(null)

const validate = () => {

  return Promise.all([
    nodeCascaderRef.value ? nodeCascaderRef.value.validate() : Promise.resolve(''),
    IntentClassifyNodeFormRef.value?.validate(),
  ]).then(() => {
    if (form_data.value.branch.length != new Set(form_data.value.branch.map((item: any) => item.content)).size) {
      throw t('views.applicationWorkflow.nodes.intentNode.error2')
    }
  }).catch((err: any) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

const application = getApplicationDetail()
function getSelectModel() {
  const obj =
    apiType.value === 'systemManage'
      ? {
          model_type: 'LLM',
          workspace_id: application.value?.workspace_id,
        }
      : {
          model_type: 'LLM',
        }
  loadSharedApi({ type: 'model', systemType: apiType.value })
    .getSelectModelList(obj)
    .then((res: any) => {
      modelOptions.value = groupBy(res?.data, 'provider')
    })
}

onMounted(() => {
  getSelectModel()
  if (typeof props.nodeModel.properties.node_data?.is_result === 'undefined') {
    if (isLastNode(props.nodeModel)) {
      set(props.nodeModel.properties.node_data, 'is_result', true)
    }
  }
  set(props.nodeModel, 'validate', validate)
})
</script>
<style lang="scss" scoped></style>
