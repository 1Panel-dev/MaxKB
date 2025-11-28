<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">{{ $t('views.workflow.nodeSetting') }}</h5>
    <el-card shadow="never" class="card-never">
      <el-form
        ref="aiChatNodeFormRef"
        @submit.prevent
        :model="form_data"
        label-position="top"
        require-asterisk-position="right"
        label-width="auto"
      >
        <el-form-item :label="$t('views.problem.relateParagraph.selectDocument')" :rules="{
            type: 'array',
            required: true,
            message: $t('views.chatLog.documentPlaceholder'),
            trigger: 'change'
          }"
        >
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            :placeholder="$t('views.chatLog.documentPlaceholder')"
            v-model="form_data.document_list"
          />
        </el-form-item>
        <el-form-item
          :label="$t('views.workflow.nodes.documentSplitNode.splitStrategy.label')"
          :rules="{
            required: true,
            message: $t('views.workflow.nodes.documentSplitNode.splitStrategy.required'),
            trigger: 'change'
          }"
        >
          <el-select
            v-model="form_data.split_strategy"
            :placeholder="$t('views.workflow.nodes.documentSplitNode.splitStrategy.placeholder')">
            <el-option
              :label="$t('views.document.setRules.intelligent.label')"
              value="auto"
            />
            <el-option
              :label="$t('views.document.setRules.advanced.label')"
              value="custom"
            />
            <el-option
              :label="$t('views.document.fileType.QA.label')"
              value="qa"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('子分块大小')">
          <el-slider
            v-model="form_data.chunk_size"
            show-input
            :show-input-controls="false"
            :min="50"
            :max="100000"
          />
        </el-form-item>
        <div v-if="form_data.split_strategy === 'custom'">
          <div class="set-rules__form">
            <div class="form-item mb-16">
              <div class="title flex align-center mb-8">
                          <span style="margin-right: 4px">{{
                              $t('views.document.setRules.patterns.label')
                            }}</span>
                <el-tooltip
                  effect="dark"
                  :content="$t('views.document.setRules.patterns.tooltip')"
                  placement="right"
                >
                  <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                </el-tooltip>
              </div>
              <div @click.stop>
                <el-select
                  v-model="form_data.patterns"
                  multiple
                  :reserve-keyword="false"
                  allow-create
                  default-first-option
                  filterable
                  :placeholder="$t('views.document.setRules.patterns.placeholder')"
                >
                  <el-option
                    v-for="(item, index) in splitPatternList"
                    :key="index"
                    :label="item.key"
                    :value="item.value"
                  >
                  </el-option>
                </el-select>
              </div>
            </div>
            <div class="form-item mb-16">
              <div class="title mb-8">
                {{ $t('views.document.setRules.limit.label') }}
              </div>
              <el-slider
                v-model="form_data.limit"
                show-input
                :show-input-controls="false"
                :min="50"
                :max="100000"
              />
            </div>
            <div class="form-item mb-16">
              <div class="title mb-8">
                {{ $t('views.document.setRules.with_filter.label') }}
              </div>
              <el-switch size="small" v-model="form_data.with_filter" />
              <div style="margin-top: 4px">
                <el-text type="info">
                  {{ $t('views.document.setRules.with_filter.text') }}
                </el-text
                >
              </div>
            </div>
          </div>
        </div>
        <el-form-item v-if="form_data.split_strategy !== 'qa'">
          <template #label>
            <div class="flex-between">
              <span>分段标题设置为分段的关联问题</span>
              <el-select v-model="form_data.paragraph_title_relate_problem_type" size="small"
                         style="width: 100px">
                <el-option
                  :label="$t('views.workflow.nodes.searchDocumentNode.custom')"
                  value="custom"
                />
                <el-option
                  :label="$t('views.workflow.variable.Referencing')"
                  value="referencing"
                />
              </el-select>
            </div>
          </template>
          <el-switch
            v-if="form_data.paragraph_title_relate_problem_type === 'custom'"
            size="small"
            v-model="form_data.paragraph_title_relate_problem"
          />
          <NodeCascader
            v-else
            ref="nodeCascaderRef2"
            :nodeModel="nodeModel"
            class="w-full"
            :placeholder="$t('views.chatLog.documentPlaceholder')"
            v-model="form_data.paragraph_title_relate_problem_reference"
          />
        </el-form-item>
        <el-form-item>
          <template #label>
            <div class="flex-between">
              <span>文档名称设置为分段的关联问题</span>
              <el-select v-model="form_data.document_name_relate_problem_type" size="small"
                         style="width: 100px">
                <el-option
                  :label="$t('views.workflow.nodes.searchDocumentNode.custom')"
                  value="custom"
                />
                <el-option
                  :label="$t('views.workflow.variable.Referencing')"
                  value="referencing"
                />
              </el-select>
            </div>
          </template>
          <el-switch
            v-if="form_data.document_name_relate_problem_type === 'custom'"
            size="small"
            v-model="form_data.document_name_relate_problem"
          />
          <NodeCascader
            v-else
            ref="nodeCascaderRef3"
            :nodeModel="nodeModel"
            class="w-full"
            :placeholder="$t('views.chatLog.documentPlaceholder')"
            v-model="form_data.document_name_relate_problem_reference"
          />
        </el-form-item>
      </el-form>
    </el-card>
  </NodeContainer>
</template>

<script setup lang="ts">
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import { computed, onMounted, ref } from 'vue'
import { set } from 'lodash'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import type { FormInstance } from 'element-plus'
import type { KeyValue } from '@/api/type/common.ts'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api.ts'
import { useRoute } from 'vue-router'

const route = useRoute()
const {
  query: { id } // id为knowledgeID
} = route as any

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const props = defineProps<{ nodeModel: any }>()
const splitPatternList = ref<Array<KeyValue<string, string>>>([])

const form = {
  document_list: [],
  split_strategy: 'auto',
  paragraph_title_relate_problem_type: 'custom',
  paragraph_title_relate_problem: false,
  paragraph_title_relate_problem_reference: [],
  document_name_relate_problem_type: 'custom',
  document_name_relate_problem: false,
  document_name_relate_problem_reference: [],
  limit: 4096,
  chunk_size: 256,
  patterns: [],
  with_filter: false
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


const aiChatNodeFormRef = ref<FormInstance>()
const nodeCascaderRef = ref()
const nodeCascaderRef2 = ref()
const nodeCascaderRef3 = ref()

const validate = () => {
  return Promise.all([
    nodeCascaderRef.value ? nodeCascaderRef.value.validate() : Promise.resolve(''),
    nodeCascaderRef2.value ? nodeCascaderRef2.value.validate() : Promise.resolve(''),
    nodeCascaderRef3.value ? nodeCascaderRef3.value.validate() : Promise.resolve(''),
    aiChatNodeFormRef.value?.validate()
  ]).catch((err: any) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

const patternLoading = ref<boolean>(false)
const initSplitPatternList = () => {
  loadSharedApi({ type: 'document', systemType: apiType.value })
    .listSplitPattern(id, patternLoading)
    .then((ok: any) => {
      splitPatternList.value = ok.data
    })
}


onMounted(() => {
  initSplitPatternList()

  set(props.nodeModel, 'validate', validate)
})

</script>

<style lang="scss" scoped>

</style>
