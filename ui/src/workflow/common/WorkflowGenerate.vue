<template>
  <el-dialog
    v-model="dialogVisible"
    :title="$t('workflow.aiGenerate.title')"
    width="680px"
    :close-on-click-modal="false"
    :close-on-press-escape="!generating"
    @close="handleClose"
  >
    <!-- 输入态 -->
    <div v-if="!generating && !stages.length" class="workflow-generate-container">
      <el-form :model="formData" label-position="top">
        <el-form-item :label="$t('workflow.aiGenerate.description')">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="6"
            :placeholder="$t('workflow.aiGenerate.descriptionPlaceholder')"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>

        <el-form-item :label="$t('workflow.aiGenerate.model')">
          <el-select
            v-model="formData.model_id"
            :placeholder="$t('workflow.aiGenerate.modelPlaceholder')"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="model in llmModelList"
              :key="model.id"
              :label="model.name"
              :value="model.id"
            >
              <div class="model-option">
                <span>{{ model.name }}</span>
                <span class="model-provider">{{ model.provider }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>

      <div class="tips-section" v-if="!formData.description">
        <p class="tips-title">{{ $t('workflow.aiGenerate.tips') }}</p>
        <div class="example-list">
          <div
            v-for="(example, index) in examples"
            :key="index"
            class="example-item"
            @click="runExample(example)"
          >
            <el-icon><Document /></el-icon>
            <span>{{ example.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 进度态 -->
    <div v-else class="workflow-progress">
      <!-- 进度条 -->
      <el-progress
        class="generate-progress"
        :percentage="progress"
        :status="progressStatus"
        :stroke-width="8"
        :format="formatProgress"
      />

      <!-- 阶段列表 -->
      <div class="stage-list">
        <div 
          v-for="(stage, index) in stages" 
          :key="index" 
          class="stage-item"
          :class="{ 'is-active': index === stages.length - 1 && !done && !errored }"
        >
          <div class="stage-icon-wrapper">
            <el-icon v-if="errored && index === stages.length - 1" class="stage-icon error">
              <CircleClose />
            </el-icon>
            <el-icon v-else-if="index < stages.length - 1 || done" class="stage-icon done">
              <CircleCheck />
            </el-icon>
            <el-icon v-else class="stage-icon loading">
              <Loading />
            </el-icon>
          </div>
          <div class="stage-content">
            <span class="stage-text">{{ stage.message || stage }}</span>
            <!-- 资源匹配结果 -->
            <div v-if="stage.matched" class="matched-resources">
              <div v-if="stage.matched.knowledge?.length" class="resource-group">
                <span class="resource-label">知识库：</span>
                <el-tag v-for="kb in stage.matched.knowledge" :key="kb.id" size="small" type="info">
                  {{ kb.name }}
                </el-tag>
              </div>
              <div v-if="stage.matched.tools?.length" class="resource-group">
                <span class="resource-label">工具：</span>
                <el-tag v-for="tool in stage.matched.tools" :key="tool.id" size="small" type="warning">
                  {{ tool.name }}
                </el-tag>
              </div>
              <div v-if="stage.matched.applications?.length" class="resource-group">
                <span class="resource-label">应用：</span>
                <el-tag v-for="app in stage.matched.applications" :key="app.id" size="small" type="success">
                  {{ app.name }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <template #footer>
      <template v-if="!generating && !stages.length">
        <el-button @click="handleClose">{{ $t('common.cancel') }}</el-button>
        <el-button
          type="primary"
          @click="handleGenerate"
          :disabled="!formData.description || !formData.model_id"
        >
          {{ $t('workflow.aiGenerate.generate') }}
        </el-button>
      </template>
      <template v-else>
        <el-button v-if="errored || done" @click="resetToInput">
          {{ $t('workflow.aiGenerate.regenerate') }}
        </el-button>
        <el-button @click="handleClose" :disabled="generating">
          {{ $t('common.close') }}
        </el-button>
      </template>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import {
  Document,
  CircleCheck,
  CircleClose,
  Loading,
} from '@element-plus/icons-vue'
import { generateWorkflowStream } from '@/api/application/workflow-generate'
import modelApi from '@/api/model/model'

const { t } = useI18n()

interface Props {
  visible: boolean
}
const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'generated', data: any): void
}>()

const llmModelList = ref<any[]>([])
const formData = reactive({ description: '', model_id: '' })

// 进度状态
const generating = ref(false)
const stages = ref<any[]>([])
const planText = ref('')
const done = ref(false)
const errored = ref(false)
const progress = ref(0)

const progressStatus = computed(() =>
  errored.value ? 'exception' : done.value ? 'success' : ''
)

// 进度条：非线性仿真——真实阶段只提供"地板"，中间用一条"迅速逼近天花板、再磨蹭"的曲线填满
const progressFloor = ref(0) // 已确认里程碑（只增）
const progressCeiling = ref(0) // 缓动目标：地板往上留一段"磨蹭区间"
let progressRaf: number | null = null
const PROGRESS_K = 0.06 // 每帧向天花板逼近的比例（越大越活泼）
const PROGRESS_BAND = 14 // 天花板超出已确认里程碑的幅度

const animateProgress = () => {
  const target = progressCeiling.value
  if (progress.value < target) {
    // 指数缓动：离天花板越远步子越大（迅速逼近），越近越小（磨蹭）；+0.04 防止彻底停住
    progress.value = Math.min(target, progress.value + (target - progress.value) * PROGRESS_K + 0.04)
  }
  progressRaf = requestAnimationFrame(animateProgress)
}
const startProgress = () => {
  stopProgress()
  progressRaf = requestAnimationFrame(animateProgress)
}
const stopProgress = () => {
  if (progressRaf != null) {
    cancelAnimationFrame(progressRaf)
    progressRaf = null
  }
}
// 真实阶段抬升地板与天花板（floor/ceiling 只增，保证单调不回退）
const bumpProgress = (milestone: number) => {
  if (milestone <= 0) return
  if (milestone > progressFloor.value) progressFloor.value = milestone
  progressCeiling.value = Math.max(
    progressCeiling.value,
    Math.min(progressFloor.value + PROGRESS_BAND, 99),
  )
}
const formatProgress = (p: number) => `${Math.round(p)}%`

// 阶段文案 → 里程碑百分比（关键词顺序敏感：更具体的放前面）
const stageMilestones: Array<[string, number]> = [
  ['理解需求', 10],
  ['分析可用资源', 20],
  ['可用资源', 22],
  ['匹配', 30],
  ['规划完成', 55],
  ['规划', 45],
  ['生成节点', 70],
  ['结构校验通过', 85],
  ['校验', 80],
  ['调试运行通过', 96],
  ['调试运行', 92],
  ['已生成可编辑工作流', 98],
  ['生成完成', 100],
]

const progressFromStage = (message: string): number => {
  for (const [keyword, percent] of stageMilestones) {
    if (message.includes(keyword)) return percent
  }
  return 0
}

const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value),
})

const examples = [
  // 意图多分支型：intent 三分支 + 知识检索 + 命中/未命中判断
  {
    label: '做一个公司 IT 服务台助手',
    value:
      '做一个公司 IT 服务台助手：先分辨用户是想查报销政策、报修电脑、还是重置账号密码。查政策的就从知识库检索后用大模型整理成清晰回答，查不到就提示去提交工单；报修和改密码分别给出操作指引；纯闲聊就友好回应一句。',
  },
  // 文档提炼型：文档提取 + 大模型总结的线性管道，没有意图分类
  {
    label: '做一个合同要点提炼助手',
    value:
      '做一个合同要点提炼助手：用户把一段合同或文档内容发进来，先自动从中提取关键信息（比如甲乙双方、金额、期限、违约责任等），再用大模型把这些要点整理成一份条理清晰的摘要返回给用户；如果内容为空或识别不出有效信息，就提示用户重新提供文本。',
  },
  // 表单收集 + 阈值分流型：先用表单收集字段，再按数值区间走不同分支
  {
    label: '做一个请假申请预审助手',
    value:
      '做一个请假申请预审助手：先通过表单收集请假人、请假类型、开始时间、结束时间和请假事由，然后根据请假天数判断——3 天以内提示可直接线上提交，3 到 7 天提示需要主管审批，超过 7 天提示需要走线下纸质流程并附上注意事项。',
  },
]

const fetchModelList = async () => {
  try {
    const res = await modelApi.getSelectModelList({ model_type: 'LLM' })
    if (res.data) {
      llmModelList.value = res.data
    }
  } catch (error) {
    console.error('获取模型列表失败:', error)
  }
}

const handleEvent = (evt: any) => {
  if (evt.type === 'stage') {
    stages.value.push({
      message: evt.message,
      matched: evt.matched || null,
    })
    // 真实阶段只抬"地板/天花板"，具体数值由缓动动画平滑逼近
    bumpProgress(progressFromStage(evt.message || ''))
  } else if (evt.type === 'plan') {
    // 规划内容仅在后台累积，不再向用户展示
    planText.value += evt.content
  } else if (evt.type === 'error') {
    errored.value = true
    generating.value = false
    stopProgress()
    stages.value.push({ message: evt.error })
    ElMessage.error(evt.error || t('workflow.aiGenerate.error'))
  } else if (evt.type === 'done') {
    done.value = true
    generating.value = false
    progressFloor.value = 100
    progressCeiling.value = 100
    progress.value = 100
    stopProgress()
    ElMessage.success(t('workflow.aiGenerate.success'))
    emit('generated', evt.workflow)
    setTimeout(() => handleClose(), 500)
  }
}

// 点击示例：直接用示例内容触发生成，不回填到文本框展示
const runExample = (example: { label: string; value: string }) => {
  if (!formData.model_id) {
    ElMessage.warning(t('workflow.aiGenerate.fillRequired'))
    return
  }
  formData.description = example.value
  handleGenerate()
}

const handleGenerate = async () => {
  if (!formData.description || !formData.model_id) {
    ElMessage.warning(t('workflow.aiGenerate.fillRequired'))
    return
  }
  generating.value = true
  done.value = false
  errored.value = false
  stages.value = []
  planText.value = ''
  progress.value = 0
  progressFloor.value = 0
  progressCeiling.value = 10 // 起步就给一点天花板，条立刻开始动
  startProgress()

  try {
    const response = await generateWorkflowStream({
      description: formData.description,
      model_id: formData.model_id,
    })
    if (!response.ok || !response.body) {
      throw new Error(t('workflow.aiGenerate.error'))
    }
    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''
    let finished = false
    while (!finished) {
      const { done: streamDone, value } = await reader.read()
      if (streamDone) break
      buffer += decoder.decode(value, { stream: true })
      const matches = buffer.match(/data:.*?}\n\n/g)
      if (matches) {
        buffer = buffer.replace(matches.join(''), '')
        for (const item of matches) {
          const evt = JSON.parse(item.replace(/^data:/, '').trim())
          handleEvent(evt)
          if (evt.is_end) finished = true
        }
      }
    }
  } catch (error: any) {
    errored.value = true
    generating.value = false
    stopProgress()
    ElMessage.error(error?.message || t('workflow.aiGenerate.error'))
  } finally {
    generating.value = false
  }
}

const resetToInput = () => {
  stopProgress()
  stages.value = []
  planText.value = ''
  done.value = false
  errored.value = false
  generating.value = false
  progress.value = 0
  progressFloor.value = 0
  progressCeiling.value = 0
}

const handleClose = () => {
  if (generating.value) return
  resetToInput()
  formData.description = ''
  formData.model_id = ''
  dialogVisible.value = false
}

onMounted(() => {
  fetchModelList()
})

onBeforeUnmount(() => {
  stopProgress()
})
</script>

<style scoped lang="scss">
.workflow-generate-container {
  .model-option {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .model-provider {
      color: var(--el-text-color-secondary);
      font-size: 12px;
    }
  }

  .tips-section {
    margin-top: 16px;
    padding: 16px;
    background-color: var(--el-fill-color-light);
    border-radius: 8px;

    .tips-title {
      font-size: 14px;
      color: var(--el-text-color-regular);
      margin-bottom: 12px;
    }

    .example-list {
      display: flex;
      flex-direction: column;
      gap: 8px;

      .example-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        background-color: var(--el-bg-color);
        border-radius: 6px;
        cursor: pointer;
        font-size: 13px;
        color: var(--el-text-color-regular);
        transition: all 0.2s;

        &:hover {
          background-color: var(--el-color-primary-light-9);
          color: var(--el-color-primary);
        }

        .el-icon {
          flex-shrink: 0;
        }
      }
    }
  }
}

.workflow-progress {
  min-height: 200px;

  .generate-progress {
    margin-bottom: 20px;

    // 关掉 el-progress 自带的 width 过渡，让 rAF 缓动成为唯一动画源，避免两套动画打架发飘
    :deep(.el-progress-bar__inner) {
      transition: none;
    }
  }

  .stage-list {
    display: flex;
    flex-direction: column;
    gap: 16px;

    .stage-item {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      font-size: 14px;
      color: var(--el-text-color-regular);
      transition: all 0.3s;

      &.is-active {
        .stage-text {
          color: var(--el-color-primary);
          font-weight: 500;
        }
      }

      .stage-icon-wrapper {
        flex-shrink: 0;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .stage-icon {
        font-size: 18px;

        &.done {
          color: var(--el-color-success);
        }

        &.error {
          color: var(--el-color-danger);
        }

        &.loading {
          color: var(--el-color-primary);
          animation: rotate 1s linear infinite;
        }
      }

      .stage-content {
        flex: 1;
        min-width: 0;

        .stage-text {
          display: block;
          line-height: 1.5;
        }

        .matched-resources {
          margin-top: 8px;
          padding: 8px 12px;
          background-color: var(--el-fill-color-lighter);
          border-radius: 4px;

          .resource-group {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 4px;

            &:last-child {
              margin-bottom: 0;
            }

            .resource-label {
              font-size: 12px;
              color: var(--el-text-color-secondary);
              flex-shrink: 0;
            }

            .el-tag {
              margin-right: 4px;
            }
          }
        }
      }
    }
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
