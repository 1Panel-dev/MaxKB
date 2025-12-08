<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">{{ $t('views.applicationWorkflow.nodeSetting') }}</h5>
    <el-card shadow="never" class="card-never">
      <el-form
        @submit.prevent
        :model="form_data"
        label-position="top"
        hide-required-asterisk
        label-width="auto"
        ref="knowledgeNodeFormRef"
      >
        <el-form-item>
          <template #label>
            <div class="flex-between">
              <span>
                {{ $t('views.applicationWorkflow.nodes.searchDocumentNode.selectKnowledge') }}
              </span>
              <span>
                <el-button
                  v-if="form_data.search_scope_type === 'custom'"
                  type="primary"
                  link
                  @click="openKnowledgeDialog"
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
                <el-button text @click="removeKnowledge(item)">
                  <el-icon>
                    <Close />
                  </el-icon>
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
                    <span class="color-danger">*</span></span
                  >
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
          :label="$t('views.applicationWorkflow.nodes.searchDocumentNode.searchSetting')"
        >
          <el-radio-group v-model="form_data.search_mode">
            <el-radio value="auto">
              <span class="flex align-center">
                {{ $t('views.applicationWorkflow.nodes.searchDocumentNode.auto') }}
                <el-tooltip
                  :content="$t('views.applicationWorkflow.nodes.searchDocumentNode.autoTooltip')"
                  placement="top"
                >
                  <AppIcon iconName="app-warning" class="app-warning-icon ml-4"></AppIcon>
                </el-tooltip>
              </span>
            </el-radio>
            <el-radio value="custom" v-if="form_data.search_scope_type === 'custom'">
              <span class="flex align-center">
                {{ $t('views.applicationWorkflow.nodes.searchDocumentNode.custom') }}
                <el-tooltip
                  c
                  :content="$t('views.applicationWorkflow.nodes.searchDocumentNode.customTooltip')"
                  placement="top"
                >
                  <AppIcon iconName="app-warning" class="app-warning-icon ml-4"></AppIcon>
                </el-tooltip>
              </span>
            </el-radio>
          </el-radio-group>
        </el-form-item>
        <div class="w-full">
          <el-form-item
            v-if="form_data.search_mode === 'auto'"
            prop="question_reference"
            :rules="{
              message: $t(
                'views.applicationWorkflow.nodes.searchKnowledgeNode.searchQuestion.requiredMessage',
              ),
              trigger: 'blur',
              required: true,
            }"
          >
            <template #label>
              <span>
                {{ $t('views.applicationWorkflow.nodes.searchKnowledgeNode.searchQuestion.label') }}
                <span class="color-danger">*</span></span
              >
            </template>
            <NodeCascader
              ref="nodeCascaderRef2"
              :nodeModel="nodeModel"
              class="w-full"
              :placeholder="
                $t('views.applicationWorkflow.nodes.searchKnowledgeNode.searchQuestion.placeholder')
              "
              v-model="form_data.question_reference"
            />
          </el-form-item>
          <div v-else>
            <div class="flex align-center mb-8">
              <el-text type="info" class="lighter" size="small">
                {{ $t('views.applicationWorkflow.nodes.conditionNode.conditions.info') }}
              </el-text>
              <el-select
                v-model="form_data.search_condition_type"
                size="small"
                style="width: 60px; margin: 0 8px"
              >
                <el-option :label="$t('views.applicationWorkflow.condition.AND')" value="AND" />
                <el-option :label="$t('views.applicationWorkflow.condition.OR')" value="OR" />
              </el-select>
              <el-text type="info" class="lighter" size="small">
                {{ $t('views.applicationWorkflow.nodes.conditionNode.conditions.label') }}
              </el-text>
            </div>
            <div v-for="(c, index) in form_data.search_condition_list" :key="index">
              <el-row :gutter="8" class="mb-8">
                <el-col :span="8">
                  <el-select v-model="c.key" filterable @focus="getAllTags(form_data.knowledge_id_list)">
                    <el-option
                      v-for="tag in form_data.knowledge_tags"
                      :key="tag"
                      :label="tag.key"
                      :value="tag.key"
                    />
                  </el-select>
                </el-col>
                <el-col :span="7">
                  <el-select v-model="c.compare">
                    <el-option
                      v-for="item in compareList"
                      :key="item.value"
                      :value="item.value"
                      :label="item.label"
                    />
                  </el-select>
                </el-col>
                <el-col :span="8">
                  <el-input
                    v-model="c.value"
                    :placeholder="
                      $t('views.applicationWorkflow.nodes.searchDocumentNode.valueMessage')
                    "
                  ></el-input>
                </el-col>
                <el-col :span="1">
                  <el-button link @click="delCondition(index)" type="info" class="mt-4">
                    <AppIcon iconName="app-delete"></AppIcon>
                  </el-button>
                </el-col>
              </el-row>
            </div>
            <el-button link type="primary" @click="addCondition" class="mt-8">
              <AppIcon iconName="app-add-outlined" class="mr-4"></AppIcon>
              {{ $t('views.applicationWorkflow.nodes.conditionNode.addCondition') }}
            </el-button>
          </div>
        </div>
      </el-form>
    </el-card>
    <AddKnowledgeDialog
      ref="AddKnowledgeDialogRef"
      @addData="addKnowledge"
      :data="knowledgeList"
      :loading="knowledgeLoading"
    />
  </NodeContainer>
</template>
<script setup lang="ts">
import { cloneDeep, set } from 'lodash'

import NodeContainer from '@/workflow/common/NodeContainer.vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import AddKnowledgeDialog from '@/views/application/component/AddKnowledgeDialog.vue'
import type { FormInstance } from 'element-plus'
import { computed, onMounted, ref, watch } from 'vue'
import { relatedObject } from '@/utils/array'
import { t } from '@/locales'
import AppIcon from '@/components/app-icon/AppIcon.vue'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { useRoute } from 'vue-router'

const route = useRoute()

const props = defineProps<{ nodeModel: any }>()
const nodeCascaderRef = ref()
const nodeCascaderRef2 = ref()
const compareList = [
  { value: 'contain', label: t('views.applicationWorkflow.compare.contain') },
  { value: 'not_contain', label: t('views.applicationWorkflow.compare.not_contain') },
  { value: 'eq', label: t('views.applicationWorkflow.compare.eq') },
]

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else if (route.path.includes('share/')) {
    return 'workspaceShare'
  } else {
    return 'workspace'
  }
})

const form = {
  knowledge_id_list: [],
  search_scope_type: 'custom',
  search_scope_source: 'knowledge',
  search_scope_reference: [],
  search_mode: 'auto',
  question_reference: [],
  search_condition_type: 'AND',
  search_condition_list: [],
  knowledge_tags: [],
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
const AddKnowledgeDialogRef = ref<InstanceType<typeof AddKnowledgeDialog>>()
const knowledgeList = ref<any>([])
const knowledgeLoading = ref(false)

function removeKnowledge(id: any) {
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

function openKnowledgeDialog() {
  if (AddKnowledgeDialogRef.value) {
    AddKnowledgeDialogRef.value.open(form_data.value.knowledge_id_list)
  }
}

function addCondition() {
  const list = cloneDeep(form_data.value.search_condition_list)
  list.push({
    key: '',
    compare: 'contain',
    value: '',
  })
  set(form_data.value, 'search_condition_list', list)
}

function delCondition(index: number) {
  const list = cloneDeep(form_data.value.search_condition_list)
  list.splice(index, 1)
  set(form_data.value, 'search_condition_list', list)
}

function getAllTags(knowledge_ids: any) {
  if (knowledge_ids.length === 0) {
    set(form_data.value, 'knowledge_tags', [])
    return
  }
  loadSharedApi({ type: 'knowledge', systemType: apiType.value })
    .getAllTags({ knowledge_ids: knowledge_ids }, {})
    .then((res: any) => {
      set(form_data.value, 'knowledge_tags', res.data)
    })
}

const validate = () => {
  return Promise.all([
    nodeCascaderRef.value?.validate(),
    nodeCascaderRef2.value?.validate(),
    knowledgeNodeFormRef.value?.validate(),
  ]).catch((err) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

onMounted(() => {
  // console.log(props.nodeModel.properties.node_data)
  knowledgeList.value = props.nodeModel.properties.node_data.knowledge_list
  set(props.nodeModel, 'validate', validate)
})
</script>
<style lang="scss" scoped></style>
