<template>
  <div class="h-full">
    <ContentContainer>
      <template #header>
        <div class="shared-header">
          <span class="title">{{ t('views.chatUser.title') }}</span>
          <el-icon size="12">
            <rightOutlined></rightOutlined>
          </el-icon>
          <span class="sub-title">{{ t('views.chatUser.title') }}</span>
        </div>
      </template>
      <el-card class="h-full">
        <div class="flex-between mb-16">
          <div>
            <el-button type="primary" @click="createUser()"
                       v-hasPermission="new ComplexPermission([RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE.getWorkspaceRole, RoleConst.USER.getWorkspaceRole,],
              [PermissionConst.WORKSPACE_CHAT_USER_CREATE.getWorkspacePermission],[],'OR')"
            >
              {{ t('views.userManage.createUser') }}
            </el-button>
            <el-button @click="syncUsers">
              {{ $t('views.chatUser.syncUsers') }}
            </el-button>
            <el-button :disabled="multipleSelection.length === 0" @click="setUserGroups"
                       v-hasPermission="new ComplexPermission([RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE.getWorkspaceRole, RoleConst.USER.getWorkspaceRole,],
                [PermissionConst.WORKSPACE_CHAT_USER_GROUP.getWorkspacePermission],[],'OR')"
            >
              {{ $t('views.chatUser.setUserGroups') }}
            </el-button>
            <el-button :disabled="multipleSelection.length === 0" @click="handleBatchDelete"
                       v-hasPermission="new ComplexPermission([RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE.getWorkspaceRole, RoleConst.USER.getWorkspaceRole,],
                [PermissionConst.WORKSPACE_CHAT_USER_DELETE.getWorkspacePermission],[],'OR')"
            >
              {{ $t('common.delete') }}
            </el-button>
          </div>
          <div class="flex-between complex-search">
            <el-select class="complex-search__left" v-model="search_type" style="width: 120px"
                       @change="search_type_change">
              <el-option :label="$t('views.login.loginForm.username.label')" value="username"/>
              <el-option :label="$t('views.userManage.userForm.nick_name.label')"
                         value="nick_name"/>
            </el-select>
            <el-input v-if="search_type === 'username'" v-model="search_form.username"
                      @change="getList"
                      style="width: 220px"
                      clearable/>
            <el-input v-if="search_type === 'nick_name'" v-model="search_form.nick_name"
                      @change="getList"
                      style="width: 220px" clearable/>
          </div>
        </div>
        <app-table class="mt-16" :data="userTableData" :pagination-config="paginationConfig"
                   @sizeChange="handleSizeChange" @changePage="getList" v-loading="loading"
                   @selection-change="handleSelectionChange" @sort-change="handleSortChange">
          <el-table-column type="selection" width="55"/>
          <el-table-column prop="nick_name"
                           :label="$t('views.userManage.userForm.nick_name.label')"/>
          <el-table-column prop="username" :label="$t('common.username')"/>
          <el-table-column prop="is_active" :label="$t('common.status.label')">
            <template #default="{ row }">
              <div v-if="row.is_active" class="flex align-center">
                <el-icon class="color-success mr-8" style="font-size: 16px">
                  <SuccessFilled/>
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

          <el-table-column prop="email" :label="$t('views.login.loginForm.email.label')"
                           show-overflow-tooltip>
            <template #default="{ row }">
              {{ row.email || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="phone" :label="$t('views.userManage.userForm.phone.label')">
            <template #default="{ row }">
              {{ row.phone || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="user_group_names" :label="$t('views.chatUser.group.title')"
                           min-width="100">
            <template #default="{ row }">
              <TagGroup :tags="row.user_group_names"/>
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
                <el-switch size="small" v-model="row.is_active"
                           :before-change="() => changeState(row)"/>
              </span>
              <el-divider direction="vertical"/>
              <span class="mr-8">
                <el-button type="primary" text @click.stop="editUser(row)"
                           :title="$t('common.edit')"
                           v-hasPermission="new ComplexPermission([RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE.getWorkspaceRole, RoleConst.USER.getWorkspaceRole,],
                    [PermissionConst.WORKSPACE_CHAT_USER_EDIT.getWorkspacePermission],[],'OR')"
                >
                  <el-icon>
                    <EditPen/>
                  </el-icon>
                </el-button>
              </span>

              <span class="mr-8">
                <el-button type="primary" text @click.stop="editPwdUser(row)"
                           :title="$t('views.userManage.setting.updatePwd')"
                           v-hasPermission="new ComplexPermission([RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE.getWorkspaceRole, RoleConst.USER.getWorkspaceRole,],
                [PermissionConst.WORKSPACE_CHAT_USER_EDIT.getWorkspacePermission],[],'OR')"
                >
                  <el-icon>
                    <Lock/>
                  </el-icon>
                </el-button>
              </span>
              <span>
                <el-button :disabled="row.role === 'ADMIN'" type="primary" text
                           @click.stop="deleteUserManage(row)"
                           :title="$t('common.delete')"
                           v-hasPermission="new ComplexPermission([RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE.getWorkspaceRole, RoleConst.USER.getWorkspaceRole,],
                [PermissionConst.WORKSPACE_CHAT_USER_DELETE.getWorkspacePermission],[],'OR')"
                >
                  <el-icon>
                    <Delete/>
                  </el-icon>
                </el-button>
              </span>
            </template>
          </el-table-column>
        </app-table>
      </el-card>
    </ContentContainer>

    <UserDrawer :title="title" :optionLoading="optionLoading" :chatGroupList="chatGroupList"
                ref="UserDrawerRef"
                @refresh="refresh"/>
    <UserPwdDialog ref="UserPwdDialogRef" @refresh="refresh"/>
    <SetUserGroupsDialog :optionLoading="optionLoading" :chatGroupList="chatGroupList"
                         ref="setUserGroupsRef"
                         @refresh="refresh"/>
    <SyncUsersDialog ref="syncUsersDialogRef" @refresh="refresh"/>
  </div>
</template>

<script lang="ts" setup>
import {onMounted, ref, reactive} from 'vue'
import UserDrawer from './component/UserDrawer.vue'
import UserPwdDialog from './component/UserPwdDialog.vue'
import SetUserGroupsDialog from './component/SetUserGroupsDialog.vue'
import SyncUsersDialog from './component/SyncUsersDialog.vue'
import userManageApi from '@/api/system/chat-user'
import {datetimeFormat} from '@/utils/time'
import {MsgSuccess, MsgConfirm} from '@/utils/message'
import {t} from '@/locales'
import iconMap from '@/components/app-icon/icons/common'
import type {ChatUserItem} from '@/api/type/systemChatUser'
import SystemGroupApi from '@/api/system/user-group'
import type {ListItem} from '@/api/type/common'
import {PermissionConst, RoleConst} from '@/utils/permission/data'
import {ComplexPermission} from '@/utils/permission/type'

const rightOutlined = iconMap['right-outlined'].iconReader()

const search_type = ref('name')
const search_form = ref<{
  username: string,
  nick_name?: string,
}>({
  username: '',
  nick_name: '',
})
const search_type_change = () => {
  search_form.value = {username: '', nick_name: ''}
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
  const params = {
    [search_type.value]: search_form.value[search_type.value as keyof typeof search_form.value],
  }
  return userManageApi
    .getUserManage(paginationConfig, params, loading)
    .then((res) => {
      userTableData.value = res.data.records
      paginationConfig.total = res.data.total
    })
}

const orderBy = ref<string>('')

function handleSortChange({prop, order}: { prop: string; order: string }) {
  orderBy.value = order === 'ascending' ? prop : `-${prop}`
  getList()
}

function handleSizeChange() {
  paginationConfig.current_page = 1
  getList()
}

function changeState(row: ChatUserItem) {
  const obj = {
    ...row,
    is_active: !row.is_active,
  }
  const str = obj.is_active ? t('common.status.enableSuccess') : t('common.status.disableSuccess')
  userManageApi
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
  MsgConfirm(
    `${t('views.userManage.delete.confirmTitle')}${row.nick_name} ?`,
    '',
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
    .catch(() => {
    })
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
    const res = await SystemGroupApi.getUserGroup(optionLoading)
    chatGroupList.value = res.data
  } catch (e) {
    console.error(e)
  }
}

function handleBatchDelete() {
  MsgConfirm(
    t('views.chatUser.batchDeleteUser', {count: multipleSelection.value.length}),
    '',
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      userManageApi.batchDelete(multipleSelection.value.map(item => (item.id)), loading).then(async () => {
        MsgSuccess(t('common.deleteSuccess'))
        await getList()
      })
    })
    .catch(() => {
    })
}

const setUserGroupsRef = ref<InstanceType<typeof SetUserGroupsDialog>>()

function setUserGroups() {
  setUserGroupsRef.value?.open(multipleSelection.value.map(item => (item.id)))
}

const syncUsersDialogRef = ref<InstanceType<typeof SyncUsersDialog>>()

function syncUsers() {
  syncUsersDialogRef.value?.open()
}
</script>

<style lang="scss" scoped>
.shared-header {
  color: #646a73;
  font-weight: 400;
  font-size: 14px;
  line-height: 22px;
  display: flex;
  align-items: center;

  :deep(.el-icon i) {
    height: 12px;
  }

  .sub-title {
    color: #1f2329;
  }
}

.content-container {
  height: 100%;
  display: flex;
  flex-direction: column;

  :deep(.content-container__main) {
    flex: 1;
  }
}
</style>
