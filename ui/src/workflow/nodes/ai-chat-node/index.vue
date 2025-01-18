<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">节点设置</h5>
    <el-card shadow="never" class="card-never" style="--el-card-padding: 12px">
      <el-form
        @submit.prevent
        :model="chat_data"
        label-position="top"
        require-asterisk-position="right"
        class="mb-24"
        label-width="auto"
        ref="aiChatNodeFormRef"
        hide-required-asterisk
      >
        <el-form-item
          label="AI 模型"
          prop="model_id"
          :rules="{
            required: true,
            message: '请选择 AI 模型',
            trigger: 'change'
          }"
        >
          <template #label>
            <div class="flex-between w-full">
              <div>
                <span>AI 模型<span class="danger">*</span></span>
              </div>
              <el-button
                :disabled="!chat_data.model_id"
                type="primary"
                link
                @click="openAIParamSettingDialog(chat_data.model_id)"
                @refreshForm="refreshParam"
              >
                {{ $t('common.paramSetting') }}
              </el-button>
            </div>
          </template>
          <ModelSelect
            @change="model_change"
            @wheel="wheel"
            :teleported="false"
            v-model="chat_data.model_id"
            :placeholder="$t('views.application.applicationForm.form.aiModel.placeholder')"
            :options="modelOptions"
            @submitModel="getModel"
            showFooter
          ></ModelSelect>
        </el-form-item>

        <el-form-item label="角色设定">
          <MdEditorMagnify
            title="角色设定"
            v-model="chat_data.system"
            style="height: 100px"
            @submitDialog="submitSystemDialog"
            placeholder="角色设定"
          />
        </el-form-item>
        <el-form-item
          label="提示词"
          prop="prompt"
          :rules="{
            required: true,
            message: '请输入提示词',
            trigger: 'blur'
          }"
        >
          <template #label>
            <div class="flex align-center">
              <div class="mr-4">
                <span>提示词<span class="danger">*</span></span>
              </div>
              <el-tooltip effect="dark" placement="right" popper-class="max-w-200">
                <template #content
                  >通过调整提示词内容，可以引导大模型聊天方向，该提示词会被固定在上下文的开头，可以使用变量。
                </template>
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>
            </div>
          </template>
          <MdEditorMagnify
            @wheel="wheel"
            title="提示词"
            v-model="chat_data.prompt"
            style="height: 150px"
            @submitDialog="submitDialog"
          />
        </el-form-item>
        <el-form-item label="历史聊天记录">
          <template #label>
            <div class="flex-between">
              <div>历史聊天记录</div>
              <el-select v-model="chat_data.dialogue_type" type="small" style="width: 100px">
                <el-option :label="$t('views.applicationWorkflow.node')" value="NODE" />
                <el-option label="工作流" value="WORKFLOW" />
              </el-select>
            </div>
          </template>
          <el-input-number
            v-model="chat_data.dialogue_number"
            :min="0"
            :value-on-clear="0"
            controls-position="right"
            class="w-full"
            :step="1"
            :step-strictly="true"
          />
        </el-form-item>
        <el-form-item label="返回内容" @click.prevent>
          <template #label>
            <div class="flex align-center">
              <div class="mr-4">
                <span>返回内容<span class="danger">*</span></span>
              </div>
              <el-tooltip effect="dark" placement="right" popper-class="max-w-200">
                <template #content>
                  关闭后该节点的内容则不输出给用户。
                  如果你想让用户看到该节点的输出内容，请打开开关。
                </template>
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>
            </div>
          </template>
          <el-switch size="small" v-model="chat_data.is_result" />
        </el-form-item>
      </el-form>
    </el-card>

    <AIModeParamSettingDialog ref="AIModeParamSettingDialogRef" @refresh="refreshParam" />
  </NodeContainer>
</template>
<script setup lang="ts">
import { set, groupBy } from 'lodash'
import { app } from '@/main'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted } from 'vue'
import applicationApi from '@/api/application'
import useStore from '@/stores'
import { isLastNode } from '@/workflow/common/data'
import AIModeParamSettingDialog from '@/views/application/component/AIModeParamSettingDialog.vue'

const { model } = useStore()

const wheel = (e: any) => {
  if (e.ctrlKey === true) {
    e.preventDefault()
    return true
  } else {
    e.stopPropagation()
    return true
  }
}

function submitSystemDialog(val: string) {
  set(props.nodeModel.properties.node_data, 'system', val)
}

function submitDialog(val: string) {
  set(props.nodeModel.properties.node_data, 'prompt', val)
}

const model_change = (model_id?: string) => {
  if (model_id) {
    AIModeParamSettingDialogRef.value?.reset_default(model_id, id)
  } else {
    refreshParam({})
  }
}
const {
  params: { id }
} = app.config.globalProperties.$route as any

// @ts-ignore
const defaultPrompt = `已知信息：
{{知识库检索.data}}
问题：
{{开始.question}}`
const form = {
  model_id: '',
  system: '',
  prompt: defaultPrompt,
  dialogue_number: 1,
  is_result: false,
  temperature: null,
  max_tokens: null,
  dialogue_type: 'WORKFLOW'
}

const chat_data = computed({
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
const props = defineProps<{ nodeModel: any }>()

const aiChatNodeFormRef = ref<FormInstance>()

const modelOptions = ref<any>(null)
const AIModeParamSettingDialogRef = ref<InstanceType<typeof AIModeParamSettingDialog>>()
const validate = () => {
  return aiChatNodeFormRef.value?.validate().catch((err) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

function getModel() {
  if (id) {
    applicationApi.getApplicationModel(id).then((res: any) => {
      modelOptions.value = groupBy(res?.data, 'provider')
    })
  } else {
    model.asyncGetModel().then((res: any) => {
      modelOptions.value = groupBy(res?.data, 'provider')
    })
  }
}

const openAIParamSettingDialog = (modelId: string) => {
  if (modelId) {
    AIModeParamSettingDialogRef.value?.open(modelId, id, chat_data.value.model_params_setting)
  }
}

function refreshParam(data: any) {
  set(props.nodeModel.properties.node_data, 'model_params_setting', data)
}

onMounted(() => {
  getModel()
  if (typeof props.nodeModel.properties.node_data?.is_result === 'undefined') {
    if (isLastNode(props.nodeModel)) {
      set(props.nodeModel.properties.node_data, 'is_result', true)
    }
  }
  set(props.nodeModel, 'validate', validate)
  if (!chat_data.value.dialogue_type) {
    chat_data.value.dialogue_type = 'WORKFLOW'
  }
})
</script>
<style lang="scss" scoped></style>
