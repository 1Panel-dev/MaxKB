<template>
  <div class="authentication-setting p-16-24">
    <h4>{{ $t('views.system.authentication.title') }}</h4>
    <el-tabs v-model="activeName" class="mt-4" @tab-click="handleClick">
      <template v-for="(item, index) in tabList" :key="index">
        <el-tab-pane :label="item.label" :name="item.name">
          <component :is="item.component" />
        </el-tab-pane>
      </template>
    </el-tabs>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import LDAP from './component/LDAP.vue'
import CAS from './component/CAS.vue'
import OIDC from './component/OIDC.vue'
import SCAN from './component/SCAN.vue'
import OAuth2 from './component/OAuth2.vue'
import { t } from '@/locales'
import useStore from '@/stores'

const { user } = useStore()
const router = useRouter()

const activeName = ref('LDAP')
const tabList = [
  {
    label: t('views.system.authentication.ldap.title'),
    name: 'LDAP',
    component: LDAP
  },
  {
    label: t('views.system.authentication.cas.title'),
    name: 'CAS',
    component: CAS
  },
  {
    label: t('views.system.authentication.oidc.title'),
    name: 'OIDC',
    component: OIDC
  },
  {
    label: t('views.system.authentication.oauth2.title'),
    name: 'OAuth2',
    component: OAuth2
  },
  {
    label: t('views.system.authentication.scanTheQRCode.title'),
    name: 'SCAN',
    component: SCAN
  }
]

function handleClick() {}

onMounted(() => {
  if (user.isExpire()) {
    router.push({ path: `/application` })
  }
})
</script>
<style lang="scss" scoped>
.authentication-setting__main {
  background-color: var(--app-view-bg-color);
  box-sizing: border-box;
  min-width: 700px;
  height: calc(100vh - var(--app-header-height) - var(--app-view-padding) * 2 - 70px);
  box-sizing: border-box;
  :deep(.form-container) {
    width: 70%;
    margin: 0 auto;
  }
}
</style>
