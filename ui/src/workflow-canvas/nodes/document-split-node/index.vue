<script setup lang="ts">
import { computed, inject, nextTick, onBeforeUnmount, onMounted, useTemplateRef } from 'vue'
import type { FormInstance } from 'element-plus'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
import { createAnchorGuard } from '@/workflow-canvas/core/utils'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { splitPatternOptions } from './constant'

defineOptions({ name: 'WorkflowDocumentSplitNode' })

type ConfigurableField = 'chunk_size' | 'patterns' | 'limit' | 'with_filter' | 'paragraph_title_relate_problem' | 'document_name_relate_problem'
type DocumentSplitForm = {
  document_list: string[]
  split_strategy: 'auto' | 'custom' | 'qa'
  chunk_size: number
  limit: number
  patterns: string[]
  with_filter: boolean
  paragraph_title_relate_problem: boolean
  document_name_relate_problem: boolean
} & { [K in `${ConfigurableField}_type`]: 'custom' | 'referencing' } & { [K in `${ConfigurableField}_reference`]: string[] }

const getModel = inject<() => WorkflowNodeModel>('getModel')!
const model = getModel()
const formRef = useTemplateRef<FormInstance>('formRef')
const anchorGuard = createAnchorGuard(model)

// 默认值与引用数组一次性补齐，读取表单时不修改节点。
const defaultForm: DocumentSplitForm = {
  document_list: [],
  split_strategy: 'auto',
  paragraph_title_relate_problem_type: 'custom',
  paragraph_title_relate_problem: false,
  paragraph_title_relate_problem_reference: [],
  document_name_relate_problem_type: 'custom',
  document_name_relate_problem: false,
  document_name_relate_problem_reference: [],
  limit: 4096,
  limit_type: 'custom',
  limit_reference: [],
  chunk_size: 256,
  chunk_size_type: 'custom',
  chunk_size_reference: [],
  patterns: [],
  patterns_type: 'custom',
  patterns_reference: [],
  with_filter: false,
  with_filter_type: 'custom',
  with_filter_reference: [],
}
const savedForm = model.properties.node_data as Partial<DocumentSplitForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  document_list: Array.isArray(savedForm?.document_list) ? savedForm.document_list : defaultForm.document_list,
  patterns: Array.isArray(savedForm?.patterns) ? savedForm.patterns : defaultForm.patterns,
  chunk_size_reference: Array.isArray(savedForm?.chunk_size_reference) ? savedForm.chunk_size_reference : defaultForm.chunk_size_reference,
  patterns_reference: Array.isArray(savedForm?.patterns_reference) ? savedForm.patterns_reference : defaultForm.patterns_reference,
  limit_reference: Array.isArray(savedForm?.limit_reference) ? savedForm.limit_reference : defaultForm.limit_reference,
  with_filter_reference: Array.isArray(savedForm?.with_filter_reference) ? savedForm.with_filter_reference : defaultForm.with_filter_reference,
  paragraph_title_relate_problem_reference: Array.isArray(savedForm?.paragraph_title_relate_problem_reference)
    ? savedForm.paragraph_title_relate_problem_reference
    : defaultForm.paragraph_title_relate_problem_reference,
  document_name_relate_problem_reference: Array.isArray(savedForm?.document_name_relate_problem_reference)
    ? savedForm.document_name_relate_problem_reference
    : defaultForm.document_name_relate_problem_reference,
}
const formData = computed(() => model.properties.node_data as DocumentSplitForm)

// 切换来源或策略后清理隐藏字段提示，节点统一使用表单校验。
function clearHiddenValidation() {
  anchorGuard.reset()
  void nextTick(() => formRef.value?.clearValidate())
}
function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error })) ?? Promise.resolve()
}
onMounted(() => {
  model.validate = validate
})
onBeforeUnmount(() => anchorGuard.reset())
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">节点设置</h6>
    <div class="mk-gray-card">
      <el-form ref="formRef" @submit.prevent :model="formData" label-position="top" require-asterisk-position="right" label-width="auto">
        <!-- 选择文档 -->
        <el-form-item label="选择文档" prop="document_list" :rules="{ type: 'array', required: true, message: '请选择文档', trigger: 'change' }">
          <NodeCascader :node-model="model" class="w-full!" placeholder="请选择文档" v-model="formData.document_list" />
        </el-form-item>
        <!-- 分段策略 -->
        <el-form-item label="分段策略" prop="split_strategy" :rules="{ required: true, message: '请选择分段策略', trigger: 'change' }">
          <el-select v-model="formData.split_strategy" placeholder="请选择分段策略" :teleported="false" @change="clearHiddenValidation">
            <el-option label="智能分段（推荐）" value="auto" />
            <el-option label="高级分段" value="custom" />
            <el-option label="QA 问答对" value="qa" />
          </el-select>
        </el-form-item>
        <!-- 子分块长度 -->
        <el-form-item
          :prop="formData.chunk_size_type === 'referencing' ? 'chunk_size_reference' : 'chunk_size'"
          :rules="formData.chunk_size_type === 'referencing' ? [{ type: 'array', required: true, message: '请选择引用变量', trigger: 'change' }] : []"
        >
          <template #label>
            <div class="flex-between w-full gap-2">
              <span class="flex items-center gap-1">
                <span>子分块长度</span>
                <el-tooltip effect="dark" placement="right">
                  <template #content>
                    核心目标是平衡检索精度与召回效率<br />
                    避免过短拆分：单块＜50 字易导致语义碎片化，检索时可能因缺少上下文无法匹配查询意图<br />
                    避免过长拆分：单块＞500 字会增加冗余信息，降低检索精准度，且占用更多存储和计算资源
                  </template>
                  <MkIcon name="icon_info_outlined" class="text-N600!" />
                </el-tooltip>
              </span>
              <el-select
                v-model="formData.chunk_size_type"
                size="small"
                class="w-18! shrink-0"
                :teleported="false"
                @visible-change="anchorGuard.setOverlayVisible('chunk_size_type', $event)"
                @change="clearHiddenValidation"
              >
                <el-option label="引用" value="referencing" />
                <el-option label="自定义" value="custom" />
              </el-select>
            </div>
          </template>
          <el-input-number
            v-if="formData.chunk_size_type === 'custom'"
            v-model="formData.chunk_size"
            :min="50"
            :max="100000"
            :value-on-clear="0"
            controls-position="right"
            align="left"
            class="w-full!"
            :step="1"
            :step-strictly="true"
          />
          <NodeCascader v-else :node-model="model" class="w-full!" placeholder="请选择引用变量" v-model="formData.chunk_size_reference" />
        </el-form-item>

        <!-- 分段标识 -->
        <el-form-item
          v-if="formData.split_strategy === 'custom'"
          :prop="formData.patterns_type === 'referencing' ? 'patterns_reference' : 'patterns'"
          :rules="formData.patterns_type === 'referencing' ? [{ type: 'array', required: true, message: '请选择引用变量', trigger: 'change' }] : []"
        >
          <template #label>
            <div class="flex-between w-full gap-2">
              <div class="flex items-center gap-1">
                <span> 分段标识 </span>
                <el-tooltip effect="dark" content="按照所选符号先后顺序做递归分割，分割结果超出分段长度将截取至分段长度。" placement="right">
                  <MkIcon name="icon_info_outlined" class="text-N600!" />
                </el-tooltip>
              </div>
              <el-select
                :teleported="false"
                v-model="formData.patterns_type"
                size="small"
                class="w-18! shrink-0"
                @visible-change="anchorGuard.setOverlayVisible('patterns_type', $event)"
                @change="clearHiddenValidation"
              >
                <el-option label="引用" value="referencing" />
                <el-option label="自定义" value="custom" />
              </el-select>
            </div>
          </template>
          <el-select
            :teleported="false"
            v-if="formData.patterns_type === 'custom'"
            v-model="formData.patterns"
            multiple
            :reserve-keyword="false"
            allow-create
            default-first-option
            filterable
            placeholder="请选择分段标识"
            @visible-change="anchorGuard.setOverlayVisible('patterns', $event)"
          >
            <el-option v-for="pattern in splitPatternOptions" :key="pattern.value" :label="pattern.label" :value="pattern.value"> </el-option>
          </el-select>
          <NodeCascader v-else :node-model="model" class="w-full!" placeholder="请选择引用变量" v-model="formData.patterns_reference" />
        </el-form-item>

        <!-- 分段长度 -->
        <el-form-item
          v-if="formData.split_strategy === 'custom'"
          :prop="formData.limit_type === 'referencing' ? 'limit_reference' : 'limit'"
          :rules="formData.limit_type === 'referencing' ? [{ type: 'array', required: true, message: '请选择引用变量', trigger: 'change' }] : []"
        >
          <template #label>
            <div class="flex-between w-full gap-2">
              <span> 分段长度 </span>
              <el-select
                v-model="formData.limit_type"
                size="small"
                class="w-18! shrink-0"
                :teleported="false"
                @visible-change="anchorGuard.setOverlayVisible('limit_type', $event)"
                @change="clearHiddenValidation"
              >
                <el-option label="引用" value="referencing" />
                <el-option label="自定义" value="custom" />
              </el-select>
            </div>
          </template>
          <el-input-number
            v-if="formData.limit_type === 'custom'"
            v-model="formData.limit"
            :min="50"
            :max="100000"
            :value-on-clear="0"
            controls-position="right"
            class="w-full!"
            :step="1"
            :step-strictly="true"
          />
          <NodeCascader v-else :node-model="model" class="w-full!" placeholder="请选择引用变量" v-model="formData.limit_reference" />
        </el-form-item>
        <!-- 自动清洗 -->
        <el-form-item
          v-if="formData.split_strategy === 'custom'"
          :prop="formData.with_filter_type === 'referencing' ? 'with_filter_reference' : 'with_filter'"
          :rules="
            formData.with_filter_type === 'referencing' ? [{ type: 'array', required: true, message: '请选择引用变量', trigger: 'change' }] : []
          "
        >
          <template #label>
            <div class="flex-between w-full gap-2">
              <div class="flex items-center gap-1">
                <span> 自动清洗 </span>
                <el-tooltip effect="dark" content="去掉重复多余符号空格、空行、制表符" placement="right">
                  <MkIcon name="icon_info_outlined" class="text-N600!" />
                </el-tooltip>
              </div>
              <el-select
                v-model="formData.with_filter_type"
                size="small"
                class="w-18! shrink-0"
                :teleported="false"
                @visible-change="anchorGuard.setOverlayVisible('with_filter_type', $event)"
                @change="clearHiddenValidation"
              >
                <el-option label="引用" value="referencing" />
                <el-option label="自定义" value="custom" />
              </el-select>
            </div>
          </template>
          <el-switch v-if="formData.with_filter_type === 'custom'" size="small" v-model="formData.with_filter" />
          <NodeCascader v-else :node-model="model" class="w-full!" placeholder="请选择引用变量" v-model="formData.with_filter_reference" />
        </el-form-item>

        <!-- 分段标题设置为分段的关联问题 -->
        <el-form-item
          class="mk-hide-asterisk"
          v-if="formData.split_strategy !== 'qa'"
          :prop="
            formData.paragraph_title_relate_problem_type === 'referencing'
              ? 'paragraph_title_relate_problem_reference'
              : 'paragraph_title_relate_problem'
          "
          :rules="
            formData.paragraph_title_relate_problem_type === 'referencing'
              ? [{ type: 'array', required: true, message: '请选择引用变量', trigger: 'change' }]
              : []
          "
        >
          <template #label>
            <div class="flex-between w-full gap-2">
              <span class="mk-required"> 分段标题设置为分段的关联问题</span>
              <el-select
                v-model="formData.paragraph_title_relate_problem_type"
                size="small"
                class="w-18! shrink-0"
                :teleported="false"
                @visible-change="anchorGuard.setOverlayVisible('paragraph_title_relate_problem_type', $event)"
                @change="clearHiddenValidation"
              >
                <el-option label="引用" value="referencing" />
                <el-option label="自定义" value="custom" />
              </el-select>
            </div>
          </template>
          <el-switch
            v-if="formData.paragraph_title_relate_problem_type === 'custom'"
            size="small"
            v-model="formData.paragraph_title_relate_problem"
          />
          <NodeCascader
            v-else
            :node-model="model"
            class="w-full!"
            placeholder="请选择引用变量"
            v-model="formData.paragraph_title_relate_problem_reference"
          />
        </el-form-item>

        <!-- 文档名称设置为分段的关联问题 -->
        <el-form-item
          class="mk-hide-asterisk"
          :prop="
            formData.document_name_relate_problem_type === 'referencing' ? 'document_name_relate_problem_reference' : 'document_name_relate_problem'
          "
          :rules="
            formData.document_name_relate_problem_type === 'referencing'
              ? [{ type: 'array', required: true, message: '请选择引用变量', trigger: 'change' }]
              : []
          "
        >
          <template #label>
            <div class="flex-between w-full gap-2">
              <span class="mk-required">文档名称设置为分段的关联问题</span>
              <el-select
                v-model="formData.document_name_relate_problem_type"
                size="small"
                class="w-18! shrink-0"
                :teleported="false"
                @visible-change="anchorGuard.setOverlayVisible('document_name_relate_problem_type', $event)"
                @change="clearHiddenValidation"
              >
                <el-option label="引用" value="referencing" />
                <el-option label="自定义" value="custom" />
              </el-select>
            </div>
          </template>
          <el-switch v-if="formData.document_name_relate_problem_type === 'custom'" size="small" v-model="formData.document_name_relate_problem" />
          <NodeCascader
            v-else
            :node-model="model"
            class="w-full!"
            placeholder="请选择引用变量"
            v-model="formData.document_name_relate_problem_reference"
          />
        </el-form-item>
      </el-form>
    </div>
  </NodeContainer>
</template>
