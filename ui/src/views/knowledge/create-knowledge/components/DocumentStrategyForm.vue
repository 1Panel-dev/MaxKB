<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { DocumentStrategy, ModelItem, ModelProviderItem, ToolItem } from '@/api/types'
import ModelApi from '@/api/admin/workspace/model'
import ProviderApi from '@/api/admin/model-provider'
import ToolApi from '@/api/admin/workspace/tool/tool'
import SelectModel from '@/components/business/select-model/index.vue'

defineOptions({ name: 'DocumentStrategyForm' })

/* 文档处理策略 */
const formRef = ref<FormInstance>()
const strategy = reactive<DocumentStrategy>({
  split: { mode: 'smart', patterns: null, min_length: 500, max_length: 4096, child_length: 256, auto_clean: true },
  visual: { enabled: false, strategy: 'model', model_id: null, tool_id: null },
  index: { title_as_question: false },
})
const visualModelId = computed({
  get: () => strategy.visual.model_id ?? '',
  set: (value: string) => {
    strategy.visual.model_id = value || null
  },
})
const strategyRules: FormRules = {
  'split.min_length': [
    {
      validator: (_rule, value: number, callback) =>
        callback(value > strategy.split.max_length ? new Error('最小分段长度不能超过最大分段长度') : undefined),
      trigger: 'change',
    },
  ],
}
const splitPatternOptions = ['#', '##', '###', '####', '#####', '######'].map((heading) => ({
  label: heading,
  value: `(?m)^${heading} .*`,
}))
const splitPatterns = ref<string[]>(splitPatternOptions.slice(0, 4).map((option) => option.value))
const splitOptions = [
  { value: 'smart', title: '智能分段（推荐）', desc: '不了解如何设置分段规则时推荐使用智能分段' },
  { value: 'advanced', title: '高级分段', desc: '用户可根据文档规范自行设置分段标识符、分段长度以及清洗规则' },
] as const
function validate() {
  return formRef.value?.validate().catch(() => false) ?? Promise.resolve(false)
}
function getStrategy(): DocumentStrategy {
  return {
    split: {
      ...(strategy.split.mode === 'smart'
        ? { mode: 'smart' as const, min_length: 0, max_length: 4096, child_length: 256, auto_clean: false }
        : strategy.split),
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
const optionsLoading = ref(false)
const modelOptions = ref<ModelItem[]>([])
const providerOptions = ref<ModelProviderItem[]>([])
const toolOptions = ref<ToolItem[]>([])
const selectedVisualTool = computed(() => toolOptions.value.find((tool) => tool.id === strategy.visual.tool_id))
function loadOptions() {
  optionsLoading.value = true
  return Promise.all([
    ModelApi.getModelListWithShared({ model_type: 'IMAGE' }),
    ProviderApi.getProviderListByModelType('IMAGE'),
    ToolApi.getToolListWithShared(),
  ])
    .then(([models, providers, tools]) => {
      modelOptions.value = models
      providerOptions.value = providers
      toolOptions.value = tools
    })
    .finally(() => {
      optionsLoading.value = false
    })
}
onMounted(loadOptions)
defineExpose({ validate, getStrategy })
</script>

<template>
  <el-form ref="formRef" :model="strategy" :rules="strategyRules" label-position="top" require-asterisk-position="right" @submit.prevent>
    <el-form-item label="分段规则">
      <div class="w-full space-y-2" role="radiogroup">
        <template v-for="option in splitOptions" :key="option.value">
          <!-- 选择分段规则 -->
          <MkSourceCard
            :title="option.title"
            class="min-h-0!"
            :class="{ 'border-primary!': strategy.split.mode === option.value }"
            :aria-checked="strategy.split.mode === option.value"
            @click="strategy.split.mode = option.value"
          >
            <template #icon>
              <el-avatar v-if="option.value === 'smart'" shape="square" :size="24" class="shrink-0">
                <MkIcon name="icon_center-alignment_outlined" :size="15" />
              </el-avatar>
              <el-avatar v-else shape="square" :size="24" class="shrink-0 bg-warning!">
                <MkIcon name="icon_setting" :size="15" />
              </el-avatar>
            </template>
            <template #subtitle>{{ option.desc }}</template>
            <template v-if="option.value === 'advanced' && strategy.split.mode === 'advanced'" #default>
              <div class="mk-gray-card-lg cursor-default text-N900" @click.stop @keydown.stop>
                <el-form-item>
                  <template #label>
                    <span class="flex-align-center gap-1">
                      分段标识
                      <MkTooltip content="按照所选符号先后顺序做递归分割，分割结果超出分段长度将截取至分段长度。" placement="top">
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
                    placeholder="请选择或输入分段标识"
                    class="w-full"
                  >
                    <el-option v-for="pattern in splitPatternOptions" :key="pattern.value" :label="pattern.label" :value="pattern.value" />
                  </el-select>
                </el-form-item>
                <el-form-item label="分段长度" prop="split.min_length">
                  <div class="flex-align-center w-full gap-2">
                    <el-input-number
                      v-model="strategy.split.min_length"
                      :min="50"
                      :max="100000"
                      controls-position="right"
                      align="left"
                      class="min-w-0 flex-1"
                    />
                    <span>–</span>
                    <el-input-number
                      v-model="strategy.split.max_length"
                      :min="50"
                      :max="100000"
                      controls-position="right"
                      align="left"
                      class="min-w-0 flex-1"
                    />
                  </div>
                </el-form-item>
                <el-form-item>
                  <template #label>
                    <span class="flex-align-center gap-1">
                      子块长度
                      <MkTooltip content="子块长度仅用户向量检索，命中后将回溯显示其所在分段" placement="top">
                        <MkIcon name="icon_info_outlined" class="text-N600!"></MkIcon>
                      </MkTooltip>
                    </span>
                  </template>
                  <el-input-number
                    v-model="strategy.split.child_length"
                    :min="50"
                    :max="100000"
                    controls-position="right"
                    align="left"
                    class="w-full!"
                  />
                </el-form-item>
                <el-form-item label="自动清洗" class="mb-0!">
                  <div>
                    <el-switch v-model="strategy.split.auto_clean" />
                    <p class="text-N600">去掉重复多余符号空格、空行、制表符</p>
                  </div>
                </el-form-item>
              </div>
            </template>
          </MkSourceCard>
        </template>
      </div>
    </el-form-item>
    <el-form-item label="图片处理">
      <el-card shadow="never" class="w-full">
        <div class="flex-between gap-4">
          <div>
            <h6>视觉增强</h6>
            <p class="mt-1 text-N600 text-sm">识别文档中图片，将图片按照策略发给模型或工具处理，并将返回内容写入图片的描述中</p>
          </div>
          <el-switch v-model="strategy.visual.enabled" />
        </div>
        <div v-if="strategy.visual.enabled" class="mk-gray-card-lg mt-4">
          <el-form-item label="增强策略" required>
            <el-radio-group v-model="strategy.visual.strategy">
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
              :disabled="optionsLoading"
              placeholder="请选择视觉模型"
              teleported
              can-add
              @refresh="loadOptions"
            />
          </el-form-item>
          <el-form-item
            v-else
            label="增强工具"
            prop="visual.tool_id"
            :rules="{ required: true, message: '请选择增强工具', trigger: 'change' }"
            class="mb-0! mt-4"
          >
            <el-select v-model="strategy.visual.tool_id" placeholder="请选择增强工具" filterable class="w-full">
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
    </el-form-item>
    <el-form-item label="索引增强">
      <el-card shadow="never" class="w-full">
        <div class="flex-between">
          <div>
            <h6>分段标题设置为问题索引</h6>
            <p class="mt-1 text-N600 text-sm">开启后会将分段标题自动添加为关联问题</p>
          </div>
          <el-switch v-model="strategy.index.title_as_question" />
        </div>
      </el-card>
    </el-form-item>
  </el-form>
</template>
