<script setup lang="ts">
import { ref, type Component } from 'vue'
import LDAP from './component/LDAP.vue'
import CAS from './component/CAS.vue'
import OIDC from './component/OIDC.vue'
import SCAN from './component/SCAN.vue'
import OAuth2 from './component/OAuth2.vue'
import Saml2 from './component/Saml2.vue'
import Setting from './component/Setting.vue'

interface AuthenticationTab {
  component: Component
  label: string
  name: string
}

const activeName = ref('SETTING')
const authenticationTabs: AuthenticationTab[] = [
  { label: '登录设置', name: 'SETTING', component: Setting },
  { label: 'LDAP', name: 'LDAP', component: LDAP },
  { label: 'CAS', name: 'CAS', component: CAS },
  { label: 'OIDC', name: 'OIDC', component: OIDC },
  { label: 'OAuth2', name: 'OAuth2', component: OAuth2 },
  { label: 'SAML2', name: 'SAML2', component: Saml2 },
  { label: '扫码登录', name: 'SCAN', component: SCAN },
]
</script>

<template>
  <MkViewLayout class="authentication-settings">
    <el-tabs v-model="activeName" class="authentication-tabs h-full">
      <el-tab-pane
        v-for="authenticationTab in authenticationTabs"
        :key="authenticationTab.name"
        :label="authenticationTab.label"
        :name="authenticationTab.name"
        lazy
      >
        <component :is="authenticationTab.component" />
      </el-tab-pane>
    </el-tabs>
  </MkViewLayout>
</template>

<style scoped lang="scss">
.authentication-tabs {
  :deep(.el-tabs__content) {
    height: calc(100% - 56px);
  }

  :deep(.el-tab-pane) {
    height: 100%;
  }
}
</style>
