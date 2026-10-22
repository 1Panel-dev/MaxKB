<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from 'vue'
import type { ApiKeyRecord } from '@/api/types'
import type ApplicationApiKeyApi from '@/api/admin/workspace/application/api-key'
import type SystemResourceApiKeyApi from '@/api/admin/system/resource-management/application/api-key'
import type SystemApiKeyApi from '@/api/admin/system/api-key'
import EditApiKeyDrawer from './EditApiKeyDrawer.vue'
import { getApiKeyExpiration } from './expiration'
import { copyText } from '@/utils/clipboard'
import { datetimeFormat } from '@/utils/time'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'ApiKeyList' })

const props = defineProps<{
  api: typeof ApplicationApiKeyApi | typeof SystemResourceApiKeyApi | typeof SystemApiKeyApi
  applicationId?: string
}>()
const loading = ref(false)
const apiKeys = ref<ApiKeyRecord[]>([])
const createdApiKey = ref('')
const createdDialogVisible = ref(false)
const pagination = ref({ currentPage: 1, pageSize: 20, total: 0 })
const editDrawerRef = useTemplateRef<InstanceType<typeof EditApiKeyDrawer>>('editDrawerRef')
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

function handleCreate() {
  if (loading.value) return
  loading.value = true
  const request =
    props.applicationId !== undefined
      ? (props.api as typeof ApplicationApiKeyApi | typeof SystemResourceApiKeyApi).postApiKey(props.applicationId)
      : (props.api as typeof SystemApiKeyApi).postApiKey()
  return request
    .then((record) => {
      createdApiKey.value = record.secret_key
      createdDialogVisible.value = true
      pagination.value.currentPage = 1
      return fetchApiKeys()
    })
    .finally(() => {
      loading.value = false
    })
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
      MsgSuccess(payload.is_active ? '已启用' : '已禁用')
      return fetchApiKeys().then(() => true)
    })
    .finally(() => {
      loading.value = false
    })
}

function handleDelete(record: ApiKeyRecord) {
  if (loading.value) return
  return MsgConfirm('是否删除该 API Key？', '删除后，使用该 API Key 的服务将无法访问，请谨慎操作！').then(
    () => {
      if (loading.value) return
      loading.value = true
      const request =
        props.applicationId !== undefined
          ? (props.api as typeof ApplicationApiKeyApi | typeof SystemResourceApiKeyApi).deleteApiKey(props.applicationId, record.id)
          : (props.api as typeof SystemApiKeyApi).deleteApiKey(record.id)
      return request
        .then(() => {
          MsgSuccess('删除成功')
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

function handleOpenEdit(record: ApiKeyRecord) {
  editDrawerRef.value?.open(record)
}

onMounted(loadApiKeys)
</script>

<template>
  <div v-loading="loading" :inert="loading">
    <!-- 创建 API Key -->
    <el-button type="primary" class="mb-4" @click="handleCreate">
      <MkIcon name="icon_add_outlined" />
      <span>创建</span>
    </el-button>
    <MkTable
      v-model:pagination-config="pagination"
      :data="apiKeyRows"
      :max-table-height="480"
      @current-change="loadApiKeys"
      @size-change="loadApiKeys"
    >
      <el-table-column label="API Key" min-width="160">
        <template #default="{ row }">
          <div class="flex-align-center gap-2">
            <span>
              {{ `******${row.secret_key.slice(-4)}` }}
            </span>
            <!-- 复制完整 API Key -->
            <el-button text @click="copyText(row.secret_key)">
              <MkIcon name="icon_copy_outlined" />
            </el-button>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="启用状态" width="120">
        <template #default="{ row }">
          <MkStatusLabel :active="row.is_active" />
        </template>
      </el-table-column>
      <el-table-column label="跨域设置" width="110">
        <template #default="{ row }">
          <el-tag :type="row.allow_cross_domain ? 'primary' : 'info'" size="small">
            {{ row.allow_cross_domain ? '已开启' : '未开启' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="到期时间" min-width="265">
        <template #default="{ row }">
          <span :class="{ 'text-danger': row.expiration.status === 'expired', 'text-warning': row.expiration.status === 'soon' }">
            {{ row.expiration.label }}
          </span>
          <span v-if="!row.is_permanent && row.expiration.label !== '—'">
            {{ row.expiration.label ? `（${datetimeFormat(row.expire_time)}）` : datetimeFormat(row.expire_time) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="备注" min-width="120" show-overflow-tooltip>
        <template #default="{ row }">{{ row.remark || '—' }}</template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" min-width="180">
        <template #default="{ row }">{{ datetimeFormat(row.create_time) || '—' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <div class="flex-align-center gap-3">
            <!-- 启用或禁用 API Key -->
            <el-switch :model-value="row.is_active" size="small" :before-change="() => handleChangeActive(row)" />
            <el-divider direction="vertical" />
            <!-- 编辑 API Key -->
            <MkTooltip content="编辑" placement="top">
              <el-button type="primary" text @click.stop="handleOpenEdit(row)">
                <MkIcon name="icon_edit_outlined" />
              </el-button>
            </MkTooltip>
            <!-- 删除 API Key -->
            <MkTooltip content="删除" placement="top">
              <el-button class="ml-0!" type="primary" text @click.stop="handleDelete(row)">
                <MkIcon name="icon_delete-trash_outlined" />
              </el-button>
            </MkTooltip>
          </div>
        </template>
      </el-table-column>
    </MkTable>
  </div>
  <MkDialog v-model="createdDialogVisible" title="API Key" align-center @closed="createdApiKey = ''">
    <template #subtitle>请安全保存此密钥，不要泄露。</template>
    <el-input :model-value="createdApiKey" readonly>
      <template #suffix>
        <!-- 复制新建的完整 API Key -->
        <el-button text @click="copyText(createdApiKey)" class="-mr-1">
          <MkIcon name="icon_copy_outlined" />
        </el-button>
      </template>
    </el-input>
    <template #footer>
      <!-- 关闭创建结果弹窗 -->
      <el-button plain @click="createdDialogVisible = false">知道了</el-button>
    </template>
  </MkDialog>
  <EditApiKeyDrawer v-bind="props" ref="editDrawerRef" @refresh="loadApiKeys" />
</template>
