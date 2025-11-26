<template>
  <NodeContainer :node-model="nodeModel">
    <h5 class="title-decoration-1 mb-8">{{ $t('views.workflow.nodeSetting') }}</h5>
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
          :label="$t('views.workflow.nodes.textToSpeechNode.tts_model.label')"
          prop="tts_model_id"
          :rules="{
            required: true,
            message: $t('views.application.form.voicePlay.placeholder'),
            trigger: 'change',
          }"
        >
          <template #label>
            <div class="flex-between w-full">
              <div>
                <span
                  >{{ $t('views.workflow.nodes.textToSpeechNode.tts_model.label')
                  }}<span class="color-danger">*</span></span
                >
              </div>
              <el-button
                type="primary"
                link
                @click="openTTSParamSettingDialog"
                :disabled="!form_data.tts_model_id"
                class="mr-4"
              >
                <AppIcon iconName="app-setting"></AppIcon>
              </el-button>
            </div>
          </template>
          <ModelSelect
            @wheel="wheel"
            :teleported="false"
            v-model="form_data.tts_model_id"
            :placeholder="$t('views.application.form.voicePlay.placeholder')"
            :options="modelOptions"
            showFooter
            :model-type="'TTS'"
          ></ModelSelect>
        </el-form-item>
        <el-form-item
          prop="content_list"
          :label="$t('views.workflow.nodes.textToSpeechNode.content.label')"
          :rules="{
            message: $t('views.workflow.nodes.textToSpeechNode.content.label'),
            trigger: 'blur',
            required: true,
          }"
        >
          <template #label>
            <div class="flex-between w-full">
              <div>
                <span
                  >{{ $t('views.workflow.nodes.textToSpeechNode.content.label')
                  }}<span class="color-danger">*</span></span
                >
              </div>
            </div>
          </template>
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            :placeholder="$t('views.workflow.nodes.textToSpeechNode.content.label')"
            v-model="form_data.content_list"
          />
        </el-form-item>

        <el-form-item
          :label="$t('views.workflow.nodes.aiChatNode.returnContent.label')"
          @click.prevent
        >
          <template #label>
            <div class="flex align-center">
              <div class="mr-4">
                <span>{{
                  $t('views.workflow.nodes.aiChatNode.returnContent.label')
                }}</span>
              </div>
              <el-tooltip effect="dark" placement="right" popper-class="max-w-200">
                <template #content>
                  {{ $t('views.workflow.nodes.aiChatNode.returnContent.tooltip') }}
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
import { computed, onMounted, ref, inject } from 'vue'
import { groupBy, set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import TTSModeParamSettingDialog from '@/views/application/component/TTSModeParamSettingDialog.vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import type { FormInstance } from 'element-plus'
import { MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
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

const TTSModeParamSettingDialogRef = ref<InstanceType<typeof TTSModeParamSettingDialog>>()

const modelOptions = ref<any>(null)

const aiChatNodeFormRef = ref<FormInstance>()
const nodeCascaderRef = ref()
const validate = () => {
  return Promise.all([
    nodeCascaderRef.value ? nodeCascaderRef.value.validate() : Promise.resolve(''),
    aiChatNodeFormRef.value?.validate(),
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
  model_params_setting: {},
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

const resource = getResourceDetail()
function getSelectModel() {
  const obj =
    apiType.value === 'systemManage'
      ? {
          model_type: 'TTS',
          workspace_id: resource.value?.workspace_id,
        }
      : {
          model_type: 'TTS',
        }
  loadSharedApi({ type: 'model', systemType: apiType.value })
    .getSelectModelList(obj)
    .then((res: any) => {
      modelOptions.value = groupBy(res?.data, 'provider')
    })
}

const openTTSParamSettingDialog = () => {
  const model_id = form_data.value.tts_model_id
  if (!model_id) {
    MsgSuccess(t('views.application.form.voicePlay.requiredMessage'))
    return
  }
  TTSModeParamSettingDialogRef.value?.open(model_id, id, form_data.value.model_params_setting)
}
const refreshTTSForm = (data: any) => {
  form_data.value.model_params_setting = data
}

onMounted(() => {
  getSelectModel()

  set(props.nodeModel, 'validate', validate)
})
</script>

<style scoped lang="scss"></style>
