<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import ApiKeyApi from '@/api/admin/system/api-key'
import { ADMIN_API_BASE_PATH } from '@/api/constants'
import ApiKeyList from '@/components/business/api-key-list/index.vue'
import { copyText } from '@/utils/clipboard'

defineOptions({ name: 'ApiKeyDialog' })

const { t } = useI18n({ useScope: 'global' })

const visible = ref(false)
const apiDocUrl = new URL(`${ADMIN_API_BASE_PATH}-doc/`, window.location.origin).href

function open() {
  visible.value = true
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="API Key" width="1000">
    <div class="mk-gray-card-lg mb-4 space-y-2">
      <div>{{ t('common.labels.apiDoc') }}</div>
      <el-input :model-value="apiDocUrl" readonly>
        <template #suffix>
          <!-- 复制 API 文档地址 -->
          <el-button text @click="copyText(apiDocUrl, t('common.messages.copied'))" class="-mr-1">
            <MkIcon name="icon_copy_outlined" />
          </el-button>
        </template>
      </el-input>
    </div>
    <ApiKeyList :api="ApiKeyApi" />
  </MkDialog>
</template>
