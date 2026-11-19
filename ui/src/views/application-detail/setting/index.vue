<script setup lang="ts">
import { computed, onMounted, provide, ref, useTemplateRef, watch } from 'vue'
import { cloneDeep, isEqual } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { ApplicationSettings, LongTermSettingData, SelectedKnowledge } from './settings'
import type { ApplicationDetail, ModelItem, ModelProviderItem, ToolItem } from '@/api/types'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import type { ResourceSetting as AiResourceSetting } from '@/workflow-canvas/nodes/ai-chat-node/types'
import type { ReasoningSettingData } from '@/workflow-canvas/types'
import type { FormInstance, FormItemRule } from 'element-plus'
import ProviderApi from '@/api/admin/model-provider'
import SystemModelApi from '@/api/admin/system/resource-management/model'
import SystemToolApi from '@/api/admin/system/resource-management/tool/tool'
import ModelApi from '@/api/admin/workspace/model'
import ToolApi from '@/api/admin/workspace/tool/tool'
import SelectKnowledgeDialog from '@/components/business/select-knowledge-dialog/index.vue'
import SelectModel from '@/components/business/select-model/index.vue'
import SimpleDebugConversation from '@/conversation-panel/view/simple-debug/index.vue'
import PromptGenerate from '@/workflow-canvas/component/PromptGenerate.vue'
import ThinkingSetting from '@/workflow-canvas/component/ThinkingSetting.vue'
import ResourceSetting from '@/workflow-canvas/nodes/ai-chat-node/component/resource-setting/index.vue'
import { useApplicationDetailContext } from '../context'
import ButtonKnowledgeSetting from './components/ButtonKnowledgeSetting.vue'
import ButtonLongTermSetting from './components/ButtonLongTermSetting.vue'
import { createSettings, createSettingsPayload } from './settings'
import { MsgSuccess, MsgWarning } from '@/utils/message'
import { getResourceScope, isSystemResource } from '@/utils/resource-context'
import perm from '@/permission/index.ts'

type ApplicationSettingPermissionMethod = 'publish'
function applicationSettingPermission(method: ApplicationSettingPermissionMethod): boolean {
  if (isSystem.value) return Boolean(perm.application.system[method]())
  return Boolean(perm.application.workspace[method](applicationId.value))
}

defineProps<ResourceDetailPageProps>()
defineExpose({ customHeader: true })
const { t } = useI18n({ useScope: 'global' })
const { application, applicationId, resourceApi, replaceApplicationDetail } = useApplicationDetailContext()
const isSystem = computed(() => isSystemResource())
const modelApi = computed(() => (isSystem.value ? SystemModelApi : ModelApi))
const toolApi = computed(() => (isSystem.value ? SystemToolApi : ToolApi))
provide('resourceScope', getResourceScope())
provide(
  'resourceWorkspaceId',
  computed(() => application.value?.workspace_id),
)
provide('getModelParamsForm', (modelId: string) => modelApi.value.getModelParamsForm(modelId))

/* 详情回填到设置表单，编辑数据与接口详情保持隔离。 */
const settings = ref(createSettings())
const savedSettingsPayload = ref(createSettingsPayload(settings.value))
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
    // 与本次回填使用相同的默认值，语言切换不重新生成比较基准。
    savedSettingsPayload.value = createSettingsPayload(settings.value)
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

/* 调试执行已保存的配置；草稿与详情回填结果不同时提示先保存。 */
const debugConversationRef = useTemplateRef<InstanceType<typeof SimpleDebugConversation>>('debugConversationRef')
const hasUnsavedSettings = computed(() => !!application.value && !isEqual(createSettingsPayload(settings.value), savedSettingsPayload.value))

/* 长期记忆配置确认后合并到表单草稿。 */
// 固定校验规则，避免启用开关时因规则变化提前校验；保存、发布时仍检查模型。
const longTermModelRule: FormItemRule = {
  validator: (_rule, value, callback) => {
    callback(settings.value.long_term_enable && !value ? new Error(t('application.longTermMemory.model.requiredMessage')) : undefined)
  },
}
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
      if (valid) return
      // 设置表单收起时展开，显示校验错误。
      debugConversationRef.value?.openSetting()
      MsgWarning(t('common.validation.formInvalid'))
    })
    .then((valid) => {
      if (!valid) return
      return resourceApi.application.putApplication(applicationId.value, createSettingsPayload(settings.value)).then((detail) => {
        replaceApplicationDetail(detail)
        MsgSuccess(t('common.messages.saveSuccess'))
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
      if (valid) return
      // 设置表单收起时展开，显示校验错误。
      debugConversationRef.value?.openSetting()
      MsgWarning(t('common.validation.formInvalid'))
    })
    .then((valid) => {
      if (!valid) return
      return resourceApi.application.putApplication(applicationId.value, createSettingsPayload(settings.value)).then((detail) => {
        replaceApplicationDetail(detail)
        return resourceApi.application.putApplicationPublish(applicationId.value, detail.name).then((published) => {
          replaceApplicationDetail(published)
          MsgSuccess(t('common.messages.publishSuccess'))
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
          {{ t('common.actions.save') }}
        </el-button>
        <!-- 保存并发布智能体 -->
        <el-button v-if="applicationSettingPermission('publish')" type="primary" :disabled="saving" @click="publish">
          {{ t('common.actions.publish') }}
        </el-button>
      </div>
    </div>
  </Teleport>
  <div class="application-settings -mx-6 -mb-6 min-h-0 shrink-0 overflow-hidden border-t">
    <!-- 调试对话，左侧放设置表单 -->
    <SimpleDebugConversation ref="debugConversationRef" :application="application">
      <template #setting>
        <!-- 左侧设置；收起时保留表单实例，保存、发布仍可校验 -->
        <el-scrollbar class="h-full" view-class="p-4">
          <el-form
            v-loading="saving"
            ref="formRef"
            :model="settings"
            :validate-on-rule-change="false"
            label-position="top"
            require-asterisk-position="right"
            @submit.prevent
            class="space-y-2"
          >
            <!-- 基本信息 -->
            <MkCollapse trigger-class="mk-gray-card-sm px-2! py-[9px]!">
              <template #label>
                <h6>{{ t('common.labels.basicInfo') }}</h6>
              </template>
              <div class="p-2">
                <el-form-item
                  :label="t('common.name.label')"
                  prop="name"
                  :rules="{ required: true, whitespace: true, message: t('application.fields.name.requiredMessage'), trigger: 'blur' }"
                >
                  <el-input
                    v-model="settings.name"
                    maxlength="64"
                    :placeholder="t('application.fields.name.placeholder')"
                    @blur="settings.name = settings.name.trim()"
                  />
                </el-form-item>
                <el-form-item :label="t('common.description.label')">
                  <el-input
                    v-model="settings.desc"
                    type="textarea"
                    :rows="3"
                    maxlength="256"
                    show-word-limit
                    :placeholder="t('application.fields.description.placeholder')"
                  />
                </el-form-item>
              </div>
            </MkCollapse>
            <!-- 模型设置 -->
            <MkCollapse :expanded="true" trigger-class="mk-gray-card-sm px-2! py-[9px]!">
              <template #label>
                <h6>{{ t('application.settings.model') }}</h6>
              </template>
              <div class="p-2">
                <el-form-item :label="t('workflow.model.label')">
                  <SelectModel
                    v-model="settings.model_id"
                    v-model:model-params="settings.model_params_setting"
                    :options="llmModels"
                    :provider-options="providerOptions"
                    :loading="modelLoading"
                    can-edit-params
                    can-add
                    teleported
                    :placeholder="t('workflow.model.placeholder')"
                    @refresh="loadModels"
                  />
                </el-form-item>
                <!-- 系统提示词 -->
                <el-form-item>
                  <template #label>
                    <div class="flex-between w-full">
                      <div class="flex-align-center gap-1">
                        <span>{{ t('workflow.systemPrompt.label') }}</span>
                        <MkTooltip :content="t('workflow.systemPrompt.description')" placement="right">
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
                    :placeholder="t('application.prompt.systemPlaceholder', { data: '{data}', question: '{question}', memory: '{memory}' })"
                    :title="t('workflow.systemPrompt.label')"
                  />
                </el-form-item>
                <!-- 用户提示词 -->
                <el-form-item
                  class="mk-hide-asterisk"
                  :prop="promptMode === 'references' ? 'model_setting.prompt' : 'model_setting.no_references_prompt'"
                  :rules="{ required: !!settings.model_id, whitespace: true, message: t('workflow.userPrompt.requiredMessage'), trigger: 'blur' }"
                >
                  <template #label>
                    <span class="flex-align-center gap-1">
                      <span class="mk-required">{{ t('workflow.userPrompt.label') }}</span>
                      <MkTooltip :content="t('workflow.userPrompt.description')" placement="right">
                        <MkIcon name="icon_info_outlined" class="text-N600!" />
                      </MkTooltip>
                    </span>
                  </template>
                  <!-- 切换有无引用知识库的提示词 -->
                  <el-radio-group v-model="promptMode" size="small" class="mb-2">
                    <el-radio-button value="references">{{ t('application.prompt.references') }}</el-radio-button>
                    <el-radio-button value="none">{{ t('application.prompt.noReferences') }}</el-radio-button>
                  </el-radio-group>
                  <MdEditorMagnify
                    v-if="promptMode === 'references'"
                    v-model="settings.model_setting.prompt"
                    :placeholder="t('application.prompt.userPlaceholder', { data: '{data}', question: '{question}' })"
                    :title="`${t('workflow.userPrompt.label')}（${t('application.prompt.references')}）`"
                  />
                  <MdEditorMagnify
                    v-if="promptMode === 'none'"
                    v-model="settings.model_setting.no_references_prompt"
                    :placeholder="t('application.prompt.userPlaceholder', { data: '{data}', question: '{question}' })"
                    :title="`${t('workflow.userPrompt.label')} （${t('application.prompt.noReferences')}）`"
                  />
                </el-form-item>

                <el-form-item :label="t('workflow.history.label')">
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
                  <h6>{{ t('knowledge.title') }}</h6>
                  <div>
                    <!-- 参数设置 -->
                    <ButtonKnowledgeSetting :setting="settings" @submit="handleKnowledgeSettingSubmit" />
                    <!-- 选择关联知识库 -->
                    <el-button text type="primary" @click.stop="handleOpenKnowledge"><MkIcon name="icon_add_outlined" /></el-button>
                  </div>
                </div>
              </template>
              <div class="p-2">
                <div v-if="!selectedKnowledge.length" class="text-center text-N600">{{ t('application.knowledgeSetting.empty') }}</div>
                <div v-else class="space-y-2">
                  <template v-for="knowledge in selectedKnowledge" :key="knowledge.id">
                    <el-card class="small" shadow="never">
                      <div class="flex-between">
                        <span class="flex-align-center min-w-0 gap-2">
                          <KnowledgeIcon :type="knowledge.type" :size="20" class="shrink-0 small" />
                          <span class="truncate" :title="knowledge.name || knowledge.id">{{ knowledge.name || knowledge.id }}</span>
                        </span>
                        <!-- 移除知识库 -->
                        <el-button text @click="removeKnowledge(knowledge.id)"><MkIcon name="icon_close_outlined" /></el-button>
                      </div>
                    </el-card>
                  </template>
                </div>
              </div>
            </MkCollapse>
            <!-- 开场白 -->
            <MkCollapse trigger-class="mk-gray-card-sm px-2! py-[9px]!">
              <template #label>
                <h6>{{ t('application.prologue.label') }}</h6>
              </template>
              <div class="p-2">
                <el-form-item :label="t('application.prologue.label')">
                  <MdEditorMagnify v-model="settings.prologue" :title="t('application.prologue.label')" />
                </el-form-item>
              </div>
            </MkCollapse>
            <!-- 技能 -->
            <MkCollapse trigger-class="mk-gray-card-sm px-2! py-[9px]!">
              <template #label>
                <div class="flex-between w-full">
                  <h6>{{ t('application.settings.skills') }}</h6>
                  <!-- 控制是否展示技能执行过程 -->
                  <el-checkbox v-model="settings.mcp_output_enable" @click.stop>{{ t('workflow.skills.outputExecution') }}</el-checkbox>
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
                <h6>{{ t('application.settings.advanced') }}</h6>
              </template>
              <div class="p-2">
                <!-- 长期记忆 -->
                <el-form-item class="mk-hide-asterisk mb-2!" prop="long_term_model_id" :rules="longTermModelRule">
                  <template #label>
                    <div class="flex-between">
                      <span class="flex-align-center gap-1">
                        <span :class="settings.long_term_enable ? 'mk-required' : ''">{{ t('application.longTermMemory.label') }}</span>
                        <MkTooltip :content="t('application.longTermMemory.description', { memory: '{memory}' })" placement="right">
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
                        <el-switch
                          v-model="settings.long_term_enable"
                          size="small"
                          :validate-event="false"
                          @change="formRef?.clearValidate('long_term_model_id')"
                        />
                      </span>
                    </div>
                  </template>
                </el-form-item>
                <!-- 输出思考 -->
                <div class="flex-between mb-4">
                  <span>{{ t('workflow.thinking.label') }}</span>
                  <div class="flex-align-center gap-2">
                    <!-- 输出思考设置 -->
                    <ThinkingSetting v-if="settings.model_setting.reasoning_content_enable" v-model="thinkingSetting" />
                    <el-switch v-model="settings.model_setting.reasoning_content_enable" size="small" />
                  </div>
                </div>
                <!-- 语音输入 -->
                <div class="flex-between">
                  <span :class="settings.stt_model_enable ? 'mk-required' : ''">{{ t('application.speechInput.label') }}</span>
                  <span class="flex-align-center gap-3">
                    <el-checkbox v-if="settings.stt_model_enable" v-model="settings.stt_autosend">
                      {{ t('application.speechInput.autoSend') }}
                    </el-checkbox>
                    <el-switch v-model="settings.stt_model_enable" size="small" @change="changeSpeechInputEnabled" />
                  </span>
                </div>
                <el-form-item
                  v-if="settings.stt_model_enable"
                  class="mt-2"
                  prop="stt_model_id"
                  :rules="{ required: true, message: t('application.speechInput.model.requiredMessage'), trigger: 'change' }"
                >
                  <SelectModel
                    v-model="settings.stt_model_id"
                    v-model:model-params="settings.stt_model_params_setting"
                    :options="sttModels"
                    :provider-options="providerOptions"
                    can-edit-params
                    can-add
                    teleported
                    :placeholder="t('application.speechInput.model.placeholder')"
                    @refresh="loadModels"
                  />
                </el-form-item>

                <!-- 语音播放 -->
                <div class="flex-between mt-4">
                  <span :class="settings.tts_model_enable && settings.tts_type !== 'BROWSER' ? 'mk-required' : ''">
                    {{ t('application.speechPlayback.label') }}
                  </span>
                  <span class="flex-align-center gap-3">
                    <el-checkbox v-if="settings.tts_model_enable" v-model="settings.tts_autoplay">
                      {{ t('application.speechPlayback.autoPlay') }}
                    </el-checkbox>
                    <el-switch v-model="settings.tts_model_enable" size="small" @change="changeSpeechPlaybackEnabled" />
                  </span>
                </div>
                <el-form-item
                  v-if="settings.tts_model_enable"
                  class="mt-2"
                  prop="tts_model_id"
                  :rules="{
                    required: settings.tts_type === 'TTS',
                    message: t('application.speechPlayback.model.requiredMessage'),
                    trigger: 'change',
                  }"
                >
                  <el-radio-group v-model="settings.tts_type" class="mb-2">
                    <el-radio value="BROWSER">{{ t('application.speechPlayback.browser') }}</el-radio>
                    <el-radio value="TTS">{{ t('application.speechPlayback.custom') }}</el-radio>
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
                    :placeholder="t('application.speechPlayback.model.placeholder')"
                    @refresh="loadModels"
                  />
                </el-form-item>
              </div>
            </MkCollapse>
          </el-form>
        </el-scrollbar>
      </template>
      <template v-if="hasUnsavedSettings" #notice>
        <div class="shrink-0 px-3 pb-2">
          <el-alert type="warning" :closable="false" show-icon :title="t('application.settings.unsavedMessage')" />
        </div>
      </template>
    </SimpleDebugConversation>
  </div>
  <SelectKnowledgeDialog ref="knowledgeDialogRef" @submit="selectKnowledge" />
</template>

<style scoped lang="scss">
/* 扣除应用顶栏和当前页面标题栏，设置与对话在剩余高度内独立滚动。 */
.application-settings {
  height: calc(100dvh - var(--mk-header-height) - var(--spacing) * 16);
}
</style>
