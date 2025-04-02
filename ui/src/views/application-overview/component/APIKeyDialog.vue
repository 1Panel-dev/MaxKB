<template>
  <el-dialog
    title="API Key"
    v-model="dialogVisible"
    width="800"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    align-center
  >
    <el-button type="primary" class="mb-16" @click="createApiKey">
      {{ $t('common.create') }}
    </el-button>
    <el-table :data="apiKey" class="mb-16" :loading="loading" height="420">
      <el-table-column prop="secret_key" label="API Key">
        <template #default="{ row }">
          <span class="vertical-middle lighter break-all">
            {{ row.secret_key }}
          </span>
          <el-button type="primary" text @click="copyClick(row.secret_key)">
            <AppIcon iconName="app-copy"></AppIcon>
          </el-button>
        </template>
      </el-table-column>
      <el-table-column :label="$t('common.status.label')" width="70">
        <template #default="{ row }">
          <div @click.stop>
            <el-switch
              size="small"
              v-model="row.is_active"
              :before-change="() => changeState(row)"
            />
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="name" :label="$t('common.createDate')" width="170">
        <template #default="{ row }">
          {{ datetimeFormat(row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column :label="$t('common.operation')" align="left" width="90">
        <template #default="{ row }">
          <span class="mr-4">
            <el-tooltip effect="dark" :content="$t('common.setting')" placement="top">
              <el-button type="primary" text @click.stop="settingApiKey(row)">
                <el-icon><Setting /></el-icon>
              </el-button>
            </el-tooltip>
          </span>
          <el-tooltip effect="dark" :content="$t('common.delete')" placement="top">
            <el-button type="primary" text @click="deleteApiKey(row)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>
    <SettingAPIKeyDialog ref="SettingAPIKeyDialogRef" @refresh="refresh" />
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { copyClick } from '@/utils/clipboard'
import overviewApi from '@/api/application-overview'
import SettingAPIKeyDialog from './SettingAPIKeyDialog.vue'
import { datetimeFormat } from '@/utils/time'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { t } from '@/locales'
const route = useRoute()
const {
  params: { id }
} = route

const emit = defineEmits(['addData'])

const SettingAPIKeyDialogRef = ref()
const dialogVisible = ref<boolean>(false)
const loading = ref(false)
const apiKey = ref<any>(null)

watch(dialogVisible, (bool) => {
  if (!bool) {
    apiKey.value = null
  }
})

function settingApiKey(row: any) {
  SettingAPIKeyDialogRef.value.open(row, 'APPLICATION')
}

function deleteApiKey(row: any) {
  MsgConfirm(
    // @ts-ignore
    `${t('views.applicationOverview.appInfo.APIKeyDialog.msgConfirm1')}: ${row.secret_key}?`,
    t('views.applicationOverview.appInfo.APIKeyDialog.msgConfirm2'),
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      overviewApi.delAPIKey(id as string, row.id, loading).then(() => {
        MsgSuccess(t('common.deleteSuccess'))
        getApiKeyList()
      })
    })
    .catch(() => {})
}

function changeState(row: any) {
  const obj = {
    is_active: !row.is_active
  }
  const str = obj.is_active
    ? t('views.applicationOverview.appInfo.APIKeyDialog.enabledSuccess')
    : t('views.applicationOverview.appInfo.APIKeyDialog.disabledSuccess')
  overviewApi
    .putAPIKey(id as string, row.id, obj, loading)
    .then((res) => {
      MsgSuccess(str)
      getApiKeyList()
      return true
    })
    .catch(() => {
      return false
    })
}

function createApiKey() {
  overviewApi.postAPIKey(id as string, loading).then((res) => {
    getApiKeyList()
  })
}

const open = () => {
  getApiKeyList()
  dialogVisible.value = true
}

function getApiKeyList() {
  overviewApi.getAPIKey(id as string, loading).then((res) => {
    apiKey.value = res.data
  })
}

function refresh() {
  getApiKeyList()
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
