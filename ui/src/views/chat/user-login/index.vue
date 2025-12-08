<template>
  <UserLoginLayout v-if="!loading" v-loading="loading">
    <div class="user-login-container p-24">
      <div v-if="isPc" class="flex-center" style="margin-bottom: 32px">
        <el-avatar
          v-if="isAppIcon(chatUser.chat_profile?.icon)"
          shape="square"
          :size="32"
          class="mr-8"
          style="background: none"
        >
          <img :src="chatUser.chat_profile?.icon" alt=""/>
        </el-avatar>
        <LogoIcon v-else height="32px" class="mr-8"/>
        <h1>{{ chatUser.chat_profile?.application_name }}</h1>
      </div>
      <!-- 移动端头部标题-->
      <div v-else class="user-login__header">
        <div class="flex-between">
          <div class="flex align-center">
            <div class="mr-12 ml-16 flex">
              <el-avatar
                v-if="isAppIcon(chatUser.chat_profile?.icon)"
                shape="square"
                :size="32"
                style="background: none"
              >
                <img :src="chatUser.chat_profile?.icon" alt=""/>
              </el-avatar>
              <LogoIcon v-else height="32px"/>
            </div>

            <h4
              class="ellipsis"
              style="max-width: 270px"
              :title="chatUser.chat_profile?.application_name"
            >
              {{ chatUser.chat_profile?.application_name }}
            </h4>
          </div>
        </div>
      </div>

      <el-card class="login-card" v-if="chatUser.chat_profile?.authentication_type == 'password'">
        <h2 class="mb-24">
          {{ $t('views.applicationOverview.appInfo.LimitDialog.authenticationValue') }}
        </h2>
        <PasswordAuth></PasswordAuth>
      </el-card>

      <el-card class="login-card" v-else style="--el-card-padding: 0">
        <h2 class="mb-24" v-if="!showQrCodeTab && (loginMode === 'LDAP' || loginMode === 'LOCAL')">
          {{ loginMode == 'LOCAL' ? $t('views.login.title') : loginMode }}
        </h2>
        <div v-if="!showQrCodeTab && (loginMode === 'LDAP' || loginMode === 'LOCAL')">
          <el-form
            class="login-form"
            :rules="rules"
            :model="loginForm"
            ref="loginFormRef"
            @keyup.enter="loginHandle"
          >
            <div class="mb-24">
              <el-form-item prop="username">
                <el-input
                  size="large"
                  class="input-item"
                  v-model="loginForm.username"
                  @blur="handleUsernameBlur(loginForm.username)"
                  :placeholder="$t('views.login.loginForm.username.placeholder')"
                >
                </el-input>
              </el-form-item>
            </div>
            <div class="mb-24">
              <el-form-item prop="password">
                <el-input
                  type="password"
                  size="large"
                  class="input-item"
                  v-model="loginForm.password"
                  :placeholder="$t('views.login.loginForm.password.placeholder')"
                  show-password
                >
                </el-input>
              </el-form-item>
            </div>
            <div class="mb-24" v-if="loginMode !== 'LDAP'&& identifyCode">
              <el-form-item prop="captcha">
                <div class="flex-between w-full">
                  <el-input
                    size="large"
                    class="input-item"
                    v-model="loginForm.captcha"
                    :placeholder="$t('views.login.loginForm.captcha.placeholder')"
                  >
                  </el-input>

                  <img
                    :src="identifyCode"
                    alt=""
                    height="38"
                    class="ml-8 cursor border border-r-6"
                    @click="makeCode(loginForm.username)"
                  />
                </div>
              </el-form-item>
            </div>
          </el-form>

          <el-button
            size="large"
            type="primary"
            class="w-full"
            @click="loginHandle"
            :loading="loading"
          >
            {{ $t('views.login.buttons.login') }}
          </el-button>
        </div>
        <div v-if="showQrCodeTab">
          <QrCodeTab :tabs="orgOptions"/>
        </div>
        <div class="login-gradient-divider lighter mt-24" v-if="modeList.length > 1">
          <span>{{ $t('views.login.moreMethod') }}</span>
        </div>
        <div class="text-center mt-16">
          <template v-for="item in modeList">
            <el-button
              v-if="item !== 'LOCAL' && loginMode !== item && item !== 'QR_CODE'"
              circle
              :key="item"
              class="login-button-circle color-secondary"
              @click="changeMode(item)"
            >
              <span
                :style="{
                  'font-size': item === 'OAUTH2' ? '8px' : '10px',
                  color: theme.themeInfo?.theme,
                }"
              >{{ item }}</span
              >
            </el-button>
            <el-button
              v-if="item === 'QR_CODE' && loginMode !== item"
              circle
              :key="item"
              class="login-button-circle color-secondary"
              @click="changeMode('QR_CODE')"
            >
              <img src="@/assets/icon_qr_outlined.svg" width="25px"/>
            </el-button>
            <el-button
              v-if="item === 'LOCAL' && loginMode != 'LOCAL'"
              circle
              :key="item"
              class="login-button-circle color-secondary"
              style="font-size: 24px"
              icon="UserFilled"
              @click="changeMode('LOCAL')"
            />
          </template>
        </div>
      </el-card>
    </div>
  </UserLoginLayout>
</template>
<script setup lang="ts">
import {onMounted, ref, onBeforeMount, computed} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import type {FormInstance, FormRules} from 'element-plus'
import type {LoginRequest} from '@/api/type/login'
import UserLoginLayout from '@/layout/login-layout/UserLoginLayout.vue'
import loginApi from '@/api/chat/chat.ts'
import {t} from '@/locales'
import useResize from '@/layout/hooks/useResize'
import useStore from '@/stores'
import {useI18n} from 'vue-i18n'
import QrCodeTab from '@/views/chat/user-login/scanCompinents/QrCodeTab.vue'
import {MsgConfirm, MsgError} from '@/utils/message.ts'
import PasswordAuth from '@/views/chat/auth/component/password.vue'
import {isAppIcon, loadScript} from '@/utils/common'
import forge from "node-forge";
import * as dd from "dingtalk-jsapi";

useResize()
const router = useRouter()

const {theme, chatUser, common} = useStore()
const {locale} = useI18n({useScope: 'global'})
const loading = ref<boolean>(false)
const route = useRoute()
const identifyCode = ref<string>('')
const {
  params: {accessToken},
  query: {mode},
} = route as any

const isPc = computed(() => {
  console.log(common.isMobile())
  let modeName = ''
  if (!mode || mode === 'pc') {
    modeName = common.isMobile() ? 'mobile' : 'pc'
  } else {
    modeName = mode
  }
  console.log(modeName)
  return modeName === 'pc'
})

const loginFormRef = ref<FormInstance>()
const loginForm = ref<LoginRequest>({
  username: '',
  password: '',
  captcha: '',
})

const max_attempts = ref<number>(1)  // 声明为 ref
const rules = ref<FormRules<LoginRequest>>({
  username: [
    {
      required: true,
      message: t('views.login.loginForm.username.requiredMessage'),
      trigger: 'blur',
    },
  ],
  password: [
    {
      required: true,
      message: t('views.login.loginForm.password.requiredMessage'),
      trigger: 'blur',
    },
  ],
  captcha: [
    {
      required: false,
      message: t('views.login.loginForm.captcha.requiredMessage'),
      trigger: 'blur',
    },
  ],
})

const loginHandle = () => {
  loginFormRef.value?.validate().then(() => {
    if (loginMode.value === 'LDAP') {
      chatUser.ldapLogin(loginForm.value).then((ok) => {
        router.push({
          name: 'chat',
          params: {accessToken: chatUser.accessToken},
          query: route.query,
        })
      })
    } else {
      const publicKey = forge.pki.publicKeyFromPem(chatUser?.chat_profile?.rasKey as any);
      const jsonData = JSON.stringify(loginForm.value);
      const utf8Bytes = forge.util.encodeUtf8(jsonData);
      const encrypted = publicKey.encrypt(utf8Bytes, 'RSAES-PKCS1-V1_5');
      const encryptedBase64 = forge.util.encode64(encrypted);
      chatUser.login({
        encryptedData: encryptedBase64,
        username: loginForm.value.username
      }).then((ok) => {
        router.push({
          name: 'chat',
          params: {accessToken: chatUser.accessToken},
          query: route.query,
        })
      }).catch(() => {
        makeCode(loginForm.value.username)
      })
    }
  })
}

function makeCode(username?: string) {
  loginApi.getCaptcha(username, accessToken).then((res: any) => {
    identifyCode.value = res.data.captcha
  })
}

onBeforeMount(() => {
  locale.value = chatUser.getLanguage()
})

const modeList = ref<string[]>([])
const QrList = ref<any[]>([''])
const loginMode = ref('')
const showQrCodeTab = ref(false)

interface qrOption {
  key: string
  value: string
}

const orgOptions = ref<qrOption[]>([])

function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

function redirectAuth(authType: string, needMessage: boolean = false) {
  if (authType === 'LDAP' || authType === '' || authType === 'password') {
    return
  }
  loginApi.getAuthSetting(authType, loading).then((res: any) => {
    if (!res.data || !res.data.config) {
      return
    }

    const config = res.data.config
    const queryParams = new URLSearchParams(route.query as any).toString()
    // 构造带查询参数的redirectUrl
    let redirectUrl = `${config.redirectUrl}/${accessToken}`
    if (queryParams) {
      redirectUrl += `?${queryParams}`
    }
    let url
    if (authType === 'CAS') {
      url = config.ldpUri
      url +=
        url.indexOf('?') !== -1
          ? `&service=${encodeURIComponent(redirectUrl)}`
          : `?service=${encodeURIComponent(redirectUrl)}`
    } else if (authType === 'OIDC') {
      const scope = config.scope || 'openid+profile+email'
      url = `${config.authEndpoint}?client_id=${config.clientId}&redirect_uri=${redirectUrl}&response_type=code&scope=${scope}`
      if (config.state) {
        url += `&state=${config.state}`
      }
    } else if (authType === 'OAuth2') {
      url = `${config.authEndpoint}?client_id=${config.clientId}&response_type=code&redirect_uri=${redirectUrl}&state=${uuidv4()}`
      if (config.scope) {
        url += `&scope=${config.scope}`
      }
    }
    if (!url) {
      return
    }
    if (needMessage) {
      MsgConfirm(t('views.login.jump_tip'), '', {
        confirmButtonText: t('views.login.jump'),
        cancelButtonText: t('common.cancel'),
        confirmButtonClass: '',
      })
        .then(() => {
          window.location.href = url
        })
        .catch(() => {
        })
    } else {
      console.log('url', url)
      window.location.href = url
    }
  })
}

function changeMode(val: string) {
  loginMode.value = val === 'LDAP' ? val : 'LOCAL'
  if (val !== 'LOCAL') {
    loginMode.value = val
  }
  if (val === 'QR_CODE') {
    loginMode.value = val
    showQrCodeTab.value = true
    return
  }
  showQrCodeTab.value = false
  loginForm.value = {
    username: '',
    password: '',
    captcha: '',
  }
  redirectAuth(val)
  loginFormRef.value?.clearValidate()
}

function handleUsernameBlur(username: string) {
  makeCode(username)
}

onBeforeMount(() => {
  if (chatUser.chat_profile?.max_attempts) {
    max_attempts.value = chatUser.chat_profile.max_attempts
  }
  if (chatUser.chat_profile?.login_value) {
    modeList.value = chatUser.chat_profile.login_value
    if (modeList.value.includes('LOCAL')) {
      modeList.value = ['LOCAL', ...modeList.value.filter((item) => item !== 'LOCAL')]
    } else if (modeList.value.includes('LDAP')) {
      modeList.value = ['LDAP', ...modeList.value.filter((item) => item !== 'LDAP')]
    }
    loginMode.value = modeList.value[0] || 'LOCAL'
    if (!modeList.value.includes('LOCAL') && !modeList.value.includes('LDAP')) {
      loginMode.value = ''
    }
    if (modeList.value.length == 1 && ['CAS', 'OIDC', 'OAuth2'].includes(modeList.value[0])) {
      redirectAuth(modeList.value[0])
    }
    // 这里的modeList 是oauth2 cas ldap oidc 这四个 还会有 lark wecom dingtalk
    // 获取到的 modeList中除'CAS', 'OIDC', 'OAuth2' LOCAL之外的登录方式
    QrList.value = modeList.value.filter(
      (item) => !['CAS', 'OIDC', 'OAuth2', 'LOCAL', 'LDAP'].includes(item),
    )
    // modeList需要去掉lark wecom dingtalk
    modeList.value = modeList.value.filter((item) => !['lark', 'wecom', 'dingtalk'].includes(item))
    if (QrList.value.length > 0) {
      QrList.value.forEach((item) => {
        orgOptions.value.push({
          key: item,
          value:
            item === 'wecom'
              ? t('views.system.authentication.scanTheQRCode.wecom')
              : item === 'dingtalk'
                ? t('views.system.authentication.scanTheQRCode.dingtalk')
                : t('views.system.authentication.scanTheQRCode.lark'),
        })
      })
      if (!modeList.value.includes('LOCAL') && !modeList.value.includes('LDAP')) {
        showQrCodeTab.value = true
      }
      modeList.value = ['QR_CODE', ...modeList.value]
    }
  }
})
declare const window: any
onBeforeMount(() => {
  const route = useRoute()
  const currentUrl = ref(route.fullPath)
  const params = new URLSearchParams(currentUrl.value.split('?')[1])
  const client = params.get('client')

  const handleDingTalk = () => {
    const code = params.get('corpId')
    if (code) {
      dd.runtime.permission.requestAuthCode({corpId: code}).then((res) => {
        console.log('DingTalk client request success:', res)
        chatUser.dingOauth2Callback(res.code, accessToken).then(() => {
          router.push({
            name: 'chat',
            params: {accessToken: accessToken},
            query: route.query,
          })
        })
      })
    }
  }

  const handleLark = () => {
    const appId = params.get('appId')
    const callRequestAuthCode = () => {
      window.tt?.requestAuthCode({
        appId: appId,
        success: (res: any) => {
          chatUser.larkCallback(res.code, accessToken).then(() => {
            router.push({
              name: 'chat',
              params: {accessToken: accessToken},
              query: route.query,
            })
          })
        },
        fail: (error: any) => {
          MsgError(error)
        },
      })
    }

    loadScript('https://lf-scm-cn.feishucdn.com/lark/op/h5-js-sdk-1.5.44.js', {
      jsId: 'lark-sdk',
      forceReload: true,
    })
      .then(() => {
        if (window.tt) {
          window.tt?.requestAccess({
            appID: appId,
            scopeList: [],
            success: (res: any) => {
              chatUser.larkCallback(res.code, accessToken).then(() => {
                router.push({
                  name: 'chat',
                  params: {accessToken: accessToken},
                  query: route.query,
                })
              })
            },
            fail: (error: any) => {
              const {errno} = error
              if (errno === 103) {
                callRequestAuthCode()
              }
            },
          })
        } else {
          callRequestAuthCode()
        }
      })
      .catch((error) => {
        console.error('SDK 加载失败:', error)
      })
  }

  switch (client) {
    case 'dingtalk':
      handleDingTalk()
      break
    case 'lark':
      handleLark()
      break
    default:
      break
  }
})
</script>
<style lang="scss" scoped>
.user-login {
  &__header {
    background: var(--app-header-bg-color);
    position: fixed;
    width: 100%;
    left: 0;
    top: 0;
    z-index: 100;
    height: var(--app-header-height);
    line-height: var(--app-header-height);
    box-sizing: border-box;
    border-bottom: 1px solid var(--el-border-color);
  }
}

.user-login-container {
  width: 480px;

  .login-card {
    padding: 18px;
  }
}

.login-gradient-divider {
  position: relative;
  text-align: center;
  color: var(--el-color-info);

  ::before {
    content: '';
    width: 25%;
    height: 1px;
    background: linear-gradient(90deg, rgba(222, 224, 227, 0) 0%, #dee0e3 100%);
    position: absolute;
    left: 16px;
    top: 50%;
  }

  ::after {
    content: '';
    width: 25%;
    height: 1px;
    background: linear-gradient(90deg, #dee0e3 0%, rgba(222, 224, 227, 0) 100%);
    position: absolute;
    right: 16px;
    top: 50%;
  }
}

.login-button-circle {
  padding: 20px !important;
  margin: 0 4px;
  width: 32px;
  height: 32px;
  text-align: center;
}
</style>
