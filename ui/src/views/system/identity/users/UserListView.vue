<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import userManageApi from '@/api/admin/system/user-manage'
import type {
  ComplexSearchFieldOption,
  ComplexSearchValue,
  SystemUser,
  SystemUserQuery,
} from '@/types'
import { datetimeFormat } from '@/utils/time'

const route = useRoute()
const searchField = ref('username')
const searchKeyword = ref<ComplexSearchValue>()
const searchFields: ComplexSearchFieldOption[] = [
  { label: '用户名', value: 'username' },
  { label: '姓名', value: 'nick_name' },
  { label: '邮箱', value: 'email' },
  {
    label: '状态',
    value: 'is_active',
    type: 'select',
    options: [
      { label: '启用', value: true },
      { label: '禁用', value: false },
    ],
  },
]
const paginationConfig = ref({
  currentPage: 1,
  pageSize: 20,
  total: 0,
})
const systemUsersData = ref<SystemUser[]>([])
const systemUsersLoading = ref(false)

function getSystemUserQuery(): SystemUserQuery | undefined {
  if (searchKeyword.value === '' || searchKeyword.value === undefined) return undefined

  return { [searchField.value]: searchKeyword.value }
}

function loadSystemUsers() {
  systemUsersLoading.value = true
  userManageApi
    .getUserManagePage(paginationConfig.value, getSystemUserQuery())
    .then((pageData) => {
      systemUsersData.value = pageData.records
      paginationConfig.value = {
        currentPage: pageData.current,
        pageSize: pageData.size,
        total: pageData.total,
      }
    })
    .finally(() => {
      systemUsersLoading.value = false
    })
}

function handleSearchChange() {
  paginationConfig.value.currentPage = 1
  loadSystemUsers()
}

function handlePageSizeChange() {
  paginationConfig.value.currentPage = 1
  loadSystemUsers()
}

onMounted(() => loadSystemUsers())
</script>

<template>
  <div class="system-identity-users px-6">
    <header class="flex-between py-4">
      <h4>{{ route.meta.title }}</h4>
      <MkComplexSearch
        v-model="searchKeyword"
        v-model:field="searchField"
        :fields="searchFields"
        @change="handleSearchChange"
      />
    </header>

    <MkTable
      v-model:pagination-config="paginationConfig"
      :data="systemUsersData"
      v-loading="systemUsersLoading"
      max-height="516"
      row-key="id"
      @current-change="loadSystemUsers"
      @size-change="handlePageSizeChange"
    >
      <el-table-column type="selection" width="40" />
      <el-table-column prop="nick_name" label="姓名" show-overflow-tooltip />
      <el-table-column prop="username" label="用户名" show-overflow-tooltip />

      <el-table-column prop="creator" label="创建人" width="120" />
      <el-table-column label="创建时间" width="180">
        <template #default="{ row }: { row: SystemUser }">
          {{ datetimeFormat(row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }: { row: SystemUser }">
          <div class="flex items-center gap-1">
            <el-switch v-model="row.is_active" size="small" />
          </div>
        </template>
      </el-table-column>
    </MkTable>
  </div>
</template>

<style scoped lang="scss"></style>
