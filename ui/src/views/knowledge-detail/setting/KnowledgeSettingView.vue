<script setup lang="ts">
import { computed, reactive, ref, useTemplateRef, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { cloneDeep } from 'lodash'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import { KNOWLEDGE_TYPE } from '@/api/enums'
import type { KnowledgeItem } from '@/api/types'
import { KNOWLEDGE_TYPE_LABELS, KNOWLEDGE_TYPE_MAP } from '@/constants/knowledge'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import KnowledgeBaseForm from '@/views/knowledge/create-knowledge/components/KnowledgeBaseForm.vue'
import { useKnowledgeDetailContext } from '../context'

defineOptions({ name: 'KnowledgeSettingView' })

const { knowledge, replaceKnowledgeDetail } = useKnowledgeDetailContext()

/* 详情与基本信息 */

const baseFormRef = useTemplateRef<InstanceType<typeof KnowledgeBaseForm>>('baseFormRef')
const saving = ref(false)
const knowledgeTypeLabel = computed(() => (knowledge.value ? KNOWLEDGE_TYPE_LABELS[KNOWLEDGE_TYPE_MAP[knowledge.value.type]] : ''))
const originalEmbeddingModelId = ref('')

/* 类型配置与校验 */
const settingFormRef = ref<FormInstance>()
const settingForm = reactive({
  source_url: '',
  selector: '',
  app_id: '',
  app_secret: '',
  folder_token: '',
  file_count_limit: 50,
  file_size_limit: 100,
})
const settingRules: FormRules<typeof settingForm> = {
  source_url: [{ required: true, whitespace: true, message: '请输入 Web 站点 URL', trigger: 'blur' }],
  app_id: [{ required: true, whitespace: true, message: '请输入 App ID', trigger: 'blur' }],
  app_secret: [{ required: true, whitespace: true, message: '请输入 App Secret', trigger: 'blur' }],
  folder_token: [{ required: true, whitespace: true, message: '请输入 Folder Token', trigger: 'blur' }],
}
const knowledgeTypeDescriptions = {
  [KNOWLEDGE_TYPE.BASE]: '通过上传文件或手动录入构建知识库',
  [KNOWLEDGE_TYPE.WEB]: '通过网站链接构建知识库',
  [KNOWLEDGE_TYPE.LARK]: '通过飞书文档构建知识库',
  [KNOWLEDGE_TYPE.WORKFLOW]: '通过自定义工作流方式构建知识库',
}

// 等待异步详情与基本信息表单挂载完成后回填，不直接修改详情中的配置。
watch(
  [knowledge, baseFormRef],
  ([detail, baseForm]) => {
    if (!detail || !baseForm) return
    Object.assign(baseForm.form, {
      name: detail.name,
      desc: detail.desc ?? '',
      embedding_model_id: detail.embedding_model_id ?? '',
    })
    originalEmbeddingModelId.value = detail.embedding_model_id ?? ''
    const meta = detail.meta ?? {}
    Object.assign(settingForm, {
      source_url: typeof meta.source_url === 'string' ? meta.source_url : '',
      selector: typeof meta.selector === 'string' ? meta.selector : '',
      app_id: typeof meta.app_id === 'string' ? meta.app_id : '',
      app_secret: typeof meta.app_secret === 'string' ? meta.app_secret : '',
      folder_token: typeof meta.folder_token === 'string' ? meta.folder_token : '',
      file_count_limit: detail.file_count_limit ?? 50,
      file_size_limit: detail.file_size_limit ?? 100,
    })
    settingFormRef.value?.clearValidate()
  },
  { immediate: true, flush: 'post' },
)

/* 保存设置；更换向量模型时先确认，保存完成后重新向量化 */
function handleSave() {
  saving.value = true
  return Promise.all([baseFormRef.value?.validate(), settingFormRef.value?.validate().catch(() => false)])
    .then(([baseValid, settingValid]) => {
      const detail = knowledge.value
      const baseForm = baseFormRef.value?.form
      if (!baseValid || !settingValid || !detail || !baseForm) return

      const payload: Partial<KnowledgeItem> = {
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
        ? MsgConfirm('更换向量模型', '更换向量模型后，需要对知识库中的文档重新向量化，是否继续？', {
            confirmButtonText: '保存并重新向量化',
            confirmButtonType: 'primary',
          })
        : Promise.resolve()

      return confirmation.then(() => {
        const request =
          detail.type === KNOWLEDGE_TYPE.LARK ? KnowledgeApi.putLarkKnowledge(detail.id, payload) : KnowledgeApi.putKnowledge(detail.id, payload)
        // 返回完整请求链，向量化失败时保留原模型基准，允许再次保存重试。
        return request.then((savedKnowledge) => {
          const embeddingRequest = embeddingModelChanged ? KnowledgeApi.putReEmbeddingKnowledge(detail.id) : Promise.resolve()
          return embeddingRequest.then(() => {
            replaceKnowledgeDetail({ ...detail, ...savedKnowledge })
            MsgSuccess('保存成功')
          })
        })
      })
    })
    .catch(() => {})
    .finally(() => {
      saving.value = false
    })
}
</script>

<template>
  <div v-if="knowledge" class="max-w-200 pb-6">
    <KnowledgeBaseForm ref="baseFormRef" :disabled="saving" />
    <el-form
      class="mt-4"
      ref="settingFormRef"
      :model="settingForm"
      :rules="settingRules"
      :disabled="saving"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item label="知识库类型" required>
        <el-card shadow="never" class="small w-full" style="--el-card-padding: 8px 12px">
          <div class="flex items-center gap-2">
            <KnowledgeIcon :type="knowledge.type" />
            <div>
              <div>{{ knowledgeTypeLabel }}</div>
              <div class="text-N600">{{ knowledgeTypeDescriptions[knowledge.type] }}</div>
            </div>
          </div>
        </el-card>
      </el-form-item>
      <template v-if="knowledge.type === KNOWLEDGE_TYPE.WEB">
        <el-form-item label="Web 站点 URL" prop="source_url">
          <el-input
            v-model="settingForm.source_url"
            placeholder="请输入 Web 站点 URL"
            @blur="settingForm.source_url = settingForm.source_url.trim()"
          />
        </el-form-item>
        <el-form-item label="选择器" prop="selector">
          <el-input
            v-model="settingForm.selector"
            placeholder="请输入 CSS 选择器，默认 body"
            @blur="settingForm.selector = settingForm.selector.trim()"
          />
        </el-form-item>
      </template>
      <template v-else-if="knowledge.type === KNOWLEDGE_TYPE.LARK">
        <el-form-item label="App ID" prop="app_id">
          <el-input v-model="settingForm.app_id" placeholder="请输入 App ID" @blur="settingForm.app_id = settingForm.app_id.trim()" />
        </el-form-item>
        <el-form-item label="App Secret" prop="app_secret">
          <el-input v-model="settingForm.app_secret" type="password" autocomplete="new-password" show-password placeholder="请输入 App Secret" />
        </el-form-item>
        <el-form-item label="Folder Token" prop="folder_token">
          <el-input
            v-model="settingForm.folder_token"
            placeholder="请输入 Folder Token"
            @blur="settingForm.folder_token = settingForm.folder_token.trim()"
          />
        </el-form-item>
      </template>
      <MkCollapse v-else-if="knowledge.type === KNOWLEDGE_TYPE.BASE" indicator-position="after" trigger="indicator" trigger-class="mb-2">
        <template #label>
          <h6>其他设置</h6>
        </template>
        <el-form-item label="每次上传最多文件数">
          <MkSlider v-model="settingForm.file_count_limit" show-input :min="1" :max="1000" />
        </el-form-item>
        <el-form-item>
          <template #label>
            <div class="flex items-center gap-1">
              <span>上传的每个文档最大 (MB)</span>
              <MkTooltip content="建议根据服务器配置调整，否则可能会造成服务宕机" placement="right">
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </MkTooltip>
            </div>
          </template>
          <MkSlider v-model="settingForm.file_size_limit" show-input :min="1" :max="1000" />
        </el-form-item>
      </MkCollapse>
    </el-form>

    <!-- 保存知识库设置 -->
    <el-button class="mt-4" type="primary" :loading="saving" @click="handleSave">保存</el-button>
  </div>
</template>
