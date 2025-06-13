<template>
  <div class="p-16-24">
    <h2 class="mb-16">{{ $t('views.userManage.title') }}</h2>
    <el-card>
      <div class="flex-between mb-16">
        <el-button type="primary" @click="createUser">{{
          $t('views.userManage.createUser')
        }}</el-button>
        <div class="flex-between complex-search">
          <el-select
            class="complex-search__left"
            v-model="search_type"
            style="width: 120px"
            @change="search_type_change"
          >
            <el-option :label="$t('views.login.loginForm.username.label')" value="name" />
          </el-select>
          <el-input
            v-if="search_type === 'name'"
            v-model="search_form.name"
            @change="getList"
            :placeholder="$t('common.searchBar.placeholder')"
            style="width: 220px"
            clearable
          />
        </div>
      </div>
      <app-table
        class="mt-16"
        :data="userTableData"
        :pagination-config="paginationConfig"
        @sizeChange="handleSizeChange"
        @changePage="getList"
        v-loading="loading"
      >
        <el-table-column prop="nick_name" :label="$t('views.userManage.userForm.nick_name.label')" />
        <el-table-column prop="username" :label="$t('views.login.loginForm.username.label')" />
        <el-table-column prop="is_active" :label="$t('common.status.label')">
          <template #default="{ row }">
            <div v-if="row.is_active" class="flex align-center">
              <el-icon class="color-success mr-8" style="font-size: 16px"
                ><SuccessFilled
              /></el-icon>
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
          :label="$t('views.userManage.userForm.email.label')"
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
              <el-switch
                :disabled="row.role === 'ADMIN'"
                size="small"
                v-model="row.is_active"
                :before-change="() => changeState(row)"
              />
            </span>
            <el-divider direction="vertical" />
            <span class="mr-8">
              <el-button type="primary" text @click.stop="editUser(row)" :title="$t('common.edit')">
                <el-icon><EditPen /></el-icon>
              </el-button>
            </span>

            <span class="mr-8">
              <el-button
                type="primary"
                text
                @click.stop="editPwdUser(row)"
                :title="$t('views.userManage.setting.updatePwd')"
              >
                <el-icon><Lock /></el-icon>
              </el-button>
            </span>
            <span>
              <el-button
                :disabled="row.role === 'ADMIN'"
                type="primary"
                text
                @click.stop="deleteUserManage(row)"
                :title="$t('common.delete')"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </span>
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
import userManageApi from '@/api/user/user-manage'
import { datetimeFormat } from '@/utils/time'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { t } from '@/locales'
const search_type = ref('name')
const search_form = ref<{
  name: string
}>({
  name: '',
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
  search_form.value = { name: '' }
}
function handleSizeChange() {
  paginationConfig.current_page = 1
  getList()
}

function getList() {
  return userManageApi
    .getUserManage(paginationConfig, search_form.value.name, loading)
    .then((res) => {
      userTableData.value = res.data.records
      paginationConfig.total = res.data.total
    })
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
function editUser(row: any) {
  title.value = t('views.userManage.editUser')
  UserDrawerRef.value.open(row)
}

function createUser() {
  title.value = t('views.userManage.createUser')
  UserDrawerRef.value.open()
  // common.asyncGetValid(ValidType.User, ValidCount.User, loading).then(async (res: any) => {
  //   if (res?.data) {
  //     title.value = t('views.userManage.createUser')
  //     UserDrawerRef.value.open()
  //   } else if (res?.code === 400) {
  //     MsgConfirm(t('common.tip'), t('views.userManage.tip.professionalMessage'), {
  //       cancelButtonText: t('common.confirm'),
  //       confirmButtonText: t('common.professional'),
  //     })
  //       .then(() => {
  //         window.open('https://maxkb.cn/pricing.html', '_blank')
  //       })
  //       .catch(() => {})
  //   }
  // })
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
