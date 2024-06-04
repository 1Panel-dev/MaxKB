<template>
  <el-dialog title="API Key" v-model="dialogVisible" width="800">
    <el-button type="primary" class="mb-16" @click="createApiKey">
      {{ $t('views.applicationOverview.appInfo.APIKeyDialog.creatApiKey') }}
    </el-button>
    <el-table :data="apiKey" class="mb-16" :loading="loading">
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
      <el-table-column
        :label="$t('views.applicationOverview.appInfo.APIKeyDialog.status')"
        width="60"
      >
        <template #default="{ row }">
          <div @click.stop>
            <el-switch size="small" v-model="row.is_active" @change="changeState($event, row)" />
          </div>
        </template>
      </el-table-column>
      <el-table-column
        prop="name"
        :label="$t('views.applicationOverview.appInfo.APIKeyDialog.creationDate')"
        width="170"
      >
        <template #default="{ row }">
          {{ datetimeFormat(row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column
        :label="$t('views.applicationOverview.appInfo.APIKeyDialog.operations')"
        align="left"
        width="80"
      >
        <template #default="{ row }">
          <span class="mr-4">
            <el-tooltip
              effect="dark"
              :content="$t('views.applicationOverview.appInfo.APIKeyDialog.settings')"
              placement="top"
            >
              <el-button type="primary" text @click.stop="settingApiKey(row)">
                <el-icon><Setting /></el-icon>
              </el-button>
            </el-tooltip>
          </span>
          <el-tooltip
            effect="dark"
            :content="$t('views.applicationOverview.appInfo.APIKeyDialog.delete')"
            placement="top"
          >
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
  SettingAPIKeyDialogRef.value.open(row)
}

function deleteApiKey(row: any) {
  MsgConfirm(
    // @ts-ignore
    `${t('views.applicationOverview.appInfo.APIKeyDialog.msgConfirm1')}: ${row.secret_key}?`,
    t('views.applicationOverview.appInfo.APIKeyDialog.msgConfirm2'),
    {
      confirmButtonText: t('views.applicationOverview.appInfo.APIKeyDialog.confirmDelete'),
      cancelButtonText: t('views.applicationOverview.appInfo.APIKeyDialog.cancel'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      overviewApi.delAPIKey(id as string, row.id, loading).then(() => {
        MsgSuccess(t('views.applicationOverview.appInfo.APIKeyDialog.deleteSuccess'))
        getApiKeyList()
      })
    })
    .catch(() => {})
}

function changeState(bool: Boolean, row: any) {
  const obj = {
    is_active: bool
  }
  const str = bool
    ? t('views.applicationOverview.appInfo.APIKeyDialog.enabledSuccess')
    : t('views.applicationOverview.appInfo.APIKeyDialog.disabledSuccess')
  overviewApi.putAPIKey(id as string, row.id, obj, loading).then((res) => {
    MsgSuccess(str)
    getApiKeyList()
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
<style lang="scss" scope></style>
