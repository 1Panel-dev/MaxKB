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
          :label="$t('views.applicationWorkflow.nodes.imageUnderstandNode.model.label')"
          prop="model_id"
          :rules="{
            required: true,
            message: $t(
              'views.applicationWorkflow.nodes.imageUnderstandNode.model.requiredMessage',
            ),
            trigger: 'change',
          }"
        >
          <template #label>
            <div class="flex-between w-full">
              <div>
                <span
                  >{{ t('views.applicationWorkflow.nodes.imageUnderstandNode.model.label')
                  }}<span class="color-danger">*</span></span
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
            @wheel="wheel"
            :teleported="false"
            v-model="form_data.model_id"
            :placeholder="
              $t('views.applicationWorkflow.nodes.imageUnderstandNode.model.requiredMessage')
            "
            :options="modelOptions"
            showFooter
            :model-type="'IMAGE'"
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
            message: $t('views.application.form.prompt.requiredMessage'),
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
                <template #content>{{ $t('views.application.form.prompt.tooltip') }} </template>
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
        <el-form-item>
          <template #label>
            <div class="flex-between">
              <div>{{ $t('views.application.form.historyRecord.label') }}</div>
              <el-select v-model="form_data.dialogue_type" type="small" style="width: 100px">
                <el-option :label="$t('views.applicationWorkflow.node')" value="NODE" />
                <el-option :label="$t('views.applicationWorkflow.workflow')" value="WORKFLOW" />
              </el-select>
            </div>
          </template>
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
          :label="$t('views.applicationWorkflow.nodes.imageUnderstandNode.image.label')"
          :rules="{
            type: 'array',
            required: true,
            message: $t(
              'views.applicationWorkflow.nodes.imageUnderstandNode.image.requiredMessage',
            ),
            trigger: 'change',
          }"
        >
          <template #label
            >{{ $t('views.applicationWorkflow.nodes.imageUnderstandNode.image.label')
            }}<span class="color-danger">*</span></template
          >
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            :placeholder="
              $t('views.applicationWorkflow.nodes.imageUnderstandNode.image.requiredMessage')
            "
            v-model="form_data.image_list"
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
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import { computed, onMounted, ref, inject } from 'vue'
import { groupBy, set } from 'lodash'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import type { FormInstance } from 'element-plus'
import AIModeParamSettingDialog from '@/views/application/component/AIModeParamSettingDialog.vue'
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

const props = defineProps<{ nodeModel: any }>()
const modelOptions = ref<any>(null)
const AIModeParamSettingDialogRef = ref<InstanceType<typeof AIModeParamSettingDialog>>()

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

const defaultPrompt = `{{${t('views.applicationWorkflow.nodes.startNode.label')}.question}}`

const form = {
  model_id: '',
  system: '',
  prompt: defaultPrompt,
  dialogue_number: 0,
  dialogue_type: 'NODE',
  is_result: true,
  temperature: null,
  max_tokens: null,
  image_list: ['start-node', 'image'],
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

const application = getApplicationDetail()
function getSelectModel() {
  const obj =
    apiType.value === 'systemManage'
      ? {
          model_type: 'IMAGE',
          workspace_id: application.value?.workspace_id,
        }
      : {
          model_type: 'IMAGE',
        }
  loadSharedApi({ type: 'model', systemType: apiType.value })
    .getSelectModelList(obj)
    .then((res: any) => {
      modelOptions.value = groupBy(res?.data, 'provider')
    })
}

function submitSystemDialog(val: string) {
  set(props.nodeModel.properties.node_data, 'system', val)
}

function submitDialog(val: string) {
  set(props.nodeModel.properties.node_data, 'prompt', val)
}

const openAIParamSettingDialog = (modelId: string) => {
  if (modelId) {
    AIModeParamSettingDialogRef.value?.open(modelId, id, form_data.value.model_params_setting)
  }
}

function refreshParam(data: any) {
  set(props.nodeModel.properties.node_data, 'model_params_setting', data)
}

onMounted(() => {
  getSelectModel()

  set(props.nodeModel, 'validate', validate)
})
</script>

<style scoped lang="scss"></style>
