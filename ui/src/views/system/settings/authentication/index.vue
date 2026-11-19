<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Component } from 'vue'
import { LOGIN_METHOD } from '@/api/enums'
import CAS from './components/CAS.vue'
import LDAP from './components/LDAP.vue'
import LoginSetting from './components/LoginSetting.vue'
import OAuth2 from './components/OAuth2.vue'
import OIDC from './components/OIDC.vue'
import SCAN from './components/SCANLogin.vue'
import Saml2 from './components/Saml2.vue'

interface AuthenticationTab {
  component: Component
  label: string
  name: string
}

const { t } = useI18n({ useScope: 'global' })
const activeName = ref('LoginSetting')
const authenticationTabs = computed<AuthenticationTab[]>(() => [
  { label: t('auth.loginSettings.title'), name: 'LoginSetting', component: LoginSetting },
  { label: 'LDAP', name: LOGIN_METHOD.LDAP, component: LDAP },
  { label: 'CAS', name: LOGIN_METHOD.CAS, component: CAS },
  { label: 'OIDC', name: LOGIN_METHOD.OIDC, component: OIDC },
  { label: 'OAuth2', name: LOGIN_METHOD.OAUTH2, component: OAuth2 },
  { label: 'SAML2', name: LOGIN_METHOD.SAML2, component: Saml2 },
  { label: t('auth.qrCode.label'), name: 'SCAN', component: SCAN },
])
const activeAuthenticationComponent = computed(() => authenticationTabs.value.find((tab) => tab.name === activeName.value)?.component)
</script>

<template>
  <MkViewLayout :title="t('system.menu.userAuthentication')" class="system-settings-authentication">
    <template #default="{ title, Header }">
      <component :is="Header">
        <div class="w-full">
          <h4 class="mb-4">{{ title }}</h4>
          <el-tabs v-model="activeName">
            <el-tab-pane
              v-for="authenticationTab in authenticationTabs"
              :key="authenticationTab.name"
              :label="authenticationTab.label"
              :name="authenticationTab.name"
            />
          </el-tabs>
        </div>
      </component>

      <KeepAlive>
        <component :is="activeAuthenticationComponent" />
      </KeepAlive>
    </template>
  </MkViewLayout>
</template>

<style scoped lang="scss"></style>
