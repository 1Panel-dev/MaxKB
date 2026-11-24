<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ApplicationDisplaySetting } from '@/api/types'
import { useApplicationDetailContext } from '../../context'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'DisplaySettingDialog' })

const { t } = useI18n({ useScope: 'global' })

const { applicationId, resourceApi } = useApplicationDetailContext()
// 社区版仅编辑语言、知识来源与执行详情。
type DisplaySettingForm = Pick<ApplicationDisplaySetting, 'show_source' | 'show_exec'>

// 打开时查询本次配置，关闭动画结束后统一清理草稿。
const visible = ref(false)
const loading = ref(false)
const displayForm = ref<DisplaySettingForm>({
  show_source: false,
  show_exec: false,
})

function open() {
  visible.value = true
  return loadSetting()
}

function loadSetting() {
  if (loading.value) return
  loading.value = true
  return resourceApi.application
    .getAccessToken(applicationId.value)
    .then((config) => {
      displayForm.value = {
        show_source: config.show_source ?? false,
        show_exec: config.show_exec ?? false,
      }
    })
    .finally(() => {
      loading.value = false
    })
}

function handleClosed() {
  displayForm.value = {
    show_source: false,
    show_exec: false,
  }
}

// 保存成功关闭，失败保留输入；重复提交由入口保护。
function handleSave() {
  loading.value = true
  return resourceApi.application
    .putAccessToken(applicationId.value, displayForm.value)
    .then(() => {
      MsgSuccess(t('common.messages.settingsSuccess'))
      visible.value = false
    })
    .finally(() => {
      loading.value = false
    })
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" :title="t('application.overview.display.title')" @closed="handleClosed">
    <div v-loading="loading">
      <el-form :model="displayForm" label-position="top" require-asterisk-position="right" @submit.prevent>
        <div class="flex-column gap-3">
          <el-checkbox v-model="displayForm.show_source">{{ t('application.overview.display.showSource') }}</el-checkbox>
          <el-checkbox v-model="displayForm.show_exec">{{ t('application.overview.display.showExecution') }}</el-checkbox>
        </div>
      </el-form>
    </div>
    <template #footer>
      <!-- 取消展示设置 -->
      <el-button plain :disabled="loading" @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 保存社区版展示设置 -->
      <el-button type="primary" :loading="loading" @click="handleSave">{{ t('common.actions.save') }}</el-button>
    </template>
  </MkDialog>
</template>
