<template>
  <div class="flex align-center top-about">
    <el-button
      round
      @click="toUrl('https://maxkb.cn/pricing.html')"
      class="pricing-button mr-8"
      v-hasPermission="EditionConst.IS_CE"
    >
      <AppIcon iconName="app-pricing" class="mr-8"></AppIcon>
      {{ $t('common.upgrade') }}
    </el-button>
    <el-tooltip
      v-if="
        hasPermission(
          [
            RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
            PermissionConst.TRIGGER_READ.getWorkspacePermissionWorkspaceManageRole,
          ],
          'OR',
        )
      "
      effect="dark"
      :content="$t('views.trigger.title')"
      placement="top"
    >
      <el-button
        text
        @click="router.push({ name: 'trigger' })"
        :class="route.path.includes('trigger') ? 'active' : ''"
      >
        <AppIcon
          iconName="app-trigger"
          :class="route.path.includes('trigger') ? 'color-primary' : 'color-secondary'"
          style="font-size: 20px"
        ></AppIcon>
      </el-button>
    </el-tooltip>
    <el-tooltip
      effect="dark"
      :content="$t('layout.github')"
      placement="top"
      v-if="theme.themeInfo?.showProject"
    >
      <el-button text @click="toUrl(theme.themeInfo?.projectUrl)">
        <AppIcon
          iconName="app-github"
          class="cursor color-secondary"
          style="font-size: 20px"
        ></AppIcon>
      </el-button>
    </el-tooltip>
    <el-tooltip
      effect="dark"
      :content="$t('layout.wiki')"
      placement="top"
      v-if="theme.themeInfo?.showUserManual"
    >
      <el-button text @click="toUrl(theme.themeInfo?.userManualUrl)">
        <AppIcon
          iconName="app-user-manual"
          class="cursor color-secondary"
          style="font-size: 20px"
        ></AppIcon>
      </el-button>
    </el-tooltip>
    <el-tooltip
      effect="dark"
      :content="$t('layout.forum')"
      placement="top"
      v-if="theme.themeInfo?.showForum"
    >
      <el-button text @click="toUrl(theme.themeInfo?.forumUrl)">
        <AppIcon
          iconName="app-help"
          class="cursor color-secondary"
          style="font-size: 20px"
        ></AppIcon>
      </el-button>
    </el-tooltip>
  </div>
</template>
<script setup lang="ts">
import useStore from '@/stores'
import { hasPermission } from '@/utils/permission'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
import { useRoute, useRouter } from 'vue-router'
const route = useRoute()
const router = useRouter()
const { theme, user } = useStore()

function toUrl(url: string) {
  window.open(url, '_blank')
}
</script>
<style scoped lang="scss">
.top-about {
  .el-button.is-text {
    max-height: 32px;
    padding: 6px !important;
  }
  .el-button + .el-button {
    margin-left: 4px !important;
  }
  .active {
    background: #ffffff;
    &:hover {
      background: #ffffff;
    }
  }
}
.pricing-button {
  background: linear-gradient(90deg, #3370ff 0%, #7f3bf5 100%);
  color: #ffffff;
}
</style>
