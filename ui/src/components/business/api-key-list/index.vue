<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type SystemApiKeyApi from '@/api/admin/system/api-key'
import type SystemResourceApiKeyApi from '@/api/admin/system/resource-management/application/api-key'
import type ApplicationApiKeyApi from '@/api/admin/workspace/application/api-key'
import type { ApiKeyRecord } from '@/api/types'
import ButtonCreateApiKey from './create-api-key/index.vue'
import ButtonEditApiKey from './edit-api-key/index.vue'
import { getApiKeyExpiration } from './expiration'
import { copyText } from '@/utils/clipboard'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { datetimeFormat } from '@/utils/time'

defineOptions({ name: 'ApiKeyList' })
const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{
  api: typeof ApplicationApiKeyApi | typeof SystemResourceApiKeyApi | typeof SystemApiKeyApi
  applicationId?: string
}>()
const loading = ref(false)
const apiKeys = ref<ApiKeyRecord[]>([])
const pagination = ref({ currentPage: 1, pageSize: 20, total: 0 })
const apiKeyRows = computed(() => apiKeys.value.map((record) => ({ ...record, expiration: getApiKeyExpiration(record) })))

function fetchApiKeys() {
  const request =
    props.applicationId !== undefined
      ? (props.api as typeof ApplicationApiKeyApi | typeof SystemResourceApiKeyApi).getApiKeyPage(props.applicationId, pagination.value)
      : (props.api as typeof SystemApiKeyApi).getApiKeyPage(pagination.value)
  return request.then((page) => {
    apiKeys.value = page.records
    pagination.value.total = page.total
  })
}

function loadApiKeys() {
  if (loading.value) return
  loading.value = true
  return fetchApiKeys().finally(() => {
    loading.value = false
  })
}

function handleCreated() {
  pagination.value.currentPage = 1
  return fetchApiKeys()
}

function handleChangeActive(record: ApiKeyRecord) {
  if (loading.value) return false
  loading.value = true
  const payload = { is_active: !record.is_active }
  const request =
    props.applicationId !== undefined
      ? (props.api as typeof ApplicationApiKeyApi | typeof SystemResourceApiKeyApi).putApiKey(props.applicationId, record.id, payload)
      : (props.api as typeof SystemApiKeyApi).putApiKey(record.id, payload)
  return request
    .then(() => {
      MsgSuccess(payload.is_active ? t('common.status.enabled') : t('common.status.disabled'))
      return fetchApiKeys().then(() => true)
    })
    .finally(() => {
      loading.value = false
    })
}

function handleDelete(record: ApiKeyRecord) {
  if (loading.value) return
  return MsgConfirm(t('apiKey.delete.title', { name: `******${record.secret_key.slice(-4)}` }), t('apiKey.delete.description')).then(
    () => {
      if (loading.value) return
      loading.value = true
      const request =
        props.applicationId !== undefined
          ? (props.api as typeof ApplicationApiKeyApi | typeof SystemResourceApiKeyApi).deleteApiKey(props.applicationId, record.id)
          : (props.api as typeof SystemApiKeyApi).deleteApiKey(record.id)
      return request
        .then(() => {
          MsgSuccess(t('common.messages.deleteSuccess'))
          const total = Math.max(0, pagination.value.total - 1)
          pagination.value.currentPage = Math.min(pagination.value.currentPage, Math.max(1, Math.ceil(total / pagination.value.pageSize)))
          return fetchApiKeys()
        })
        .finally(() => {
          loading.value = false
        })
    },
    () => undefined,
  )
}

onMounted(loadApiKeys)
</script>

<template>
  <div v-loading="loading" :inert="loading">
    <!-- 创建 API Key  -->
    <div class="mb-4">
      <ButtonCreateApiKey :api="props.api" :application-id="props.applicationId" v-model:loading="loading" :refresh="handleCreated" />
    </div>

    <MkTable
      v-model:pagination-config="pagination"
      :data="apiKeyRows"
      :max-table-height="425"
      @current-change="loadApiKeys"
      @size-change="loadApiKeys"
    >
      <el-table-column label="API Key" width="140">
        <template #default="{ row }">
          <div class="flex-align-center gap-2">
            <span>
              {{ `******${row.secret_key.slice(-4)}` }}
            </span>
            <!-- 复制完整 API Key -->
            <el-button text @click="copyText(row.secret_key, t('common.messages.copied'))">
              <MkIcon name="icon_copy_outlined" />
            </el-button>
          </div>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.status.activeLabel')" width="130">
        <template #default="{ row }">
          <MkStatusLabel :active="row.is_active" />
        </template>
      </el-table-column>
      <el-table-column :label="t('apiKey.cors.label')" width="130">
        <template #default="{ row }">
          <el-tag :type="row.allow_cross_domain ? 'primary' : 'info'" size="small">
            {{ row.allow_cross_domain ? t('apiKey.cors.opened') : t('apiKey.cors.closed') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('apiKey.expiration.label')" width="265">
        <template #default="{ row }">
          <span :class="{ 'text-danger': row.expiration.status === 'expired', 'text-warning': row.expiration.status === 'soon' }">
            {{ row.expiration.label }}
          </span>
          <span v-if="!row.is_permanent && row.expiration.label !== '—'">
            {{ row.expiration.label ? `（${datetimeFormat(row.expire_time)}）` : datetimeFormat(row.expire_time) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.labels.remark')" width="180" show-overflow-tooltip>
        <template #default="{ row }">{{ row.remark || '—' }}</template>
      </el-table-column>
      <el-table-column prop="create_time" :label="t('common.labels.createTime')" width="180">
        <template #default="{ row }">{{ datetimeFormat(row.create_time) || '—' }}</template>
      </el-table-column>
      <el-table-column :label="t('common.labels.operation')" width="140" fixed="right">
        <template #default="{ row }">
          <div class="flex-align-center gap-3">
            <!-- 启用或禁用 API Key -->
            <el-switch :model-value="row.is_active" size="small" :before-change="() => handleChangeActive(row)" />
            <el-divider direction="vertical" />
            <!-- 编辑API Key -->
            <ButtonEditApiKey :api="props.api" :application-id="props.applicationId" :record="row" @refresh="loadApiKeys" />
            <!-- 删除 API Key -->
            <MkTooltip :content="t('common.actions.delete')" placement="top">
              <el-button class="ml-0!" type="primary" text @click.stop="handleDelete(row)">
                <MkIcon name="icon_delete-trash_outlined" />
              </el-button>
            </MkTooltip>
          </div>
        </template>
      </el-table-column>
    </MkTable>
  </div>
</template>
