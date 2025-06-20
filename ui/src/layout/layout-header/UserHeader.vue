·
<template>
  <div class="app-top-bar-container border-b flex-center">
    <div class="logo mt-4">
      <LogoFull />
    </div>

    <div class="flex-between w-full">
      <div class="ml-24 flex align-center">
        <!-- 企业版: 工作空间下拉框-->
        <el-divider
          class="mr-8"
          direction="vertical"
          v-if="hasPermission(EditionConst.IS_EE, 'OR')"
        />
        <WorkspaceDropdown v-if="hasPermission(EditionConst.IS_EE, 'OR')" />
      </div>
      <TopMenu></TopMenu>
      <TopAbout></TopAbout>
    </div>
    <Avatar></Avatar>
  </div>
</template>
<script setup lang="ts">
import TopMenu from './top-menu/index.vue'
import Avatar from './avatar/index.vue'
import TopAbout from './top-about/index.vue'
import { EditionConst } from '@/utils/permission/data'
import { hasPermission } from '@/utils/permission/index'
</script>
<style lang="scss" scoped>
.app-top-bar-container {
  height: var(--app-header-height);
  box-sizing: border-box;
  padding: var(--app-header-padding);
}
</style>
