<template>
  <el-drawer v-model="dialogVisible" size="60%">
    <template #header>
      <h4>{{ $t('views.applicationOverview.appInfo.accessControl') }}</h4>
    </template>
    <el-form
      label-position="top"
      ref="limitFormRef"
      :model="form"
      require-asterisk-position="right"
    >
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
      <el-form-item :label="$t('views.applicationOverview.appInfo.LimitDialog.authentication')">
        <el-switch size="small" v-model="form.authentication" @change="firstGeneration"></el-switch>
      </el-form-item>
      <el-radio-group v-if="form.authentication" v-model="form.method" class="card__radio">
        <el-card shadow="never" class="mb-16" :class="form.method === 'replace' ? 'active' : ''">
          <el-radio value="replace" size="large">
            <p class="mb-4 lighter">
              {{ $t('views.applicationOverview.appInfo.LimitDialog.authenticationValue') }}
            </p>
          </el-radio>
          <el-form-item class="ml-24">
            <el-input
              class="authentication-append-input"
              v-model="form.authentication_value"
              readonly
              style="width: 268px"
            >
              <template #append>
                <el-tooltip :content="$t('common.copy')" placement="top">
                  <el-button
                    type="primary"
                    text
                    @click="copyClick(form.authentication_value)"
                    style="margin: 0 0 0 4px !important"
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
        </el-card>

        <el-card shadow="never" class="mb-16" :class="form.method === 'complete' ? 'active' : ''">
          <el-radio value="complete" size="large">
            <p class="mb-16 lighter">
              {{ $t('views.system.authentication.title') }}
              <el-button type="primary" link @click="router.push({ path: '' })">
                {{ '去配置对话用户' }}
              </el-button>
            </p>
          </el-radio>
          <el-form-item
            label="登录方式"
            :rules="[
              {
                required: true,
                message: $t('请选择登录方式'),
                trigger: 'change',
              },
            ]"
            prop="checkList"
            class="ml-24 border-t"
            style="padding-top: 16px"
          >
            <el-checkbox-group v-model="form.checkList">
              <el-checkbox label="账号登录" value="账号登录" />
              <el-checkbox label="LDAP" value="LDAP" />
              <el-checkbox label="OIDC" value="OIDC" />
              <el-checkbox label="CAS" value="CAS" />
              <el-checkbox label="企业微信" value="企业微信" />
              <el-checkbox label="钉钉" value="钉钉" />
              <el-checkbox label="飞书" value="飞书" />
            </el-checkbox-group>
          </el-form-item>
        </el-card>
      </el-radio-group>

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
      <div>
        <el-button @click.prevent="dialogVisible = false">{{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit(limitFormRef)" :loading="loading">
          {{ $t('common.create') }}
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import applicationApi from '@/api/application/application'
import { MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
import { copyClick } from '@/utils/clipboard'

const router = useRouter()
const route = useRoute()
const {
  params: { id },
} = route

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
  :deep(.el-input-group__append) {
    padding: 0 !important;
  }
}
</style>
