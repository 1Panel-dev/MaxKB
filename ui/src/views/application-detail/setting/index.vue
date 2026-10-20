<script setup lang="ts">
import { computed, onMounted, provide, ref, useTemplateRef, watch } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import type { ApplicationDetail, ModelItem, ModelProviderItem, ToolItem } from '@/api/types'
import ModelApi from '@/api/admin/workspace/model'
import SystemModelApi from '@/api/admin/system/resource-management/model'
import ToolApi from '@/api/admin/workspace/tool/tool'
import SystemToolApi from '@/api/admin/system/resource-management/tool/tool'
import ProviderApi from '@/api/admin/model-provider'
import SelectModel from '@/components/business/select-model/index.vue'
import SelectKnowledgeDialog from '@/components/business/select-knowledge-dialog/index.vue'
import PromptGenerate from '@/workflow-canvas/component/PromptGenerate.vue'
import ThinkingSetting from '@/workflow-canvas/component/ThinkingSetting.vue'
import type { ReasoningSettingData } from '@/workflow-canvas/types'
import ButtonLongTermSetting from './components/ButtonLongTermSetting.vue'
import ResourceSetting from '@/workflow-canvas/nodes/ai-chat-node/component/resource-setting/index.vue'
import type { ResourceSetting as AiResourceSetting } from '@/workflow-canvas/nodes/ai-chat-node/types'
import { MsgSuccess, MsgWarning } from '@/utils/message'
import { getResourceScope, isSystemResource } from '@/utils/resource-context'
import { useApplicationDetailContext } from '../context'
import { createSettings, createSettingsPayload, type ApplicationSettings, type SelectedKnowledge, type LongTermSettingData } from './settings'
import ButtonKnowledgeSetting from './components/ButtonKnowledgeSetting.vue'

defineProps<ResourceDetailPageProps>()
defineExpose({ customHeader: true })
const { application, applicationId, resourceApi, replaceApplicationDetail } = useApplicationDetailContext()
const isSystem = computed(() => isSystemResource())
const modelApi = computed(() => (isSystem.value ? SystemModelApi : ModelApi))
const toolApi = computed(() => (isSystem.value ? SystemToolApi : ToolApi))
provide('resourceScope', getResourceScope())
provide('getModelParamsForm', (modelId: string) => modelApi.value.getModelParamsForm(modelId))

/* 详情回填到设置表单，编辑数据与接口详情保持隔离。 */
const settings = ref(createSettings())
const formRef = useTemplateRef<FormInstance>('formRef')
const saving = ref(false)
const promptMode = ref<'references' | 'none'>('none')

const selectedKnowledge = ref<SelectedKnowledge[]>([])
const applicationOptions = ref<ApplicationDetail[]>([])
const toolOptions = ref<ToolItem[]>([])

/* 模型及关联资源名称：按当前资源范围加载，失败不清理已有 ID。 */
const modelOptions = ref<ModelItem[]>([])
const providerOptions = ref<ModelProviderItem[]>([])
const modelLoading = ref(false)
function loadModels() {
  const currentApplicationId = applicationId.value
  modelLoading.value = true
  return modelApi.value
    .getModelListWithShared(isSystem.value ? { workspace_id: application.value?.workspace_id } : undefined)
    .then((models) => {
      if (currentApplicationId === applicationId.value) modelOptions.value = models
    })
    .finally(() => {
      modelLoading.value = false
    })
}
const llmModels = computed(() => modelOptions.value.filter((model) => model.model_type === 'LLM'))
const sttModels = computed(() => modelOptions.value.filter((model) => model.model_type === 'STT'))
const ttsModels = computed(() => modelOptions.value.filter((model) => model.model_type === 'TTS'))

/* 详情更新统一回填；模型随应用加载，关联资源有 ID 且缺少回显数据时再查询。 */
watch(
  application,
  (detail, previousDetail) => {
    settings.value = createSettings(detail)
    selectedKnowledge.value = cloneDeep(detail?.knowledge_list ?? (detail?.knowledge_id_list ?? []).map((id) => ({ id })))
    if (!detail) return
    if (detail.id !== previousDetail?.id || detail.workspace_id !== previousDetail.workspace_id) {
      void loadModels().catch(() => {})
      applicationOptions.value = []
      toolOptions.value = []
    }

    const query = isSystem.value ? { workspace_id: detail.workspace_id } : undefined
    if (settings.value.application_ids.length && !applicationOptions.value.length) {
      void resourceApi.application
        .getAllApplication(query)
        .then((resources) => {
          if (application.value?.id === detail.id && application.value.workspace_id === detail.workspace_id) applicationOptions.value = resources
        })
        .catch(() => {})
    }
    if ((settings.value.tool_ids.length || settings.value.skill_tool_ids.length || settings.value.mcp_tool_ids.length) && !toolOptions.value.length) {
      void toolApi.value
        .getToolListWithShared(query)
        .then((resources) => {
          if (application.value?.id === detail.id && application.value.workspace_id === detail.workspace_id) toolOptions.value = resources
        })
        .catch(() => {})
    }
  },
  { immediate: true },
)

/* 长期记忆配置确认后合并到表单草稿。 */
const longTermSetting = computed<LongTermSettingData>({
  get: (): LongTermSettingData => ({
    long_term_model_id: settings.value.long_term_model_id,
    long_term_model_params_setting: settings.value.long_term_model_params_setting,
    long_term_trigger_type: settings.value.long_term_trigger_type,
    long_term_trigger_setting: settings.value.long_term_trigger_setting,
  }),
  set: (value) => {
    Object.assign(settings.value, cloneDeep(value))
    formRef.value?.clearValidate('long_term_model_id')
  },
})

/* 思考设置只合并标记字段，保留同一对象中的系统和用户提示词。 */
const thinkingSetting = computed<ReasoningSettingData>({
  get: () => ({
    reasoning_content_enable: settings.value.model_setting.reasoning_content_enable,
    reasoning_content_start: settings.value.model_setting.reasoning_content_start,
    reasoning_content_end: settings.value.model_setting.reasoning_content_end,
  }),
  set: (value) => {
    Object.assign(settings.value.model_setting, value)
  },
})

/* 语音设置：关闭后清理模型，播放恢复为浏览器方式。 */
function changeSpeechInputEnabled(enabled: boolean | number | string) {
  if (!enabled) settings.value.stt_model_id = ''
}
function changeSpeechPlaybackEnabled(enabled: boolean | number | string) {
  if (enabled) return
  settings.value.tts_model_id = ''
  settings.value.tts_type = 'BROWSER'
}

/* 资源选择：弹窗只维护临时选择，确认后更新对应 ID 和名称快照。 */
const knowledgeDialogRef = useTemplateRef<InstanceType<typeof SelectKnowledgeDialog>>('knowledgeDialogRef')
function handleOpenKnowledge() {
  knowledgeDialogRef.value?.open(selectedKnowledge.value)
}
function selectKnowledge(knowledge: SelectedKnowledge[]) {
  selectedKnowledge.value = knowledge
  settings.value.knowledge_id_list = knowledge.map(({ id }) => id)
}
function handleKnowledgeSettingSubmit(config: Partial<ApplicationSettings>) {
  Object.assign(settings.value, config)
}
function removeKnowledge(knowledgeId: string) {
  selectKnowledge(selectedKnowledge.value.filter(({ id }) => id !== knowledgeId))
}
function updateResources(changes: Partial<AiResourceSetting>) {
  Object.assign(settings.value, changes)
  if (changes.application_ids) settings.value.application_enable = true
  if (changes.tool_ids || changes.skill_tool_ids) settings.value.tool_enable = true
  if (changes.mcp_tool_ids || changes.mcp_servers !== undefined) settings.value.mcp_enable = true
}

/* 保存配置：校验通过后提交，成功更新详情并提示。 */
function submit() {
  if (!formRef.value || saving.value) return
  saving.value = true
  return formRef.value
    .validate((valid) => {
      if (!valid) MsgWarning('请检查表单填写内容')
    })
    .then((valid) => {
      if (!valid) return
      return resourceApi.application.putApplication(applicationId.value, createSettingsPayload(settings.value)).then((detail) => {
        replaceApplicationDetail(detail)
        MsgSuccess('保存成功')
      })
    })
    .catch(() => {
      // 请求错误由请求层提示，保留当前输入。
    })
    .finally(() => {
      saving.value = false
    })
}

/* 发布配置：先保存，保存成功后再发布。 */
function publish() {
  if (!formRef.value || saving.value) return
  saving.value = true
  return formRef.value
    .validate((valid) => {
      if (!valid) MsgWarning('请检查表单填写内容')
    })
    .then((valid) => {
      if (!valid) return
      return resourceApi.application.putApplication(applicationId.value, createSettingsPayload(settings.value)).then((detail) => {
        replaceApplicationDetail(detail)
        return resourceApi.application.putApplicationPublish(applicationId.value, detail.name).then((published) => {
          replaceApplicationDetail(published)
          MsgSuccess('发布成功')
        })
      })
    })
    .catch(() => {
      // 保存失败不发布；发布失败保留已经保存的配置。
    })
    .finally(() => {
      saving.value = false
    })
}

onMounted(() => {
  void ProviderApi.getProviderList()
    .then((providers) => {
      providerOptions.value = providers
    })
    .catch(() => {})
})
</script>

<template>
  <Teleport v-if="headerTarget" :to="headerTarget">
    <div class="flex-between gap-4">
      <h4>{{ title }}</h4>
      <div class="flex-align-center">
        <!-- 保存智能体设置 -->
        <el-button plain :loading="saving" @click="submit">
          <MkIcon name="icon_save_outlined" class="mr-1" />
          保存
        </el-button>
        <!-- 保存并发布智能体 -->
        <el-button type="primary" :disabled="saving" @click="publish">发布</el-button>
      </div>
    </div>
  </Teleport>
  <div class="application-settings -mx-6 -mb-6 grid min-h-0 shrink-0 grid-cols-2 overflow-hidden border-t">
    <!-- 左侧设置 -->
    <el-scrollbar class="min-h-0" view-class="p-4">
      <el-form
        v-loading="saving"
        ref="formRef"
        :model="settings"
        label-position="top"
        require-asterisk-position="right"
        @submit.prevent
        class="space-y-2"
      >
        <!-- 基本信息 -->
        <MkCollapse trigger-class="mk-gray-card-sm px-2! py-[9px]!">
          <template #label>
            <h6>基本信息</h6>
          </template>
          <div class="p-2">
            <el-form-item label="智能体名称" prop="name" :rules="{ required: true, whitespace: true, message: '请输入智能体名称', trigger: 'blur' }">
              <el-input v-model="settings.name" maxlength="64" placeholder="请输入智能体名称" @blur="settings.name = settings.name.trim()" />
            </el-form-item>
            <el-form-item label="描述">
              <el-input
                v-model="settings.desc"
                type="textarea"
                :rows="3"
                maxlength="256"
                show-word-limit
                placeholder="描述该智能体的应用场景及用途"
              />
            </el-form-item>
          </div>
        </MkCollapse>
        <!-- 模型设置 -->
        <MkCollapse :expanded="true" trigger-class="mk-gray-card-sm px-2! py-[9px]!">
          <template #label>
            <h6>模型设置</h6>
          </template>
          <div class="p-2">
            <el-form-item label="AI 模型">
              <SelectModel
                v-model="settings.model_id"
                v-model:model-params="settings.model_params_setting"
                :options="llmModels"
                :provider-options="providerOptions"
                :loading="modelLoading"
                can-edit-params
                can-add
                teleported
                placeholder="请选择 AI 模型"
                @refresh="loadModels"
              />
            </el-form-item>
            <!-- 系统提示词 -->
            <el-form-item>
              <template #label>
                <div class="flex-between w-full">
                  <div class="flex-align-center gap-1">
                    <span>系统提示词</span>
                    <MkTooltip content="设定模型扮演的角色或遵循的指令" placement="right">
                      <MkIcon name="icon_info_outlined" class="text-N600!" />
                    </MkTooltip>
                  </div>
                  <!-- 生成系统提示词 -->
                  <PromptGenerate
                    :model-id="settings.model_id"
                    :model-params-setting="settings.model_params_setting"
                    @replace="settings.model_setting.system = $event"
                  />
                </div>
              </template>
              <MdEditorMagnify
                v-model="settings.model_setting.system"
                placeholder="系统提示词，可以引用系统中的变量：{data} 是命中知识库中的分段；{question} 是用户提出的问题，{memory}开启长期记忆后的用户记忆。"
                title="系统提示词"
              />
            </el-form-item>
            <!-- 用户提示词 -->
            <el-form-item
              class="mk-hide-asterisk"
              :prop="promptMode === 'references' ? 'model_setting.prompt' : 'model_setting.no_references_prompt'"
              :rules="{ required: !!settings.model_id, whitespace: true, message: '请输入用户提示词', trigger: 'blur' }"
            >
              <template #label>
                <span class="flex-align-center gap-1">
                  <span class="mk-required">用户提示词</span>
                  <MkTooltip content="用户向模型提出的问题或输入的指令" placement="right">
                    <MkIcon name="icon_info_outlined" class="text-N600!" />
                  </MkTooltip>
                </span>
              </template>
              <!-- 切换有无引用知识库的提示词 -->
              <el-radio-group v-model="promptMode" size="small" class="mb-2">
                <el-radio-button value="references">引用知识库</el-radio-button>
                <el-radio-button value="none">无引用知识库</el-radio-button>
              </el-radio-group>
              <MdEditorMagnify
                v-if="promptMode === 'references'"
                v-model="settings.model_setting.prompt"
                placeholder="用户提示词，可以引用系统中的变量：{data} 是命中知识库中的分段；{question} 是用户提出的问题。"
                title="用户提示词（引用知识库）"
              />
              <MdEditorMagnify
                v-if="promptMode === 'none'"
                v-model="settings.model_setting.no_references_prompt"
                placeholder="用户提示词，可以引用系统中的变量：{data} 是命中知识库中的分段；{question} 是用户提出的问题。"
                title="用户提示词 （无引用知识库）"
              />
            </el-form-item>

            <el-form-item label="历史聊天记录">
              <el-input-number
                v-model="settings.dialogue_number"
                :min="0"
                :value-on-clear="0"
                controls-position="right"
                align="left"
                :step="1"
                :step-strictly="true"
              />
            </el-form-item>
          </div>
        </MkCollapse>
        <!-- 知识库 -->
        <MkCollapse :expanded="true" trigger-class="mk-gray-card-sm px-2! py-[9px]!">
          <template #label>
            <div class="flex-between w-full">
              <h6>知识库</h6>
              <div>
                <!-- 参数设置 -->
                <ButtonKnowledgeSetting :setting="settings" @submit="handleKnowledgeSettingSubmit" />
                <!-- 选择关联知识库 -->
                <el-button text type="primary" @click.stop="handleOpenKnowledge"><MkIcon name="icon_add_outlined" /></el-button>
              </div>
            </div>
          </template>
          <div class="p-2">
            <div v-if="!selectedKnowledge.length" class="text-center text-N600">关联的知识库显示在这里</div>
            <div v-else class="space-y-2">
              <template v-for="knowledge in selectedKnowledge" :key="knowledge.id">
                <el-card class="small" shadow="never">
                  <div class="flex-between">
                    <span class="flex-align-center min-w-0 gap-2">
                      <KnowledgeIcon :type="knowledge.type" :size="20" class="shrink-0 small" />
                      <span class="truncate" :title="knowledge.name || knowledge.id">{{ knowledge.name || knowledge.id }}</span>
                    </span>
                    <!-- 移除知识库 -->
                    <el-button text title="移除知识库" @click="removeKnowledge(knowledge.id)"><MkIcon name="icon_close_outlined" /></el-button>
                  </div>
                </el-card>
              </template>
            </div>
          </div>
        </MkCollapse>
        <!-- 开场白 -->
        <MkCollapse trigger-class="mk-gray-card-sm px-2! py-[9px]!">
          <template #label>
            <h6>开场白</h6>
          </template>
          <div class="p-2">
            <el-form-item label="开场白">
              <MdEditorMagnify v-model="settings.prologue" title="开场白" />
            </el-form-item>
          </div>
        </MkCollapse>
        <!-- 技能 -->
        <MkCollapse trigger-class="mk-gray-card-sm px-2! py-[9px]!">
          <template #label>
            <div class="flex-between w-full">
              <h6>技能</h6>
              <!-- 控制是否展示技能执行过程 -->
              <el-checkbox v-model="settings.mcp_output_enable" @click.stop>输出执行过程</el-checkbox>
            </div>
          </template>
          <div class="p-2">
            <ResourceSetting
              :setting="settings"
              :application-options="applicationOptions"
              :tool-options="toolOptions"
              :skill-options="toolOptions"
              :mcp-options="toolOptions"
              @update="updateResources"
            />
          </div>
        </MkCollapse>
        <!-- 高级设置 -->
        <MkCollapse trigger-class="mk-gray-card-sm px-2! py-[9px]!">
          <template #label>
            <h6>高级设置</h6>
          </template>
          <div class="p-2">
            <!-- 长期记忆 -->
            <el-form-item
              class="mk-hide-asterisk mb-2!"
              prop="long_term_model_id"
              :rules="{ required: settings.long_term_enable, message: '请选择长期记忆模型', trigger: 'change' }"
            >
              <template #label>
                <div class="flex-between">
                  <span class="flex-align-center gap-1">
                    <span :class="settings.long_term_enable ? 'mk-required' : ''">长期记忆</span>
                    <MkTooltip
                      content="开启后，从开启时间记录新对话并按周期生成记忆，可通过 {memory} 变量在系统提示词中调用。关闭后，将清空对话用户的长期记忆，再次开启将重新从开启时点开始累积。"
                      placement="right"
                    >
                      <MkIcon name="icon_info_outlined" class="text-N600!" />
                    </MkTooltip>
                  </span>
                  <span class="flex-align-center gap-2">
                    <!-- 长期记忆设置 -->
                    <ButtonLongTermSetting
                      v-if="settings.long_term_enable"
                      v-model="longTermSetting"
                      :model-options="llmModels"
                      :provider-options="providerOptions"
                    />
                    <el-switch v-model="settings.long_term_enable" size="small" />
                  </span>
                </div>
              </template>
            </el-form-item>
            <!-- 输出思考 -->
            <div class="flex-between mb-4">
              <span>输出思考</span>
              <div class="flex-align-center gap-2">
                <!-- 输出思考设置 -->
                <ThinkingSetting v-if="settings.model_setting.reasoning_content_enable" v-model="thinkingSetting" />
                <el-switch v-model="settings.model_setting.reasoning_content_enable" size="small" />
              </div>
            </div>
            <!-- 语音输入 -->
            <div class="flex-between">
              <span :class="settings.stt_model_enable ? 'mk-required' : ''">语音输入</span>
              <span class="flex-align-center gap-3">
                <el-checkbox v-if="settings.stt_model_enable" v-model="settings.stt_autosend">自动发送</el-checkbox>
                <el-switch v-model="settings.stt_model_enable" size="small" @change="changeSpeechInputEnabled" />
              </span>
            </div>
            <el-form-item
              v-if="settings.stt_model_enable"
              class="mt-2"
              prop="stt_model_id"
              :rules="{ required: true, message: '请选择语音输入模型', trigger: 'change' }"
            >
              <SelectModel
                v-model="settings.stt_model_id"
                v-model:model-params="settings.stt_model_params_setting"
                :options="sttModels"
                :provider-options="providerOptions"
                can-edit-params
                can-add
                teleported
                placeholder="请选择语音输入模型"
                @refresh="loadModels"
              />
            </el-form-item>

            <!-- 语音播放 -->
            <div class="flex-between mt-4">
              <span :class="settings.tts_model_enable && settings.tts_type !== 'BROWSER' ? 'mk-required' : ''">语音播放</span>
              <span class="flex-align-center gap-3">
                <el-checkbox v-if="settings.tts_model_enable" v-model="settings.tts_autoplay">自动播放</el-checkbox>
                <el-switch v-model="settings.tts_model_enable" size="small" @change="changeSpeechPlaybackEnabled" />
              </span>
            </div>
            <el-form-item
              v-if="settings.tts_model_enable"
              class="mt-2"
              prop="tts_model_id"
              :rules="{ required: settings.tts_type === 'TTS', message: '请选择语音播放模型', trigger: 'change' }"
            >
              <el-radio-group v-model="settings.tts_type" class="mb-2">
                <el-radio value="BROWSER">浏览器播放（免费）</el-radio>
                <el-radio value="TTS">自定义</el-radio>
              </el-radio-group>
              <SelectModel
                v-if="settings.tts_type === 'TTS'"
                v-model="settings.tts_model_id"
                v-model:model-params="settings.tts_model_params_setting"
                :options="ttsModels"
                :provider-options="providerOptions"
                can-edit-params
                can-add
                teleported
                placeholder="请选择语音播放模型"
                @refresh="loadModels"
              />
            </el-form-item>
          </div>
        </MkCollapse>
      </el-form>
    </el-scrollbar>
    <!-- 右侧预览设置 -->
    <section class="min-h-0 min-w-0 border-l">
      <el-scrollbar height="100%" view-class="p-4">
        <!-- // TODO: 预览智能体调试对话 -->
        <div>简易对话调试</div>
      </el-scrollbar>
    </section>
  </div>
  <SelectKnowledgeDialog ref="knowledgeDialogRef" @submit="selectKnowledge" />
</template>

<style scoped lang="scss">
/* 扣除应用顶栏和当前页面标题栏，两栏在剩余高度内独立滚动。 */
.application-settings {
  height: calc(100dvh - var(--mk-header-height) - var(--spacing) * 16);
}
</style>
