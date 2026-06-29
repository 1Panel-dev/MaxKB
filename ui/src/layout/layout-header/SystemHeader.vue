·
<template>
  <div class="app-top-bar-container flex-center">
    <div class="logo-container flex align-center">
      <img src="@/assets/logo/logo.png" alt="logo" class="header-logo" />
      <span class="logo-text">MaxKB</span>
    </div>

    <div class="flex-between w-full align-center">
      <h4><el-divider class="ml-16 mr-16" direction="vertical" />{{ $t('views.system.title') }}</h4>
      <div class="flex align-center mr-8">
        <TopAbout type="system"></TopAbout>
        <el-divider class="ml-8 mr-8" direction="vertical" />
        <el-button
          link
          @click="goHome"
          style="color: var(--text-primary)"
          v-if="
            hasPermission(
              [
                RoleConst.USER.getWorkspaceRole,
                RoleConst.EXTENDS_USER.getWorkspaceRole,
                RoleConst.EXTENDS_WORKSPACE_MANAGE.getWorkspaceRole,
                RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              ],
              'OR',
            )
          "
        >
          <AppIcon class="mr-8" iconName="app-workspace" style="font-size: 16px"></AppIcon>
          {{ $t('views.workspace.toWorkspace') }}</el-button
        >
      </div>
    </div>
    <Avatar></Avatar>
  </div>
</template>
<script setup lang="ts">
import { RoleConst } from '@/utils/permission/data'
import Avatar from './avatar/index.vue'
import TopAbout from './top-about/index.vue'
import { useRouter } from 'vue-router'
import { hasPermission } from '@/utils/permission'

const router = useRouter()
const goHome = () => {
  router.push('/')
}
</script>
<style lang="scss" scoped>
.app-top-bar-container {
  height: var(--app-header-height);
  box-sizing: border-box;
  padding: var(--app-header-padding);
}

.logo-container {
  gap: 10px;
}

.header-logo {
  height: 32px;
  width: auto;
  object-fit: contain;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #1A6DFF 0%, #3D7DF3 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>
