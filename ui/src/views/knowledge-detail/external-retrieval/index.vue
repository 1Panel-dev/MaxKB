<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { KnowledgeExternalRetrievalPayload, KnowledgeExternalRetrievalSetting } from '@/api/types'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import { formatKnowledgeApiExample, formatKnowledgeMcpConfig } from '@/views/knowledge/external-retrieval-config'
import { copyText } from '@/utils/clipboard'
import { MsgSuccess } from '@/utils/message'
import { isSystemResource, isSystemSharedResource, isWorkspaceSharedResource } from '@/utils/resource-context'
import { perm } from '@/permission'
/**
 * 知识库「外部检索服务」权限判断
 */
type KnowledgeExternalServicePermissionMethod = 'knowledgeExternalServiceRead' | 'knowledgeExternalServiceEdit'

function knowledgeExternalServicePermission(method: KnowledgeExternalServicePermissionMethod): boolean {
  if (isSystemResource()) return Boolean(perm.knowledge.system[method]())
  if (isSystemSharedResource()) return Boolean(perm.knowledge.share[method]())
  if (isWorkspaceSharedResource()) return false // 共享知识库在工作空间侧只读
  return Boolean(perm.knowledge.workspace[method](knowledgeId.value))
}

defineOptions({ name: 'ExternalRetrievalView' })
defineProps<ResourceDetailPageProps>()
defineExpose({ customHeader: true })

const { t } = useI18n({ useScope: 'global' })
const { knowledgeId, resourceApi } = useKnowledgeDetailContext()

// 读取当前资源范围的真实配置，查询失败时展示重试入口。
const setting = ref<KnowledgeExternalRetrievalSetting | null>(null)
const loading = ref(false)
const saving = ref(false)
const loadFailed = ref(false)

async function loadExternalRetrieval() {
  loading.value = true
  setting.value = null
  loadFailed.value = false
  try {
    setting.value = await resourceApi.externalRetrieval.getKnowledgeExternalRetrieval(knowledgeId.value)
  } catch {
    loadFailed.value = true
  } finally {
    loading.value = false
  }
}

// 仅保存本次切换的字段，成功后按完整响应更新开关及配置示例。
async function handleSettingChange(field: keyof KnowledgeExternalRetrievalPayload, value: string | number | boolean) {
  if (!setting.value || loading.value || saving.value || !knowledgeExternalServicePermission('knowledgeExternalServiceEdit')) return
  saving.value = true
  try {
    const result = await resourceApi.externalRetrieval.putKnowledgeExternalRetrieval?.(knowledgeId.value, { [field]: value === true })
    if (!result) return
    setting.value = result
    MsgSuccess(t('common.messages.saveSuccess'))
  } catch {
    // 请求层统一提示错误，保留已保存的开关与示例，允许再次操作。
  } finally {
    saving.value = false
  }
}

const mcpConfig = computed(() => (setting.value ? formatKnowledgeMcpConfig(setting.value.mcp_config, window.location.origin) : ''))
const apiExample = computed(() => (setting.value ? formatKnowledgeApiExample(setting.value, window.location.origin) : ''))

watch([knowledgeId, () => resourceApi.externalRetrieval], loadExternalRetrieval, { immediate: true })
</script>

<template>
  <Teleport v-if="headerTarget" :to="headerTarget">
    <div class="flex-align-center gap-2">
      <h4>{{ title }}</h4>
      <MkTooltip placement="right" :content="t('knowledge.externalRetrieval.description')">
        <MkIcon name="icon_info_outlined" class="text-N600!" />
      </MkTooltip>
    </div>
  </Teleport>

  <div v-loading="loading || saving" :inert="loading || saving" class="min-h-40 w-full max-w-200">
    <MkEmpty v-if="loadFailed" :description="t('knowledge.externalRetrieval.loadFailed')">
      <!-- 重新加载外部检索服务配置 -->
      <el-button type="primary" @click="loadExternalRetrieval">{{ t('common.actions.reload') }}</el-button>
    </MkEmpty>
    <div v-else-if="setting" class="space-y-4">
      <!-- TODO 两个开关等调试 -->
      <section>
        <div class="mb-2">
          <span>{{ t('knowledge.externalRetrieval.apiService.label') }}</span>
          <span class="text-N600">（{{ t('knowledge.externalRetrieval.apiService.description') }}）</span>
        </div>
        <!-- 切换外部检索服务 -->
        <el-switch
          :disabled="!knowledgeExternalServicePermission('knowledgeExternalServiceEdit')"
          :model-value="setting.enabled"
          @change="handleSettingChange('enabled', $event)"
        />
      </section>
      <section v-if="setting.enabled">
        <div class="mb-2">
          <span>{{ t('knowledge.externalRetrieval.authentication.label') }}</span>
          <span class="text-N600">({{ t('knowledge.externalRetrieval.authentication.description') }})</span>
        </div>
        <!-- 切换对话用户授权 -->
        <el-switch
          :disabled="!knowledgeExternalServicePermission('knowledgeExternalServiceEdit')"
          :model-value="setting.authentication"
          @change="handleSettingChange('authentication', $event)"
        />
      </section>
      <section>
        <div class="mb-2">{{ t('knowledge.externalRetrieval.apiExample') }}</div>
        <div class="group relative">
          <el-input :model-value="apiExample" readonly :autosize="{ minRows: 8, maxRows: 24 }" type="textarea" />
          <!-- 复制 API 调用示例 -->
          <el-button
            class="group-hover-visible absolute right-3 top-3 z-10 shadow-md"
            circle
            :disabled="!apiExample"
            @click="copyText(apiExample, t('common.messages.copied'))"
          >
            <MkIcon name="icon_copy_outlined" />
          </el-button>
        </div>
      </section>

      <section>
        <div class="mb-2">{{ t('resource.mcpConfig.title') }}</div>
        <div class="group relative">
          <el-input :model-value="mcpConfig" readonly :autosize="{ minRows: 8, maxRows: 24 }" type="textarea" />
          <!-- 复制 MCP 配置 -->
          <el-button
            class="group-hover-visible absolute right-3 top-3 z-10 shadow-md"
            circle
            :disabled="!mcpConfig"
            @click="copyText(mcpConfig, t('common.messages.copied'))"
          >
            <MkIcon name="icon_copy_outlined" />
          </el-button>
        </div>
      </section>
    </div>
  </div>
</template>
