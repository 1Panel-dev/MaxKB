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
          :label="$t('views.application.form.aiModel.label')"
          prop="model_id"
          :rules="{
            required: true,
            message: $t('views.application.form.aiModel.placeholder'),
            trigger: 'change',
          }"
        >
          <template #label>
            <div class="flex-between w-full">
              <div>
                <span
                  >{{ $t('views.application.form.aiModel.label')
                  }}<span class="color-danger ml-4">*</span></span
                >
              </div>

              <el-button
                :disabled="!form_data.model_id"
                type="primary"
                link
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
              'views.applicationWorkflow.nodes.parameterExtractionNode.extractParameters.variableListPlaceholder',
            ),
            trigger: 'blur',
            required: true,
          }"
        >
          <ParametersFieldTable
            ref="ParametersFieldTableRef"
            :node-model="nodeModel"
          ></ParametersFieldTable>
        </el-form-item>
      </el-form>
    </el-card>
    <AIModeParamSettingDialog ref="AIModeParamSettingDialogRef" @refresh="refreshParam" />
  </NodeContainer>
</template>
<script setup lang="ts">
import { computed, onMounted, ref, inject } from 'vue'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import AIModeParamSettingDialog from '@/views/application/component/AIModeParamSettingDialog.vue'
import ParametersFieldTable from '@/workflow/nodes/parameter-extraction-node/component/ParametersFieldTable.vue'
import { useRoute } from 'vue-router'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { set, groupBy } from 'lodash'
const getApplicationDetail = inject('getApplicationDetail') as any
const props = defineProps<{ nodeModel: any }>()
const AIModeParamSettingDialogRef = ref<InstanceType<typeof AIModeParamSettingDialog>>()
const route = useRoute()
const {
  params: { id },
} = route as any
const openAIParamSettingDialog = (modelId: string) => {
  if (modelId) {
    AIModeParamSettingDialogRef.value?.open(modelId, id, form_data.value.model_params_setting)
  }
}
function refreshParam(data: any) {
  set(props.nodeModel.properties.node_data, 'model_params_setting', data)
}
const application = getApplicationDetail()
const modelOptions = ref<any>(null)
const wheel = (e: any) => {
  if (e.ctrlKey === true) {
    e.preventDefault()
    return true
  } else {
    e.stopPropagation()
    return true
  }
}
const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
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

const form = {
  input_variable: [],
  model_params_setting: {},
  model_id: '',
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

const model_change = (model_id?: string) => {
  if (model_id) {
    AIModeParamSettingDialogRef.value?.reset_default(model_id, id)
  } else {
    refreshParam({})
  }
}

const VariableSplittingRef = ref()
const validate = async () => {
  return VariableSplittingRef.value.validate().catch((err: any) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

onMounted(() => {
  getSelectModel()
  set(props.nodeModel, 'validate', validate)
})
</script>
<style lang="scss" scoped></style>
