<template>
  <NodeContainer :node-model="nodeModel">
    <h5 class="title-decoration-1 mb-8">节点设置</h5>
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
          label="图片生成模型"
          prop="model_id"
          :rules="{
            required: true,
            message: '请选择图片生成模型',
            trigger: 'change'
          }"
        >
          <template #label>
            <div class="flex-between w-full">
              <div>
                <span>图片生成模型<span class="danger">*</span></span>
              </div>
              <el-button
                :disabled="!form_data.model_id"
                type="primary"
                link
                @click="openAIParamSettingDialog(form_data.model_id)"
                @refreshForm="refreshParam"
              >
                {{ $t('views.application.applicationForm.form.paramSetting') }}
              </el-button>
            </div>
          </template>
          <el-select
            @change="model_change"
            @wheel="wheel"
            :teleported="false"
            v-model="form_data.model_id"
            placeholder="请选择图片生成模型"
            class="w-full"
            popper-class="select-model"
            :clearable="true"
          >
            <el-option-group
              v-for="(value, label) in modelOptions"
              :key="value"
              :label="relatedObject(providerOptions, label, 'provider')?.name"
            >
              <el-option
                v-for="item in value.filter((v: any) => v.status === 'SUCCESS')"
                :key="item.id"
                :label="item.name"
                :value="item.id"
                class="flex-between"
              >
                <div class="flex align-center">
                  <span
                    v-html="relatedObject(providerOptions, label, 'provider')?.icon"
                    class="model-icon mr-8"
                  ></span>
                  <span>{{ item.name }}</span>
                  <el-tag v-if="item.permission_type === 'PUBLIC'" type="info" class="info-tag ml-8"
                    >公用
                  </el-tag>
                </div>
                <el-icon class="check-icon" v-if="item.id === form_data.model_id">
                  <Check />
                </el-icon>
              </el-option>
              <!-- 不可用 -->
              <el-option
                v-for="item in value.filter((v: any) => v.status !== 'SUCCESS')"
                :key="item.id"
                :label="item.name"
                :value="item.id"
                class="flex-between"
                disabled
              >
                <div class="flex">
                  <span
                    v-html="relatedObject(providerOptions, label, 'provider')?.icon"
                    class="model-icon mr-8"
                  ></span>
                  <span>{{ item.name }}</span>
                  <span class="danger">（不可用）</span>
                </div>
                <el-icon class="check-icon" v-if="item.id === form_data.model_id">
                  <Check />
                </el-icon>
              </el-option>
            </el-option-group>
          </el-select>
        </el-form-item>


        <el-form-item
          label="提示词(正向)"
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
                <span>提示词(正向)<span class="danger">*</span></span>
              </div>
              <el-tooltip effect="dark" placement="right" popper-class="max-w-200">
                <template #content
                  >正向提示词，用来描述生成图像中期望包含的元素和视觉特点
                </template>
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>
            </div>
          </template>
          <MdEditorMagnify
            @wheel="wheel"
            title="提示词(正向)"
            v-model="form_data.prompt"
            style="height: 150px"
            @submitDialog="submitDialog"
          />
        </el-form-item>
        <el-form-item
          label="提示词(负向)"
          prop="prompt"
          :rules="{
            required: false,
            message: '请输入提示词',
            trigger: 'blur'
          }"
        >
          <template #label>
            <div class="flex align-center">
              <div class="mr-4">
                <span>提示词(负向)</span>
              </div>
              <el-tooltip effect="dark" placement="right" popper-class="max-w-200">
                <template #content
                  >反向提示词，用来描述不希望在画面中看到的内容，可以对画面进行限制。
                </template>
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>
            </div>
          </template>
          <MdEditorMagnify
            @wheel="wheel"
            title="提示词(负向)"
            v-model="form_data.negative_prompt"
            placeholder="请描述不想生成的图片内容，比如：颜色、血腥内容"
            style="height: 150px"
            @submitDialog="submitNegativeDialog"
          />
        </el-form-item>
        <!--
        <el-form-item>
          <template #label>
            <div class="flex-between">
              <div>历史聊天记录</div>
              <el-select v-model="form_data.dialogue_type" type="small" style="width: 100px">
                <el-option label="节点" value="NODE" />
                <el-option label="工作流" value="WORKFLOW" />
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
        -->
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
import { relatedObject } from '@/utils/utils'
import type { Provider } from '@/api/type/model'
import applicationApi from '@/api/application'
import { app } from '@/main'
import useStore from '@/stores'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import type { FormInstance } from 'element-plus'
import AIModeParamSettingDialog from '@/views/application/component/AIModeParamSettingDialog.vue'

const { model } = useStore()

const {
  params: { id }
} = app.config.globalProperties.$route as any

const props = defineProps<{ nodeModel: any }>()
const modelOptions = ref<any>(null)
const providerOptions = ref<Array<Provider>>([])
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

const defaultPrompt = `{{开始.question}}`

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

function getProvider() {
  model.asyncGetProvider().then((res: any) => {
    providerOptions.value = res?.data
  })
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
  getProvider()

  set(props.nodeModel, 'validate', validate)
})
</script>

<style scoped lang="scss"></style>
