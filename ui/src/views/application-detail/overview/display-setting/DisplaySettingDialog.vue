<script setup lang="ts">
import { ref } from 'vue'
import type { ApplicationDisplaySetting } from '@/api/types'
import { MsgSuccess } from '@/utils/message'
import { useApplicationDetailContext } from '../../context'

defineOptions({ name: 'DisplaySettingDialog' })

const { applicationId, resourceApi } = useApplicationDetailContext()
// 社区版仅编辑语言、知识来源与执行详情。
type DisplaySettingForm = Pick<ApplicationDisplaySetting, 'language' | 'show_source' | 'show_exec'>

const languageOptions = [
  { value: 'zh-CN', label: '简体中文' },
  { value: 'zh-Hant', label: '繁體中文' },
  { value: 'en-US', label: 'English' },
]

// 打开时查询本次配置，关闭动画结束后统一清理草稿。
const visible = ref(false)
const loading = ref(false)
const displayForm = ref<DisplaySettingForm>({
  show_source: false,
  show_exec: false,
  language: '',
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
        language: config.language ?? '',
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
    language: '',
  }
}

// 保存成功关闭，失败保留输入；重复提交由入口保护。
function handleSave() {
  loading.value = true
  return resourceApi.application
    .putAccessToken(applicationId.value, displayForm.value)
    .then(() => {
      MsgSuccess('设置成功')
      visible.value = false
    })
    .finally(() => {
      loading.value = false
    })
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="显示设置" @closed="handleClosed">
    <div v-loading="loading">
      <el-form :model="displayForm" label-position="top" require-asterisk-position="right" @submit.prevent>
        <el-form-item label="语言">
          <el-select v-model="displayForm.language" clearable placeholder="请选择">
            <el-option v-for="language in languageOptions" :key="language.value" :label="language.label" :value="language.value" />
          </el-select>
        </el-form-item>
        <div class="flex-column gap-3">
          <el-checkbox v-model="displayForm.show_source">显示知识来源</el-checkbox>
          <el-checkbox v-model="displayForm.show_exec">显示执行详情</el-checkbox>
        </div>
      </el-form>
    </div>
    <template #footer>
      <!-- 取消展示设置 -->
      <el-button plain :disabled="loading" @click="visible = false">取消</el-button>
      <!-- 保存社区版展示设置 -->
      <el-button type="primary" :loading="loading" @click="handleSave">保存</el-button>
    </template>
  </MkDialog>
</template>
