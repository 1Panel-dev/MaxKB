<template>
  <UserLoginLayout v-if="!loading" v-loading="loading">
    <LoginContainer :subTitle="theme.themeInfo?.slogan || $t('theme.defaultSlogan')">
      <h2 class="mb-24" v-if="!showQrCodeTab">
        {{ loginMode == 'LOCAL' ? $t('views.login.title') : loginMode }}</h2>
      <div v-if="!showQrCodeTab">
        <el-form
          class="login-form"
          :rules="rules"
          :model="loginForm"
          ref="loginFormRef"
          @keyup.enter="login"
        >
          <div class="mb-24">
            <el-form-item prop="username">
              <el-input
                size="large"
                class="input-item"
                v-model="loginForm.username"
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
          <div class="mb-24" v-if="loginMode !== 'LDAP'">
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
                  class="ml-8 cursor border border-r-4"
                  @click="makeCode"
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
        <div class="operate-container flex-between mt-12">
          <el-button
            :loading="loading"
            class="forgot-password"
            @click="router.push('/forgot_password')"
            link
            type="primary"
          >
            {{ $t('views.login.forgotPassword') }}?
          </el-button>
        </div>
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
                color: user.themeInfo?.theme,
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
            <img src="@/assets/scan/icon_qr_outlined.svg" width="25px"/>
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
    </LoginContainer>
  </UserLoginLayout>
</template>
<script setup lang="ts">
import {onMounted, ref, onBeforeMount} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import type {FormInstance, FormRules} from 'element-plus'
import type {LoginRequest} from '@/api/type/login'
import LoginContainer from '@/layout/login-layout/LoginContainer.vue'
import UserLoginLayout from '@/layout/login-layout/UserLoginLayout.vue'
import loginApi from '@/api/chat/chat.ts'
import {t, getBrowserLang} from '@/locales'
import useStore from '@/stores'
import {useI18n} from 'vue-i18n'
import QrCodeTab from '@/views/login/scanCompinents/QrCodeTab.vue'
import {MsgConfirm, MsgError} from '@/utils/message.ts'
import useUserStore from "@/stores/modules/user.ts";
// import * as dd from 'dingtalk-jsapi'
// import {loadScript} from '@/utils/utils'

const router = useRouter()
const {login, user, theme, chatUser} = useStore()
const {locale} = useI18n({useScope: 'global'})
const loading = ref<boolean>(false)
const route = useRoute()
const identifyCode = ref<string>('')
const {
  params: {accessToken}
} = route as any
const loginFormRef = ref<FormInstance>()
const loginForm = ref<LoginRequest>({
  username: '',
  password: '',
  captcha: '',
})

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
      required: true,
      message: t('views.login.loginForm.captcha.requiredMessage'),
      trigger: 'blur',
    },
  ],
})

const loginHandle = () => {
  loginFormRef.value?.validate().then(() => {
    if (loginMode.value === 'LDAP') {
      loginApi.ldapLogin(accessToken, loginForm.value,).then((ok) => {
        localStorage.setItem('token', ok?.data?.token)
        const user = useUserStore()
        return user.profile(loading)
      })
    } else {
      loginApi.login(accessToken, loginForm.value,).then((ok) => {
        localStorage.setItem('token', ok?.data?.token)
        const user = useUserStore()
        return user.profile(loading)
      })
    }
  })
}

function makeCode() {
  loginApi.getCaptcha().then((res: any) => {
    identifyCode.value = res.data.captcha
  })
}

onBeforeMount(() => {
  makeCode()
})

const modeList = ref<string[]>([])
//const QrList = ref<any[]>([''])
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
  if (authType === 'LDAP' || authType === '') {
    return
  }
  loginApi.getAuthSetting(authType, loading).then((res: any) => {
    if (!res.data || !res.data.config) {
      return;
    }

    const config = res.data.config;
    const redirectUrl = eval(`\`${config.redirectUrl}/${accessToken}\``);
    let url;
    if (authType === 'CAS') {
      url = config.ldpUri;
      url += url.indexOf('?') !== -1
        ? `&service=${encodeURIComponent(redirectUrl)}`
        : `?service=${encodeURIComponent(redirectUrl)}`;
    } else if (authType === 'OIDC') {
      const scope = config.scope || 'openid+profile+email';
      url = `${config.authEndpoint}?client_id=${config.clientId}&redirect_uri=${redirectUrl}&response_type=code&scope=${scope}`;
      if (config.state) {
        url += `&state=${config.state}`;
      }
    } else if (authType === 'OAuth2') {
      url = `${config.authEndpoint}?client_id=${config.clientId}&response_type=code&redirect_uri=${redirectUrl}&state=${uuidv4()}`;
      if (config.scope) {
        url += `&scope=${config.scope}`;
      }
    }
    if (!url) {
      return;
    }
    if (needMessage) {
      MsgConfirm(t('views.login.jump_tip'), '', {
        confirmButtonText: t('views.login.jump'),
        cancelButtonText: t('common.cancel'),
        confirmButtonClass: '',
      })
        .then(() => {
          window.location.href = url;
        })
        .catch(() => {
        });
    } else {
      console.log('url', url);
      window.location.href = url;
    }
  });
}

function changeMode(val: string) {
  loginMode.value = val === 'LDAP' ? val : 'LOCAL'
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

onBeforeMount(() => {
  if (chatUser.chat_profile?.login_value) {
    modeList.value = chatUser.chat_profile.login_value
    loginMode.value = modeList.value[0] || 'LOCAL'
    if (modeList.value.length == 1 && ['CAS', 'OIDC', 'OAuth2'].includes(modeList.value[0])) {
      redirectAuth(modeList.value[0])
    }
  }
  // user
  //   .getQrType()
  //   .then((res) => {
  //     if (res.length > 0) {
  //       modeList.value = ['QR_CODE', ...modeList.value]
  //       QrList.value = res
  //       QrList.value.forEach((item) => {
  //         orgOptions.value.push({
  //           key: item,
  //           value:
  //             item === 'wecom'
  //               ? t('views.system.authentication.scanTheQRCode.wecom')
  //               : item === 'dingtalk'
  //                 ? t('views.system.authentication.scanTheQRCode.dingtalk')
  //                 : t('views.system.authentication.scanTheQRCode.lark'),
  //         })
  //       })
  //     }
  //   })
  //   .finally(() => (loading.value = false))
})
//declare const window: any

// onMounted(() => {
//   makeCode()
//   const route = useRoute()
//   const currentUrl = ref(route.fullPath)
//   const params = new URLSearchParams(currentUrl.value.split('?')[1])
//   const client = params.get('client')
//
//   const handleDingTalk = () => {
//     const code = params.get('corpId')
//     if (code) {
//       dd.runtime.permission.requestAuthCode({corpId: code}).then((res) => {
//         console.log('DingTalk client request success:', res)
//         user.dingOauth2Callback(res.code).then(() => {
//           router.push({name: 'home'})
//         })
//       })
//     }
//   }
//
//   const handleLark = () => {
//     const appId = params.get('appId')
//     const callRequestAuthCode = () => {
//       window.tt?.requestAuthCode({
//         appId: appId,
//         success: (res: any) => {
//           user.larkCallback(res.code).then(() => {
//             router.push({name: 'home'})
//           })
//         },
//         fail: (error: any) => {
//           MsgError(error)
//         },
//       })
//     }
//
//     loadScript('https://lf-scm-cn.feishucdn.com/lark/op/h5-js-sdk-1.5.35.js', {
//       jsId: 'lark-sdk',
//       forceReload: true,
//     })
//       .then(() => {
//         if (window.tt) {
//           window.tt.requestAccess({
//             appID: appId,
//             scopeList: [],
//             success: (res: any) => {
//               user.larkCallback(res.code).then(() => {
//                 router.push({name: 'home'})
//               })
//             },
//             fail: (error: any) => {
//               const {errno} = error
//               if (errno === 103) {
//                 callRequestAuthCode()
//               }
//             },
//           })
//         } else {
//           callRequestAuthCode()
//         }
//       })
//       .catch((error) => {
//         console.error('SDK 加载失败:', error)
//       })
//   }
//
//   switch (client) {
//     case 'dingtalk':
//       handleDingTalk()
//       break
//     case 'lark':
//       handleLark()
//       break
//     default:
//       break
//   }
// })
</script>
<style lang="scss" scoped>
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
