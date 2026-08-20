<script setup lang="ts">
import { ref, type Component } from 'vue'
import { LOGIN_METHOD } from '@/api/enums'
import LDAP from './components/LDAP.vue'
import CAS from './components/CAS.vue'
import OIDC from './components/OIDC.vue'
import SCAN from './components/SCANLogin.vue'
import OAuth2 from './components/OAuth2.vue'
import Saml2 from './components/Saml2.vue'
import LoginSetting from './components/LoginSetting.vue'

interface AuthenticationTab {
  component: Component
  label: string
  name: string
}

const activeName = ref('LoginSetting')
const authenticationTabs: AuthenticationTab[] = [
  { label: '登录设置', name: 'LoginSetting', component: LoginSetting },
  { label: 'LDAP', name: LOGIN_METHOD.LDAP, component: LDAP },
  { label: 'CAS', name: LOGIN_METHOD.CAS, component: CAS },
  { label: 'OIDC', name: LOGIN_METHOD.OIDC, component: OIDC },
  { label: 'OAuth2', name: LOGIN_METHOD.OAUTH2, component: OAuth2 },
  { label: 'SAML2', name: LOGIN_METHOD.SAML2, component: Saml2 },
  { label: '扫码登录', name: 'SCAN', component: SCAN },
]
</script>

<template>
  <MkViewLayout class="system-settings-authentication">
    <el-tabs v-model="activeName" class="authentication-tabs min-h-0 flex-1 flex-col">
      <template v-for="authenticationTab in authenticationTabs" :key="authenticationTab.name">
        <el-tab-pane
          class="h-full"
          :label="authenticationTab.label"
          :name="authenticationTab.name"
          lazy
        >
          <el-scrollbar>
            <div class="py-4">
              <component :is="authenticationTab.component" />
            </div>
          </el-scrollbar>
        </el-tab-pane>
      </template>
    </el-tabs>
  </MkViewLayout>
</template>

<style scoped lang="scss"></style>
