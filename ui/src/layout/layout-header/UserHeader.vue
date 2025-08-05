·
<template>
  <div class="app-top-bar-container border-b flex-center">
    <div class="logo mt-4">
      <LogoFull />
    </div>

    <div class="flex-between w-full">
      <div class="ml-24 flex align-center w-120">
        <!-- 企业版: 工作空间下拉框-->
        <el-divider
          class="mr-8"
          direction="vertical"
          v-if="hasPermission(EditionConst.IS_EE, 'OR')"
        />
        <WorkspaceDropdown
          v-if="hasPermission(EditionConst.IS_EE, 'OR')"
          :data="user.workspace_list"
          :currentWorkspace="currentWorkspace"
          @changeWorkspace="changeWorkspace"
        />
      </div>
      <TopMenu></TopMenu>
      <TopAbout class="mr-12"></TopAbout>
    </div>
    <Avatar></Avatar>
  </div>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopMenu from './top-menu/index.vue'
import Avatar from './avatar/index.vue'
import TopAbout from './top-about/index.vue'
import { EditionConst } from '@/utils/permission/data'
import { hasPermission } from '@/utils/permission/index'
import type { WorkspaceItem } from '@/api/type/workspace'
import useStore from '@/stores'
const router = useRouter()
const route = useRoute()

const { user } = useStore()
const currentWorkspace = computed(() => {
  return user.workspace_list.find((w) => w.id == user.workspace_id)
})

function changeWorkspace(item: WorkspaceItem) {
  const {
    meta: { activeMenu },
  } = route as any
  if (item.id === user.workspace_id) return
  user.setWorkspaceId(item.id || 'default')
  if (activeMenu.includes('application') && route.path != '/application') {
    router.push('/application')
  } else if (activeMenu.includes('knowledge') && route.path != '/knowledge') {
    router.push('/knowledge')
  } else {
    window.location.reload()
  }
}
</script>
<style lang="scss" scoped>
.app-top-bar-container {
  height: var(--app-header-height);
  box-sizing: border-box;
  padding: var(--app-header-padding);
}
</style>
