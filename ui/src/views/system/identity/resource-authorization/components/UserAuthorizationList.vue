<script setup lang="ts">
import type { CommonUserOption } from '@/api/types'
import { useStore } from '@/stores'
import MkSearchList from '@/components/mk-search-list/index.vue'

defineOptions({ name: 'UserAuthorizationList' })

defineProps<{ activeId: string; users: CommonUserOption[] }>()
const emit = defineEmits<{ select: [user: CommonUserOption] }>()

const { auth } = useStore()

function getUserRoleText(user: CommonUserOption) {
  return user.roles?.join('，') ?? ''
}

function handleUserSelect(user: CommonUserOption) {
  emit('select', user)
}
</script>

<template>
  <MkSearchList :data="users" :default-active="activeId" :props="{ label: 'nick_name', value: 'id' }" @click="handleUserSelect">
    <template #default="{ row }">
      <div class="flex min-w-0 flex-1 items-center gap-2">
        <span class="min-w-0 truncate" :title="row.nick_name">{{ row.nick_name }}</span>
        <span v-if="(auth.isEE || auth.isPE) && row.roles?.length" class="min-w-0 truncate text-N600" :title="getUserRoleText(row)"> ({{ getUserRoleText(row) }}) </span>
      </div>
    </template>
  </MkSearchList>
</template>
