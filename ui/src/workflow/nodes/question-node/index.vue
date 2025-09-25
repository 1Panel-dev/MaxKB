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
        ref="questionNodeFormRef"
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
        <el-form-item>
          <template #label>
            <div class="flex-between">
              <div class="flex align-center">
                <span>{{ $t('views.application.form.roleSettings.label') }}</span>
                <el-tooltip
                  effect="dark"
                  :content="$t('views.application.form.roleSettings.tooltip')"
                  placement="right"
                >
                  <AppIcon iconName="app-warning" class="app-warning-icon ml-4"></AppIcon>
                </el-tooltip>
              </div>
            </div>
          </template>
          <MdEditorMagnify
            :title="$t('views.application.form.roleSettings.label')"
            v-model="form_data.system"
            style="height: 100px"
            @submitDialog="submitSystemDialog"
            :placeholder="`${t('views.applicationWorkflow.SystemPromptPlaceholder')}{{${t('views.applicationWorkflow.nodes.startNode.label')}.question}}`"
          />
        </el-form-item>
        <el-form-item
          :label="$t('views.application.form.prompt.label')"
          prop="prompt"
          :rules="{
            required: true,
            message: $t('views.application.form.prompt.tooltip'),
            trigger: 'blur',
          }"
        >
          <template #label>
            <div class="flex align-center">
              <div class="mr-4">
                <span
                  >{{ $t('views.application.form.prompt.label')
                  }}<span class="color-danger">*</span></span
                >
              </div>
              <el-tooltip effect="dark" placement="right" popper-class="max-w-200">
                <template #content>{{ $t('views.application.form.prompt.tooltip') }}</template>
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>
            </div>
          </template>
          <MdEditorMagnify
            @wheel="wheel"
            :title="$t('views.application.form.prompt.label')"
            v-model="form_data.prompt"
            style="height: 150px"
            @submitDialog="submitDialog"
            :placeholder="`${t('views.applicationWorkflow.UserPromptPlaceholder')}{{${t('views.applicationWorkflow.nodes.startNode.label')}.question}}`"
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
          :label="$t('views.applicationWorkflow.nodes.aiChatNode.returnContent.label')"
          @click.prevent
        >
          <template #label>
            <div class="flex align-center">
              <div class="mr-4">
                <span>{{
                  $t('views.applicationWorkflow.nodes.aiChatNode.returnContent.label')
                }}</span>
              </div>
              <el-tooltip effect="dark" placement="right" popper-class="max-w-200">
                <template #content>
                  {{ $t('views.applicationWorkflow.nodes.aiChatNode.returnContent.tooltip') }}
                </template>
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>
            </div>
          </template>
          <el-switch size="small" v-model="form_data.is_result" />
        </el-form-item>
      </el-form>
    </el-card>

    <AIModeParamSettingDialog ref="AIModeParamSettingDialogRef" @refresh="refreshParam" />
  </NodeContainer>
</template>
<script setup lang="ts">
import { set, groupBy } from 'lodash'

import NodeContainer from '@/workflow/common/NodeContainer.vue'
import AIModeParamSettingDialog from '@/views/application/component/AIModeParamSettingDialog.vue'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted, inject } from 'vue'
import { isLastNode } from '@/workflow/common/data'
import { t } from '@/locales'
import { useRoute } from 'vue-router'
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

const AIModeParamSettingDialogRef = ref<InstanceType<typeof AIModeParamSettingDialog>>()

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
function submitDialog(val: string) {
  set(props.nodeModel.properties.node_data, 'prompt', val)
}

function submitSystemDialog(val: string) {
  set(props.nodeModel.properties.node_data, 'system', val)
}

const defaultPrompt = `{{${t('views.applicationWorkflow.nodes.startNode.label')}.question}}`

const form = {
  model_id: '',
  system: defaultPrompt,
  prompt: t('views.applicationWorkflow.nodes.questionNode.systemDefault'),
  dialogue_number: 1,
  is_result: false,
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
    }
    return props.nodeModel.properties.node_data
  },
  set: (value) => {
    set(props.nodeModel.properties, 'node_data', value)
  },
})
const props = defineProps<{ nodeModel: any }>()

const questionNodeFormRef = ref<FormInstance>()

const modelOptions = ref<any>(null)

const validate = () => {
  return questionNodeFormRef.value?.validate().catch((err) => {
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
