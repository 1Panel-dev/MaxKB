<script setup lang="ts">
import { useTemplateRef } from 'vue'
import type { SystemUserGroup } from '@/api/types'
import MkSearchList from '@/components/mk-search-list/index.vue'
import UserGroupMembersDrawer from '@/components/business/resource-authorization-drawer/user-group/UserGroupMembersDrawer.vue'

defineOptions({ name: 'UserGroupAuthorizationList' })

defineProps<{ activeId: string; userGroups: SystemUserGroup[] }>()
const emit = defineEmits<{ select: [userGroup: SystemUserGroup] }>()

function handleUserGroupSelect(userGroup: SystemUserGroup) {
  emit('select', userGroup)
}

/* 查看用户组成员 */
const membersDrawerRef = useTemplateRef<InstanceType<typeof UserGroupMembersDrawer>>('membersDrawerRef')

function handleOpenMembersDrawer(userGroup: SystemUserGroup) {
  membersDrawerRef.value?.open(userGroup)
}
</script>

<template>
  <MkSearchList :data="userGroups" :default-active="activeId" :props="{ label: 'name', value: 'id' }" @click="handleUserGroupSelect">
    <template #default="{ row }">
      <div class="flex min-w-0 flex-1 items-center gap-2">
        <span class="min-w-0 truncate" :title="row.name">{{ row.name }}</span>
        <span class="mk-link text-primary" @click.stop="handleOpenMembersDrawer(row)"> ({{ row.count }}) </span>
      </div>
    </template>
  </MkSearchList>
  <UserGroupMembersDrawer ref="membersDrawerRef" />
</template>
