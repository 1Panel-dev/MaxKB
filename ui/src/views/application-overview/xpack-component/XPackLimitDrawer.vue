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
          :max="10000000"
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
        @click.prevent
      >
        <el-switch size="small" v-model="form.authentication" @change="firstGeneration"></el-switch>
      </el-form-item>
      <el-radio-group
        v-if="form.authentication"
        v-model="form.authentication_value.type"
        class="card__radio"
      >
        <el-card
          shadow="never"
          class="mb-16"
          :class="form.authentication_value?.type === 'password' ? 'active' : ''"
        >
          <el-radio value="password" size="large">
            <p class="mb-4 lighter">
              {{ $t('views.applicationOverview.appInfo.LimitDialog.authenticationValue') }}
            </p>
          </el-radio>
          <el-form-item class="ml-24" v-if="form.authentication_value.type === 'password'">
            <el-input
              class="authentication-append-input"
              v-model="form.authentication_value.password_value"
              readonly
              style="width: 268px"
            >
              <template #append>
                <el-tooltip :content="$t('common.copy')" placement="top">
                  <el-button
                    type="primary"
                    text
                    @click="copyClick(form.authentication_value.password_value)"
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
                    <el-icon>
                      <RefreshRight/>
                    </el-icon>
                  </el-button>
                </el-tooltip>
              </template>
            </el-input>
          </el-form-item>
        </el-card>
        <el-card
          shadow="never"
          class="mb-16"
          :class="form.authentication_value.type === 'login' ? 'active' : ''"
        >
          <el-radio value="login" size="large">
            <p class="mb-16 lighter">
              {{ $t('views.system.authentication.title') }}
              <el-button type="primary" link @click="router.push({ name: 'applicationChatUser' })">
                {{ $t('views.applicationOverview.appInfo.LimitDialog.toSettingChatUser') }}
              </el-button>
            </p>
          </el-radio>
          <el-form-item
            v-if="form.authentication_value.type === 'login'"
            :label="$t('views.applicationOverview.appInfo.LimitDialog.loginMethod')"
            :rules="[
              {
                required: true,
                message: $t('views.applicationOverview.appInfo.LimitDialog.loginMethodRequired'),
                trigger: 'change',
              },
            ]"
            prop="authentication_value.login_value"
            class="ml-24 border-t"
            style="padding-top: 16px"
          >
            <el-checkbox-group v-model="form.authentication_value.login_value">
              <template v-for="t in auth_list" :key="t.value">
                <el-checkbox :label="t.label" :value="t.value"/>
              </template>
            </el-checkbox-group>
          </el-form-item>
          <el-form-item
            class="ml-24"
            v-if="
              form.authentication_value.type === 'login' &&
              form.authentication_value?.login_value?.includes('LOCAL')
            "
            :label="$t('views.system.display_code')"
            :rules="[
              {
                required: true,
                message: $t('views.applicationOverview.appInfo.LimitDialog.displayCodeRequired'),
                trigger: 'change',
              },
            ]"
            prop="authentication_value.max_attempts"
          >
            <span style="font-size: 13px">
              {{ $t('views.system.loginFailed') }}
            </span>
            <el-input-number
              style="margin-left: 8px"
              v-model="form.authentication_value.max_attempts"
              :min="-1"
              :max="10"
              :step="1"
              controls-position="right"
            />
            <span style="margin-left: 8px; font-size: 13px">
              {{ $t('views.system.loginFailedMessage') }}
            </span>
            <span style="margin-left: 8px; color: #909399; font-size: 12px">
              ({{ $t('views.system.display_codeTip') }})
            </span>
          </el-form-item>
        </el-card>
      </el-radio-group>

      <el-form-item
        :label="$t('views.applicationOverview.appInfo.LimitDialog.whitelistLabel')"
        @click.prevent
      >
        <el-switch size="small" v-model="form.white_active"></el-switch>
      </el-form-item>
      <el-form-item v-if="form.white_active">
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
        <el-button @click.prevent="dialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submit(limitFormRef)" :loading="loading">
          {{ $t('common.save') }}
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>
<script setup lang="ts">
import {ref, watch, computed} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import type {FormInstance, FormRules} from 'element-plus'
import {MsgSuccess} from '@/utils/message'
import {t} from '@/locales'
import {copyClick} from '@/utils/clipboard'
import {loadSharedApi} from '@/utils/dynamics-api/shared-api'

const router = useRouter()
const route = useRoute()
const {
  params: {id},
} = route

const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const emit = defineEmits(['refresh'])
const auth_list = ref<Array<{ label: string; value: string }>>([])
const limitFormRef = ref()
const form = ref<any>({
  access_num: 0,
  white_active: true,
  white_list: '',
  authentication_value: {
    type: 'password',
    max_attempts: 1,
  },
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
  form.value.authentication_value = data.authentication_value || {
    type: 'password',
  }
  if (
    form.value.authentication_value.type === 'password' &&
    !form.value.authentication_value.password_value
  ) {
    refreshAuthentication()
  }
  if (!form.value.authentication_value.max_attempts) {
    form.value.authentication_value.max_attempts = 1
  }
  form.value.authentication = data.authentication
  dialogVisible.value = true
  loadSharedApi({type: 'application', systemType: apiType.value})
    .getChatUserAuthType()
    .then((ok: any) => {
      auth_list.value = ok.data
    })
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
      loadSharedApi({type: 'application', systemType: apiType.value})
        .putAccessToken(id as string, obj, loading)
        .then(() => {
          emit('refresh')
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
  form.value.authentication_value.password_value = generateAuthenticationValue()
}

function firstGeneration() {
  if (form.value.authentication && !form.value.authentication_value.password_value) {
    form.value.authentication_value = {
      type: 'password',
      password_value: generateAuthenticationValue(),
    }
    if (!form.value.authentication_value.max_attempts) {
      form.value.authentication_value.max_attempts = 1
    }
  }
}

defineExpose({open})
</script>
<style lang="scss" scoped>
.authentication-append-input {
  :deep(.el-input-group__append) {
    padding: 0 !important;
  }
}
</style>
