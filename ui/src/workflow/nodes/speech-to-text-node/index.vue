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
          :label="$t('views.applicationWorkflow.nodes.speechToTextNode.stt_model.label')"
          prop="stt_model_id"
          :rules="{
            required: true,
            message: $t('views.application.form.voiceInput.placeholder'),
            trigger: 'change',
          }"
        >
          <template #label>
            <div class="flex-between w-full">
              <div>
                <span
                  >{{ $t('views.applicationWorkflow.nodes.speechToTextNode.stt_model.label')
                  }}<span class="color-danger">*</span></span
                >
              </div>
              <el-button
                type="primary"
                link
                @click="openSTTParamSettingDialog"
                :disabled="!form_data.stt_model_id"
                class="mr-4"
              >
                <AppIcon iconName="app-setting"></AppIcon>
              </el-button>
            </div>
          </template>
          <ModelSelect
            @wheel="wheel"
            :teleported="false"
            @change="sttModelChange"
            v-model="form_data.stt_model_id"
            :placeholder="$t('views.application.form.voiceInput.placeholder')"
            :options="modelOptions"
            showFooter
            :model-type="'STT'"
          ></ModelSelect>
        </el-form-item>
        <el-form-item
          :label="$t('views.applicationWorkflow.nodes.speechToTextNode.audio.label')"
          prop="audio_list"
          :rules="{
            message: $t('views.applicationWorkflow.nodes.speechToTextNode.audio.label'),
            trigger: 'change',
            required: true,
          }"
        >
          <template #label>
            <div class="flex-between w-full">
              <div>
                <span
                  >{{ $t('views.applicationWorkflow.nodes.speechToTextNode.audio.label')
                  }}<span class="color-danger">*</span></span
                >
              </div>
            </div>
          </template>
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            :placeholder="$t('views.applicationWorkflow.nodes.speechToTextNode.audio.placeholder')"
            v-model="form_data.audio_list"
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
    <STTModeParamSettingDialog ref="STTModeParamSettingDialogRef" @refresh="refreshSTTForm" />
  </NodeContainer>
</template>

<script setup lang="ts">
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import { computed, onMounted, ref, inject } from 'vue'
import { groupBy, set } from 'lodash'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import type { FormInstance } from 'element-plus'
import { MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
import { useRoute } from 'vue-router'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import STTModeParamSettingDialog from '@/views/application/component/STTModelParamSettingDialog.vue'
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

const props = defineProps<{ nodeModel: any }>()
const modelOptions = ref<any>(null)
const STTModeParamSettingDialogRef = ref<InstanceType<typeof STTModeParamSettingDialog>>()


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
  stt_model_id: '',
  is_result: true,
  audio_list: [],
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


const openSTTParamSettingDialog = () => {
  const model_id = form_data.value.stt_model_id
  if (!model_id) {
    MsgSuccess(t('views.application.form.voiceInput.requiredMessage'))
    return
  }
  STTModeParamSettingDialogRef.value?.open(
      model_id,
      id,
      form_data.value.model_params_setting,
    )
}

const refreshSTTForm = (data: any) => {
  set(props.nodeModel.properties.node_data, 'model_params_setting', data)
}

function sttModelChange(model_id: string) {
  if (model_id) {
    STTModeParamSettingDialogRef.value?.reset_default(model_id, id)
  } else {
    refreshSTTForm({})
  }
}

const application = getApplicationDetail()
function getSelectModel() {
  const obj =
    apiType.value === 'systemManage'
      ? {
          model_type: 'STT',
          workspace_id: application.value?.workspace_id,
        }
      : {
          model_type: 'STT',
        }
  loadSharedApi({ type: 'model', systemType: apiType.value })
    .getSelectModelList(obj)
    .then((res: any) => {
      modelOptions.value = groupBy(res?.data, 'provider')
    })
}
onMounted(() => {
  getSelectModel()

  set(props.nodeModel, 'validate', validate)
})
</script>

<style scoped lang="scss"></style>
