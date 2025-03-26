<template>
  <NodeContainer :node-model="nodeModel">
    <h5 class="title-decoration-1 mb-8">{{ $t('views.applicationWorkflow.nodeSetting') }}</h5>
    <el-card shadow="never" class="card-never">
      <el-form
        @submit.prevent
        :model="form_data"
        label-position="top"
        require-asterisk-position="right"
        label-width="auto"
        ref="aiChatNodeFormRef"
        hide-required-asterisk
      >
        <el-form-item
          :label="$t('views.applicationWorkflow.nodes.imageGenerateNode.model.label')"
          prop="model_id"
          :rules="{
            required: true,
            message: $t('views.applicationWorkflow.nodes.imageGenerateNode.model.requiredMessage'),
            trigger: 'change'
          }"
        >
          <template #label>
            <div class="flex-between w-full">
              <div>
                <span
                  >{{ $t('views.applicationWorkflow.nodes.imageGenerateNode.model.label')
                  }}<span class="danger">*</span></span
                >
              </div>
              <el-button
                :disabled="!form_data.model_id"
                type="primary"
                link
                @click="openAIParamSettingDialog(form_data.model_id)"
                @refreshForm="refreshParam"
              >
                <el-icon><Setting /></el-icon>
              </el-button>
            </div>
          </template>

          <ModelSelect
            @change="model_change"
            @wheel="wheel"
            :teleported="false"
            v-model="form_data.model_id"
            :placeholder="
              $t('views.applicationWorkflow.nodes.imageGenerateNode.model.requiredMessage')
            "
            :options="modelOptions"
            showFooter
            :model-type="'TTI'"
          ></ModelSelect>
        </el-form-item>

        <el-form-item
          :label="$t('views.applicationWorkflow.nodes.imageGenerateNode.prompt.label')"
          prop="prompt"
          :rules="{
            required: true,
            message: $t('views.application.applicationForm.form.prompt.requiredMessage'),
            trigger: 'blur'
          }"
        >
          <template #label>
            <div class="flex align-center">
              <div class="mr-4">
                <span
                  >{{ $t('views.applicationWorkflow.nodes.imageGenerateNode.prompt.label')
                  }}<span class="danger">*</span></span
                >
              </div>
              <el-tooltip effect="dark" placement="right" popper-class="max-w-200">
                <template #content
                  >{{ $t('views.applicationWorkflow.nodes.imageGenerateNode.prompt.tooltip') }}
                </template>
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>
            </div>
          </template>
          <MdEditorMagnify
            @wheel="wheel"
            :title="$t('views.applicationWorkflow.nodes.imageGenerateNode.prompt.label')"
            v-model="form_data.prompt"
            style="height: 150px"
            @submitDialog="submitDialog"
          />
        </el-form-item>
        <el-form-item
          :label="$t('views.applicationWorkflow.nodes.imageGenerateNode.negative_prompt.label')"
          prop="prompt"
          :rules="{
            required: false,
            message: $t('views.application.applicationForm.form.prompt.requiredMessage'),
            trigger: 'blur'
          }"
        >
          <template #label>
            <div class="flex align-center">
              <div class="mr-4">
                <span>{{
                  $t('views.applicationWorkflow.nodes.imageGenerateNode.negative_prompt.label')
                }}</span>
              </div>
              <el-tooltip effect="dark" placement="right" popper-class="max-w-200">
                <template #content
                  >{{
                    $t('views.applicationWorkflow.nodes.imageGenerateNode.negative_prompt.tooltip')
                  }}
                </template>
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>
            </div>
          </template>
          <MdEditorMagnify
            @wheel="wheel"
            :title="$t('views.applicationWorkflow.nodes.imageGenerateNode.negative_prompt.label')"
            v-model="form_data.negative_prompt"
            :placeholder="
              $t('views.applicationWorkflow.nodes.imageGenerateNode.negative_prompt.placeholder')
            "
            style="height: 150px"
            @submitDialog="submitNegativeDialog"
          />
        </el-form-item>
        <el-form-item
          :label="$t('views.applicationWorkflow.nodes.aiChatNode.returnContent.label')"
          @click.prevent
        >
          <template #label>
            <div class="flex align-center">
              <div class="mr-4">
                <span
                  >{{ $t('views.applicationWorkflow.nodes.aiChatNode.returnContent.label')
                  }}</span
                >
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
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import { computed, onMounted, ref } from 'vue'
import { groupBy, set } from 'lodash'
import applicationApi from '@/api/application'
import { app } from '@/main'
import useStore from '@/stores'
import type { FormInstance } from 'element-plus'
import AIModeParamSettingDialog from '@/views/application/component/AIModeParamSettingDialog.vue'
import { t } from '@/locales'
const { model } = useStore()

const {
  params: { id }
} = app.config.globalProperties.$route as any

const props = defineProps<{ nodeModel: any }>()
const modelOptions = ref<any>(null)
const AIModeParamSettingDialogRef = ref<InstanceType<typeof AIModeParamSettingDialog>>()

const aiChatNodeFormRef = ref<FormInstance>()
const validate = () => {
  return aiChatNodeFormRef.value?.validate().catch((err) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
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

const defaultPrompt = `{{${t('views.applicationWorkflow.nodes.startNode.label')}.question}}`

const form = {
  model_id: '',
  system: '',
  prompt: defaultPrompt,
  negative_prompt: '',
  dialogue_number: 0,
  dialogue_type: 'NODE',
  is_result: true,
  temperature: null,
  max_tokens: null,
  image_list: ['start-node', 'image']
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

function getModel() {
  if (id) {
    applicationApi.getApplicationTTIModel(id).then((res: any) => {
      modelOptions.value = groupBy(res?.data, 'provider')
    })
  } else {
    model.asyncGetModel().then((res: any) => {
      modelOptions.value = groupBy(res?.data, 'provider')
    })
  }
}

const model_change = () => {
  if (form_data.value.model_id) {
    AIModeParamSettingDialogRef.value?.reset_default(form_data.value.model_id, id)
  } else {
    refreshParam({})
  }
}

const openAIParamSettingDialog = (modelId: string) => {
  if (modelId) {
    AIModeParamSettingDialogRef.value?.open(modelId, id, form_data.value.model_params_setting)
  }
}

function refreshParam(data: any) {
  set(props.nodeModel.properties.node_data, 'model_params_setting', data)
}

function submitDialog(val: string) {
  set(props.nodeModel.properties.node_data, 'prompt', val)
}

function submitNegativeDialog(val: string) {
  set(props.nodeModel.properties.node_data, 'negative_prompt', val)
}

onMounted(() => {
  getModel()

  set(props.nodeModel, 'validate', validate)
})
</script>

<style scoped lang="scss"></style>
