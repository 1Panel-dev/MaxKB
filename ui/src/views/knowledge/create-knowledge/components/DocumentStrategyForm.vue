<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { DocumentStrategy, ModelItem, ModelProviderItem, ToolItem } from '@/api/types'
import type { FormInstance } from 'element-plus'
import ProviderApi from '@/api/admin/model-provider'
import SystemResourceModelApi from '@/api/admin/system/resource-management/model'
import SystemResourceToolApi from '@/api/admin/system/resource-management/tool/tool'
import SystemSharedModelApi from '@/api/admin/system/shared-resources/model'
import SystemSharedToolApi from '@/api/admin/system/shared-resources/tool/tool'
import ModelApi from '@/api/admin/workspace/model'
import ToolApi from '@/api/admin/workspace/tool/tool'
import SelectModel from '@/components/business/select-model/index.vue'
import { DOCUMENT_SPLIT_PATTERN_OPTIONS } from '@/constants/document'
import { isSystemResource, isSystemSharedResource } from '@/utils/resource-context'

defineOptions({ name: 'DocumentStrategyForm' })
const { t } = useI18n({ useScope: 'global' })

/* 文档处理策略 */
const formRef = ref<FormInstance>()
const strategy = reactive<DocumentStrategy>({
  split: { mode: 'smart', patterns: null, limit: 4096, child_length: 256, auto_clean: true },
  visual: { enabled: false, strategy: 'model', model_id: null, tool_id: null },
  index: { title_as_question: false },
})
const visualModelId = computed({
  get: () => strategy.visual.model_id ?? '',
  set: (value: string) => {
    strategy.visual.model_id = value || null
  },
})

const splitPatterns = ref<string[]>([])
const splitModes = ['smart', 'advanced'] as const
function validate() {
  return formRef.value?.validate().catch(() => false) ?? Promise.resolve(false)
}
// 设置页回填独立草稿；智能分段的固定提交值不作为高级分段的编辑默认值。
function setStrategy(value?: DocumentStrategy | null) {
  Object.assign(strategy.split, {
    mode: 'smart',
    patterns: null,
    limit: 4096,
    child_length: 256,
    auto_clean: true,
    ...(value?.split.mode === 'advanced' ? cloneDeep(value.split) : {}),
  })
  Object.assign(strategy.visual, { enabled: false, strategy: 'model', model_id: null, tool_id: null, ...cloneDeep(value?.visual) })
  Object.assign(strategy.index, { title_as_question: false, ...cloneDeep(value?.index) })
  splitPatterns.value = value?.split.mode === 'advanced' ? cloneDeep(value.split.patterns ?? []) : []
  formRef.value?.clearValidate()
  void handleVisualChange()
}
function getStrategy(): DocumentStrategy {
  return {
    split: {
      ...(strategy.split.mode === 'smart' ? { mode: 'smart' as const, limit: 4096, child_length: 256, auto_clean: false } : strategy.split),
      patterns: strategy.split.mode === 'advanced' && splitPatterns.value.length ? [...splitPatterns.value] : null,
    },
    visual: {
      ...strategy.visual,
      model_id: strategy.visual.strategy === 'model' ? strategy.visual.model_id : null,
      tool_id: strategy.visual.strategy === 'tool' ? strategy.visual.tool_id : null,
    },
    index: { ...strategy.index },
  }
}

/* 视觉模型与工具选项 */
const requestModelApi = computed(() => {
  if (isSystemResource()) return SystemResourceModelApi
  if (isSystemSharedResource()) return SystemSharedModelApi
  return ModelApi
})
const requestToolApi = computed(() => {
  if (isSystemResource()) return SystemResourceToolApi
  if (isSystemSharedResource()) return SystemSharedToolApi
  return ToolApi
})
const modelOptionsLoading = ref(false)
const toolOptionsLoading = ref(false)
const modelOptions = ref<ModelItem[]>([])
const providerOptions = ref<ModelProviderItem[]>([])
const toolOptions = ref<ToolItem[]>([])
const selectedVisualTool = computed(() => toolOptions.value.find((tool) => tool.id === strategy.visual.tool_id))
function loadModelOptions() {
  if (!strategy.visual.enabled || strategy.visual.strategy !== 'model' || modelOptionsLoading.value) return
  modelOptionsLoading.value = true
  return Promise.all([requestModelApi.value.getModelListWithShared({ model_type: 'IMAGE' }), ProviderApi.getProviderList({ model_type: 'IMAGE' })])
    .then(([models, providers]) => {
      modelOptions.value = models
      providerOptions.value = providers
    })
    .catch(() => {
      // 请求层统一提示错误，保留已有选项供再次加载。
    })
    .finally(() => {
      modelOptionsLoading.value = false
    })
}

function loadToolOptions() {
  if (!strategy.visual.enabled || strategy.visual.strategy !== 'tool' || toolOptionsLoading.value) return
  toolOptionsLoading.value = true
  return requestToolApi.value
    .getToolListWithShared()
    .then((tools) => {
      toolOptions.value = tools
    })
    .catch(() => {
      // 请求层统一提示错误，保留已有选项供再次加载。
    })
    .finally(() => {
      toolOptionsLoading.value = false
    })
}

function handleVisualChange() {
  if (!strategy.visual.enabled) return
  return strategy.visual.strategy === 'model' ? loadModelOptions() : loadToolOptions()
}
defineExpose({ validate, getStrategy, setStrategy })
</script>

<template>
  <el-form ref="formRef" :model="strategy" :validate-on-rule-change="false" label-position="top" require-asterisk-position="right" @submit.prevent>
    <p class="mb-2">{{ t('knowledge.documentStrategy.splitRules') }}</p>

    <div class="w-full space-y-2">
      <template v-for="mode in splitModes" :key="mode">
        <!-- 选择分段规则 -->
        <MkResourceCard
          :title="t(`knowledge.documentStrategy.${mode}.label`)"
          class="min-h-0!"
          :class="{ 'border-primary!': strategy.split.mode === mode }"
          :aria-checked="strategy.split.mode === mode"
          @click="strategy.split.mode = mode"
        >
          <template #icon>
            <el-avatar v-if="mode === 'smart'" shape="square" :size="24" class="shrink-0">
              <MkIcon name="icon_center-alignment_outlined" :size="15" />
            </el-avatar>
            <el-avatar v-else shape="square" :size="24" class="shrink-0 bg-warning!">
              <MkIcon name="icon_setting" :size="15" />
            </el-avatar>
          </template>
          <template #subtitle>{{ t(`knowledge.documentStrategy.${mode}.description`) }}</template>
          <template v-if="mode === 'advanced' && strategy.split.mode === 'advanced'" #default>
            <div class="mk-gray-card-lg cursor-default text-N900" @click.stop @keydown.stop>
              <el-form-item>
                <template #label>
                  <span class="flex-align-center gap-1">
                    {{ t('knowledge.documentStrategy.delimiter.label') }}
                    <MkTooltip :content="t('knowledge.documentStrategy.delimiter.description')" placement="right">
                      <MkIcon name="icon_info_outlined" class="text-N600!"></MkIcon>
                    </MkTooltip>
                  </span>
                </template>
                <el-select
                  v-model="splitPatterns"
                  multiple
                  filterable
                  allow-create
                  default-first-option
                  :placeholder="t('knowledge.documentStrategy.delimiter.placeholder')"
                  class="w-full"
                >
                  <el-option v-for="pattern in DOCUMENT_SPLIT_PATTERN_OPTIONS" :key="pattern.value" :label="pattern.label" :value="pattern.value" />
                </el-select>
              </el-form-item>
              <el-form-item :label="t('knowledge.documentStrategy.paragraphLength')">
                <MkSlider v-model="strategy.split.limit" show-input :min="50" :max="100000" />
              </el-form-item>
              <el-form-item>
                <template #label>
                  <span class="flex-align-center gap-1">
                    {{ t('knowledge.documentStrategy.childChunkLength.label') }}
                    <MkTooltip :content="t('knowledge.documentStrategy.childChunkLength.description')" placement="right">
                      <MkIcon name="icon_info_outlined" class="text-N600!"></MkIcon>
                    </MkTooltip>
                  </span>
                </template>

                <MkSlider v-model="strategy.split.child_length" show-input :min="64" :max="1024" />
              </el-form-item>
              <el-form-item class="mb-0!">
                <template #label>
                  <span class="flex-align-center">
                    <span>{{ t('knowledge.documentStrategy.autoClean.label') }}</span>
                    <span class="text-N600">{{ t('knowledge.documentStrategy.autoClean.description') }}</span>
                  </span>
                </template>

                <el-switch v-model="strategy.split.auto_clean" />
              </el-form-item>
            </div>
          </template>
        </MkResourceCard>
      </template>
    </div>
    <p class="mt-4 mb-2">{{ t('knowledge.documentStrategy.imageProcessing') }}</p>

    <el-card shadow="never" class="w-full">
      <div class="flex-between gap-4">
        <div>
          <h6>{{ t('knowledge.documentStrategy.visualEnhancement.label') }}</h6>
          <p class="mt-1 text-N600 text-sm">{{ t('knowledge.documentStrategy.visualEnhancement.description') }}</p>
        </div>
        <el-switch v-model="strategy.visual.enabled" @change="handleVisualChange" />
      </div>
      <div v-if="strategy.visual.enabled" class="mk-gray-card-lg mt-4">
        <el-form-item :label="t('knowledge.documentStrategy.enhancementMethod.label')" required>
          <el-radio-group v-model="strategy.visual.strategy" @change="handleVisualChange">
            <el-radio value="model">{{ t('knowledge.documentStrategy.enhancementMethod.model') }}</el-radio>
            <el-radio value="tool">{{ t('knowledge.documentStrategy.enhancementMethod.tool') }}</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item
          v-if="strategy.visual.strategy === 'model'"
          :label="t('model.types.image.label')"
          prop="visual.model_id"
          :rules="{ required: true, message: t('knowledge.documentStrategy.visionModel.requiredMessage'), trigger: 'change' }"
          class="mb-0! mt-4"
        >
          <SelectModel
            v-model="visualModelId"
            :options="modelOptions"
            :provider-options="providerOptions"
            :loading="modelOptionsLoading"
            :placeholder="t('knowledge.documentStrategy.visionModel.placeholder')"
            teleported
            can-add
            @refresh="loadModelOptions"
          />
        </el-form-item>
        <el-form-item
          v-else
          :label="t('knowledge.documentStrategy.enhancementTool.label')"
          prop="visual.tool_id"
          :rules="{ required: true, message: t('knowledge.documentStrategy.enhancementTool.requiredMessage'), trigger: 'change' }"
          class="mb-0! mt-4"
        >
          <el-select
            v-model="strategy.visual.tool_id"
            :loading="toolOptionsLoading"
            :placeholder="t('knowledge.documentStrategy.enhancementTool.placeholder')"
            filterable
            clearable
            class="w-full"
          >
            <template #label="{ label }">
              <div class="flex-align-center gap-2">
                <ToolIcon
                  v-if="selectedVisualTool"
                  :icon="selectedVisualTool.icon"
                  :type="selectedVisualTool.tool_type"
                  :size="20"
                  class="shrink-0"
                />
                <span class="truncate" :title="label">{{ label }}</span>
              </div>
            </template>
            <template v-for="tool in toolOptions" :key="tool.id">
              <el-option :label="tool.name" :value="tool.id">
                <div class="flex-align-center gap-2">
                  <ToolIcon :icon="tool.icon" :type="tool.tool_type" :size="20" class="shrink-0" />
                  <span class="truncate" :title="tool.name">{{ tool.name }}</span>
                </div>
              </el-option>
            </template>
          </el-select>
        </el-form-item>
      </div>
    </el-card>
    <p class="mt-4 mb-2">{{ t('knowledge.documentStrategy.indexEnhancement') }}</p>

    <el-card shadow="never" class="w-full">
      <div class="flex-between">
        <div>
          <h6>{{ t('knowledge.documentStrategy.titleAsQuestion.label') }}</h6>
          <p class="mt-1 text-N600 text-sm">{{ t('knowledge.documentStrategy.titleAsQuestion.description') }}</p>
        </div>
        <el-switch v-model="strategy.index.title_as_question" />
      </div>
    </el-card>
  </el-form>
</template>
