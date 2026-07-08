<template>
  <el-dialog
    :title="$t('common.setting')"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-form label-position="top" ref="settingFormRef" :model="form">
      <el-form-item
        :label="$t('views.applicationOverview.appInfo.SettingAPIKeyDialog.allowCrossDomainLabel')"
        @click.prevent
      >
        <el-switch size="small" v-model="form.allow_cross_domain"></el-switch>
      </el-form-item>
      <el-form-item>
        <el-input
          v-model="form.cross_domain_list"
          :placeholder="
            $t('views.applicationOverview.appInfo.SettingAPIKeyDialog.crossDomainPlaceholder')
          "
          :rows="10"
          type="textarea"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submit(settingFormRef)" :loading="loading">
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
import overviewSystemApi from '@/api/system/api-key'
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

const settingFormRef = ref()
const form = ref<any>({
  allow_cross_domain: false,
  cross_domain_list: '',
})

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

const APIKeyId = ref('')
const APIType = ref('APPLICATION')
const isCreate = ref(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      allow_cross_domain: false,
      cross_domain_list: '',
    }
  }
})

const open = (data: any, type: string) => {
  if (data) {
    isCreate.value = false
    APIKeyId.value = data.id
    form.value.allow_cross_domain = data.allow_cross_domain
    form.value.cross_domain_list = data.cross_domain_list?.length
      ? data.cross_domain_list?.join('\n')
      : ''
  } else {
    isCreate.value = true
  }
  APIType.value = type
  dialogVisible.value = true
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      const obj = {
        allow_cross_domain: form.value.allow_cross_domain,
        cross_domain_list: form.value.cross_domain_list
          ? form.value.cross_domain_list.split('\n').filter(function (item: string) {
              return item !== ''
            })
          : [],
      }

      const apiCall =
        APIType.value === 'APPLICATION'
          ? loadSharedApi({ type: 'applicationKey', systemType: apiType.value }).putAPIKey(
              id as string,
              APIKeyId.value,
              obj,
              loading,
            )
          : overviewSystemApi.putAPIKey(APIKeyId.value, obj, loading)

      apiCall.then(() => {
        emit('refresh')

        MsgSuccess(t('common.settingSuccess'))
        dialogVisible.value = false
      })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
