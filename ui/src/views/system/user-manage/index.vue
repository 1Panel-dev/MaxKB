<template>
  <div class="p-16-24">
    <h2 class="mb-16">{{ $t('views.userManage.title') }}</h2>
    <el-card class="main-calc-height">
      <div class="flex-between mb-16">
        <el-button
          type="primary"
          @click="createUser"
          v-hasPermission="[RoleConst.ADMIN, PermissionConst.USER_CREATE]"
          >{{ $t('views.userManage.createUser') }}
        </el-button>
        <div class="flex-between complex-search">
          <el-select
            class="complex-search__left"
            v-model="search_type"
            style="width: 120px"
            @change="search_type_change"
          >
            <el-option :label="$t('views.login.loginForm.username.label')" value="username" />
            <el-option :label="$t('views.userManage.userForm.nick_name.label')" value="nick_name" />
            <el-option :label="$t('views.login.loginForm.email.label')" value="email" />
            <el-option :label="$t('common.status.label')" value="is_active" />
            <el-option
              v-if="user.isEE() || user.isPE()"
              :label="$t('views.userManage.source.label')"
              value="source"
            />
          </el-select>
          <el-input
            v-if="search_type === 'username'"
            v-model="search_form.username"
            @change="getList"
            style="width: 220px"
            clearable
            :placeholder="$t('common.inputPlaceholder')"
          />
          <el-input
            v-else-if="search_type === 'nick_name'"
            v-model="search_form.nick_name"
            @change="getList"
            style="width: 220px"
            clearable
            :placeholder="$t('common.inputPlaceholder')"
          />
          <el-input
            v-else-if="search_type === 'email'"
            v-model="search_form.email"
            @change="getList"
            style="width: 220px"
            clearable
            :placeholder="$t('common.inputPlaceholder')"
          />
          <el-select
            v-else-if="search_type === 'is_active'"
            v-model="search_form.is_active"
            @change="getList"
            clearable
            style="width: 220px"
          >
            <el-option :label="$t('common.status.enabled')" :value="true" />
            <el-option :label="$t('common.status.disabled')" :value="false" />
          </el-select>
          <el-select
            v-else-if="search_type === 'source'"
            v-model="search_form.source"
            @change="getList"
            style="width: 220px"
            clearable
            :placeholder="$t('common.inputPlaceholder')"
          >
            <el-option :label="$t('views.userManage.source.local')" value="LOCAL" />
            <el-option label="CAS" value="CAS" />
            <el-option label="LDAP" value="LDAP" />
            <el-option label="OIDC" value="OIDC" />
            <el-option label="OAuth2" value="OAuth2" />
            <el-option :label="$t('views.userManage.source.wecom')" value="wecom" />
            <el-option :label="$t('views.userManage.source.lark')" value="lark" />
            <el-option :label="$t('views.userManage.source.dingtalk')" value="dingtalk" />
          </el-select>
        </div>
      </div>
      <app-table
        class="mt-16"
        :data="userTableData"
        :pagination-config="paginationConfig"
        @sizeChange="handleSizeChange"
        @changePage="getList"
        v-loading="loading"
        :maxTableHeight="280"
      >
        <el-table-column
          prop="nick_name"
          :label="$t('views.userManage.userForm.nick_name.label')"
          min-width="180"
          show-overflow-tooltip
        />
        <el-table-column
          prop="username"
          min-width="180"
          show-overflow-tooltip
          :label="$t('views.login.loginForm.username.label')"
        />
        <el-table-column width="100" prop="is_active" :label="$t('common.status.label')">
          <template #default="{ row }">
            <div v-if="row.is_active" class="flex align-center">
              <el-icon class="color-success mr-8" style="font-size: 16px">
                <SuccessFilled />
              </el-icon>
              <span class="color-secondary">
                {{ $t('common.status.enabled') }}
              </span>
            </div>
            <div v-else class="flex align-center">
              <AppIcon iconName="app-disabled" class="color-secondary mr-8"></AppIcon>
              <span class="color-secondary">
                {{ $t('common.status.disabled') }}
              </span>
            </div>
          </template>
        </el-table-column>

        <el-table-column
          prop="email"
          :label="$t('views.login.loginForm.email.label')"
          show-overflow-tooltip
          min-width="180"
        >
          <template #default="{ row }">
            {{ row.email || '-' }}
          </template>
        </el-table-column>
        <el-table-column
          prop="phone"
          width="120"
          :label="$t('views.userManage.userForm.phone.label')"
        >
          <template #default="{ row }">
            {{ row.phone || '-' }}
          </template>
        </el-table-column>
        <el-table-column
          prop="role_name"
          :label="$t('views.role.member.role')"
          width="210"
          v-if="user.isEE() || user.isPE()"
        >
          <template #default="{ row }">
            <el-popover :width="400">
              <template #reference>
                <TagGroup
                  class="cursor"
                  style="width: fit-content"
                  :tags="row.role_name"
                  tooltipDisabled
                />
              </template>
              <template #default>
                <el-table :data="row.role_workspace">
                  <el-table-column prop="role" :label="$t('views.role.member.role')">
                  </el-table-column>
                  <el-table-column prop="workspace" :label="$t('views.workspace.title')">
                  </el-table-column>
                </el-table>
              </template>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column prop="source" width="100" :label="$t('views.userManage.source.label')">
          <template #default="{ row }">
            {{
              row.source === 'LOCAL'
                ? $t('views.userManage.source.local')
                : row.source === 'wecom'
                  ? $t('views.userManage.source.wecom')
                  : row.source === 'lark'
                    ? $t('views.userManage.source.lark')
                    : row.source === 'dingtalk'
                      ? $t('views.userManage.source.dingtalk')
                      : row.source === 'OAUTH2' || row.source === 'OAuth2'
                        ? 'OAuth2'
                        : row.source
            }}
          </template>
        </el-table-column>

        <el-table-column :label="$t('common.createTime')" width="180">
          <template #default="{ row }">
            {{ datetimeFormat(row.create_time) }}
          </template>
        </el-table-column>

        <el-table-column :label="$t('common.operation')" width="160" align="left" fixed="right">
          <template #default="{ row }">
            <span @click.stop>
              <el-switch
                :disabled="row.role === 'ADMIN' || row.id === user.userInfo?.id"
                size="small"
                v-model="row.is_active"
                :before-change="() => changeState(row)"
                v-if="hasPermission([RoleConst.ADMIN, PermissionConst.USER_EDIT], 'OR')"
              />
            </span>
            <el-divider direction="vertical" />
            <el-tooltip effect="dark" :content="$t('common.edit')" placement="top">
              <span class="mr-8">
                <el-button
                  type="primary"
                  text
                  @click.stop="editUser(row)"
                  :title="$t('common.edit')"
                  v-if="hasPermission([RoleConst.ADMIN, PermissionConst.USER_EDIT], 'OR')"
                >
                  <AppIcon iconName="app-edit"></AppIcon>
                </el-button>
              </span>
            </el-tooltip>
            <el-tooltip
              effect="dark"
              :content="$t('views.userManage.setting.updatePwd')"
              placement="top"
            >
              <span class="mr-8">
                <el-button
                  type="primary"
                  text
                  @click.stop="editPwdUser(row)"
                  :title="$t('views.userManage.setting.updatePwd')"
                  v-if="hasPermission([RoleConst.ADMIN, PermissionConst.USER_EDIT], 'OR')"
                >
                  <AppIcon iconName="app-key"></AppIcon>
                </el-button>
              </span>
            </el-tooltip>
            <el-tooltip effect="dark" :content="$t('common.delete')" placement="top">
              <el-button
                :disabled="row.role === 'ADMIN' || row.id === user.userInfo?.id"
                type="primary"
                text
                @click.stop="deleteUserManage(row)"
                :title="$t('common.delete')"
                v-if="hasPermission([RoleConst.ADMIN, PermissionConst.USER_DELETE], 'OR')"
              >
                <AppIcon iconName="app-delete"></AppIcon>
              </el-button>
            </el-tooltip>
          </template>
        </el-table-column>
      </app-table>
    </el-card>
    <UserDrawer :title="title" ref="UserDrawerRef" @refresh="refresh" />
    <UserPwdDialog ref="UserPwdDialogRef" @refresh="refresh" />
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, watch } from 'vue'
import UserDrawer from './component/UserDrawer.vue'
import UserPwdDialog from './component/UserPwdDialog.vue'
import userManageApi from '@/api/system/user-manage'
import { datetimeFormat } from '@/utils/time'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { t } from '@/locales'
import { ValidCount, ValidType } from '@/enums/common.ts'
import useStore from '@/stores'
import { PermissionConst, RoleConst } from '@/utils/permission/data'
import { hasPermission } from '@/utils/permission/index'

const { user, common } = useStore()
const search_type = ref('username')
const search_form = ref<{
  username: string
  nick_name?: string
  email?: string
  is_active?: boolean | null
  source?: string | null
}>({
  username: '',
  nick_name: '',
  email: '',
  is_active: null,
  source: '',
})

const UserDrawerRef = ref()
const UserPwdDialogRef = ref()
const loading = ref(false)

const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0,
})

const userTableData = ref<any[]>([])

const search_type_change = () => {
  search_form.value = { username: '', nick_name: '', email: '', is_active: null }
}

function handleSizeChange() {
  paginationConfig.current_page = 1
  getList()
}

function getList() {
  const params: any = {}
  const searchValue = search_form.value[search_type.value as keyof typeof search_form.value]
  if (searchValue !== undefined && searchValue !== null && searchValue !== '') {
    params[search_type.value] = searchValue
  }
  return userManageApi.getUserManage(paginationConfig, params, loading).then((res) => {
    userTableData.value = res.data.records.map((item: any) => ({
      ...item,
      role_workspace: Object.entries(item.role_workspace ?? {}).map(([role, workspaces]) => ({
        role,
        workspace:
          (workspaces as string[])?.[0] === 'None' ? '-' : (workspaces as string[])?.join(', '),
      })),
    }))
    paginationConfig.total = res.data.total
  })
}

async function changeState(row: any) {
  const obj = {
    is_active: !row.is_active,
  }
  const str = obj.is_active ? t('common.status.enableSuccess') : t('common.status.disableSuccess')
  await userManageApi
    .putUserManage(row.id, obj, loading)
    .then((res) => {
      getList()
      MsgSuccess(str)
      return true
    })
    .catch(() => {
      return false
    })
}

const title = ref('')

function editUser(row: any) {
  title.value = t('views.userManage.editUser')
  UserDrawerRef.value.open(row)
}

function createUser() {
  title.value = t('views.userManage.createUser')
  UserDrawerRef.value.open()
}

function deleteUserManage(row: any) {
  MsgConfirm(
    `${t('views.userManage.delete.confirmTitle')}${row.nick_name} ?`,
    t('views.userManage.delete.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      loading.value = true
      userManageApi.delUserManage(row.id, loading).then(() => {
        MsgSuccess(t('common.deleteSuccess'))
        getList()
      })
    })
    .catch(() => {})
}

function editPwdUser(row: any) {
  UserPwdDialogRef.value.open(row)
}

function refresh() {
  getList()
}

onMounted(() => {
  getList()
})
</script>

<style lang="scss" scoped></style>
