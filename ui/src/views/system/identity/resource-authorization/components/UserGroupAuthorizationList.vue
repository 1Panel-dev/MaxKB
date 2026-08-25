<script setup lang="ts">
import type { SystemUserGroup } from '@/api/types'
import MkSearchList from '@/components/mk-search-list/index.vue'

defineOptions({ name: 'UserGroupAuthorizationList' })

defineProps<{
  activeId: string
  userGroups: SystemUserGroup[]
}>()
const emit = defineEmits<{
  select: [userGroup: SystemUserGroup]
}>()

function handleUserGroupSelect(userGroup: SystemUserGroup) {
  emit('select', userGroup)
}
</script>

<template>
  <MkSearchList
    :data="userGroups"
    :default-active="activeId"
    :props="{ label: 'name', value: 'id' }"
    @click="handleUserGroupSelect"
  >
    <template #default="{ row }">
      <div class="flex min-w-0 flex-1 items-center gap-2">
        <span class="min-w-0 truncate" :title="row.name">{{ row.name }}</span>
        <span class="shrink-0 text-primary">({{ row.count }})</span>
      </div>
    </template>
  </MkSearchList>
</template>
