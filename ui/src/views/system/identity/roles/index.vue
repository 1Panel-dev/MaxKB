<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from 'vue'
import RoleApi from '@/api/admin/system/role'
import type { RoleItem, RoleType } from '@/api/types'
import { ROLE_TYPE_LABELS } from '@/constants'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import RoleMemberList from './components/RoleMemberList.vue'
import RolePermissionConfiguration from './components/RolePermissionConfiguration.vue'
import CreateOrUpdateRoleDialog from './dialog/CreateOrUpdateRoleDialog.vue'
import perm from '@/permission/index.ts'

type RoleDetailTab = 'permission' | 'member'
const currentTab = ref<RoleDetailTab>('permission')

/* 角色列表 */
const loadingRoles = ref(false)
const filterText = ref('')
const AllRoles = ref<RoleItem[]>([])
const currentRole = ref<RoleItem>()
const expandedRoleTypes = ref<Partial<Record<RoleType, boolean>>>({})

const roleGroups = computed(() => {
  const keyword = filterText.value.trim().toLowerCase()
  return (Object.keys(ROLE_TYPE_LABELS) as RoleType[]).map((type) => ({
    label: ROLE_TYPE_LABELS[type],
    roles: AllRoles.value.filter((role) => role.type === type && (!keyword || role.role_name.toLowerCase().includes(keyword))),
    type,
  }))
})

function loadRoles(selectedRoleId?: string) {
  loadingRoles.value = true
  return RoleApi.getRoleList()
    .then((roles) => {
      AllRoles.value = roles
      currentRole.value =
        AllRoles.value.find(({ id }) => id === selectedRoleId) ?? AllRoles.value.find(({ id }) => id === currentRole.value?.id) ?? AllRoles.value[0]
      if (currentRole.value) {
        expandedRoleTypes.value[currentRole.value.type] = true
      }
    })
    .finally(() => {
      loadingRoles.value = false
    })
}

function handleRoleSelect(role: RoleItem) {
  currentRole.value = role
}

/* 创建、重命名角色 */
const roleDialogRef = useTemplateRef<InstanceType<typeof CreateOrUpdateRoleDialog>>('roleDialogRef')

function handleOpenRoleDialog(role?: RoleItem) {
  roleDialogRef.value?.open(role)
}

function handleRoleSaved(role: RoleItem) {
  loadRoles(role.id)
}

/* 删除角色 */
function handleDeleteRole(role: RoleItem) {
  MsgConfirm(`是否刪除角色：${role.role_name}？`, '删除后，该角色下的成员都会被移除，请谨慎操作。')
    .then(() => {
      loadingRoles.value = true
      return RoleApi.deleteRole(role.id).then(() => {
        MsgSuccess('删除成功')
        return loadRoles(currentRole.value?.id === role.id ? undefined : currentRole.value?.id)
      })
    })
    .catch(() => {})
    .finally(() => {
      loadingRoles.value = false
    })
}

onMounted(() => loadRoles())
</script>

<template>
  <MkViewLayout class="system-identity-roles" :loading="loadingRoles">
    <template #aside="{ title, Header }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <MkTooltip content="创建角色" placement="top" v-if="perm.system.role.create()">
          <!-- 创建角色 -->
          <el-button class="-mr-1" text type="primary" @click="handleOpenRoleDialog()">
            <MkIcon name="icon_add_outlined" :size="18" />
          </el-button>
        </MkTooltip>
      </component>

      <div class="px-4">
        <MkSearchInput v-model="filterText" class="shrink-0" />
      </div>
      <el-scrollbar class="min-h-0 flex-1">
        <div class="px-4 pb-4 pt-2">
          <MkCollapse
            v-for="roleGroup in roleGroups"
            :key="roleGroup.type"
            v-model:expanded="expandedRoleTypes[roleGroup.type]"
            :default-expanded="false"
            :title="roleGroup.label"
            trigger-class="text-N500 py-2!"
          >
            <div class="space-y-1">
              <MkListItem
                v-for="(role, roleIndex) in roleGroup.roles"
                :key="role.id"
                :active="currentRole?.id === role.id"
                :index="roleIndex"
                label-field="role_name"
                :row="role"
                @click="handleRoleSelect(role)"
              >
                <template #default>
                  <span class="min-w-0 truncate" :title="role.role_name">{{ role.role_name }}</span>
                  <el-tag type="info" size="small" class="ml-[6px]" v-if="role.internal">系</el-tag>
                </template>
                <template v-if="!role.internal" #action-dropdown>
                  <!-- 重命名 -->
                  <MkDropdownItem v-if="perm.system.role.edit()" @click="handleOpenRoleDialog(role)">
                    <template #icon><MkIcon name="icon_rename_outlined" /></template>重命名
                  </MkDropdownItem>
                  <!-- 删除 -->
                  <MkDropdownItem v-if="perm.system.role.delete()" divided @click="handleDeleteRole(role)">
                    <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>删除
                  </MkDropdownItem>
                </template>
              </MkListItem>
            </div>
          </MkCollapse>
        </div>
      </el-scrollbar>
    </template>

    <template #default="{ Header }">
      <template v-if="currentRole">
        <component :is="Header">
          <div class="flex-align-center min-w-0 flex-1 gap-2">
            <h4 class="min-w-0 truncate" :title="currentRole.role_name">
              {{ currentRole.role_name }}
            </h4>
            <el-tag type="info" size="small" class="shrink-0"> {{ currentRole.internal ? '系' : ROLE_TYPE_LABELS[currentRole.type] }}</el-tag>
            <el-divider class="shrink-0" direction="vertical" />
            <span class="flex-align-center shrink-0 text-N500">
              <MkIcon name="icon_member_filled" class="mr-1" />{{ currentRole.user_count ?? 0 }}
            </span>
          </div>
          <el-radio-group v-model="currentTab">
            <el-radio-button value="permission" label="权限配置" />
            <el-radio-button value="member" label="成员" />
          </el-radio-group>
        </component>
        <!-- 权限配置 -->
        <RolePermissionConfiguration v-if="currentTab === 'permission'" :current-role="currentRole" />
        <!-- 成员 -->
        <RoleMemberList v-else :current-role="currentRole" />
      </template>
      <MkEmpty v-else class="flex-1" />
    </template>
  </MkViewLayout>
  <CreateOrUpdateRoleDialog ref="roleDialogRef" @refresh="handleRoleSaved" />
</template>
