<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from 'vue'
import RoleApi from '@/api/admin/system/role'
import { ROLE_TYPE } from '@/api/enums'
import type { RoleItem, RoleType } from '@/api/types'
import { ROLE_TYPE_LABELS } from '@/constants'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import RoleMemberList from './components/RoleMemberList.vue'
import RolePermissionConfiguration from './components/RolePermissionConfiguration.vue'
import CreateOrUpdateRoleDialog from './dialog/CreateOrUpdateRoleDialog.vue'

type RoleDetailTab = 'permission' | 'member'
const currentTab = ref<RoleDetailTab>('permission')

/* 角色列表 */
const loadingRoles = ref(false)
const filterText = ref('')
const AllRoles = ref<RoleItem[]>([])
const currentRole = ref<RoleItem>()

const roleGroups = computed(() => {
  const keyword = filterText.value.trim().toLowerCase()
  return (Object.keys(ROLE_TYPE_LABELS) as RoleType[]).map((type) => ({
    label: ROLE_TYPE_LABELS[type],
    roles: AllRoles.value.filter(
      (role) => role.type === type && (!keyword || role.role_name.toLowerCase().includes(keyword)),
    ),
    type,
  }))
})

function loadRoles(selectedRoleId?: string) {
  loadingRoles.value = true
  return RoleApi.getRoleList()
    .then(({ internal_role, custom_role }) => {
      AllRoles.value = [...internal_role, ...custom_role]
      currentRole.value =
        AllRoles.value.find(({ id }) => id === selectedRoleId) ??
        AllRoles.value.find(({ id }) => id === currentRole.value?.id) ??
        internal_role[0]
    })
    .finally(() => {
      loadingRoles.value = false
    })
}

function handleRoleSelect(role: RoleItem) {
  currentRole.value = role
}

// 默认展开的角色组
const DEFAULT_EXPANDED_ROLE_TYPES = new Set<RoleType>([
  ROLE_TYPE.ADMIN,
  ROLE_TYPE.WORKSPACE_MANAGE,
  ROLE_TYPE.USER,
])
function isRoleGroupDefaultExpanded(roleType: RoleType) {
  return DEFAULT_EXPANDED_ROLE_TYPES.has(roleType)
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
        <el-tooltip content="创建角色" placement="top">
          <el-button class="-mr-1" text type="primary" @click="handleOpenRoleDialog()">
            <MkIcon name="icon_add_outlined" :size="18" />
          </el-button>
        </el-tooltip>
      </component>

      <div class="px-4">
        <MkSearchInput v-model="filterText" class="shrink-0" />
      </div>
      <el-scrollbar class="min-h-0 flex-1">
        <div class="px-4 pb-4 pt-2">
          <MkCollapse
            v-for="roleGroup in roleGroups"
            :key="roleGroup.type"
            :default-expanded="isRoleGroupDefaultExpanded(roleGroup.type)"
            :title="roleGroup.label"
            trigger-class="text-N500"
          >
            <div class="flex flex-col gap-1">
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
                  <el-tag type="info" size="small" class="ml-[6px] text-N600!" v-if="role.internal"
                    >系</el-tag
                  >
                </template>
                <template v-if="!role.internal" #action-dropdown>
                  <MkDropdownItem @click="handleOpenRoleDialog(role)">
                    <template #icon><MkIcon name="icon_edit_outlined" /></template>重命名
                  </MkDropdownItem>
                  <MkDropdownItem divided @click="handleDeleteRole(role)">
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
          <div class="flex min-w-0 flex-1 items-center gap-2">
            <h4 class="min-w-0 truncate" :title="currentRole.role_name">
              {{ currentRole.role_name }}
            </h4>
            <el-tag type="info" size="small" class="shrink-0 text-N600!">
              {{ currentRole.internal ? '系' : ROLE_TYPE_LABELS[currentRole.type] }}</el-tag
            >
            <el-divider class="shrink-0" direction="vertical" />
            <span class="flex shrink-0 items-center text-N500">
              <MkIcon name="icon_member_filled" class="mr-1" />{{ currentRole.user_count ?? 0 }}
            </span>
          </div>
          <el-radio-group v-model="currentTab">
            <el-radio-button value="permission" label="权限配置" />
            <el-radio-button value="member" label="成员" />
          </el-radio-group>
        </component>
        <!-- 权限配置 -->
        <RolePermissionConfiguration
          v-if="currentTab === 'permission'"
          :current-role="currentRole"
        />
        <!-- 成员 -->
        <RoleMemberList v-else :current-role="currentRole" />
      </template>
      <MkEmpty v-else class="flex-1" />
    </template>
  </MkViewLayout>
  <CreateOrUpdateRoleDialog ref="roleDialogRef" @refresh="handleRoleSaved" />
</template>
