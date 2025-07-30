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
        <el-space direction="vertical" alignment="start" :size="2">
          <el-checkbox
            v-model="form.show_source"
            :label="$t('views.applicationOverview.appInfo.SettingDisplayDialog.showSourceLabel')"
          />

          <el-checkbox
            v-model="form.show_exec"
            :label="
              $t('views.applicationOverview.appInfo.SettingDisplayDialog.showExecutionDetail')
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
import { ref, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import type { FormInstance } from 'element-plus'
import { MsgSuccess, MsgError } from '@/utils/message'
import { langList, t } from '@/locales'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'

const route = useRoute()
const {
  params: { id },
} = route
const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const emit = defineEmits(['refresh'])

const displayFormRef = ref()
const form = ref<any>({
  show_source: false,
  show_exec: false,
  language: '',
})

const detail = ref<any>(null)

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      show_source: false,
      show_exec: false,
      language: '',
    }
  }
})
const open = (data: any, content: any) => {
  detail.value = content
  form.value.show_source = data.show_source
  form.value.show_exec = data.show_exec
  form.value.language = data.language
  dialogVisible.value = true
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      loadSharedApi({ type: 'application', systemType: apiType.value })
        .putAccessToken(id as string, form.value, loading)
        .then(() => {
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
