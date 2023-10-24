<template>
  <div>
    <el-button v-hasPermission="'USER:DELETE'">用户删除权限</el-button>
    <el-button v-hasPermission="'USER:READ'">用户只读权限</el-button>
    <el-button v-hasPermission="new Role('USER')">普通用户角色</el-button>
    <el-button v-hasPermission="[new Role('ADMIN'), new Role('USER')]"
      >普通用户或者管理员</el-button
    >
    <el-button v-hasPermission="{ permission: ['USER:READ', new Role('USER')], compare: 'AND' }"
      >普通角色并且用户只读权限</el-button
    >

    首页
  </div>
</template>
<script setup lang="ts">
import { Role } from '@/utils/permission/type'
</script>
<style lang="scss" scoped></style>
