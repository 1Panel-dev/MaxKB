<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">节点设置</h5>
    <el-card shadow="never" class="card-never">
      <el-form
        @submit.prevent
        @mousemove.stop
        @mousedown.stop
        @keydown.stop
        @click.stop
        :model="form_data"
        label-position="top"
        require-asterisk-position="right"
        label-width="auto"
        ref="DatasetNodeFormRef"
      >
        <el-form-item label="选择知识库">
          <template #label>
            <div class="flex-between">
              <span>选择知识库</span>
              <el-button type="primary" link @click="openDatasetDialog">
                <el-icon><Plus /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="w-full">
            <el-text type="info" v-if="form_data.dataset_id_list?.length === 0">
              关联的知识库展示在这里
            </el-text>
            <template v-for="(item, index) in form_data.dataset_id_list" :key="index" v-else>
              <div class="flex-between border border-r-4 white-bg mb-4" style="padding: 5px 8px">
                <div class="flex align-center" style="line-height: 20px">
                  <AppAvatar
                    v-if="relatedObject(datasetList, item, 'id')?.type === '1'"
                    class="mr-8 avatar-purple"
                    shape="square"
                    :size="20"
                  >
                    <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
                  </AppAvatar>

                  <AppAvatar v-else class="mr-8 avatar-blue" shape="square" :size="20">
                    <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                  </AppAvatar>
                  <div class="ellipsis">
                    {{ relatedObject(datasetList, item, 'id')?.name }}
                  </div>
                </div>
                <el-button text @click="removeDataset(item)">
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
            </template>
          </div>
        </el-form-item>
        <el-form-item label="检索参数">
          <template #label>
            <div class="flex-between">
              <span>检索参数</span>
              <el-button type="primary" link @click="openParamSettingDialog">
                <el-icon><Setting /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="w-full">
            <el-row>
              <el-col :span="12" class="color-secondary lighter">检索模式</el-col>
              <el-col :span="12" class="lighter">
                {{
                  SearchMode[form_data.dataset_setting.search_mode as keyof typeof SearchMode]
                }}</el-col
              >
              <el-col :span="12" class="color-secondary lighter"> 相似度高于</el-col>
              <el-col :span="12" class="lighter">
                {{ form_data.dataset_setting.similarity }}</el-col
              >
              <el-col :span="12" class="color-secondary lighter"> 引用分段 Top</el-col>
              <el-col :span="12" class="lighter"> {{ form_data.dataset_setting.top_n }}</el-col>
              <el-col :span="12" class="color-secondary lighter"> 最大引用字符数</el-col>
              <el-col :span="12" class="lighter">
                {{ form_data.dataset_setting.max_paragraph_char_number }}</el-col
              >
            </el-row>
          </div>
        </el-form-item>
        <el-form-item
          label="检索问题输入"
          prop="question_reference_address"
          :rules="{
            message: '请选择检索问题输入',
            trigger: 'blur',
            required: true
          }"
        >
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            placeholder="请选择检索问题输入"
            v-model="form_data.question_reference_address"
          />
        </el-form-item>
      </el-form>
    </el-card>
    <ParamSettingDialog ref="ParamSettingDialogRef" @refresh="refreshParam" />
    <AddDatasetDialog
      ref="AddDatasetDialogRef"
      @addData="addDataset"
      :data="datasetList"
      @refresh="refresh"
      :loading="datasetLoading"
    />
  </NodeContainer>
</template>
<script setup lang="ts">
import { set } from 'lodash'
import { app } from '@/main'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import AddDatasetDialog from '@/views/application/component/AddDatasetDialog.vue'
import ParamSettingDialog from '@/views/application/component/ParamSettingDialog.vue'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted } from 'vue'
import { relatedObject } from '@/utils/utils'
import { SearchMode } from '@/enums/application'
import useStore from '@/stores'
const { dataset, application, user } = useStore()
const {
  params: { id }
} = app.config.globalProperties.$route as any

const props = defineProps<{ nodeModel: any }>()
const nodeCascaderRef = ref()
const form = {
  dataset_id_list: [],
  dataset_setting: {
    top_n: 3,
    similarity: 0.6,
    max_paragraph_char_number: 5000,
    search_mode: 'embedding'
  },
  question_reference_address: []
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

const DatasetNodeFormRef = ref<FormInstance>()
const ParamSettingDialogRef = ref<InstanceType<typeof ParamSettingDialog>>()
const AddDatasetDialogRef = ref<InstanceType<typeof AddDatasetDialog>>()
const datasetList = ref<any>([])
const datasetLoading = ref(false)

function refreshParam(data: any) {
  set(props.nodeModel.properties.node_data, 'dataset_setting', data)
}

const openParamSettingDialog = () => {
  ParamSettingDialogRef.value?.open(form_data.value.dataset_setting, 'WORK_FLOW')
}

function removeDataset(id: any) {
  const list = props.nodeModel.properties.node_data.dataset_id_list.filter((v: any) => v !== id)
  set(props.nodeModel.properties.node_data, 'dataset_id_list', list)
}

function addDataset(val: Array<string>) {
  set(props.nodeModel.properties.node_data, 'dataset_id_list', val)
}

function openDatasetDialog() {
  if (AddDatasetDialogRef.value) {
    AddDatasetDialogRef.value.open(form_data.value.dataset_id_list)
  }
}

function getDataset() {
  if (id) {
    application.asyncGetApplicationDataset(id, datasetLoading).then((res: any) => {
      datasetList.value = res.data
    })
  } else {
    dataset.asyncGetAllDataset(datasetLoading).then((res: any) => {
      datasetList.value = res.data?.filter((v: any) => v.user_id === user.userInfo?.id)
    })
  }
}
function refresh() {
  getDataset()
}

const validate = () => {
  return Promise.all([
    nodeCascaderRef.value.validate(),
    DatasetNodeFormRef.value?.validate()
  ]).catch((err) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

onMounted(() => {
  getDataset()
  set(props.nodeModel, 'validate', validate)
})
</script>
<style lang="scss" scoped></style>
