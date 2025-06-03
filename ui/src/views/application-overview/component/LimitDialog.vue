<template>
  <el-dialog
    :title="$t('views.applicationOverview.appInfo.accessControl')"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    width="650"
  >
    <el-form label-position="top" ref="limitFormRef" :model="form">
      <!-- <el-form-item
        :label="$t('views.applicationOverview.appInfo.LimitDialog.showSourceLabel')"
        @click.prevent
      >
        <el-switch size="small" v-model="form.show_source"></el-switch>
      </el-form-item> -->
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
      <!--     身份验证 -->
      <el-form-item
        :label="$t('views.applicationOverview.appInfo.LimitDialog.authentication')"
        v-hasPermission="new ComplexPermission([], ['x-pack'], 'OR')"
      >
        <el-switch size="small" v-model="form.authentication" @change="firstGeneration"></el-switch>
      </el-form-item>
      <el-form-item
        prop="authentication_value"
        v-if="form.authentication"
        :label="$t('views.applicationOverview.appInfo.LimitDialog.authenticationValue')"
        v-hasPermission="new ComplexPermission([], ['x-pack'], 'OR')"
      >
        <el-input
          class="authentication-append-input"
          v-model="form.authentication_value"
          readonly
          style="width: 268px"
          disabled
        >
          <template #append>
            <el-tooltip :content="$t('common.copy')" placement="top">
              <el-button
                type="primary"
                text
                @click="copyClick(form.authentication_value)"
                style="margin: 0 4px !important"
              >
                <AppIcon iconName="app-copy"></AppIcon>
              </el-button>
            </el-tooltip>
            <el-tooltip :content="$t('common.refresh')" placement="top">
              <el-button
                @click="refreshAuthentication"
                type="primary"
                text
                style="margin: 0 4px 0 0 !important"
              >
                <el-icon><RefreshRight /></el-icon>
              </el-button>
            </el-tooltip>
          </template>
        </el-input>
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
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import applicationApi from '@/api/application'
import { MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
import { copyClick } from '@/utils/clipboard'
import { ComplexPermission } from '@/utils/permission/type'

const route = useRoute()
const {
  params: { id }
} = route

const emit = defineEmits(['refresh'])

const limitFormRef = ref()
const form = ref<any>({
  access_num: 0,
  white_active: true,
  white_list: '',
  authentication_value: '',
  authentication: false
})

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      access_num: 0,
      white_active: true,
      white_list: ''
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
        authentication_value: form.value.authentication_value
      }
      applicationApi.putAccessToken(id as string, obj, loading).then((res) => {
        emit('refresh')
        // @ts-ignore
        MsgSuccess(t('common.settingSuccess'))
        dialogVisible.value = false
      })
    }
  })
}
function generateAuthenticationValue(length: number = 10) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  const randomValues = new Uint8Array(length)
  window.crypto.getRandomValues(randomValues)
  return Array.from(randomValues)
    .map((value) => chars[value % chars.length])
    .join('')
}
function refreshAuthentication() {
  form.value.authentication_value = generateAuthenticationValue()
}

function firstGeneration() {
  if (form.value.authentication && !form.value.authentication_value) {
    form.value.authentication_value = generateAuthenticationValue()
  }
}

defineExpose({ open })
</script>
<style lang="scss" scoped>
.authentication-append-input {
  .el-input-group__append {
    padding: 0 !important;
  }
}
</style>
