<template>
  <NodeContainer :nodeModel="nodeModel">
    <el-form
      @submit.prevent
      :model="form_data"
      label-position="top"
      require-asterisk-position="right"
      class="mb-24"
      label-width="auto"
      ref="baseNodeFormRef"
    >
      <el-form-item
        label="应用名称"
        prop="name"
        :rules="{
          message: '应用名称不能为空',
          trigger: 'blur',
          required: true
        }"
      >
        <el-input
          v-model="form_data.name"
          maxlength="64"
          placeholder="请输入应用名称"
          show-word-limit
          @blur="form_data.name = form_data.name?.trim()"
        />
      </el-form-item>
      <el-form-item label="应用描述">
        <el-input
          v-model="form_data.desc"
          placeholder="请输入应用描述"
          :rows="3"
          type="textarea"
          maxlength="256"
          show-word-limit
        />
      </el-form-item>
      <el-form-item label="开场白">
        <MdEditor
          @wheel="wheel"
          style="height: 150px"
          v-model="form_data.prologue"
          :preview="false"
          :toolbars="[]"
          class="reply-node-editor"
          :footers="footers"
        >
          <template #defFooters>
            <el-button text type="info" @click="openDialog">
              <AppIcon iconName="app-magnify" style="font-size: 16px"></AppIcon>
            </el-button>
          </template
          >
        </MdEditor>
      </el-form-item>
      <el-form-item>
        <template #label>
          <div class="flex align-center">
            <span class="mr-4">语音输入</span>
            <el-tooltip
              effect="dark"
              content="开启后，需要设定语音转文本模型，语音输入完成后会转化为文字直接发送提问"
              placement="right"
            >
              <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
            </el-tooltip>
            <el-switch v-model="form_data.stt_model_enable" />
          </div>
        </template>
        <el-select
          v-model="form_data.stt_model_id"
          class="w-full"
          popper-class="select-model"
        >
          <el-option-group
            v-for="(value, label) in sttModelOptions"
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
                <el-tag
                  v-if="item.permission_type === 'PUBLIC'"
                  type="info"
                  class="info-tag ml-8"
                >公用
                </el-tag>
              </div>
              <el-icon class="check-icon" v-if="item.id === form_data.stt_model_id">
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
                <span class="danger">{{
                    $t('views.application.applicationForm.form.aiModel.unavailable')
                  }}</span>
              </div>
              <el-icon class="check-icon" v-if="item.id === form_data.stt_model_id">
                <Check />
              </el-icon>
            </el-option>
          </el-option-group>
        </el-select>
      </el-form-item>
      <el-form-item>
        <template #label>
          <div class="flex align-center">
            <span class="mr-4">语音播放</span>
            <el-switch v-model="form_data.tts_model_enable" />
          </div>
        </template>
        <el-select
          v-model="form_data.tts_model_id"
          class="w-full"
          popper-class="select-model"
        >
          <el-option-group
            v-for="(value, label) in ttsModelOptions"
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
                <el-tag
                  v-if="item.permission_type === 'PUBLIC'"
                  type="info"
                  class="info-tag ml-8"
                >公用
                </el-tag>
              </div>
              <el-icon class="check-icon" v-if="item.id === form_data.tts_model_id">
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
                <span class="danger">{{
                    $t('views.application.applicationForm.form.aiModel.unavailable')
                  }}</span>
              </div>
              <el-icon class="check-icon" v-if="item.id === form_data.tts_model_id">
                <Check />
              </el-icon>
            </el-option>
          </el-option-group>
        </el-select>
      </el-form-item>
    </el-form>
    <!-- 回复内容弹出层 -->
    <el-dialog v-model="dialogVisible" title="开场白" append-to-body>
      <MdEditor v-model="cloneContent" :preview="false" :toolbars="[]" :footers="[]"></MdEditor>
      <template #footer>
        <div class="dialog-footer mt-24">
          <el-button type="primary" @click="submitDialog"> 确认</el-button>
        </div>
      </template>
    </el-dialog>
  </NodeContainer>
</template>
<script setup lang="ts">
import { app } from '@/main'

import { groupBy, set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted } from 'vue'
import { relatedObject } from '@/utils/utils'
import useStore from '@/stores'
import applicationApi from '@/api/application'
const { model } = useStore()

const {
  params: { id }
} = app.config.globalProperties.$route as any

const props = defineProps<{ nodeModel: any }>()

const sttModelOptions = ref<any>(null)
const ttsModelOptions = ref<any>(null)
const providerOptions = ref<any>(null)

const form = {
  name: '',
  desc: '',
  prologue:
    '您好，我是 MaxKB 小助手，您可以向我提出 MaxKB 使用问题。\n- MaxKB 主要功能有什么？\n- MaxKB 支持哪些大语言模型？\n- MaxKB 支持哪些文档类型？'
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
const dialogVisible = ref(false)
const cloneContent = ref('')
const footers: any = [null, '=', 0]
function openDialog() {
  cloneContent.value = form_data.value.prologue
  dialogVisible.value = true
}
function submitDialog() {
  set(props.nodeModel.properties.node_data, 'prologue', cloneContent.value)
  dialogVisible.value = false
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

const baseNodeFormRef = ref<FormInstance>()

const validate = () => {
  return baseNodeFormRef.value?.validate().catch((err) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

function getProvider() {
  model
    .asyncGetProvider()
    .then((res: any) => {
      providerOptions.value = res?.data
    })
}


function getSTTModel() {
  applicationApi
    .getApplicationSTTModel(id)
    .then((res: any) => {
      sttModelOptions.value = groupBy(res?.data, 'provider')
    })
}

function getTTSModel() {
  applicationApi
    .getApplicationTTSModel(id)
    .then((res: any) => {
      ttsModelOptions.value = groupBy(res?.data, 'provider')
    })
}


onMounted(() => {
  set(props.nodeModel, 'validate', validate)
  getProvider()
  getTTSModel()
  getSTTModel()

})
</script>
<style lang="scss" scoped>
.reply-node-editor {
  :deep(.md-editor-footer) {
    border: none !important;
  }
}
</style>
