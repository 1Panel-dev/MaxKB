<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">{{ $t('views.applicationWorkflow.nodeSetting') }}</h5>
    <el-card shadow="never" class="card-never">
      <el-form
        @submit.prevent
        :model="form_data"
        label-position="top"
        require-asterisk-position="right"
        label-width="auto"
        ref="DatasetNodeFormRef"
      >
        <el-form-item :label="$t('views.log.selectDataset')">
          <template #label>
            <div class="flex-between">
              <span>{{ $t('views.log.selectDataset') }}</span>
              <el-button type="primary" link @click="openDatasetDialog">
                <el-icon><Plus /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="w-full">
            <el-text type="info" v-if="form_data.dataset_id_list?.length === 0">
              {{ $t('views.application.applicationForm.form.relatedKnowledge.placeholder') }}
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
                  <AppAvatar
                    v-else-if="relatedObject(datasetList, item, 'id')?.type === '2'"
                    class="mr-8 avatar-purple"
                    shape="square"
                    :size="20"
                    style="background: none"
                  >
                    <img src="@/assets/logo_lark.svg" style="width: 100%" alt="" />
                  </AppAvatar>
                  <AppAvatar v-else class="mr-8 avatar-blue" shape="square" :size="20">
                    <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                  </AppAvatar>

                  <div class="ellipsis" :title="relatedObject(datasetList, item, 'id')?.name">
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
        <el-form-item :label="$t('views.applicationWorkflow.nodes.searchDatasetNode.searchParam')">
          <template #label>
            <div class="flex-between">
              <span>{{ $t('views.applicationWorkflow.nodes.searchDatasetNode.searchParam') }}</span>
              <el-button type="primary" link @click="openParamSettingDialog">
                <el-icon><Setting /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="w-full">
            <el-row>
              <el-col :span="12" class="color-secondary lighter">{{
                $t('views.application.applicationForm.dialog.selectSearchMode')
              }}</el-col>
              <el-col :span="12" class="lighter">
                {{
                  $t(SearchMode[form_data.dataset_setting.search_mode as keyof typeof SearchMode])
                }}</el-col
              >
              <el-col :span="12" class="color-secondary lighter">
                {{ $t('views.application.applicationForm.dialog.similarityThreshold') }}</el-col
              >
              <el-col :span="12" class="lighter">
                {{ form_data.dataset_setting.similarity?.toFixed(3) }}</el-col
              >
              <el-col :span="12" class="color-secondary lighter">{{
                $t('views.application.applicationForm.dialog.topReferences')
              }}</el-col>
              <el-col :span="12" class="lighter"> {{ form_data.dataset_setting.top_n }}</el-col>
              <el-col :span="12" class="color-secondary lighter">
                {{ $t('views.application.applicationForm.dialog.maxCharacters') }}</el-col
              >
              <el-col :span="12" class="lighter">
                {{ form_data.dataset_setting.max_paragraph_char_number }}</el-col
              >
            </el-row>
          </div>
        </el-form-item>
        <el-form-item
          :label="$t('views.applicationWorkflow.nodes.searchDatasetNode.searchQuestion.label')"
          prop="question_reference_address"
          :rules="{
            message: $t(
              'views.applicationWorkflow.nodes.searchDatasetNode.searchQuestion.requiredMessage'
            ),
            trigger: 'blur',
            required: true
          }"
        >
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            :placeholder="
              $t('views.applicationWorkflow.nodes.searchDatasetNode.searchQuestion.placeholder')
            "
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
  set(props.nodeModel.properties.node_data, 'dataset_setting', data.dataset_setting)
}

const openParamSettingDialog = () => {
  ParamSettingDialogRef.value?.open(form_data.value, 'WORK_FLOW')
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
