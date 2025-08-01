<template>
  <el-dialog
    :title="$t('views.applicationOverview.appInfo.accessControl')"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    width="650"
  >
    <el-form label-position="top" ref="limitFormRef" :model="form">
      <el-form-item
        :label="$t('views.applicationOverview.appInfo.LimitDialog.clientQueryLimitLabel')"
      >
        <el-input-number
          v-model="form.access_num"
          :min="0"
          :step="1"
          :max="10000"
          :value-on-clear="0"
          controls-position="right"
          style="width: 268px"
          step-strictly
        />
        <span class="ml-4">{{
          $t('views.applicationOverview.appInfo.LimitDialog.timesDays')
        }}</span>
      </el-form-item>

      <el-form-item
        :label="$t('views.applicationOverview.appInfo.LimitDialog.whitelistLabel')"
        @click.prevent
      >
        <el-switch size="small" v-model="form.white_active"></el-switch>
      </el-form-item>
      <el-form-item>
        <el-input
          v-model="form.white_list"
          :placeholder="$t('views.applicationOverview.appInfo.LimitDialog.whitelistPlaceholder')"
          :rows="10"
          type="textarea"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false">{{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit(limitFormRef)" :loading="loading">
          {{ $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
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

const limitFormRef = ref()
const form = ref<any>({
  access_num: 0,
  white_active: true,
  white_list: '',
  authentication_value: '',
  authentication: false,
})

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      access_num: 0,
      white_active: true,
      white_list: '',
    }
  }
})

const open = (data: any) => {
  form.value.access_num = data.access_num
  form.value.white_active = data.white_active
  form.value.white_list = data.white_list?.length ? data.white_list?.join('\n') : ''
  form.value.authentication_value = data.authentication_value
  form.value.authentication = data.authentication
  dialogVisible.value = true
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      const obj = {
        white_list: form.value.white_list ? form.value.white_list.split('\n') : [],
        white_active: form.value.white_active,
        access_num: form.value.access_num,
        authentication: form.value.authentication,
        authentication_value: form.value.authentication_value,
      }
      loadSharedApi({ type: 'application', systemType: apiType.value })
        .putAccessToken(id as string, obj, loading)
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
