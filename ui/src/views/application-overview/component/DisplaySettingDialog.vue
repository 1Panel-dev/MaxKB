<template>
  <el-dialog
    title="显示设置"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-form label-position="top" ref="displayFormRef" :model="form">
      <el-form-item>
        <el-space direction="vertical" alignment="start">
          <el-checkbox
            v-model="form.show_source"
            :label="isWorkFlow(detail.type) ? '显示执行详情' : '显示知识来源'"
          />
        </el-space>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"
          >{{ $t('views.applicationOverview.appInfo.LimitDialog.cancelButtonText') }}
        </el-button>
        <el-button type="primary" @click="submit(displayFormRef)" :loading="loading">
          {{ $t('views.applicationOverview.appInfo.LimitDialog.saveButtonText') }}
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
import { t } from '@/locales'

const route = useRoute()
const {
  params: { id }
} = route

const emit = defineEmits(['refresh'])


const displayFormRef = ref()
const form = ref<any>({
  show_source: false
})

const detail = ref<any>(null)

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      show_source: false
    }
  }
})

const open = (data: any, content: any) => {
  detail.value = content
  form.value.show_source = data.show_source

  dialogVisible.value = true
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      const obj = {
        show_source: form.value.show_source
      }
      applicationApi.putAccessToken(id as string, obj, loading).then((res) => {
        emit('refresh')
        // @ts-ignore
        MsgSuccess(t('views.applicationOverview.appInfo.LimitDialog.settingSuccessMessage'))
        dialogVisible.value = false
      })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scope></style>
