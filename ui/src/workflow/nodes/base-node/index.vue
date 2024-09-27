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
        <MdEditorMagnify
          @wheel="wheel"
          title="开场白"
          v-model="form_data.prologue"
          style="height: 150px"
          @submitDialog="submitDialog"
        />
      </el-form-item>
      <div class="flex-between mb-16">
        <h5 class="lighter">全局变量</h5>
        <el-button link type="primary" @click="openAddDialog()">
          <el-icon class="mr-4"><Plus /></el-icon> 添加
        </el-button>
      </div>
      <el-table
        v-if="props.nodeModel.properties.input_field_list?.length > 0"
        :data="props.nodeModel.properties.input_field_list"
        class="mb-16"
      >
        <el-table-column prop="name" label="变量名" />
        <el-table-column prop="variable" label="变量" />
        <el-table-column label="输入类型">
          <template #default="{ row }">
            <el-tag type="info" class="info-tag" v-if="row.type === 'input'">文本框</el-tag>
            <el-tag type="info" class="info-tag" v-if="row.type === 'date'">日期</el-tag>
            <el-tag type="info" class="info-tag" v-if="row.type === 'select'">下拉选项</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="必填">
          <template #default="{ row }">
            <div @click.stop>
              <el-switch disabled size="small" v-model="row.is_required" />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="assignment_method" label="赋值方式">
          <template #default="{ row }">
            {{ row.assignment_method === 'user_input' ? '用户输入' : '接口传参' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" align="left" width="80">
          <template #default="{ row, $index }">
            <span class="mr-4">
              <el-tooltip effect="dark" content="修改" placement="top">
                <el-button type="primary" text @click.stop="openAddDialog(row, $index)">
                  <el-icon><EditPen /></el-icon>
                </el-button>
              </el-tooltip>
            </span>
            <el-tooltip effect="dark" content="删除" placement="top">
              <el-button type="primary" text @click="deleteField($index)">
                <el-icon>
                  <Delete />
                </el-icon>
              </el-button>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>
      <el-form-item>
        <template #label>
          <div class="flex-between">
            <div class="flex align-center">
              <span class="mr-4">语音输入</span>
              <el-tooltip
                effect="dark"
                content="开启后，需要设定语音转文本模型，语音输入完成后会转化为文字直接发送提问"
                placement="right"
              >
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>
            </div>
            <el-switch size="small" v-model="form_data.stt_model_enable" />
          </div>
        </template>

        <el-select
          v-show="form_data.stt_model_enable"
          v-model="form_data.stt_model_id"
          class="w-full"
          popper-class="select-model"
          placeholder="请选择语音识别模型"
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
                <el-tag v-if="item.permission_type === 'PUBLIC'" type="info" class="info-tag ml-8"
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
          <div class="flex-between">
            <span class="mr-4">语音播放</span>
            <el-switch size="small" v-model="form_data.tts_model_enable" />
          </div>
        </template>
        <el-radio-group v-model="form_data.tts_type" v-show="form_data.tts_model_enable">
          <el-radio label="浏览器播放(免费)" value="BROWSER" />
          <el-radio label="TTS模型" value="TTS" />
        </el-radio-group>
        <el-select
          v-if="form_data.tts_type === 'TTS' && form_data.tts_model_enable"
          v-model="form_data.tts_model_id"
          class="w-full"
          popper-class="select-model"
          placeholder="请选择语音合成模型"
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
                <el-tag v-if="item.permission_type === 'PUBLIC'" type="info" class="info-tag ml-8"
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

    <FieldFormDialog ref="FieldFormDialogRef" @refresh="refreshFieldList" />
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
import type { Provider } from '@/api/type/model'
import FieldFormDialog from './component/FieldFormDialog.vue'
import { MsgError, MsgWarning } from '@/utils/message'
import { t } from '@/locales'
const { model } = useStore()

const {
  params: { id }
} = app.config.globalProperties.$route as any

const props = defineProps<{ nodeModel: any }>()

const sttModelOptions = ref<any>(null)
const ttsModelOptions = ref<any>(null)
const providerOptions = ref<Array<Provider>>([])

const form = {
  name: '',
  desc: '',
  prologue: t('views.application.prompt.defaultPrologue')
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

function submitDialog(val: string) {
  set(props.nodeModel.properties.node_data, 'prologue', val)
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
  if (
    form_data.value.tts_model_enable &&
    !form_data.value.tts_model_id &&
    form_data.value.tts_type === 'TTS'
  ) {
    return Promise.reject({ node: props.nodeModel, errMessage: '请选择语音播放模型' })
  }
  if (form_data.value.stt_model_enable && !form_data.value.stt_model_id) {
    return Promise.reject({ node: props.nodeModel, errMessage: '请选择语音输入模型' })
  }
  return baseNodeFormRef.value?.validate().catch((err) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

function getProvider() {
  model.asyncGetProvider().then((res: any) => {
    providerOptions.value = res?.data
  })
}

function getSTTModel() {
  applicationApi.getApplicationSTTModel(id).then((res: any) => {
    sttModelOptions.value = groupBy(res?.data, 'provider')
  })
}

function getTTSModel() {
  applicationApi.getApplicationTTSModel(id).then((res: any) => {
    ttsModelOptions.value = groupBy(res?.data, 'provider')
  })
}

const currentIndex = ref(null)
const FieldFormDialogRef = ref()
const inputFieldList = ref<any[]>([])

function openAddDialog(data?: any, index?: any) {
  if (typeof index !== 'undefined') {
    currentIndex.value = index
  }

  FieldFormDialogRef.value.open(data)
}

function deleteField(index: any) {
  inputFieldList.value.splice(index, 1)
  props.nodeModel.graphModel.eventCenter.emit('refreshFieldList', inputFieldList.value)
}

function refreshFieldList(data: any) {
  for (let i = 0; i < inputFieldList.value.length; i++) {
    if (inputFieldList.value[i].variable === data.variable && currentIndex.value !== i) {
      MsgError('变量已存在: ' + data.variable)
      return
    }
  }
  if (currentIndex.value !== null) {
    inputFieldList.value.splice(currentIndex.value, 1, data)
  } else {
    inputFieldList.value.push(data)
  }
  currentIndex.value = null
  FieldFormDialogRef.value.close()
  props.nodeModel.graphModel.eventCenter.emit('refreshFieldList', inputFieldList.value)
}

onMounted(() => {
  set(props.nodeModel, 'validate', validate)
  if (props.nodeModel.properties.input_field_list) {
    props.nodeModel.properties.input_field_list.forEach((item: any) => {
      inputFieldList.value.push(item)
    })
  }
  set(props.nodeModel.properties, 'input_field_list', inputFieldList)
  if (!props.nodeModel.properties.node_data.tts_type) {
    set(props.nodeModel.properties.node_data, 'tts_type', 'BROWSER')
  }
  getProvider()
  getTTSModel()
  getSTTModel()
})
</script>
<style lang="scss" scoped></style>
