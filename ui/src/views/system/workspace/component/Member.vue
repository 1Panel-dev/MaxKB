<template>
  <div class="flex-between mb-16">
    <el-button
      type="primary"
      @click="handleAdd"
      v-hasPermission="
        new ComplexPermission(
          [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE.getWorkspaceRole],
          [PermissionConst.WORKSPACE_ADD_MEMBER, PermissionConst.WORKSPACE_WORKSPACE_ADD_MEMBER.getWorkspacePermissionWorkspaceManageRole],
          [],
            'OR',)"
    >
      {{ $t('views.role.member.add') }}
    </el-button>
    <div class="flex complex-search">
      <el-select class="complex-search__left" v-model="searchType" style="width: 120px">
        <el-option :label="$t('views.login.loginForm.username.label')" value="username"/>
        <el-option :label="$t('views.userManage.userForm.nick_name.label')" value="nick_name"/>
      </el-select>
      <el-input
        v-if="searchType === 'username'"
        v-model="searchForm.username"
        @change="getList"
        :placeholder="$t('common.inputPlaceholder')"
        style="width: 220px"
        clearable
      />
      <el-input
        v-else-if="searchType === 'nick_name'"
        v-model="searchForm.nick_name"
        @change="getList"
        :placeholder="$t('common.inputPlaceholder')"
        style="width: 220px"
        clearable/>
    </div>
  </div>
  <app-table
    :data="tableData"
    :pagination-config="paginationConfig"
    @sizeChange="handleSizeChange"
    @changePage="getList"
    v-loading="loading"
    class="member-table"
    :span-method="objectSpanMethod"
    :maxTableHeight="320"
  >
    <el-table-column prop="nick_name" :label="$t('views.userManage.userForm.nick_name.label')"/>
    <el-table-column prop="username" :label="$t('views.login.loginForm.username.label')"/>
    <el-table-column prop="role_name" :label="$t('views.role.member.role')"/>
    <el-table-column :label="$t('common.operation')" width="100" fixed="right">
      <template #default="{ row }">
        <el-tooltip
          effect="dark"
          :content="`${$t('views.role.member.delete.button')}`"
          placement="top"
        >
          <el-button
            type="primary"
            text
            @click.stop="handleDelete(row)"
            v-hasPermission="
              new ComplexPermission(
              [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE.getWorkspaceRole],
              [PermissionConst.WORKSPACE_REMOVE_MEMBER, PermissionConst.WORKSPACE_WORKSPACE_REMOVE_MEMBER.getWorkspacePermissionWorkspaceManageRole],
              [],
                'OR',)"
          >
            <AppIcon iconName="app-delete-users"></AppIcon>
          </el-button>
        </el-tooltip>
      </template>
    </el-table-column>
  </app-table>
  <AddMemberDrawer
    ref="addMemberDrawerRef"
    :currentWorkspace="props.currentWorkspace"
    @refresh="getList"
  />
</template>

<script setup lang="ts">
import {onMounted, ref, reactive, watch} from 'vue'
import {MsgSuccess, MsgConfirm} from '@/utils/message'
import {t} from '@/locales'
import AddMemberDrawer from './AddMemberDrawer.vue'
import type {WorkspaceMemberItem, WorkspaceItem} from '@/api/type/workspace'
import {PermissionConst, RoleConst} from '@/utils/permission/data'
import {ComplexPermission} from '@/utils/permission/type'
import {loadPermissionApi} from "@/utils/dynamics-api/permission-api.ts";


const props = defineProps<{
  currentWorkspace?: WorkspaceItem
}>()

const loading = ref(false)

const searchType = ref('username')
const searchForm = ref<Record<string, any>>({
  username: '',
  nick_name: '',
})
const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0,
})

const tableData = ref<WorkspaceMemberItem[]>([])

async function getList() {
  if (!props.currentWorkspace?.id) return
  try {
    const params = {
      [searchType.value]: searchForm.value[searchType.value],
    }
    const res = await loadPermissionApi('workspace').getWorkspaceMemberList(
      props.currentWorkspace?.id,
      paginationConfig,
      params,
      loading,
    )
    tableData.value = res.data.records
    paginationConfig.total = res.data.total
  } catch (error) {
    console.error(error)
  }
}

function handleSizeChange() {
  paginationConfig.current_page = 1
  getList()
}

onMounted(() => {
  getList()
})

watch(
  () => props.currentWorkspace?.id,
  () => {
    getList()
  },
)

const objectSpanMethod = ({row, column, rowIndex, columnIndex}: any) => {
  if (column.property === 'nick_name' || column.property === 'username') {
    const sameUserRows = tableData.value.filter(item => item.user_id === row.user_id);
    if (rowIndex === tableData.value.findIndex(item => item.user_id === row.user_id)) {
      return {
        rowspan: sameUserRows.length,
        colspan: 1
      };
    } else {
      return {
        rowspan: 0,
        colspan: 0
      };
    }
  }
};

const addMemberDrawerRef = ref<InstanceType<typeof AddMemberDrawer>>()

function handleAdd() {
  addMemberDrawerRef.value?.open()
}

function handleDelete(row: WorkspaceMemberItem) {
  MsgConfirm(`${t('views.workspace.member.delete.confirmTitle')}${row.nick_name} ?`, '', {
    confirmButtonText: t('common.confirm'),
    confirmButtonClass: 'danger',
  })
    .then(() => {
      loading.value = true
      loadPermissionApi('workspace').deleteWorkspaceMember(
        props.currentWorkspace?.id as string,
        row.user_relation_id,
        loading,
      ).then(() => {
        MsgSuccess(t('common.deleteSuccess'))
        getList()
      })
    })
    .catch(() => {
    })
}
</script>

<style lang="scss" scoped>
.member-table :deep(.el-table__cell):nth-child(2) {
  border-right: 1px solid var(--el-table-border-color);
}
</style>

