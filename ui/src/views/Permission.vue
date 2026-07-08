<template>
  <div>说明: v-hasPermission 是使用v-show 本质上组件是渲染的 v-if="hasPermission('xxxx')"</div>
  <div>这种方式组件不会渲染(用于比如像组件挂载的时候需要调用接口,不想让组件渲染)</div>
  <div>比如工作空间的下拉列表组件使用v-if 示例： 企业版组件:</div>

  <button v-if="hasPermission(EditionConst.IS_CE, 'OR')">我是社区版组件</button>

  <button v-hasPermission="EditionConst.IS_CE">我是社区版组件</button>
  <!-- ================我是企业版组件================== -->
  <button v-if="hasPermission(EditionConst.IS_EE, 'OR')">我是企业版组件</button>
  <button v-hasPermission="EditionConst.IS_EE">我是企业版组件</button>

  <!-- ================企业版组件 并且是ADMIN角色================== -->
  <button v-if="hasPermission([EditionConst.IS_EE, RoleConst.ADMIN], 'AND')">
    我是企业版并且是ADMIN角色
  </button>
  <button
    v-hasPermission="new ComplexPermission([RoleConst.ADMIN], [], [EditionConst.IS_EE], 'AND')"
  >
    我是企业版并且是ADMIN角色
  </button>
  <!-- ================企业版组件 并且是当前工作空间管理员================== -->
  <button
    v-if="hasPermission([EditionConst.IS_EE, RoleConst.WORKSPACE_MANAGE.getWorkspaceRole], 'AND')"
  >
    我是企业版并且拥有当前工作空间管理员角色
  </button>
  <button
    v-hasPermission="
      new ComplexPermission(
        [RoleConst.WORKSPACE_MANAGE.getWorkspaceRole],
        [],
        [EditionConst.IS_EE],
        'OR',
      )
    "
  >
    我是企业版并且拥有当前工作空间管理员角色
  </button>
  <!-- ================企业版组件 （并且是当前工作空间管理员 或者有用户只读）================== -->
  <button
    v-if="
      hasPermission(
        new ComplexPermission(
          [RoleConst.WORKSPACE_MANAGE.getWorkspaceRole],
          [PermissionConst.USER_READ],
          [EditionConst.IS_EE],
          'OR',
        ),
        'OR',
      )
    "
  >
    我是企业版 （并且是当前工作空间管理员 或者有用户只读）
  </button>
  <button
    v-hasPermission="
      new ComplexPermission(
        [RoleConst.WORKSPACE_MANAGE.getWorkspaceRole],
        [PermissionConst.USER_READ],
        [EditionConst.IS_EE],
        'OR',
      )
    "
  >
    我是企业版（并且是当前工作空间管理员 或者有用户只读）
  </button>
</template>
<script setup lang="ts">
import { PermissionConst, EditionConst, RoleConst } from '@/utils/permission/data'
import { hasPermission } from '@/utils/permission/index'
import { ComplexPermission } from '@/utils/permission/type'
</script>
<style lang="scss" scoped></style>
