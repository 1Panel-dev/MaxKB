<template>
  <login-layout v-if="user.isEnterprise() ? user.themeInfo : true" v-loading="loading">
    <LoginContainer :subTitle="user.themeInfo?.slogan || '欢迎使用 MaxKB 智能知识库问答系统'">
      <h2 class="mb-24">{{ loginMode || '普通登录' }}</h2>
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
                placeholder="请输入用户名"
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
                placeholder="请输入密码"
                show-password
            >
            </el-input>
          </el-form-item>
        </div>
      </el-form>
      <el-button size="large" type="primary" class="w-full" @click="login">登录</el-button>
      <div class="operate-container flex-between mt-12">
        <!-- <el-button class="register" @click="router.push('/register')" link type="primary">
          注册
        </el-button> -->
        <el-button
            class="forgot-password"
            @click="router.push('/forgot_password')"
            link
            type="primary"
        >
          忘记密码?
        </el-button>
      </div>

      <div class="login-gradient-divider lighter mt-24" v-if="modeList.length > 1">
        <span>更多登录方式</span>
      </div>
      <div class="text-center mt-16">
        <template v-for="item in modeList">
          <el-button
              v-if="item !== '' && loginMode !== item"
              circle
              :key="item"
              class="login-button-circle color-secondary"
              @click="changeMode(item)"
          >{{ item }}
          </el-button>
          <el-button
              v-if="item === '' && loginMode !== ''"
              circle
              :key="item"
              class="login-button-circle color-secondary"
              style="font-size: 24px"
              icon="UserFilled"
              @click="changeMode('')"
          />
        </template>
      </div>
    </LoginContainer>
  </login-layout>
</template>
<script setup lang="ts">
import {onMounted, ref, onBeforeMount} from 'vue'
import type {LoginRequest} from '@/api/type/user'
import {useRouter} from 'vue-router'
import type {FormInstance, FormRules} from 'element-plus'
import useStore from '@/stores'
import authApi from "@/api/auth-setting";
import {MsgConfirm, MsgSuccess} from "@/utils/message";
import {t} from "@/locales";
import systemKeyApi from "@/api/system-api-key";

const loading = ref<boolean>(false)
const {user} = useStore()
const router = useRouter()
const loginForm = ref<LoginRequest>({
  username: '',
  password: ''
})

const rules = ref<FormRules<LoginRequest>>({
  username: [
    {
      required: true,
      message: '请输入用户名',
      trigger: 'blur'
    }
  ],
  password: [
    {
      required: true,
      message: '请输入密码',
      trigger: 'blur'
    }
  ]
})
const loginFormRef = ref<FormInstance>()

const modeList = ref<string[]>([''])
const loginMode = ref('')

function redirectAuth(authType: string) {
  if (authType === 'LDAP' || authType === '') {
    return;
  }
  authApi.getAuthSetting(authType, loading).then((res: any) => {
    if (!res.data) {
      return;
    }
    MsgConfirm(
        `${t('login.jump_tip')}`,
        t(''),
        {
          confirmButtonText: t('login.jump'),
          cancelButtonText: t('views.applicationOverview.appInfo.APIKeyDialog.cancel'),
          confirmButtonClass: ''
        }
    )
        .then(() => {
          if (!res.data.config_data) {
            return;
          }
          const config = res.data.config_data
          const redirectUrl = eval(`\`${config.redirectUrl}\``);
          let url;
          if (authType === 'CAS') {
            url = `${config.ldpUri}?service=${encodeURIComponent(redirectUrl)}`;
          }
          if (authType === 'OIDC') {
            url = `${config.authEndpoint}?client_id=${config.clientId}&redirect_uri=${redirectUrl}&response_type=code&scope=openid+profile+email`;
          }
          if (url) {
            window.location.href = url;
          }
        })
        .catch(() => {
        })
  });
}


function changeMode(val: string) {
  loginMode.value = val === 'LDAP' ? val : '';
  loginForm.value = {
    username: '',
    password: ''
  }
  redirectAuth(val)
  loginFormRef.value?.clearValidate()
}

const login = () => {
  loginFormRef.value?.validate().then(() => {
    loading.value = true
    user
        .login(loginMode.value, loginForm.value.username, loginForm.value.password)
        .then(() => {
          router.push({name: 'home'})
        })
        .finally(() => (loading.value = false))
  })
}

onMounted(() => {
  user.asyncGetProfile().then((res) => {
    if (user.isEnterprise()) {
      loading.value = true
      user
          .getAuthType()
          .then((res) => {
            modeList.value = [...modeList.value, ...res]
          })
          .finally(() => (loading.value = false))
    }
  })
})
onBeforeMount(() => {
  if (user.isEnterprise()) {
    user.theme(loading)
  }
})
</script>
<style lang="scss" scope>
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
  padding: 25px !important;
}
</style>
