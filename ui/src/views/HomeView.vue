<script setup lang="ts">
import PermissionConst from '@/utils/permission/data'
</script>

<template>
  首页
  <div v-hasPermission="PermissionConst.USER_READ.getWorkspacePermission('default')">
    default工作空间用户只读
  </div>
  <div v-hasPermission="PermissionConst.USER_READ.getWorkspacePermission('default1')">
    default1工作空间用户只读
  </div>
  <div v-hasPermission="PermissionConst.USER_READ">用户只读</div>
  <div
    v-hasPermission="
      PermissionConst.KNOWLEDGE_READ.getWorkspaceResourcePermission('default', 'KNOWLEDGE', 'xxx')
    "
  >
    default工作空间的知识库xxx权限
  </div>
</template>
