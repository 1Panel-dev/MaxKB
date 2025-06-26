<template>
  <div>
    <div class="flex-between mb-16">
      <el-button
        type="primary"
        @click="handleAdd"
        v-hasPermission="
          new ComplexPermission(
            [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE.getWorkspaceRole],
            [PermissionConst.ROLE_ADD_MEMBER.getWorkspacePermission],
            [],
            'OR',
          )
        "
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
      class="mt-16"
      :data="tableData"
      :pagination-config="paginationConfig"
      @sizeChange="handleSizeChange"
      @changePage="getList"
      v-loading="loading"
    >
      <el-table-column prop="nick_name" :label="$t('views.userManage.userForm.nick_name.label')" />
      <el-table-column prop="username" :label="$t('views.login.loginForm.username.label')" />
      <el-table-column
        v-if="props.currentRole?.type !== RoleTypeEnum.ADMIN"
        prop="workspace_name"
        :label="$t('views.role.member.workspace')"
      />
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
                  [PermissionConst.ROLE_REMOVE_MEMBER.getWorkspacePermission],
                  [],
                  'OR',
                )
              "
            >
              <AppIcon iconName="app-delete-users"></AppIcon>
            </el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </app-table>
  </div>
  <AddMemberDrawer ref="addMemberDrawerRef" :currentRole="props.currentRole" @refresh="getList" />
</template>

<script setup lang="ts">
import { onMounted, ref, reactive, watch } from 'vue'
import type { RoleItem, RoleMemberItem } from '@/api/type/role'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { t } from '@/locales'
import AddMemberDrawer from './AddMemberDrawer.vue'
import { RoleTypeEnum } from '@/enums/system'
import { loadPermissionApi } from '@/utils/dynamics-api/permission-api'
import { PermissionConst, RoleConst } from '@/utils/permission/data'
import { ComplexPermission } from '@/utils/permission/type'
const props = defineProps<{
  currentRole?: RoleItem
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

const tableData = ref<RoleMemberItem[]>([])

async function getList() {
  try {
    const params = {
      [searchType.value]: searchForm.value[searchType.value],
    }
    const res = await loadPermissionApi('role').getRoleMemberList(
      props.currentRole?.id as string,
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
  () => props.currentRole?.id,
  () => {
    getList()
  },
)

const addMemberDrawerRef = ref<InstanceType<typeof AddMemberDrawer>>()

function handleAdd() {
  addMemberDrawerRef.value?.open()
}

function handleDelete(row: RoleMemberItem) {
  MsgConfirm(`${t('views.role.member.delete.confirmTitle')}${row.nick_name} ?`, '', {
    confirmButtonText: t('common.confirm'),
    confirmButtonClass: 'danger',
  })
    .then(() => {
      loading.value = true
      loadPermissionApi('role')
        .deleteRoleMember(props.currentRole?.id as string, row.user_relation_id, loading)
        .then(() => {
          MsgSuccess(t('common.deleteSuccess'))
          getList()
        })
    })
    .catch(() => {})
}
</script>
