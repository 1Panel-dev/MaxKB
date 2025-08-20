<template>
  <div class="chat-user p-24">
    <el-breadcrumb separator-icon="ArrowRight" class="mb-16">
      <el-breadcrumb-item>{{ t('views.chatUser.title') }}</el-breadcrumb-item>
      <el-breadcrumb-item>
        <h5 class="ml-4 color-text-primary">{{ t('views.chatUser.title') }}</h5>
      </el-breadcrumb-item>
    </el-breadcrumb>
    <el-card style="height: calc(var(--app-main-height) + 10px)">
      <div class="flex-between mb-16">
        <div>
          <el-button
            type="primary"
            @click="createUser()"
            v-hasPermission="
              new ComplexPermission(
                [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
                [PermissionConst.CHAT_USER_CREATE, PermissionConst.WORKSPACE_CHAT_USER_CREATE],
                [],
                'OR',
              )
            "
          >
            {{ t('views.userManage.createUser') }}
          </el-button>
          <el-button
            @click="syncUsers"
            v-hasPermission="
              new ComplexPermission([RoleConst.ADMIN], [PermissionConst.CHAT_USER_SYNC], [], 'OR')
            "
          >
            {{ $t('views.chatUser.syncUsers') }}
          </el-button>
          <el-button
            :disabled="multipleSelection.length === 0"
            @click="setUserGroups"
            v-hasPermission="
              new ComplexPermission(
                [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
                [PermissionConst.CHAT_USER_GROUP, PermissionConst.WORKSPACE_CHAT_USER_GROUP],
                [],
                'OR',
              )
            "
          >
            {{ $t('views.chatUser.setUserGroups') }}
          </el-button>
          <el-button
            :disabled="multipleSelection.length === 0"
            @click="handleBatchDelete"
            v-hasPermission="
              new ComplexPermission(
                [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
                [PermissionConst.WORKSPACE_CHAT_USER_DELETE, PermissionConst.CHAT_USER_DELETE],
                [],
                'OR',
              )
            "
          >
            {{ $t('common.delete') }}
          </el-button>
        </div>
        <div class="flex-between complex-search">
          <el-select
            class="complex-search__left"
            v-model="search_type"
            style="width: 120px"
            @change="search_type_change"
          >
            <el-option :label="$t('views.login.loginForm.username.label')" value="username" />
            <el-option :label="$t('views.userManage.userForm.nick_name.label')" value="nick_name" />
            <el-option :label="$t('common.status.label')" value="is_active" />
            <el-option :label="$t('views.userManage.source.label')" value="source" />
          </el-select>
          <el-input
            v-if="search_type === 'username'"
            v-model="search_form.username"
            @change="getList"
            style="width: 220px"
            clearable
          />
          <el-input
            v-if="search_type === 'nick_name'"
            v-model="search_form.nick_name"
            @change="getList"
            style="width: 220px"
            clearable
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
        @selection-change="handleSelectionChange"
        @sort-change="handleSortChange"
        :maxTableHeight="270"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column
          prop="nick_name"
          :label="$t('views.userManage.userForm.nick_name.label')"
          min-width="180"
          show-overflow-tooltip
        />
        <el-table-column
          prop="username"
          :label="$t('common.username')"
          min-width="180"
          show-overflow-tooltip
        />
        <el-table-column prop="is_active" :label="$t('common.status.label')" width="100">
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
          :label="$t('views.userManage.userForm.phone.label')"
          width="120"
        >
          <template #default="{ row }">
            {{ row.phone || '-' }}
          </template>
        </el-table-column>
        <el-table-column
          prop="user_group_names"
          :label="$t('views.chatUser.group.title')"
          min-width="150"
        >
          <template #default="{ row }">
            <TagGroup :tags="row.user_group_names" />
          </template>
        </el-table-column>
        <el-table-column prop="source" :label="$t('views.userManage.source.label')">
          <template #default="{ row }">
            {{
              row.source === 'LOCAL'
                ? $t('views.userManage.source.localCreate')
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
                size="small"
                v-model="row.is_active"
                :before-change="() => changeState(row)"
                v-if="
                  hasPermission(
                    new ComplexPermission(
                      [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
                      [PermissionConst.CHAT_USER_EDIT, PermissionConst.WORKSPACE_CHAT_USER_EDIT],
                      [],
                      'OR',
                    ),
                    'OR',
                  )
                "
              />
            </span>
            <el-divider direction="vertical" />
            <span class="mr-8">
              <el-button
                type="primary"
                text
                @click.stop="editUser(row)"
                :title="$t('common.edit')"
                v-if="
                  hasPermission(
                    new ComplexPermission(
                      [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
                      [PermissionConst.CHAT_USER_EDIT, PermissionConst.WORKSPACE_CHAT_USER_EDIT],
                      [],
                      'OR',
                    ),
                    'OR',
                  )
                "
              >
                <AppIcon iconName="app-edit"></AppIcon>
              </el-button>
            </span>

            <span class="mr-8">
              <el-button
                type="primary"
                text
                @click.stop="editPwdUser(row)"
                :title="$t('views.userManage.setting.updatePwd')"
                v-if="
                  hasPermission(
                    new ComplexPermission(
                      [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
                      [PermissionConst.CHAT_USER_EDIT, PermissionConst.WORKSPACE_CHAT_USER_EDIT],
                      [],
                      'OR',
                    ),
                    'OR',
                  )
                "
              >
                <AppIcon iconName="app-key"></AppIcon>
              </el-button>
            </span>
            <span>
              <el-button
                :disabled="row.role === 'ADMIN'"
                type="primary"
                text
                @click.stop="deleteUserManage(row)"
                :title="$t('common.delete')"
                v-if="
                  hasPermission(
                    new ComplexPermission(
                      [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
                      [
                        PermissionConst.CHAT_USER_DELETE,
                        PermissionConst.WORKSPACE_CHAT_USER_DELETE,
                      ],
                      [],
                      'OR',
                    ),
                    'OR',
                  )
                "
              >
                <AppIcon iconName="app-delete"></AppIcon>
              </el-button>
            </span>
          </template>
        </el-table-column>
      </app-table>
    </el-card>

    <UserDrawer
      :title="title"
      :optionLoading="optionLoading"
      :chatGroupList="chatGroupList"
      ref="UserDrawerRef"
      @refresh="refresh"
    />
    <UserPwdDialog ref="UserPwdDialogRef" @refresh="refresh" />
    <SetUserGroupsDialog
      :optionLoading="optionLoading"
      :chatGroupList="chatGroupList"
      ref="setUserGroupsRef"
      @refresh="refresh"
    />
    <SyncUsersDialog ref="syncUsersDialogRef" @refresh="refresh" />
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive } from 'vue'
import UserDrawer from './component/UserDrawer.vue'
import UserPwdDialog from './component/UserPwdDialog.vue'
import SetUserGroupsDialog from './component/SetUserGroupsDialog.vue'
import SyncUsersDialog from './component/SyncUsersDialog.vue'
import userManageApi from '@/api/system/chat-user'
import { datetimeFormat } from '@/utils/time'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { t } from '@/locales'
import type { ChatUserItem } from '@/api/type/systemChatUser'
import SystemGroupApi from '@/api/system/user-group'
import type { ListItem } from '@/api/type/common'
import { PermissionConst, RoleConst } from '@/utils/permission/data'
import { ComplexPermission } from '@/utils/permission/type'
import { hasPermission } from '@/utils/permission'
import { loadPermissionApi } from '@/utils/dynamics-api/permission-api.ts'

const search_type = ref('username')
const search_form = ref<{
  username: string
  nick_name?: string
  source?: string
  is_active?: boolean | null
}>({
  username: '',
  nick_name: '',
  source: '',
  is_active: null,
})
const search_type_change = () => {
  search_form.value = { username: '', nick_name: '', source: '', is_active: null }
}

const loading = ref(false)

const multipleSelection = ref<any[]>([])

function handleSelectionChange(val: any[]) {
  multipleSelection.value = val
}

const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0,
})

const userTableData = ref<ChatUserItem[]>([])

function getList() {
  const params: any = {}
  const searchValue = search_form.value[search_type.value as keyof typeof search_form.value]
  if (searchValue !== undefined && searchValue !== null && searchValue !== '') {
    params[search_type.value] = searchValue
  }
  return loadPermissionApi('chatUser')
    .getUserManage(paginationConfig, params, loading)
    .then((res: any) => {
      userTableData.value = res.data.records
      paginationConfig.total = res.data.total
    })
}

const orderBy = ref<string>('')

function handleSortChange({ prop, order }: { prop: string; order: string }) {
  orderBy.value = order === 'ascending' ? prop : `-${prop}`
  getList()
}

function handleSizeChange() {
  paginationConfig.current_page = 1
  getList()
}

async function changeState(row: ChatUserItem) {
  const obj = {
    ...row,
    is_active: !row.is_active,
  }
  const str = obj.is_active ? t('common.status.enableSuccess') : t('common.status.disableSuccess')
  await loadPermissionApi('chatUser')
    .putUserManage(row.id, obj, loading)
    .then(() => {
      getList()
      MsgSuccess(str)
      return true
    })
    .catch(() => {
      return false
    })
}

const title = ref('')
const UserDrawerRef = ref()

function editUser(row: ChatUserItem) {
  title.value = t('views.userManage.editUser')
  UserDrawerRef.value.open(row)
}

function createUser() {
  title.value = t('views.userManage.createUser')
  UserDrawerRef.value.open()
}

function deleteUserManage(row: ChatUserItem) {
  MsgConfirm(`${t('views.userManage.delete.confirmTitle')}${row.nick_name} ?`, '', {
    confirmButtonText: t('common.confirm'),
    confirmButtonClass: 'danger',
  })
    .then(() => {
      loading.value = true
      loadPermissionApi('chatUser')
        .delUserManage(row.id, loading)
        .then(() => {
          MsgSuccess(t('common.deleteSuccess'))
          getList()
        })
    })
    .catch(() => {})
}

const UserPwdDialogRef = ref()

function editPwdUser(row: ChatUserItem) {
  UserPwdDialogRef.value.open(row)
}

function refresh() {
  getList()
}

onMounted(() => {
  getChatGroupList()
  getList()
})

const optionLoading = ref(false)
const chatGroupList = ref<ListItem[]>([])

async function getChatGroupList() {
  try {
    const res = await loadPermissionApi('userGroup').getUserGroup(optionLoading)
    chatGroupList.value = res.data
  } catch (e) {
    console.error(e)
  }
}

function handleBatchDelete() {
  MsgConfirm(t('views.chatUser.batchDeleteUser', { count: multipleSelection.value.length }), '', {
    confirmButtonText: t('common.confirm'),
    confirmButtonClass: 'danger',
  })
    .then(() => {
      loadPermissionApi('chatUser')
        .batchDelete(
          multipleSelection.value.map((item) => item.id),
          loading,
        )
        .then(async () => {
          MsgSuccess(t('common.deleteSuccess'))
          await getList()
        })
    })
    .catch(() => {})
}

const setUserGroupsRef = ref<InstanceType<typeof SetUserGroupsDialog>>()

function setUserGroups() {
  setUserGroupsRef.value?.open(multipleSelection.value.map((item) => item.id))
}

const syncUsersDialogRef = ref<InstanceType<typeof SyncUsersDialog>>()

function syncUsers() {
  syncUsersDialogRef.value?.open()
}
</script>

<style lang="scss" scoped></style>
