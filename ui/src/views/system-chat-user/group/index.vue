<template>
  <div class="group p-24">
    <el-breadcrumb separator-icon="ArrowRight" class="mb-16">
      <el-breadcrumb-item>{{ t('views.chatUser.title') }}</el-breadcrumb-item>
      <el-breadcrumb-item>
        <h5 class="ml-4 color-text-primary">{{ t('views.chatUser.group.title') }}</h5>
      </el-breadcrumb-item>
    </el-breadcrumb>
    <el-card style="--el-card-padding: 0">
      <div class="flex">
        <div class="user-left border-r">
          <div class="p-24 pb-0">
            <div class="flex-between mb-12">
              <h4 class="medium">{{ $t('views.chatUser.group.title') }}</h4>
              <el-tooltip
                effect="dark"
                :content="`${$t('common.create')}${$t('views.chatUser.group.title')}`"
                placement="top"
              >
                <el-button
                  type="primary"
                  text
                  @click="createOrUpdate()"
                  v-hasPermission="
                    new ComplexPermission(
                      [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
                      [
                        PermissionConst.WORKSPACE_USER_GROUP_CREATE,
                        PermissionConst.USER_GROUP_CREATE,
                      ],
                      [],
                      'OR',
                    )
                  "
                >
                  <AppIcon iconName="app-add-outlined"></AppIcon>
                </el-button>
              </el-tooltip>
            </div>

            <el-input
              v-model="filterText"
              :placeholder="$t('common.search')"
              prefix-icon="Search"
              clearable
              filterable
            />
          </div>

          <div class="list-height-left">
            <el-scrollbar v-loading="loading">
              <div class="p-8-16">
                <common-list
                  :data="filterList"
                  @click="clickUserGroup"
                  :default-active="current?.id"
                  @mouseenter="mouseenter"
                  @mouseleave="mouseId = ''"
                >
                  <template #default="{ row }">
                    <div class="flex-between">
                      <span class="ellipsis" :title="row.name">{{ i18n_name(row.name) }}</span>
                      <div @click.stop v-show="mouseId === row.id">
                        <el-dropdown
                          :teleported="false"
                          trigger="click"
                          v-if="editPermission() || dlePermission()"
                        >
                          <el-button text>
                            <AppIcon iconName="app-more"></AppIcon>
                          </el-button>
                          <template #dropdown>
                            <el-dropdown-menu style="min-width: 80px">
                              <el-dropdown-item
                                @click.stop="createOrUpdate(row)"
                                class="p-8"
                                v-if="editPermission()"
                              >
                                <AppIcon iconName="app-edit" class="color-secondary"></AppIcon>
                                {{ $t('common.rename') }}
                              </el-dropdown-item>
                              <el-dropdown-item
                                @click.stop="deleteGroup(row)"
                                class="border-t p-8"
                                v-if="dlePermission()"
                              >
                                <AppIcon iconName="app-delete" class="color-secondary"></AppIcon>
                                {{ $t('common.delete') }}
                              </el-dropdown-item>
                            </el-dropdown-menu>
                          </template>
                        </el-dropdown>
                      </div>
                    </div>
                  </template>
                  <template #empty>
                    <span></span>
                  </template>
                </common-list>
              </div>
            </el-scrollbar>
          </div>
        </div>

        <!-- 右边 -->
        <div class="user-right" v-loading="rightLoading">
          <div class="flex align-center">
            <h4 class="medium ellipsis" :title="current?.name">{{ i18n_name(current?.name as string) }}</h4>
            <el-divider direction="vertical" class="mr-8 ml-8" />
            <AppIcon
              iconName="app-workspace"
              style="font-size: 16px"
              class="color-input-placeholder"
            ></AppIcon>
            <span class="color-input-placeholder ml-4">
              {{ paginationConfig.total }}
            </span>
          </div>

          <div class="flex-between mb-16" style="margin-top: 20px">
            <div>
              <el-button
                type="primary"
                @click="createUser()"
                v-hasPermission="
                  new ComplexPermission(
                    [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
                    [
                      PermissionConst.WORKSPACE_USER_GROUP_ADD_MEMBER,
                      PermissionConst.USER_GROUP_ADD_MEMBER,
                    ],
                    [],
                    'OR',
                  )
                "
              >
                {{ t('views.role.member.add') }}
              </el-button>
              <el-button
                :disabled="multipleSelection.length === 0"
                @click="handleDeleteUser()"
                v-hasPermission="
                  new ComplexPermission(
                    [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
                    [
                      PermissionConst.WORKSPACE_USER_GROUP_REMOVE_MEMBER,
                      PermissionConst.USER_GROUP_REMOVE_MEMBER,
                    ],
                    [],
                    'OR',
                  )
                "
              >
                {{ $t('common.remove') }}
              </el-button>
            </div>
            <div class="flex-between complex-search">
              <el-select class="complex-search__left" v-model="searchType" style="width: 120px">
                <el-option :label="$t('views.login.loginForm.username.label')" value="username" />
                <el-option
                  :label="$t('views.userManage.userForm.nick_name.label')"
                  value="nick_name"
                />
                <el-option :label="$t('views.userManage.source.label')" value="source" />
              </el-select>
              <el-input
                v-if="searchType === 'username'"
                v-model="searchForm.username"
                @change="getList"
                :placeholder="$t('common.searchBar.placeholder')"
                style="width: 220px"
                clearable
              />
              <el-input
                v-else-if="searchType === 'nick_name'"
                v-model="searchForm.nick_name"
                @change="getList"
                :placeholder="$t('common.searchBar.placeholder')"
                style="width: 220px"
                clearable
              />
              <el-select
                v-else-if="searchType === 'source'"
                v-model="searchForm.source"
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
            :data="tableData"
            :pagination-config="paginationConfig"
            @sizeChange="handleSizeChange"
            @changePage="getList"
            @selection-change="handleSelectionChange"
            :maxTableHeight="330"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column
              prop="nick_name"
              :label="$t('views.userManage.userForm.nick_name.label')"
              show-overflow-tooltip
            />
            <el-table-column prop="username" :label="$t('views.login.loginForm.username.label')" />
            <el-table-column prop="source" :label="$t('views.userManage.source.label')">
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
            <el-table-column :label="$t('common.operation')" width="100" fixed="right">
              <template #default="{ row }">
                <el-tooltip effect="dark" :content="`${$t('common.remove')}`" placement="top">
                  <el-button
                    type="primary"
                    text
                    @click.stop="handleDeleteUser(row)"
                    v-hasPermission="
                      new ComplexPermission(
                        [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
                        [
                          PermissionConst.WORKSPACE_USER_GROUP_REMOVE_MEMBER,
                          PermissionConst.USER_GROUP_REMOVE_MEMBER,
                        ],
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
      </div>
    </el-card>

    <CreateOrUpdateGroupDialog ref="createOrUpdateGroupDialogRef" @refresh="refresh" />
    <CreateGroupUserDialog ref="createGroupUserDialogRef" @refresh="getList" />
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, watch, reactive } from 'vue'
import SystemGroupApi from '@/api/system/user-group'
import { t } from '@/locales'
import { i18n_name } from '@/utils/common'
import type { ChatUserGroupUserItem } from '@/api/type/systemChatUser'
import CreateOrUpdateGroupDialog from './component/CreateOrUpdateGroupDialog.vue'
import CreateGroupUserDialog from './component/CreateGroupUserDialog.vue'
import type { ListItem } from '@/api/type/common'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { PermissionConst, RoleConst } from '@/utils/permission/data'
import { ComplexPermission } from '@/utils/permission/type'
import { hasPermission } from '@/utils/permission/index'
import { loadPermissionApi } from '@/utils/dynamics-api/permission-api.ts'

const filterText = ref('')
const loading = ref(false)
const list = ref<ListItem[]>([])
const filterList = ref<ListItem[]>([]) // 搜索过滤后列表
const current = ref<ListItem>()

async function getUserGroupList() {
  try {
    const res = await loadPermissionApi('userGroup').getUserGroup(loading)
    list.value = res.data
    filterList.value = filter(list.value, filterText.value)
  } catch (error) {
    console.error(error)
  }
}

const editPermission = () => {
  return hasPermission(
    new ComplexPermission(
      [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
      [PermissionConst.WORKSPACE_USER_GROUP_EDIT, PermissionConst.USER_GROUP_EDIT],
      [],
      'OR',
    ),
    'OR',
  )
}

const dlePermission = () => {
  return hasPermission(
    new ComplexPermission(
      [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
      [PermissionConst.WORKSPACE_USER_GROUP_DELETE, PermissionConst.USER_GROUP_DELETE],
      [],
      'OR',
    ),
    'OR',
  )
}

onMounted(async () => {
  await getUserGroupList()
  current.value = list.value[0]
})

function filter(list: ListItem[], filterText: string) {
  if (!filterText.length) {
    return list
  }
  return list.filter((v: ListItem) => v.name.toLowerCase().includes(filterText.toLowerCase()))
}

watch(filterText, (val: string) => {
  filterList.value = filter(list.value, val)
})

function clickUserGroup(item: ListItem) {
  current.value = item
}

const createOrUpdateGroupDialogRef = ref<InstanceType<typeof CreateOrUpdateGroupDialog>>()

function createOrUpdate(item?: ListItem) {
  createOrUpdateGroupDialogRef.value?.open(item)
}

function deleteGroup(item: ListItem) {
  MsgConfirm(
    `${t('views.chatUser.group.delete.confirmTitle')}${item.name} ?`,
    t('views.chatUser.group.delete.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      loadPermissionApi('userGroup')
        .delUserGroup(item.id as string, loading)
        .then(async () => {
          MsgSuccess(t('common.deleteSuccess'))
          await getUserGroupList()
          current.value = item.id === current.value?.id ? list.value[0] : current.value
        })
    })
    .catch(() => {})
}

async function refresh(group?: ListItem) {
  await getUserGroupList()
  // 创建后选中新建的
  if (group) {
    current.value = group
  } else {
    current.value = list.value.find((item) => item.id === current.value?.id)
  }
}

const rightLoading = ref(false)

const searchType = ref('username')
const searchForm = ref<Record<string, any>>({
  username: '',
  nick_name: '',
  source: '',
})
const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0,
})

const tableData = ref<ChatUserGroupUserItem[]>([])

async function getList() {
  if (!current.value?.id) return
  try {
    const params = {
      [searchType.value]: searchForm.value[searchType.value as keyof typeof searchForm.value],
    }
    const res = await loadPermissionApi('userGroup').getUserListByGroup(
      current.value?.id,
      paginationConfig,
      params,
      rightLoading,
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

watch(
  () => current.value?.id,
  () => {
    getList()
  },
)

const createGroupUserDialogRef = ref<InstanceType<typeof CreateGroupUserDialog>>()

function createUser() {
  createGroupUserDialogRef.value?.open(current.value?.id as string)
}

const multipleSelection = ref<any[]>([])

function handleSelectionChange(val: any[]) {
  multipleSelection.value = val
}

function handleDeleteUser(item?: ChatUserGroupUserItem) {
  MsgConfirm(
    item
      ? `${t('views.workspace.member.delete.confirmTitle')}${item.nick_name} ?`
      : t('views.chatUser.group.batchDeleteMember', { count: multipleSelection.value.length }),
    '',
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      loadPermissionApi('userGroup')
        .postRemoveMember(
          current.value?.id as string,
          {
            group_relation_ids: item
              ? [item.user_group_relation_id]
              : multipleSelection.value.map((item) => item.user_group_relation_id),
          },
          loading,
        )
        .then(async () => {
          MsgSuccess(t('common.removeSuccess'))
          await getList()
        })
    })
    .catch(() => {})
}

const mouseId = ref('')

function mouseenter(row: any) {
  mouseId.value = row.id
}
</script>

<style lang="scss" scoped>
.user-left {
  box-sizing: border-box;
  width: var(--setting-left-width);
  min-width: var(--setting-left-width);

  .list-height-left {
    height: calc(100vh - 231px);
  }
}

.user-right {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 24px;
}
</style>
