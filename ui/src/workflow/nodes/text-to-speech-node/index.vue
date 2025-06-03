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
          :label="$t('views.applicationWorkflow.nodes.textToSpeechNode.tts_model.label')"
          prop="tts_model_id"
          :rules="{
            required: true,
            message: $t('views.application.applicationForm.form.voicePlay.placeholder'),
            trigger: 'change'
          }"
        >
          <template #label>
            <div class="flex-between w-full">
              <div>
                <span
                  >{{ $t('views.applicationWorkflow.nodes.textToSpeechNode.tts_model.label')
                  }}<span class="danger">*</span></span
                >
              </div>
              <el-button
                type="primary"
                link
                @click="openTTSParamSettingDialog"
                :disabled="!form_data.tts_model_id"
                class="mr-4"
              >
                <el-icon><Setting /></el-icon>
              </el-button>
            </div>
          </template>
          <ModelSelect
            @wheel="wheel"
            :teleported="false"
            v-model="form_data.tts_model_id"
            :placeholder="$t('views.application.applicationForm.form.voicePlay.placeholder')"
            :options="modelOptions"
            showFooter
            :model-type="'TTS'"
          ></ModelSelect>
        </el-form-item>
        <el-form-item
          prop="content_list"
          :label="$t('views.applicationWorkflow.nodes.textToSpeechNode.content.label')"
          :rules="{
            message: $t('views.applicationWorkflow.nodes.textToSpeechNode.content.label'),
            trigger: 'blur',
            required: true
          }"
        >
          <template #label>
            <div class="flex-between w-full">
              <div>
                <span
                  >{{ $t('views.applicationWorkflow.nodes.textToSpeechNode.content.label')
                  }}<span class="danger">*</span></span
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
    <TTSModeParamSettingDialog ref="TTSModeParamSettingDialogRef" @refresh="refreshTTSForm" />
  </NodeContainer>
</template>

<script setup lang="ts">
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import { computed, onMounted, ref } from 'vue'
import { groupBy, set } from 'lodash'
import applicationApi from '@/api/application'
import { app } from '@/main'
import useStore from '@/stores'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import type { FormInstance } from 'element-plus'
import { MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
import TTSModeParamSettingDialog from '@/views/application/component/TTSModeParamSettingDialog.vue'

const TTSModeParamSettingDialogRef = ref<InstanceType<typeof TTSModeParamSettingDialog>>()
const { model } = useStore()

const {
  params: { id }
} = app.config.globalProperties.$route as any

const props = defineProps<{ nodeModel: any }>()
const modelOptions = ref<any>(null)

const aiChatNodeFormRef = ref<FormInstance>()
const nodeCascaderRef = ref()
const validate = () => {
  return Promise.all([
    nodeCascaderRef.value ? nodeCascaderRef.value.validate() : Promise.resolve(''),
    aiChatNodeFormRef.value?.validate()
  ]).catch((err: any) => {
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

const form = {
  tts_model_id: '',
  is_result: true,
  content_list: [],
  model_params_setting: {}
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
    applicationApi.getApplicationTTSModel(id).then((res: any) => {
      modelOptions.value = groupBy(res?.data, 'provider')
    })
  } else {
    model.asyncGetModel().then((res: any) => {
      modelOptions.value = groupBy(res?.data, 'provider')
    })
  }
}

const openTTSParamSettingDialog = () => {
  const model_id = form_data.value.tts_model_id
  if (!model_id) {
    MsgSuccess(t('views.application.applicationForm.form.voicePlay.requiredMessage'))
    return
  }
  TTSModeParamSettingDialogRef.value?.open(model_id, id, form_data.value.model_params_setting)
}
const refreshTTSForm = (data: any) => {
  form_data.value.model_params_setting = data
}

onMounted(() => {
  getModel()

  set(props.nodeModel, 'validate', validate)
})
</script>

<style scoped lang="scss"></style>
