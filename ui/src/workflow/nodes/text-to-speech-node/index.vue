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
          label="语音合成模型"
          prop="tts_model_id"
          :rules="{
            required: true,
            message: '请选择语音合成模型',
            trigger: 'change'
          }"
        >
          <template #label>
            <div class="flex-between w-full">
              <div>
                <span>语音合成模型<span class="danger">*</span></span>
              </div>
              <el-button
                type="primary"
                link
                @click="openTTSParamSettingDialog"
                :disabled="!form_data.tts_model_id"
                class="mr-4"
              >
                {{ $t('views.application.applicationForm.form.paramSetting') }}
              </el-button>
            </div>
          </template>
          <el-select
            @change="model_change"
            @wheel="wheel"
            :teleported="false"
            v-model="form_data.tts_model_id"
            placeholder="请选择语音合成模型"
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
                  <span class="ellipsis" :title="item.name">{{ item.name }}</span>
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

                  <span class="ellipsis" :title="item.name">{{ item.name }}</span>
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
          prop="content_list"
          label="选择文本内容"
          :rules="{
            message: '选择文本内容',
            trigger: 'blur',
            required: true
          }"
        >
          <template #label>
            <div class="flex-between w-full">
              <div>
                <span>选择文本内容<span class="danger">*</span></span>
              </div>
            </div>
          </template>
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            placeholder="选择文本内容"
            v-model="form_data.content_list"
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
          <el-switch size="small" v-model="form_data.is_result" />
        </el-form-item>
      </el-form>
    </el-card>
  </NodeContainer>
  <TTSModeParamSettingDialog ref="TTSModeParamSettingDialogRef" @refresh="refreshTTSForm" />
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
const providerOptions = ref<Array<Provider>>([])

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

function getProvider() {
  model.asyncGetProvider().then((res: any) => {
    providerOptions.value = res?.data
  })
}

const openTTSParamSettingDialog = () => {
  const model_id = form_data.value.tts_model_id
  if (!model_id) {
    MsgSuccess(t('请选择语音播放模型'))
    return
  }
  TTSModeParamSettingDialogRef.value?.open(model_id, id, form_data.value.model_params_setting)
}
const refreshTTSForm = (data: any) => {
  form_data.value.model_params_setting = data
}

const model_change = (model_id?: string) => {}

onMounted(() => {
  getModel()
  getProvider()

  set(props.nodeModel, 'validate', validate)
})
</script>

<style scoped lang="scss"></style>
