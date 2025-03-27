<template>
  <el-dialog
    :title="$t('views.applicationOverview.appInfo.SettingDisplayDialog.dialogTitle')"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    width="550"
  >
    <el-form label-position="top" ref="displayFormRef" :model="form">
      <el-form-item>
        <span>{{
          $t('views.applicationOverview.appInfo.SettingDisplayDialog.languageLabel')
        }}</span>
        <el-select v-model="form.language" clearable>
          <el-option
            v-for="item in langList"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-space direction="vertical" alignment="start">
          <el-checkbox
            v-model="form.show_source"
            :label="
              isWorkFlow(detail.type)
                ? $t('views.applicationOverview.appInfo.SettingDisplayDialog.showExecutionDetail')
                : $t('views.applicationOverview.appInfo.SettingDisplayDialog.showSourceLabel')
            "
          />
        </el-space>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false">{{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit(displayFormRef)" :loading="loading">
          {{ $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import type { FormInstance, FormRules, UploadFiles } from 'element-plus'
import applicationApi from '@/api/application'
import { isWorkFlow } from '@/utils/application'
import { MsgSuccess, MsgError } from '@/utils/message'
import { getBrowserLang, langList, t } from '@/locales'
const route = useRoute()
const {
  params: { id }
} = route

const emit = defineEmits(['refresh'])

const displayFormRef = ref()
const form = ref<any>({
  show_source: false,
  language: ''
})

const detail = ref<any>(null)

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      show_source: false,
      language: ''
    }
  }
})
const open = (data: any, content: any) => {
  detail.value = content
  form.value.show_source = data.show_source
  form.value.language = data.language
  dialogVisible.value = true
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      applicationApi.putAccessToken(id as string, form.value, loading).then((res) => {
        emit('refresh')
        // @ts-ignore
        MsgSuccess(t('common.settingSuccess'))
        dialogVisible.value = false
      })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
