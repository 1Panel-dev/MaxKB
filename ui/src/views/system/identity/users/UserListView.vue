<script setup lang="ts">
import { computed, ref, watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import { Delete, EditPen, Lock, Plus, Upload } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import UserFormDialog, { type UserFormValue } from './components/UserFormDialog.vue'
const route = useRoute()
interface SystemUser extends UserFormValue {
  createdAt: string
  creator: string
  enabled: boolean
  groups: string[]
  id: number
}

// type SearchField = 'email' | 'name' | 'phone' | 'username'

// const searchField = ref<SearchField>('username')
// const searchKeyword = ref('')
const paginationConfig = ref({
  currentPage: 1,
  pageSize: 20,
  total: 0,
})

const systemUsers = ref<SystemUser[]>([
  {
    id: 9,
    name: 'shaohu',
    username: 'shaohu',
    enabled: true,
    email: 'jianqiang.ma@fit2cloud.com',
    phone: '',
    role: '普通用户',
    groups: ['默认用户组'],
    creator: 'admin',
    createdAt: '2026-07-10 13:50',
  },
  {
    id: 10,
    name: '白新',
    username: 'baixin',
    enabled: true,
    email: 'ma@fit2cloud.com',
    phone: '',
    role: '普通用户',
    groups: ['默认用户组'],
    creator: 'admin',
    createdAt: '2026-07-09 08:45',
  },
  {
    id: 11,
    name: '陈晨',
    username: 'chenchen',
    enabled: true,
    email: 'chenchen@fit2cloud.com',
    phone: '',
    role: '普通用户',
    groups: ['产品组'],
    creator: 'admin',
    createdAt: '2026-07-08 10:05',
  },
  {
    id: 12,
    name: '李明',
    username: 'liming',
    enabled: true,
    email: 'liming@fit2cloud.com',
    phone: '',
    role: '普通用户',
    groups: ['研发组'],
    creator: 'admin',
    createdAt: '2026-07-07 16:20',
  },
  {
    id: 1,
    name: 'test-w',
    username: 'test-w',
    enabled: true,
    email: 'zyy1@qq.com',
    phone: '',
    role: '工作空间管理员',
    groups: ['默认用户组'],
    creator: 'admin',
    createdAt: '2026-07-18 10:20',
  },
  {
    id: 2,
    name: 'Eira1',
    username: 'Eira1',
    enabled: true,
    email: '12345678901@163.com',
    phone: '12345678901',
    role: '普通用户',
    groups: ['产品组', '研发组'],
    creator: 'admin',
    createdAt: '2026-07-17 16:32',
  },
  {
    id: 3,
    name: '司马图南',
    username: 'simatunan',
    enabled: false,
    email: '198014730@qq.com',
    phone: '23198014730',
    role: '普通用户',
    groups: ['默认用户组'],
    creator: 'admin',
    createdAt: '2026-07-16 09:15',
  },
  {
    id: 4,
    name: '吕晓',
    username: 'lvxiao',
    enabled: true,
    email: '23198014730@qq.com',
    phone: '',
    role: 'usso-工作空间管理员',
    groups: ['运营组'],
    creator: 'admin',
    createdAt: '2026-07-15 14:06',
  },
  {
    id: 5,
    name: '涂晓',
    username: 'tuixao',
    enabled: true,
    email: '33198014730@qq.com',
    phone: '',
    role: '普通用户',
    groups: ['默认用户组'],
    creator: 'admin',
    createdAt: '2026-07-14 11:42',
  },
  {
    id: 6,
    name: '裴尔',
    username: 'peier',
    enabled: true,
    email: 'jianqiang.ma@fit2cloud.com',
    phone: '',
    role: '普通用户',
    groups: ['研发组'],
    creator: 'admin',
    createdAt: '2026-07-13 17:30',
  },
  {
    id: 7,
    name: '裴尔尔',
    username: 'peierer',
    enabled: true,
    email: 'testM0@qq.com',
    phone: '',
    role: '普通用户',
    groups: ['研发组'],
    creator: 'admin',
    createdAt: '2026-07-12 09:28',
  },
  {
    id: 8,
    name: '裴晓尔',
    username: 'peixiaoer',
    enabled: true,
    email: 'majiangqiang_lz@163.com',
    phone: '',
    role: '普通用户',
    groups: ['测试组'],
    creator: 'admin',
    createdAt: '2026-07-11 15:18',
  },
  {
    id: 9,
    name: 'shaohu',
    username: 'shaohu',
    enabled: true,
    email: 'jianqiang.ma@fit2cloud.com',
    phone: '',
    role: '普通用户',
    groups: ['默认用户组'],
    creator: 'admin',
    createdAt: '2026-07-10 13:50',
  },
  {
    id: 10,
    name: '白新',
    username: 'baixin',
    enabled: true,
    email: 'ma@fit2cloud.com',
    phone: '',
    role: '普通用户',
    groups: ['默认用户组'],
    creator: 'admin',
    createdAt: '2026-07-09 08:45',
  },
  {
    id: 11,
    name: '陈晨',
    username: 'chenchen',
    enabled: true,
    email: 'chenchen@fit2cloud.com',
    phone: '',
    role: '普通用户',
    groups: ['产品组'],
    creator: 'admin',
    createdAt: '2026-07-08 10:05',
  },
  {
    id: 12,
    name: '李明',
    username: 'liming',
    enabled: true,
    email: 'liming@fit2cloud.com',
    phone: '',
    role: '普通用户',
    groups: ['研发组'],
    creator: 'admin',
    createdAt: '2026-07-07 16:20',
  },
])
</script>

<template>
  <div class="system-identity-users px-6">
    <header class="flex-between py-4">
      <h1 class="text-lg font-medium">{{ route.meta.title }}</h1>
    </header>

    <MkTable
      v-model:pagination-config="paginationConfig"
      :data="systemUsers"
      max-height="516"
      row-key="id"
    >
      <el-table-column type="selection" width="40" />
      <el-table-column prop="name" label="姓名" show-overflow-tooltip />
      <el-table-column prop="username" label="用户名" show-overflow-tooltip />

      <el-table-column prop="creator" label="创建人" width="120" />
      <el-table-column prop="createdAt" label="创建时间" width="180" />
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }: { row: SystemUser }">
          <div class="flex items-center gap-1">
            <el-switch v-model="row.enabled" size="small" />
          </div>
        </template>
      </el-table-column>
    </MkTable>
  </div>
</template>

<style scoped lang="scss"></style>
