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
        ref="knowledgeNodeFormRef"
        hide-required-asterisk
      >
        <el-form-item>
          <template #label>
            <div class="flex-between">
              <span>
                {{ $t('views.applicationWorkflow.nodes.searchDocumentNode.selectKnowledge') }}</span
              >
              <span>
                <el-button
                  v-if="form_data.search_scope_type === 'custom'"
                  type="primary"
                  link
                  @click="openknowledgeDialog"
                >
                  <AppIcon iconName="app-add-outlined"></AppIcon>
                </el-button>
                <el-select
                  :teleported="false"
                  size="small"
                  v-model="form_data.search_scope_type"
                  style="width: 85px"
                >
                  <el-option
                    :label="$t('views.applicationWorkflow.nodes.searchDocumentNode.custom')"
                    value="custom"
                  />
                  <el-option
                    :label="$t('views.applicationWorkflow.variable.Referencing')"
                    value="referencing"
                  />
                </el-select>
              </span>
            </div>
          </template>
          <div class="w-full" v-if="form_data.search_scope_type === 'custom'">
            <el-text type="info" v-if="form_data.knowledge_id_list?.length === 0">
              {{ $t('views.application.form.relatedKnowledge.placeholder') }}
            </el-text>
            <template v-for="(item, index) in form_data.knowledge_id_list" :key="index" v-else>
              <div class="flex-between border border-r-6 white-bg mb-4" style="padding: 5px 8px">
                <div class="flex align-center" style="line-height: 20px">
                  <KnowledgeIcon
                    :type="relatedObject(knowledgeList, item, 'id')?.type"
                    class="mr-8"
                    :size="20"
                  />

                  <div class="ellipsis" :title="relatedObject(knowledgeList, item, 'id')?.name">
                    {{ relatedObject(knowledgeList, item, 'id')?.name }}
                  </div>
                </div>
                <el-button text @click="removeknowledge(item)">
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
            </template>
          </div>
          <div class="w-full" v-else>
            <el-form-item
              prop="search_scope_reference"
              :rules="{
                message: $t('views.applicationWorkflow.variable.placeholder'),
                trigger: 'blur',
                required: true,
              }"
            >
              <template #label>
                <div class="flex-between">
                  <span>
                    {{ $t('views.applicationWorkflow.nodes.searchDocumentNode.select_variable') }}
                    <span class="color-danger">*</span>
                  </span>
                  <span>
                    <el-select
                      :teleported="false"
                      size="small"
                      v-model="form_data.search_scope_source"
                      style="width: 95px"
                      @change="form_data.search_scope_reference = []"
                    >
                      <el-option
                        :label="
                          $t('views.applicationWorkflow.nodes.searchDocumentNode.knowledge_list')
                        "
                        value="knowledge"
                      />
                      <el-option
                        :label="
                          $t('views.applicationWorkflow.nodes.searchDocumentNode.document_list')
                        "
                        value="document"
                      />
                    </el-select>
                  </span>
                </div>
              </template>
              <NodeCascader
                ref="nodeCascaderRef"
                :nodeModel="nodeModel"
                class="w-full"
                :placeholder="$t('views.applicationWorkflow.variable.placeholder')"
                v-model="form_data.search_scope_reference"
              />
            </el-form-item>
          </div>
        </el-form-item>
        <el-form-item
          :label="$t('views.applicationWorkflow.nodes.searchKnowledgeNode.searchParam')"
        >
          <template #label>
            <div class="flex-between">
              <span
                >{{ $t('views.applicationWorkflow.nodes.searchKnowledgeNode.searchParam') }}
              </span>
              <el-button type="primary" link @click="openParamSettingDialog">
                <AppIcon iconName="app-setting"></AppIcon>
              </el-button>
            </div>
          </template>
          <div class="w-full">
            <el-row>
              <el-col :span="12" class="color-secondary lighter">{{
                $t('views.application.dialog.selectSearchMode')
              }}</el-col>
              <el-col :span="12" class="lighter">
                {{
                  $t(SearchMode[form_data.knowledge_setting.search_mode as keyof typeof SearchMode])
                }}</el-col
              >
              <el-col :span="12" class="color-secondary lighter">
                {{ $t('views.application.dialog.similarityThreshold') }}</el-col
              >
              <el-col :span="12" class="lighter">
                {{ form_data.knowledge_setting.similarity?.toFixed(3) }}</el-col
              >
              <el-col :span="12" class="color-secondary lighter">{{
                $t('views.application.dialog.topReferences')
              }}</el-col>
              <el-col :span="12" class="lighter"> {{ form_data.knowledge_setting.top_n }}</el-col>
              <el-col :span="12" class="color-secondary lighter">
                {{ $t('views.application.dialog.maxCharacters') }}</el-col
              >
              <el-col :span="12" class="lighter">
                {{ form_data.knowledge_setting.max_paragraph_char_number }}</el-col
              >
            </el-row>
          </div>
        </el-form-item>
        <el-form-item
          prop="question_reference_address"
          :rules="{
            message: $t(
              'views.applicationWorkflow.nodes.searchKnowledgeNode.searchQuestion.requiredMessage',
            ),
            trigger: 'blur',
            required: true,
          }"
        >
          <template #label>
            <div class="flex-between">
              <span>
                {{ $t('views.applicationWorkflow.nodes.searchKnowledgeNode.searchQuestion.label') }}
                <span class="color-danger">*</span></span
              >
            </div>
          </template>
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            :placeholder="
              $t('views.applicationWorkflow.nodes.searchKnowledgeNode.searchQuestion.placeholder')
            "
            v-model="form_data.question_reference_address"
          />
        </el-form-item>
        <el-form-item
          prop="show_knowledge"
          :rules="{
            message: $t(
              'views.applicationWorkflow.nodes.searchKnowledgeNode.showKnowledge.requiredMessage',
            ),
            trigger: 'blur',
            required: true,
          }"
          @click.prevent
        >
          <template #label>
            <div class="flex-between">
              <span>
                {{ $t('views.applicationWorkflow.nodes.searchKnowledgeNode.showKnowledge.label') }}
                <span class="color-danger">*</span></span
              >
            </div>
          </template>
          <el-switch size="small" v-model="form_data.show_knowledge" />
        </el-form-item>
      </el-form>
    </el-card>
    <ParamSettingDialog ref="ParamSettingDialogRef" @refresh="refreshParam" />
    <AddknowledgeDialog
      ref="AddknowledgeDialogRef"
      @addData="addKnowledge"
      :data="knowledgeList"
      :loading="knowledgeLoading"
    />
  </NodeContainer>
</template>
<script setup lang="ts">
import { set } from 'lodash'

import NodeContainer from '@/workflow/common/NodeContainer.vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import AddknowledgeDialog from '@/views/application/component/AddKnowledgeDialog.vue'
import ParamSettingDialog from '@/views/application/component/ParamSettingDialog.vue'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted } from 'vue'
import { relatedObject } from '@/utils/array'
import { SearchMode } from '@/enums/application'
import AppIcon from '@/components/app-icon/AppIcon.vue'

const props = defineProps<{ nodeModel: any }>()
const nodeCascaderRef = ref()
const form = {
  knowledge_id_list: [],
  knowledge_setting: {
    top_n: 3,
    similarity: 0.6,
    max_paragraph_char_number: 5000,
    search_mode: 'embedding',
  },
  question_reference_address: [],
  show_knowledge: false,
  search_scope_type: 'custom',
  search_scope_source: 'knowledge',
  search_scope_reference: [],
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

const knowledgeNodeFormRef = ref<FormInstance>()
const ParamSettingDialogRef = ref<InstanceType<typeof ParamSettingDialog>>()
const AddknowledgeDialogRef = ref<InstanceType<typeof AddknowledgeDialog>>()
const knowledgeList = ref<any>([])
const knowledgeLoading = ref(false)

function refreshParam(data: any) {
  set(props.nodeModel.properties.node_data, 'knowledge_setting', data.knowledge_setting)
}

const openParamSettingDialog = () => {
  ParamSettingDialogRef.value?.open(form_data.value, 'WORK_FLOW')
}

function removeknowledge(id: any) {
  const list = props.nodeModel.properties.node_data.knowledge_id_list.filter((v: any) => v !== id)
  set(props.nodeModel.properties.node_data, 'knowledge_id_list', list)
}

function addKnowledge(val: Array<any>) {
  set(
    props.nodeModel.properties.node_data,
    'knowledge_id_list',
    val.map((item) => item.id),
  )
  set(props.nodeModel.properties.node_data, 'knowledge_list', val)
  knowledgeList.value = val
}

function openknowledgeDialog() {
  if (AddknowledgeDialogRef.value) {
    AddknowledgeDialogRef.value.open(form_data.value.knowledge_id_list)
  }
}

const validate = () => {
  return Promise.all([
    nodeCascaderRef.value.validate(),
    knowledgeNodeFormRef.value?.validate(),
  ]).catch((err) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

onMounted(() => {
  // console.log(props.nodeModel.properties.node_data)
  knowledgeList.value = props.nodeModel.properties.node_data.knowledge_list
  form_data.value.show_knowledge = form_data.value.show_knowledge
    ? form_data.value.show_knowledge
    : false
  form_data.value.search_scope_type = form_data.value.search_scope_type
    ? form_data.value.search_scope_type
    : 'custom'
  form_data.value.search_scope_source = form_data.value.search_scope_source
    ? form_data.value.search_scope_source
    : 'knowledge'
  form_data.value.knowledge_id_list = form_data.value.knowledge_id_list
    ? form_data.value.knowledge_id_list
    : []
  set(props.nodeModel, 'validate', validate)
})
</script>
<style lang="scss" scoped></style>
