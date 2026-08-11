<template>
  <div class="p-5 h-full flex flex-col">
    <div class="flex items-center gap-3 mb-4">
      <span class="text-lg font-semibold" style="color:var(--mk-N900)">角色管理</span>
    </div>
    <el-card class="flex-1 flex !p-0 overflow-hidden" style="--el-card-padding:0">
      <div class="flex h-full">
        <!-- Left: role list -->
        <div class="w-56 border-r shrink-0 flex flex-col">
          <div class="p-4 pb-0">
            <el-input v-model="filterText" placeholder="搜索角色" prefix-icon="Search" size="small" clearable />
          </div>
          <el-scrollbar class="flex-1 px-4 py-2" v-loading="loading">
            <!-- Built-in roles -->
            <div class="text-xs text-gray-400 ml-2 mb-2 mt-2">内置角色</div>
            <div v-if="filteredInternal.length">
              <div
                v-for="r in filteredInternal"
                :key="r.id"
                class="flex items-center px-3 py-2 rounded-md cursor-pointer text-sm mb-1"
                :class="currentRole?.id === r.id ? 'bg-primary/10 text-primary' : 'hover:bg-gray-50'"
                @click="selectRole(r)"
              >
                <span class="truncate">{{ r.role_name }}</span>
              </div>
            </div>
            <div v-else class="text-xs text-gray-300 ml-2 mb-2">暂无内置角色</div>

            <!-- Custom roles -->
            <div class="border-t my-2 pt-2 flex items-center justify-between">
              <span class="text-xs text-gray-400 ml-2">自定义角色</span>
              <el-button text type="primary" size="small" @click="openCreateDialog()">
                <MkIcon name="icon_add_outlined" :size="14" />
              </el-button>
            </div>
            <div v-if="filteredCustom.length">
              <div
                v-for="r in filteredCustom"
                :key="r.id"
                class="group flex items-center justify-between px-3 py-2 rounded-md cursor-pointer text-sm mb-1"
                :class="currentRole?.id === r.id ? 'bg-primary/10 text-primary' : 'hover:bg-gray-50'"
                @click="selectRole(r)"
                @mouseenter="hoverId = r.id"
                @mouseleave="hoverId = ''"
              >
                <span class="truncate flex-1">
                  {{ r.role_name }}
                  <span class="text-xs text-gray-400 ml-1">({{ roleTypeMap[r.type] || r.type }})</span>
                </span>
                <span v-if="hoverId === r.id" class="shrink-0 flex gap-1" @click.stop>
                  <el-button text size="small" @click="openCreateDialog(r)">编辑</el-button>
                  <el-button text type="danger" size="small" @click="deleteRole(r)">删除</el-button>
                </span>
              </div>
            </div>
            <div v-else class="text-xs text-gray-300 ml-2 mb-2">暂无自定义角色</div>

            <el-empty v-if="!loading && !filteredInternal.length && !filteredCustom.length" description="暂无角色" :image-size="50" />
          </el-scrollbar>
        </div>

        <!-- Right: permission / member tabs -->
        <div class="flex-1 flex flex-col p-4 overflow-hidden">
          <template v-if="currentRole">
            <div class="flex items-center justify-between mb-4 shrink-0">
              <div class="flex items-center gap-2">
                <span class="text-base font-semibold" style="color:var(--mk-N900)">{{ currentRole.role_name }}</span>
                <span v-if="!currentRole.internal" class="text-xs text-gray-400">
                  ({{ roleTypeMap[currentRole.type] || currentRole.type }})
                </span>
                <el-divider direction="vertical" />
                <el-icon class="text-gray-400"><UserFilled /></el-icon>
                <span class="text-xs text-gray-400">{{ currentRole.user_count || 0 }}</span>
              </div>
              <el-radio-group v-model="currentTab" size="small">
                <el-radio-button value="permission">权限配置</el-radio-button>
                <el-radio-button value="member">成员管理</el-radio-button>
              </el-radio-group>
            </div>
            <PermissionConfiguration v-if="currentTab === 'permission'" :currentRole="currentRole" />
            <Member v-else :currentRole="currentRole" />
          </template>
          <el-empty v-else description="请先选择左侧角色" :image-size="60" class="mt-10" />
        </div>
      </div>
    </el-card>
    <CreateOrUpdateRoleDialog ref="dialogRef" @refresh="onRoleCreated" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import roleApi from '@/api/system/role'
import type { RoleItem } from '@/api/type/role'
import { roleTypeMap } from './index'
import PermissionConfiguration from './component/PermissionConfiguration.vue'
import Member from './component/Member.vue'
import CreateOrUpdateRoleDialog from './component/CreateOrUpdateRoleDialog.vue'

const loading = ref(false)
const internalRoleList = ref<RoleItem[]>([])
const customRoleList = ref<RoleItem[]>([])
const currentRole = ref<RoleItem>()
const filterText = ref('')
const hoverId = ref('')
const currentTab = ref('permission')
const dialogRef = ref()

function filter(list: RoleItem[], text: string) {
  if (!text) return list
  return list.filter((r) => r.role_name?.toLowerCase().includes(text.toLowerCase()))
}

const filteredInternal = computed(() => filter(internalRoleList.value, filterText.value))
const filteredCustom = computed(() => filter(customRoleList.value, filterText.value))

async function getRole() {
  loading.value = true
  try {
    const res = await roleApi.getRoleList(loading)
    internalRoleList.value = res.data?.internal_role || []
    customRoleList.value = res.data?.custom_role || []
    console.log('[role] loaded:', internalRoleList.value.length, 'internal,', customRoleList.value.length, 'custom')
  } catch (e) {
    console.error('[role] failed to load roles:', e)
    internalRoleList.value = []
    customRoleList.value = []
  }
}

function selectRole(r: RoleItem) {
  currentRole.value = r
}

function openCreateDialog(item?: RoleItem) {
  dialogRef.value?.open(item)
}

function onRoleCreated(role?: RoleItem) {
  getRole()
  if (role) currentRole.value = role
}

function deleteRole(item: RoleItem) {
  ElMessageBox.confirm(`确认删除角色「${item.role_name}」吗？`, '提示', {
    confirmButtonText: '删除',
    confirmButtonClass: 'danger',
    type: 'warning',
  }).then(() => {
    roleApi.deleteRole(item.id).then(() => {
      ElMessage.success('删除成功')
      getRole()
      if (currentRole.value?.id === item.id) {
        currentRole.value = internalRoleList.value[0]
      }
    })
  }).catch(() => {})
}

onMounted(async () => {
  await getRole()
  if (internalRoleList.value.length) {
    currentRole.value = internalRoleList.value[0]
  }
})
</script>
