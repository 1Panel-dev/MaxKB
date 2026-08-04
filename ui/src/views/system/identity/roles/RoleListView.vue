<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowDown, UserFilled } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import { MsgSuccess } from '@/utils/message'

interface SystemRole {
  id: string
  memberCount: number
  name: string
  system?: boolean
}

interface SystemRoleGroup {
  id: string
  name: string
  roles: SystemRole[]
}

interface PermissionRow {
  category: string
  categoryRowspan: number
  module: string
  moduleRowspan: number
  object: string
  permissions: string[]
}

type RoleDetailTab = 'permissions' | 'members'

const route = useRoute()
const searchKeyword = ref('')
const selectedRoleId = ref('system-administrator')
const activeRoleDetailTab = ref<RoleDetailTab>('permissions')
const expandedRoleGroupIds = ref<string[]>(['system', 'workspace', 'general'])
const systemRoleGroups = ref<SystemRoleGroup[]>([
  {
    id: 'system',
    name: '系统管理员',
    roles: [
      { id: 'system-administrator', name: '系统管理员', memberCount: 240, system: true },
      { id: 'administrator', name: '管理员', memberCount: 16 },
    ],
  },
  {
    id: 'workspace',
    name: '工作空间管理员',
    roles: [
      { id: 'workspace-administrator', name: '工作空间管理员', memberCount: 58, system: true },
      { id: 'maintenance', name: '维护人员', memberCount: 12 },
    ],
  },
  {
    id: 'general',
    name: '普通用户',
    roles: [
      { id: 'general-user', name: '普通用户', memberCount: 106, system: true },
      { id: 'test-role', name: '测试角色', memberCount: 6 },
      { id: 'test', name: '测试', memberCount: 2 },
    ],
  },
])
const permissionRows: PermissionRow[] = [
  {
    category: '身份与权限',
    categoryRowspan: 4,
    module: '用户管理',
    moduleRowspan: 1,
    object: '用户管理',
    permissions: ['查看', '创建', '编辑', '修改密码', '启用/禁用', '删除'],
  },
  {
    category: '',
    categoryRowspan: 0,
    module: '角色',
    moduleRowspan: 1,
    object: '角色',
    permissions: ['查看', '创建', '编辑', '删除', '权限配置', '添加成员', '移除成员'],
  },
  {
    category: '',
    categoryRowspan: 0,
    module: '工作空间',
    moduleRowspan: 1,
    object: '工作空间',
    permissions: ['查看', '创建', '重命名', '删除', '添加成员', '移除成员'],
  },
  {
    category: '',
    categoryRowspan: 0,
    module: '资源授权',
    moduleRowspan: 1,
    object: '资源授权',
    permissions: ['查看', '授权'],
  },
  {
    category: '资源管理',
    categoryRowspan: 12,
    module: '智能体',
    moduleRowspan: 5,
    object: '智能体',
    permissions: ['查看', '管理', '去对话', '设置', '导出', '删除'],
  },
  {
    category: '',
    categoryRowspan: 0,
    module: '',
    moduleRowspan: 0,
    object: '概览',
    permissions: ['查看', '嵌入第三方', '访问限制', '显示设置', 'API Key', '公共访问链接'],
  },
  {
    category: '',
    categoryRowspan: 0,
    module: '',
    moduleRowspan: 0,
    object: '应用接入',
    permissions: ['查看', '企业微信应用', '飞书应用', '钉钉应用', '公众号', 'Slack'],
  },
  {
    category: '',
    categoryRowspan: 0,
    module: '',
    moduleRowspan: 0,
    object: '对话用户',
    permissions: ['查看', '编辑'],
  },
  {
    category: '',
    categoryRowspan: 0,
    module: '',
    moduleRowspan: 0,
    object: '对话日志',
    permissions: ['查看', '标注', '导出', '清除策略设置', '添加至知识库'],
  },
  {
    category: '',
    categoryRowspan: 0,
    module: '知识库',
    moduleRowspan: 5,
    object: '知识库',
    permissions: ['查看', '管理', '同步', '向量化', '设置', '导出', '删除'],
  },
  {
    category: '',
    categoryRowspan: 0,
    module: '',
    moduleRowspan: 0,
    object: '文档',
    permissions: [
      '查看',
      '上传文档',
      '编辑',
      '同步',
      '迁移',
      '向量化',
      '生成问题',
      '设置',
      '启用/禁用',
      '导出',
      '删除',
    ],
  },
  {
    category: '',
    categoryRowspan: 0,
    module: '',
    moduleRowspan: 0,
    object: '问题',
    permissions: ['查看', '创建', '编辑', '关联分段', '删除'],
  },
  {
    category: '',
    categoryRowspan: 0,
    module: '',
    moduleRowspan: 0,
    object: '命中测试',
    permissions: ['查看', '提问', '参数设置'],
  },
  {
    category: '',
    categoryRowspan: 0,
    module: '',
    moduleRowspan: 0,
    object: '对话用户',
    permissions: ['查看', '编辑'],
  },
  {
    category: '',
    categoryRowspan: 0,
    module: '工具',
    moduleRowspan: 1,
    object: '工具',
    permissions: [
      '查看',
      '创建',
      '编辑',
      '复制',
      '删除',
      '启用/禁用',
      '权限设置',
      '导入',
      '导出',
      '启动参数',
    ],
  },
  {
    category: '',
    categoryRowspan: 0,
    module: '模型',
    moduleRowspan: 1,
    object: '模型',
    permissions: ['查看', '创建', '编辑', '模型参数设置', '删除'],
  },
]

const filteredRoleGroups = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()

  if (!keyword) {
    return systemRoleGroups.value
  }

  return systemRoleGroups.value
    .map((roleGroup) => ({
      ...roleGroup,
      roles: roleGroup.roles.filter((role) => role.name.toLowerCase().includes(keyword)),
    }))
    .filter((roleGroup) => roleGroup.roles.length > 0)
})

const selectedRole = computed(() => {
  return systemRoleGroups.value
    .flatMap((roleGroup) => roleGroup.roles)
    .find((role) => role.id === selectedRoleId.value)
})

function toggleRoleGroup(roleGroupId: string) {
  expandedRoleGroupIds.value = expandedRoleGroupIds.value.includes(roleGroupId)
    ? expandedRoleGroupIds.value.filter((id) => id !== roleGroupId)
    : [...expandedRoleGroupIds.value, roleGroupId]
}

async function createRole() {
  try {
    const { value } = await ElMessageBox.prompt('请输入角色名称', '创建角色', {
      confirmButtonText: '创建',
      cancelButtonText: '取消',
      inputPattern: /\S+/,
      inputErrorMessage: '请输入角色名称',
    })
    const roleName = value.trim()
    const newRole = {
      id: `role-${Date.now()}`,
      memberCount: 0,
      name: roleName,
    }
    const generalRoleGroup = systemRoleGroups.value.find((roleGroup) => roleGroup.id === 'general')

    generalRoleGroup?.roles.push(newRole)
    selectedRoleId.value = newRole.id
    MsgSuccess('角色创建成功')
  } catch {
    return
  }
}

function selectRole(roleId: string) {
  selectedRoleId.value = roleId
  activeRoleDetailTab.value = 'permissions'
}

function permissionTableSpan({ row, columnIndex }: { row: PermissionRow; columnIndex: number }) {
  if (columnIndex === 0) {
    return row.categoryRowspan ? [row.categoryRowspan, 1] : [0, 0]
  }

  if (columnIndex === 1) {
    return row.moduleRowspan ? [row.moduleRowspan, 1] : [0, 0]
  }

  return [1, 1]
}
</script>

<template>
  <div class="system-identity-roles flex h-full">
    <aside class="flex w-60 shrink-0 flex-col border-r p-4">
      <header class="flex-between mb-4">
        <h4>{{ route.meta.title }}</h4>
        <el-button text type="primary" @click="createRole">
          <MkIcon name="icon_add_outlined" :size="18" />
        </el-button>
      </header>
      <MkSearchList v-model="searchKeyword">
        <div class="flex flex-col gap-1">
          <section v-for="roleGroup in filteredRoleGroups" :key="roleGroup.id">
            <button
              type="button"
              class="flex w-full items-center gap-2 pt-2 pb-1 text-left text-N500"
              @click="toggleRoleGroup(roleGroup.id)"
            >
              <MkIcon
                :icon="ArrowDown"
                :size="10"
                class="transition-transform"
                :class="{ '-rotate-90': !expandedRoleGroupIds.includes(roleGroup.id) }"
              />
              <span class="font-medium">{{ roleGroup.name }}</span>
            </button>

            <div v-if="expandedRoleGroupIds.includes(roleGroup.id)" class="flex flex-col gap-1">
              <button
                v-for="role in roleGroup.roles"
                :key="role.id"
                type="button"
                class="flex h-10 w-full items-center gap-1.5 rounded-md px-2 text-left"
                :class="
                  selectedRoleId === role.id
                    ? 'bg-primary/10 font-medium text-primary'
                    : 'text-N900 hover:bg-black/5'
                "
                @click="selectRole(role.id)"
              >
                <span>{{ role.name }}</span>
                <span
                  v-if="role.system"
                  class="flex h-5 items-center rounded-sm bg-black/10 px-1 text-sm text-N600"
                >
                  系
                </span>
              </button>
            </div>
          </section>
        </div>
      </MkSearchList>
    </aside>

    <div v-if="selectedRole" class="flex min-w-0 flex-1 flex-col px-6">
      <header class="flex items-center justify-between py-4">
        <div class="flex min-w-0 items-center gap-2">
          <h4 class="truncate">{{ selectedRole.name }}</h4>
          <span
            v-if="selectedRole.system"
            class="flex h-5 items-center rounded-sm bg-black/10 px-1 text-sm text-N600"
          >
            系统
          </span>
          <el-divider direction="vertical" />
          <span class="flex items-center text-N500">
            <MkIcon :icon="UserFilled" :size="16" class="mr-1" />
            {{ selectedRole.memberCount }}
          </span>
        </div>

        <div class="flex rounded-md border border-black/15 p-0.5">
          <button
            type="button"
            class="h-7 rounded px-2"
            :class="
              activeRoleDetailTab === 'permissions'
                ? 'bg-primary/10 text-primary'
                : 'text-N900 hover:bg-black/5'
            "
            @click="activeRoleDetailTab = 'permissions'"
          >
            权限配置
          </button>
          <button
            type="button"
            class="h-7 rounded px-2"
            :class="
              activeRoleDetailTab === 'members'
                ? 'bg-primary/10 text-primary'
                : 'text-N900 hover:bg-black/5'
            "
            @click="activeRoleDetailTab = 'members'"
          >
            成员
          </button>
        </div>
      </header>

      <el-scrollbar v-if="activeRoleDetailTab === 'permissions'" class="min-h-0 flex-1">
        <el-table
          :data="permissionRows"
          border
          class="role-permission-table w-full"
          :span-method="permissionTableSpan"
        >
          <el-table-column prop="category" label="分类" width="120" />
          <el-table-column prop="module" label="模块名称" width="122" />
          <el-table-column prop="object" label="操作对象" width="122" />
          <el-table-column label="权限" min-width="500">
            <template #default="{ row }">
              <div class="grid grid-cols-4 gap-x-5 gap-y-1">
                <el-checkbox
                  v-for="permission in row.permissions"
                  :key="permission"
                  :model-value="true"
                  :disabled="selectedRole.system"
                  class="!mr-0 !h-6"
                >
                  {{ permission }}
                </el-checkbox>
              </div>
            </template>
          </el-table-column>
          <el-table-column width="40" align="center">
            <template #header>
              <el-checkbox :model-value="true" :disabled="selectedRole.system" />
            </template>
            <template #default>
              <el-checkbox :model-value="true" :disabled="selectedRole.system" />
            </template>
          </el-table-column>
        </el-table>
      </el-scrollbar>

      <div v-else class="min-h-0 flex-1">
        <MkTable
          :data="[]"
          :pagination-config="{ currentPage: 1, pageSize: 10, total: 0 }"
          row-key="id"
        >
          <el-table-column prop="name" label="姓名" />
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="email" label="邮箱" />
        </MkTable>
      </div>
    </div>
  </div>
</template>

<style scoped>
.role-permission-table {
  :deep(.el-table__cell) {
    padding: 8px 0;
  }
}
</style>
