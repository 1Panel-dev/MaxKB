<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import ExternalRetrievalApi from '@/api/admin/workspace/knowledge/external-retrieval'
import type { KnowledgeExternalRetrievalPayload, KnowledgeExternalRetrievalSetting } from '@/api/types'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import { copyText } from '@/utils/clipboard'
import { MsgInfo, MsgSuccess, MsgWarning } from '@/utils/message'

defineOptions({ name: 'ExternalRetrievalView' })
defineProps<ResourceDetailPageProps>()
defineExpose({ customHeader: true })

const route = useRoute()
const knowledgeId = computed(() => String(route.params.knowledgeId ?? ''))

// 配置查询；未接入与加载失败均不回填虚假的开关或服务地址。
const setting = ref<KnowledgeExternalRetrievalSetting | null>(null)
const loading = ref(false)
const loadFailed = ref(false)

function loadExternalRetrieval() {
  if (loading.value) return
  loading.value = true
  loadFailed.value = false
  return ExternalRetrievalApi.getKnowledgeExternalRetrieval(knowledgeId.value)
    .then((result) => {
      setting.value = result
    })
    .catch(() => {
      loadFailed.value = true
    })
    .finally(() => {
      loading.value = false
    })
}

// 仅保存本次切换的字段，成功后按完整响应更新开关及配置示例。
function handleSettingChange(field: keyof KnowledgeExternalRetrievalPayload, value: string | number | boolean) {
  if (loading.value) return
  if (!setting.value) {
    if (loadFailed.value) MsgWarning('请先重新加载外部检索服务配置')
    else MsgInfo('当前范围的外部检索服务接口待接入')
    return
  }
  loading.value = true
  return ExternalRetrievalApi.putKnowledgeExternalRetrieval(knowledgeId.value, { [field]: value === true })
    .then((result) => {
      if (!result) {
        MsgInfo('当前范围的外部检索服务保存接口待接入')
        return
      }
      setting.value = result
      MsgSuccess('保存成功')
    })
    .finally(() => {
      loading.value = false
    })
}

const mcpConfig = computed(() => (setting.value ? JSON.stringify(setting.value.mcp_config, null, 2) : ''))

onMounted(() => {
  loadExternalRetrieval()
})
</script>

<template>
  <Teleport v-if="headerTarget" :to="headerTarget">
    <div class="flex-align-center gap-2">
      <h4>{{ title }}</h4>
      <MkTooltip content="第三方外部服务可通过 API / MCP 调用来检索当前知识库">
        <MkIcon name="icon_info_outlined" class="text-N600!" />
      </MkTooltip>
    </div>
  </Teleport>

  <div v-loading="loading" class="w-full max-w-200 space-y-4">
    <div>
      <div class="mb-2">
        <span>身份认证</span>
        <span class="text-N600">（开启后仅授权的对话用户可通过 API Key 检索该知识库）</span>
      </div>
      <!-- 切换身份认证 -->
      <el-switch :model-value="setting?.authentication ?? false" @change="handleSettingChange('authentication', $event)" />
    </div>

    <div>
      <div class="flex-between mb-2 gap-2">
        <span>API 服务地址</span>
        <!-- 切换外部检索服务 -->
        <el-switch :model-value="setting?.enabled ?? false" size="small" @change="handleSettingChange('enabled', $event)" />
      </div>
      <el-input :model-value="setting?.api_url ?? ''" readonly>
        <template #suffix>
          <!-- 复制 API 服务地址 -->
          <el-button text class="-mr-1" :disabled="!setting?.api_url" @click="copyText(setting?.api_url)">
            <MkIcon name="icon_copy_outlined" />
          </el-button>
        </template>
      </el-input>
    </div>

    <div>
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
    </div>

    <div>
      <div class="mb-2">MCP 配置详情</div>
      <div class="group relative">
        <el-input :model-value="mcpConfig" readonly :autosize="{ minRows: 8, maxRows: 24 }" type="textarea" />
        <!-- 复制 MCP 配置 -->
        <el-button class="group-hover-visible absolute right-3 top-3 z-10 shadow-md" circle :disabled="!mcpConfig" @click="copyText(mcpConfig)">
          <MkIcon name="icon_copy_outlined" />
        </el-button>
      </div>
    </div>
  </div>
</template>
