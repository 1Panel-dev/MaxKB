<template>
  <LayoutContainer :header="$t('views.user.title')">
    <div class="p-24">
      <div class="flex-between">
        <el-button type="primary" @click="createUser">{{ $t('views.user.createUser') }}</el-button>
        <el-input
          v-model="searchValue"
          @change="searchHandle"
          :placeholder="$t('common.search')"
          prefix-icon="Search"
          class="w-240"
          clearable
        />
      </div>

      <app-table
        class="mt-16"
        :data="tableData"
        :pagination-config="paginationConfig"
        @sizeChange="handleSizeChange"
        @changePage="getList"
        v-loading="loading"
      >
        <el-table-column prop="username" :label="$t('views.user.userForm.form.username.label')" />
        <el-table-column prop="nick_name" :label="$t('views.user.userForm.form.nick_name.label')" />
        <el-table-column
          prop="email"
          :label="$t('views.user.userForm.form.email.label')"
          show-overflow-tooltip
        />
        <el-table-column prop="phone" :label="$t('views.user.userForm.form.phone.label')" />
        <el-table-column prop="source" :label="$t('views.user.source.label')">
          <template #default="{ row }">
            {{
              row.source === 'LOCAL'
                ? $t('views.user.source.local')
                : row.source === 'wecom'
                  ? $t('views.user.source.wecom')
                  : row.source === 'lark'
                    ? $t('views.user.source.lark')
                    : row.source === 'dingtalk'
                      ? $t('views.user.source.dingtalk')
                      : row.source === 'OAUTH2' || row.source === 'OAuth2'
                        ? 'OAuth2'
                        : row.source
            }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('common.status.label')" width="80">
          <template #default="{ row }">
            <div @click.stop>
              <el-switch
                :disabled="row.role === 'ADMIN'"
                size="small"
                v-model="row.is_active"
                @change="changeState($event, row)"
              />
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="$t('common.createTime')" width="180">
          <template #default="{ row }">
            {{ datetimeFormat(row.create_time) }}
          </template>
        </el-table-column>

        <el-table-column :label="$t('common.operation')" width="110" align="left" fixed="right">
          <template #default="{ row }">
            <span class="mr-4">
              <el-tooltip effect="dark" :content="$t('common.edit')" placement="top">
                <el-button type="primary" text @click.stop="editUser(row)">
                  <el-icon><EditPen /></el-icon>
                </el-button>
              </el-tooltip>
            </span>
            <span class="mr-4">
              <el-tooltip
                effect="dark"
                :content="$t('views.user.setting.updatePwd')"
                placement="top"
              >
                <el-button type="primary" text @click.stop="editPwdUser(row)">
                  <el-icon><Lock /></el-icon>
                </el-button>
              </el-tooltip>
            </span>
            <span class="mr-4">
              <el-tooltip effect="dark" :content="$t('common.delete')" placement="top">
                <el-button
                  :disabled="row.role === 'ADMIN'"
                  type="primary"
                  text
                  @click.stop="deleteUserManage(row)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </span>
          </template>
        </el-table-column>
      </app-table>
    </div>
    <UserDialog :title="title" ref="UserDialogRef" @refresh="refresh" />
    <UserPwdDialog ref="UserPwdDialogRef" @refresh="refresh" />
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import UserDialog from './component/UserDialog.vue'
import UserPwdDialog from './component/UserPwdDialog.vue'
import { MsgSuccess, MsgConfirm, MsgAlert } from '@/utils/message'
import userApi from '@/api/user-manage'
import { datetimeFormat } from '@/utils/time'
import useStore from '@/stores'
import { ValidType, ValidCount } from '@/enums/common'
import { t } from '@/locales'

const { common, user } = useStore()

const UserDialogRef = ref()
const UserPwdDialogRef = ref()
const title = ref('')
const loading = ref(false)
const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0
})
const tableData = ref<any[]>([])

const searchValue = ref('')

function searchHandle() {
  paginationConfig.total = 0
  paginationConfig.current_page = 1
  tableData.value = []
  getList()
}

function changeState(bool: Boolean, row: any) {
  const obj = {
    is_active: bool
  }
  const str = bool ? t('common.status.enableSuccess') : t('common.status.disableSuccess')
  userApi.putUserManage(row.id, obj, loading).then((res) => {
    getList()
    MsgSuccess(str)
  })
}

function editPwdUser(row: any) {
  UserPwdDialogRef.value.open(row)
}

function editUser(row: any) {
  title.value = t('views.user.editUser')
  UserDialogRef.value.open(row)
}

function createUser() {
  common.asyncGetValid(ValidType.User, ValidCount.User, loading).then(async (res: any) => {
    if (res?.data) {
      title.value = t('views.user.createUser')
      UserDialogRef.value.open()
    } else if (res?.code === 400) {
      MsgConfirm(t('common.tip'), t('views.user.tip.professionalMessage'), {
        cancelButtonText: t('common.confirm'),
        confirmButtonText: t('common.professional')
      })
        .then(() => {
          window.open('https://maxkb.cn/pricing.html', '_blank')
        })
        .catch(() => {})
    }
  })
}

function deleteUserManage(row: any) {
  MsgConfirm(
    `${t('views.user.delete.confirmTitle')}${row.username} ?`,
    t('views.user.delete.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      loading.value = true
      userApi.delUserManage(row.id, loading).then(() => {
        MsgSuccess(t('common.deleteSuccess'))
        getList()
      })
    })
    .catch(() => {})
}

function handleSizeChange() {
  paginationConfig.current_page = 1
  getList()
}

function getList() {
  return userApi.getUserManage(paginationConfig, searchValue.value, loading).then((res) => {
    tableData.value = res.data.records
    paginationConfig.total = res.data.total
  })
}

function refresh() {
  getList()
}

onMounted(() => {
  getList()
})
</script>
<style lang="scss" scoped>
.log-table tr {
  cursor: pointer;
}
</style>
