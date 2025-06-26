<template>
  <div class="flex-between mb-16">
    <el-button
      type="primary"
      @click="handleAdd"
      v-hasPermission="
        new ComplexPermission(
          [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
          [PermissionConst.WORKSPACE_ADD_MEMBER, PermissionConst.WORKSPACE_WORKSPACE_ADD_MEMBER],
          [],
            'OR',)"
    >
      {{ $t('views.role.member.add') }}
    </el-button>
    <div class="flex complex-search">
      <el-select class="complex-search__left" v-model="searchType" style="width: 120px">
        <el-option :label="$t('views.login.loginForm.username.label')" value="username" />
      </el-select>
      <el-input
        v-if="searchType === 'username'"
        v-model="searchForm.username"
        @change="getList"
        :placeholder="$t('common.inputPlaceholder')"
        style="width: 220px"
        clearable
      />
    </div>
  </div>
  <app-table
    :data="tableData"
    :pagination-config="paginationConfig"
    @sizeChange="handleSizeChange"
    @changePage="getList"
    v-loading="loading"
  >
    <el-table-column prop="nick_name" :label="$t('views.userManage.userForm.nick_name.label')" />
    <el-table-column prop="username" :label="$t('views.login.loginForm.username.label')" />
    <el-table-column prop="role_name" :label="$t('views.role.member.role')" />
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
              [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
              [PermissionConst.WORKSPACE_REMOVE_MEMBER, PermissionConst.WORKSPACE_WORKSPACE_REMOVE_MEMBER],
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
import { onMounted, ref, reactive, watch } from 'vue'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { t } from '@/locales'
import AddMemberDrawer from './AddMemberDrawer.vue'
import WorkspaceApi from '@/api/workspace/workspace'
import type { WorkspaceMemberItem, WorkspaceItem } from '@/api/type/workspace'
import { PermissionConst, RoleConst } from '@/utils/permission/data'
import { ComplexPermission } from '@/utils/permission/type'


const props = defineProps<{
  currentWorkspace?: WorkspaceItem
}>()

const loading = ref(false)

const searchType = ref('username')
const searchForm = ref<Record<string, any>>({
  username: '',
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
    const res = await WorkspaceApi.getWorkspaceMemberList(
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
      WorkspaceApi.deleteWorkspaceMember(
        props.currentWorkspace?.id as string,
        row.user_relation_id,
        loading,
      ).then(() => {
        MsgSuccess(t('common.deleteSuccess'))
        getList()
      })
    })
    .catch(() => {})
}
</script>
