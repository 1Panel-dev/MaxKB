<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type SystemResourceApiKeyApi from '@/api/admin/system/resource-management/application/api-key'
import type ApplicationApiKeyApi from '@/api/admin/workspace/application/api-key'
import { CHAT_API_BASE_PATH } from '@/api/constants'
import ApiKeyList from '@/components/business/api-key-list/index.vue'
import { copyText } from '@/utils/clipboard'

defineOptions({ name: 'ApiKeyDialog' })

const { t } = useI18n({ useScope: 'global' })

const visible = ref(false)
const props = defineProps<{ api: typeof ApplicationApiKeyApi | typeof SystemResourceApiKeyApi; applicationId: string }>()
const baseUrl = computed(() => new URL(`${CHAT_API_BASE_PATH}/${props.applicationId}`, window.location.origin).href)

function open() {
  visible.value = true
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="API Key" width="1000">
    <div class="mk-gray-card-lg mb-4 space-y-2">
      <div>Base URL</div>
      <el-input :model-value="baseUrl" readonly>
        <template #suffix>
          <!-- 复制 Base URL -->
          <MkTooltip :content="t('common.actions.copy')" placement="top">
            <el-button text @click="copyText(baseUrl, t('common.messages.copied'))" class="-mr-1">
              <MkIcon name="icon_copy_outlined" />
            </el-button>
          </MkTooltip>
        </template>
      </el-input>
    </div>
    <ApiKeyList :api="props.api" :application-id="props.applicationId" />
  </MkDialog>
</template>
