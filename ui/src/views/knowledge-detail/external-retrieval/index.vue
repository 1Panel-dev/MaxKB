<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import type { KnowledgeExternalRetrievalPayload, KnowledgeExternalRetrievalSetting } from '@/api/types'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import { copyText } from '@/utils/clipboard'
import { MsgSuccess } from '@/utils/message'
import { isWorkspaceSharedResource } from '@/utils/resource-context'

defineOptions({ name: 'ExternalRetrievalView' })
defineProps<ResourceDetailPageProps>()
defineExpose({ customHeader: true })

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
  if (!setting.value || loading.value || saving.value || isWorkspaceSharedResource()) return
  saving.value = true
  try {
    const result = await resourceApi.externalRetrieval.putKnowledgeExternalRetrieval?.(knowledgeId.value, { [field]: value === true })
    if (!result) return
    setting.value = result
    MsgSuccess('保存成功')
  } catch {
    // 请求层统一提示错误，保留已保存的开关与示例，允许再次操作。
  } finally {
    saving.value = false
  }
}

const mcpConfig = computed(() => (setting.value ? JSON.stringify(setting.value.mcp_config, null, 2) : ''))

watch([knowledgeId, () => resourceApi.externalRetrieval], loadExternalRetrieval, { immediate: true })
</script>

<template>
  <Teleport v-if="headerTarget" :to="headerTarget">
    <div class="flex-align-center gap-2">
      <h4>{{ title }}</h4>
      <MkTooltip placement="right" content="第三方外部服务可通过 API / MCP 调用来检索当前知识库">
        <MkIcon name="icon_info_outlined" class="text-N600!" />
      </MkTooltip>
    </div>
  </Teleport>

  <div v-loading="loading || saving" :inert="loading || saving" class="min-h-40 w-full max-w-200">
    <MkEmpty v-if="loadFailed" description="外部检索服务加载失败">
      <!-- 重新加载外部检索服务配置 -->
      <el-button type="primary" @click="loadExternalRetrieval">重新加载</el-button>
    </MkEmpty>
    <div v-else-if="setting" class="space-y-4">
      <section>
        <div class="mb-2">
          <span>身份认证</span>
          <span class="text-N600">（开启后仅授权的对话用户可通过 API Key 检索该知识库）</span>
        </div>
        <!-- 切换身份认证 -->
        <el-switch
          :disabled="isWorkspaceSharedResource()"
          :model-value="setting.authentication"
          @change="handleSettingChange('authentication', $event)"
        />
      </section>
      <section>
        <div class="flex-between mb-2 gap-2">
          <span>API 服务地址</span>
          <!-- 切换外部检索服务 -->
          <el-switch
            :disabled="isWorkspaceSharedResource()"
            :model-value="setting.enabled"
            size="small"
            @change="handleSettingChange('enabled', $event)"
          />
        </div>
        <el-input :model-value="setting?.api_url ?? ''" readonly>
          <template #suffix>
            <!-- 复制 API 服务地址 -->
            <el-button text class="-mr-1" :disabled="!setting?.api_url" @click="copyText(setting?.api_url)">
              <MkIcon name="icon_copy_outlined" />
            </el-button>
          </template>
        </el-input>
      </section>

      <section>
        <div class="mb-2">API 调用示例</div>
        <div class="group relative">
          <el-input :model-value="setting?.api_example ?? ''" readonly :autosize="{ minRows: 8, maxRows: 24 }" type="textarea" />
          <!-- 复制 API 调用示例 -->
          <el-button
            class="group-hover-visible absolute right-3 top-3 z-10 shadow-md"
            circle
            :disabled="!setting?.api_example"
            @click="copyText(setting?.api_example)"
          >
            <MkIcon name="icon_copy_outlined" />
          </el-button>
        </div>
      </section>

      <section>
        <div class="mb-2">MCP 配置详情</div>
        <div class="group relative">
          <el-input :model-value="mcpConfig" readonly :autosize="{ minRows: 8, maxRows: 24 }" type="textarea" />
          <!-- 复制 MCP 配置 -->
          <el-button class="group-hover-visible absolute right-3 top-3 z-10 shadow-md" circle :disabled="!mcpConfig" @click="copyText(mcpConfig)">
            <MkIcon name="icon_copy_outlined" />
          </el-button>
        </div>
      </section>
    </div>
  </div>
</template>
