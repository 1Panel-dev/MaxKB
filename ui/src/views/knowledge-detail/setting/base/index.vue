<script setup lang="ts">
import { computed, nextTick, reactive, ref, useTemplateRef, watch } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { KnowledgeItem } from '@/api/types'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import type { FormInstance, FormRules } from 'element-plus'
import { KNOWLEDGE_TYPE } from '@/api/enums'
import KnowledgeBaseForm from '@/views/knowledge/create-knowledge/components/KnowledgeBaseForm.vue'
import { useKnowledgeDetailContext } from '../../context'
import { KNOWLEDGE_TYPE_MAP } from '@/constants/knowledge'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { isSystemResource, isSystemSharedResource, isWorkspaceSharedResource } from '@/utils/resource-context'
import { perm } from '@/permission'
/**
 * 知识库「设置」权限判断
 */
type KnowledgeSettingPermissionMethod = 'settingRead' | 'settingEdit'

function knowledgeSettingPermission(method: KnowledgeSettingPermissionMethod): boolean {
  if (isSystemResource()) return Boolean(perm.knowledge.system[method]())
  if (isSystemSharedResource()) return Boolean(perm.knowledge.share[method]())
  if (isWorkspaceSharedResource()) return false // 共享知识库在工作空间侧只读
  return Boolean(perm.knowledge.workspace[method](knowledgeId.value))
}

defineOptions({ name: 'KnowledgeBaseSettingView' })
const { t } = useI18n({ useScope: 'global' })

const { knowledge, knowledgeId, replaceKnowledgeDetail, resourceApi } = useKnowledgeDetailContext()

/* 详情与基本信息 */

const baseFormRef = useTemplateRef<InstanceType<typeof KnowledgeBaseForm>>('baseFormRef')
const saving = ref(false)
const knowledgeTypeKey = computed(() => (knowledge.value ? KNOWLEDGE_TYPE_MAP[knowledge.value.type].toLowerCase() : ''))
const originalEmbeddingModelId = ref('')

/* 类型配置与校验 */
const settingFormRef = ref<FormInstance>()
const settingForm = reactive({
  authentication: false,
  source_url: '',
  selector: '',
  app_id: '',
  app_secret: '',
  folder_token: '',
  file_count_limit: 50,
  file_size_limit: 100,
})
const settingRules = computed<FormRules<typeof settingForm>>(() => ({
  source_url: [{ required: true, whitespace: true, message: t('knowledge.fields.webRootUrl.requiredMessage'), trigger: 'blur' }],
  app_id: [{ required: true, whitespace: true, message: t('common.validation.inputFieldRequired', { label: 'App ID' }), trigger: 'blur' }],
  app_secret: [{ required: true, whitespace: true, message: t('common.validation.inputFieldRequired', { label: 'App Secret' }), trigger: 'blur' }],
  folder_token: [
    { required: true, whitespace: true, message: t('common.validation.inputFieldRequired', { label: 'Folder Token' }), trigger: 'blur' },
  ],
}))

// 等待异步详情与基本信息表单挂载完成后回填，不直接修改详情中的配置。
watch(
  [knowledge, baseFormRef],
  async ([detail, baseForm]) => {
    if (!detail || !baseForm) return
    Object.assign(baseForm.form, {
      name: detail.name,
      desc: detail.desc ?? '',
      embedding_model_id: detail.embedding_model_id ?? '',
    })
    originalEmbeddingModelId.value = detail.embedding_model_id ?? ''
    const meta = detail.meta ?? {}
    Object.assign(settingForm, {
      authentication: detail.authentication ?? false,
      source_url: typeof meta.source_url === 'string' ? meta.source_url : '',
      selector: typeof meta.selector === 'string' ? meta.selector : '',
      app_id: typeof meta.app_id === 'string' ? meta.app_id : '',
      app_secret: typeof meta.app_secret === 'string' ? meta.app_secret : '',
      folder_token: typeof meta.folder_token === 'string' ? meta.folder_token : '',
      file_count_limit: detail.file_count_limit ?? 50,
      file_size_limit: detail.file_size_limit ?? 100,
    })
    settingFormRef.value?.clearValidate()
    // 回填后校验向量模型，进入设置时即提示尚未配置的模型。
    await nextTick()
    await baseForm.validateEmbeddingModel()
  },
  { immediate: true, flush: 'post' },
)

/* 保存设置；更换向量模型时先确认，保存完成后重新向量化 */
function handleSave() {
  const knowledgeApi = resourceApi.knowledge
  if (saving.value || !knowledgeSettingPermission('settingEdit') || !('putKnowledge' in knowledgeApi)) return
  saving.value = true
  return Promise.all([baseFormRef.value?.validate(), settingFormRef.value?.validate().catch(() => false)])
    .then(([baseValid, settingValid]) => {
      const detail = knowledge.value
      const baseForm = baseFormRef.value?.form
      if (!baseValid || !settingValid || !detail || !baseForm) return

      const payload: Partial<KnowledgeItem> = {
        authentication: settingForm.authentication,
        name: baseForm.name.trim(),
        desc: baseForm.desc.trim(),
        embedding_model_id: baseForm.embedding_model_id,
        file_count_limit: settingForm.file_count_limit,
        file_size_limit: settingForm.file_size_limit,
      }
      if (detail.type === KNOWLEDGE_TYPE.WEB) {
        payload.meta = { ...cloneDeep(detail.meta), source_url: settingForm.source_url.trim(), selector: settingForm.selector.trim() }
      } else if (detail.type === KNOWLEDGE_TYPE.LARK) {
        payload.meta = {
          ...cloneDeep(detail.meta),
          app_id: settingForm.app_id.trim(),
          app_secret: settingForm.app_secret,
          folder_token: settingForm.folder_token.trim(),
        }
      }

      const embeddingModelChanged = originalEmbeddingModelId.value !== payload.embedding_model_id
      const confirmation = embeddingModelChanged
        ? MsgConfirm(t('common.dialogs.notice'), `${t('knowledge.baseSettings.embeddingModel.changeConfirm')}?`, {
            confirmButtonText: t('knowledge.actions.generateEmbeddings'),
            confirmButtonType: 'primary',
          })
        : Promise.resolve()

      return confirmation.then(() => {
        const request =
          detail.type === KNOWLEDGE_TYPE.LARK ? knowledgeApi.putLarkKnowledge(detail.id, payload) : knowledgeApi.putKnowledge(detail.id, payload)
        // 返回完整请求链，向量化失败时保留原模型基准，允许再次保存重试。
        return request.then((savedKnowledge) => {
          const embeddingRequest = embeddingModelChanged ? knowledgeApi.putReEmbeddingKnowledge(detail.id) : Promise.resolve()
          return embeddingRequest.then(() => {
            replaceKnowledgeDetail({ ...detail, ...savedKnowledge })
            MsgSuccess(t('common.messages.saveSuccess'))
          })
        })
      })
    })
    .catch(() => {})
    .finally(() => {
      saving.value = false
    })
}

defineProps<ResourceDetailPageProps>()
</script>

<template>
  <div v-loading="saving" class="max-w-200 pb-6">
    <KnowledgeBaseForm ref="baseFormRef" mode="setting" />
    <el-form
      v-if="knowledge"
      class="mt-4"
      ref="settingFormRef"
      :model="settingForm"
      :rules="settingRules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="t('knowledge.baseSettings.type.label')" required>
        <el-card shadow="never" class="small w-full">
          <div class="flex-align-center gap-2">
            <KnowledgeIcon :type="knowledge.type" />
            <div>
              <div>{{ t(`knowledge.${knowledgeTypeKey}.label`) }}</div>
              <div class="text-N600">{{ t(`knowledge.${knowledgeTypeKey}.description`) }}</div>
            </div>
          </div>
        </el-card>
      </el-form-item>
      <template v-if="knowledge.type === KNOWLEDGE_TYPE.WEB">
        <el-form-item :label="t('knowledge.fields.webRootUrl.label')" prop="source_url">
          <el-input
            v-model="settingForm.source_url"
            :placeholder="t('knowledge.fields.webRootUrl.placeholder')"
            @blur="settingForm.source_url = settingForm.source_url.trim()"
          />
        </el-form-item>
        <el-form-item :label="t('knowledge.fields.selector.label')" prop="selector">
          <el-input
            v-model="settingForm.selector"
            :placeholder="t('knowledge.fields.selector.placeholder')"
            @blur="settingForm.selector = settingForm.selector.trim()"
          />
        </el-form-item>
      </template>
      <template v-else-if="knowledge.type === KNOWLEDGE_TYPE.LARK">
        <el-form-item label="App ID" prop="app_id">
          <el-input
            v-model="settingForm.app_id"
            :placeholder="t('common.placeholders.inputField', { label: 'App ID' })"
            @blur="settingForm.app_id = settingForm.app_id.trim()"
          />
        </el-form-item>
        <el-form-item label="App Secret" prop="app_secret">
          <el-input
            v-model="settingForm.app_secret"
            type="password"
            autocomplete="new-password"
            show-password
            :placeholder="t('common.placeholders.inputField', { label: 'App Secret' })"
          />
        </el-form-item>
        <el-form-item label="Folder Token" prop="folder_token">
          <el-input
            v-model="settingForm.folder_token"
            :placeholder="t('common.placeholders.inputField', { label: 'Folder Token' })"
            @blur="settingForm.folder_token = settingForm.folder_token.trim()"
          />
        </el-form-item>
      </template>
      <h6 class="mb-4">{{ t('knowledge.baseSettings.otherSettings') }}</h6>
      <el-form-item :label="t('knowledge.baseSettings.fileCountLimit.label')">
        <MkSlider v-model="settingForm.file_count_limit" show-input :min="1" :max="1000" />
      </el-form-item>
      <el-form-item>
        <template #label>
          <div class="flex-align-center gap-1">
            <span>{{ t('knowledge.baseSettings.fileSizeLimit.label') }} (MB)</span>
            <MkTooltip :content="t('knowledge.baseSettings.fileSizeLimit.description')" placement="right">
              <MkIcon name="icon_info_outlined" class="text-N600!" />
            </MkTooltip>
          </div>
        </template>
        <MkSlider v-model="settingForm.file_size_limit" show-input :min="1" :max="1000" />
      </el-form-item>
      <div>
        <div class="mb-2">
          <span>{{ t('knowledge.baseSettings.authentication.label') }}</span>
          <span class="text-N600">（{{ t('knowledge.baseSettings.authentication.description') }}）</span>
        </div>
        <!-- 切换对话用户授权 -->
        <el-switch v-model="settingForm.authentication" :disabled="!knowledgeSettingPermission('settingEdit')" />
      </div>
    </el-form>

    <!-- 保存知识库设置 -->
    <el-button v-if="knowledgeSettingPermission('settingEdit')" class="mt-4" type="primary" :loading="saving" @click="handleSave">
      {{ t('common.actions.save') }}
    </el-button>
  </div>
</template>
