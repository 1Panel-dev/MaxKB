<script setup lang="ts">
import { computed, ref, type Component } from 'vue'
import { LOGIN_METHOD } from '@/api/enums'
import LDAP from './components/LDAP.vue'
import CAS from './components/CAS.vue'
import OIDC from './components/OIDC.vue'
import SCAN from './components/SCANLogin.vue'
import OAuth2 from './components/OAuth2.vue'

interface AuthenticationTab {
  component: Component
  label: string
  name: string
}

const activeName = ref(LOGIN_METHOD.LDAP)
const authenticationTabs: AuthenticationTab[] = [
  { label: 'LDAP', name: LOGIN_METHOD.LDAP, component: LDAP },
  { label: 'CAS', name: LOGIN_METHOD.CAS, component: CAS },
  { label: 'OIDC', name: LOGIN_METHOD.OIDC, component: OIDC },
  { label: 'OAuth2', name: LOGIN_METHOD.OAUTH2, component: OAuth2 },
  { label: '扫码登录', name: 'SCAN', component: SCAN },
]
const activeAuthenticationComponent = computed(() => authenticationTabs.find((tab) => tab.name === activeName.value)?.component)
</script>

<template>
  <MkViewLayout class="system-settings-authentication">
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
        <component :is="activeAuthenticationComponent" :key="activeName" />
      </KeepAlive>
    </template>
  </MkViewLayout>
</template>

<style scoped lang="scss"></style>
