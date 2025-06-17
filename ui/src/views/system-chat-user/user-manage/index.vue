<template>
  <ContentContainer>
    <template #header>
      <div class="shared-header">
        <span class="title">{{ t('views.system.shared_resources') }}</span>
        <el-icon size="12">
          <rightOutlined></rightOutlined>
        </el-icon>
        <span class="sub-title">{{ t('views.knowledge.title') }}</span>
      </div>
    </template>
    <el-card class="h-full">
      <div class="flex-between mb-16">
        <div>
          <el-button type="primary" @click="createUser()">
            {{ t('views.userManage.createUser') }}
          </el-button>
          <el-button :disabled="multipleSelection.length === 0">
            {{ $t('views.chatUser.syncUsers') }}
          </el-button>
          <el-button :disabled="multipleSelection.length === 0">
            {{ $t('views.chatUser.setUserGroups') }}
          </el-button>
          <el-button :disabled="multipleSelection.length === 0">
            {{ $t('common.delete') }}
          </el-button>
        </div>
        <div class="flex-between complex-search">
          <el-select class="complex-search__left" v-model="search_type" style="width: 120px"
            @change="search_type_change">
            <el-option :label="$t('views.login.loginForm.username.label')" value="name" />
          </el-select>
          <el-input v-if="search_type === 'name'" v-model="search_form.name" @change="getList"
            :placeholder="$t('common.searchBar.placeholder')" style="width: 220px" clearable />
        </div>
      </div>
      <app-table class="mt-16" :data="userTableData" :pagination-config="paginationConfig"
        @sizeChange="handleSizeChange" @changePage="getList" v-loading="loading"
        @selection-change="handleSelectionChange" @sort-change="handleSortChange">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="nick_name" :label="$t('views.userManage.userForm.nick_name.label')" />
        <el-table-column prop="username" :label="$t('common.username')" />
        <el-table-column prop="is_active" :label="$t('common.status.label')">
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
        >
          <template #default="{ row }">
            {{ row.email || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="phone" :label="$t('views.userManage.userForm.phone.label')">
          <template #default="{ row }">
            {{ row.phone || '-' }}
          </template>
        </el-table-column>
        <!-- TODO -->
        <el-table-column prop="user_group_names" :label="$t('views.chatUser.group.title')">
          <template #default="{ row }">
            {{ row.user_group_names || '-' }}
          </template>
        </el-table-column>
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

        <el-table-column :label="$t('common.createTime')" width="180">
          <template #default="{ row }">
            {{ datetimeFormat(row.create_time) }}
          </template>
        </el-table-column>

        <el-table-column :label="$t('common.operation')" width="160" align="left" fixed="right">
          <template #default="{ row }">
            <span @click.stop>
              <el-switch size="small" v-model="row.is_active" :before-change="() => changeState(row)" />
            </span>
            <el-divider direction="vertical" />
            <span class="mr-8">
              <el-button type="primary" text @click.stop="editUser(row)" :title="$t('common.edit')">
                <el-icon>
                  <EditPen />
                </el-icon>
              </el-button>
            </span>

            <span class="mr-8">
              <el-button type="primary" text @click.stop="editPwdUser(row)"
                :title="$t('views.userManage.setting.updatePwd')">
                <el-icon>
                  <Lock />
                </el-icon>
              </el-button>
            </span>
            <span>
              <el-button :disabled="row.role === 'ADMIN'" type="primary" text @click.stop="deleteUserManage(row)"
                :title="$t('common.delete')">
                <el-icon>
                  <Delete />
                </el-icon>
              </el-button>
            </span>
          </template>
        </el-table-column>
      </app-table>
    </el-card>
  </ContentContainer>

  <UserDrawer :title="title" ref="UserDrawerRef" @refresh="refresh" />
  <UserPwdDialog ref="UserPwdDialogRef" @refresh="refresh" />
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, watch } from 'vue'
import UserDrawer from './component/UserDrawer.vue'
import UserPwdDialog from './component/UserPwdDialog.vue'
import userManageApi from '@/api/system/chat-user'
import { datetimeFormat } from '@/utils/time'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { t } from '@/locales'
import iconMap from '@/components/app-icon/icons/common'

const rightOutlined = iconMap['right-outlined'].iconReader()

const search_type = ref('name')
const search_form = ref<{
  name: string
}>({
  name: '',
})
const search_type_change = () => {
  search_form.value = { name: '' }
}

const loading = ref(false)

const multipleSelection = ref<string[]>([])
function handleSelectionChange(val: string[]) {
  multipleSelection.value = val
}

const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0,
})

const userTableData = ref<any[]>([])

function getList() {
  return userManageApi
    .getUserManage(paginationConfig, search_form.value.name, loading)
    .then((res) => {
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

function changeState(row: any) {
  const obj = {
    is_active: !row.is_active,
  }
  const str = obj.is_active ? t('common.status.enableSuccess') : t('common.status.disableSuccess')
  userManageApi
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
const UserDrawerRef = ref()
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
    `${t('views.user.delete.confirmTitle')}${row.username} ?`,
    t('views.user.delete.confirmMessage'),
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

<style lang="scss" scoped>
.content-container {
  height: 100%;
  display: flex;
  flex-direction: column;

  :deep(.content-container__main) {
    flex: 1;
  }
}
</style>
