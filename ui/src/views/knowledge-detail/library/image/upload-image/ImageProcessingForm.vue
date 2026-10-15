<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import type { FormInstance } from 'element-plus'
import type { DocumentStrategy, ModelItem, ModelProviderItem, ToolItem } from '@/api/types'
import ModelApi from '@/api/admin/workspace/model'
import SystemResourceModelApi from '@/api/admin/system/resource-management/model'
import SystemSharedModelApi from '@/api/admin/system/shared-resources/model'
import ProviderApi from '@/api/admin/model-provider'
import ToolApi from '@/api/admin/workspace/tool/tool'
import SystemResourceToolApi from '@/api/admin/system/resource-management/tool/tool'
import SystemSharedToolApi from '@/api/admin/system/shared-resources/tool/tool'
import SelectModel from '@/components/business/select-model/index.vue'
import { isSystemResource, isSystemSharedResource } from '@/utils/resource-context'

defineOptions({ name: 'ImageProcessingForm' })

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

function validate() {
  return formRef.value?.validate().catch(() => false) ?? Promise.resolve(false)
}
function getStrategy(): DocumentStrategy {
  return {
    split: { ...strategy.split },
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
defineExpose({ validate, getStrategy })
</script>

<template>
  <el-form ref="formRef" :model="strategy" label-position="top" require-asterisk-position="right" @submit.prevent>
    <el-card shadow="never" class="w-full">
      <div class="flex-between gap-4">
        <div>
          <h6>视觉增强</h6>
          <p class="mt-1 text-N600 text-sm">识别文档中图片，将图片按照策略发给模型或工具处理，并将返回内容写入图片的描述中</p>
        </div>
        <!-- 启用图片视觉增强 -->
        <el-switch v-model="strategy.visual.enabled" @change="handleVisualChange" />
      </div>
      <div v-if="strategy.visual.enabled" class="mk-gray-card-lg mt-4">
        <el-form-item label="增强策略" required>
          <el-radio-group v-model="strategy.visual.strategy" @change="handleVisualChange">
            <el-radio value="model">模型增强</el-radio>
            <el-radio value="tool">工具增强</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item
          v-if="strategy.visual.strategy === 'model'"
          label="视觉模型"
          prop="visual.model_id"
          :rules="{ required: true, message: '请选择视觉模型', trigger: 'change' }"
          class="mb-0! mt-4"
        >
          <SelectModel
            v-model="visualModelId"
            :options="modelOptions"
            :provider-options="providerOptions"
            :loading="modelOptionsLoading"
            placeholder="请选择视觉模型"
            teleported
            can-add
            @refresh="loadModelOptions"
          />
        </el-form-item>
        <el-form-item
          v-else
          label="增强工具"
          prop="visual.tool_id"
          :rules="{ required: true, message: '请选择增强工具', trigger: 'change' }"
          class="mb-0! mt-4"
        >
          <el-select v-model="strategy.visual.tool_id" :loading="toolOptionsLoading" placeholder="请选择增强工具" filterable class="w-full">
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
  </el-form>
</template>
