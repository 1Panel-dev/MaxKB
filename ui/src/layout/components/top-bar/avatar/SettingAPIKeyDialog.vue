<template>
  <el-dialog :title="$t('views.applicationOverview.appInfo.SettingAPIKeyDialog.dialogTitle')" v-model="dialogVisible">
    <el-form label-position="top" ref="settingFormRef" :model="form">
      <el-form-item :label="$t('views.applicationOverview.appInfo.SettingAPIKeyDialog.allowCrossDomainLabel')"
                    @click.prevent>
        <el-switch size="small" v-model="form.allow_cross_domain"></el-switch>
      </el-form-item>
      <el-form-item>
        <el-input
            v-model="form.cross_domain_list"
            :placeholder="$t('views.applicationOverview.appInfo.SettingAPIKeyDialog.crossDomainPlaceholder')"
            :rows="10"
            type="textarea"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button
            @click.prevent="dialogVisible = false">{{
            $t('views.applicationOverview.appInfo.SettingAPIKeyDialog.cancelButtonText')
          }}</el-button>
        <el-button type="primary" @click="submit(settingFormRef)" :loading="loading">
          {{ $t('views.applicationOverview.appInfo.SettingAPIKeyDialog.saveButtonText') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import {ref, watch} from 'vue'
import {useRoute} from 'vue-router'
import type {FormInstance} from 'element-plus'
import overviewApi from '@/api/system-api-key'
import {MsgSuccess} from '@/utils/message'
import {t} from '@/locales'

const route = useRoute()
const {
  params: {id}
} = route

const emit = defineEmits(['refresh'])

const settingFormRef = ref()
const form = ref<any>({
  allow_cross_domain: false,
  cross_domain_list: ''
})

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

const APIKeyId = ref('')

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      allow_cross_domain: false,
      cross_domain_list: ''
    }
  }
})

const open = (data: any) => {
  APIKeyId.value = data.id
  form.value.allow_cross_domain = data.allow_cross_domain
  form.value.cross_domain_list = data.cross_domain_list?.length
      ? data.cross_domain_list?.join('\n')
      : ''
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
            : []
      }
      overviewApi.putAPIKey(APIKeyId.value, obj, loading).then((res) => {
        emit('refresh')
        //@ts-ignore
        MsgSuccess(t('views.applicationOverview.appInfo.SettingAPIKeyDialog.successMessage'))
        dialogVisible.value = false
      })
    }
  })
}

defineExpose({open})
</script>
<style lang="scss" scope></style>
