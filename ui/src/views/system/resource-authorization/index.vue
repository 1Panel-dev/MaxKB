<template>
  <div class="p-5 h-full flex flex-col">
    <div class="flex items-center gap-3 mb-4">
      <span class="text-lg font-semibold" style="color:var(--mk-N900)">资源授权</span>
    </div>
    <el-card class="flex-1 !p-0 overflow-hidden authorization-card" style="--el-card-padding:0">
      <!-- Left: member list -->
      <div class="w-[20%] border-r shrink-0 flex flex-col">
       <div class="p-4 pb-0">
          <h4 class="text-sm font-semibold mb-3" style="color:var(--mk-N900)">成员</h4>
          <el-input
            v-model="filterText"
            placeholder="搜索"
            prefix-icon="Search"
            size="small"
            clearable
          />
        </div>
        <el-scrollbar class="flex-1 px-4 py-2">
          <div
            v-for="u in filteredMembers"
            :key="u.id"
            class="flex items-center gap-2 px-3 py-2 rounded-md cursor-pointer text-sm mb-1"
            :class="currentUser === u.id ? 'bg-primary/10 text-primary' : 'hover:bg-gray-50'"
            @click="selectMember(u)"
          >
            <span class="truncate">{{ u.nick_name }}</span>
            <span class="text-xs shrink-0" style="color:var(--mk-N600)">({{ u.type }})</span>
          </div>
          <el-empty v-if="filteredMembers.length === 0" description="无成员" :image-size="60" />
        </el-scrollbar>
      </div>

      <!-- Right: PermissionTable -->
      <PermissionTable
        v-loading="rLoading"
        :data="treeData"
        :type="resourceType"
        @submitPermissions="submitPermissions"
      />
    </el-card>
  </div>
</template>
 
<style lang="scss" scoped>
.authorization-card :deep(.el-card__body) {
  display: flex;
  height: 100%;
}
</style>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import authApi from '@/api/system/authorization'
import PermissionTable from './component/PermissionTable.vue'

const route = useRoute()

const resourceType = computed(() => (route.meta?.resource as string) || 'APPLICATION')

// ---- member list ----
const loading = ref(false)
const rLoading = ref(false)
const memberList = ref<any[]>([])
const filterText = ref('')
const currentUser = ref('')

const filteredMembers = computed(() => {
  if (!filterText.value) return memberList.value
  const q = filterText.value.toLowerCase()
  return memberList.value.filter((u: any) => u.nick_name?.toLowerCase().includes(q))
})

async function loadMembers() {
  loading.value = true
  try {
    const workspaceId = localStorage.getItem('workspace_id') || 'default'
    const res = await authApi.getUserMember(workspaceId, loading)
    memberList.value = res.data || []
    if (memberList.value.length) {
      currentUser.value = memberList.value[0].id
      loadTree()
    }
  } catch {
    memberList.value = []
  }
}

function selectMember(u: any) {
  currentUser.value = u.id
  loadTree()
}

// ---- permission tree ----
const permissionData = ref<any[]>([])

function toTree(nodeList: any[], pField: string) {
  if (!nodeList || !nodeList.length) return []
  const list = JSON.parse(JSON.stringify(nodeList))
  const map = Object.fromEntries(list.map((i: any) => [i.id, i]))
  for (const el of list) {
    if (!el.children) el.children = []
    if (el[pField]) {
      const p = map[el[pField]]
      if (p) {
        if (!p.children) p.children = []
        p.children.push(el)
      }
    }
  }
  return list.filter((i: any) => !i[pField])
}

const treeData = computed(() => {
  if (resourceType.value === 'MODEL') return permissionData.value
  return toTree(permissionData.value, 'folder_id')
})

async function loadTree() {
  if (!currentUser.value) return
  rLoading.value = true
  try {
    const workspaceId = localStorage.getItem('workspace_id') || 'default'
    const res = await authApi.getResourceAuthorization(
      workspaceId,
      currentUser.value,
      resourceType.value,
      undefined,
      rLoading,
    )
    permissionData.value =
      res.data?.map((item: any) => {
        if (!item.folder_id && item.permission === 'NOT_AUTH') {
          return { ...item, permission: 'VIEW' }
        }
        return item
      }) || []
  } catch {
    permissionData.value = []
  }
  rLoading.value = false
}

// ---- submit ----
async function submitPermissions(payload: any[]) {
  rLoading.value = true
  try {
    const workspaceId = localStorage.getItem('workspace_id') || 'default'
    await authApi.putResourceAuthorization(
      workspaceId,
      currentUser.value,
      resourceType.value,
      payload,
      rLoading,
    )
    ElMessage.success('权限已更新')
    loadTree()
  } catch {
    ElMessage.error('权限更新失败')
  }
}

// ---- watchers ----
watch(() => route.meta?.resource, () => {
  if (currentUser.value) loadTree()
})

onMounted(loadMembers)
</script>
