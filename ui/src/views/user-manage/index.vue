<template>
  <LayoutContainer header="用户管理">
    <div class="p-24">
      <div class="flex-between">
        <el-button type="primary" @click="createUser">创建用户</el-button>
        <el-input
          v-model="searchValue"
          @change="searchHandle"
          placeholder="搜索"
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
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="nick_name" label="姓名" />
        <el-table-column prop="email" label="邮箱" show-overflow-tooltip />
        <el-table-column prop="phone" label="手机号" />
        <el-table-column prop="source" label="用户类型">
          <template #default="{ row }">
            {{ row.source === 'LOCAL' ? '系统用户' : row.source }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="60">
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
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ datetimeFormat(row.create_time) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="110" align="left" fixed="right">
          <template #default="{ row }">
            <span class="mr-4">
              <el-tooltip effect="dark" content="编辑" placement="top">
                <el-button type="primary" text @click.stop="editUser(row)">
                  <el-icon><EditPen /></el-icon>
                </el-button>
              </el-tooltip>
            </span>
            <span class="mr-4">
              <el-tooltip effect="dark" content="修改用户密码" placement="top">
                <el-button type="primary" text @click.stop="editPwdUser(row)">
                  <el-icon><Lock /></el-icon>
                </el-button>
              </el-tooltip>
            </span>
            <span class="mr-4">
              <el-tooltip effect="dark" content="删除" placement="top">
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
  const str = bool ? '启用成功' : '禁用成功'
  userApi.putUserManage(row.id, obj, loading).then((res) => {
    getList()
    MsgSuccess(str)
  })
}

function editPwdUser(row: any) {
  UserPwdDialogRef.value.open(row)
}
function editUser(row: any) {
  title.value = '编辑用户'
  UserDialogRef.value.open(row)
}

function createUser() {
  if (user.isEnterprise()) {
    title.value = '创建用户'
    UserDialogRef.value.open()
  } else {
    common.asyncGetValid(ValidType.User, ValidCount.User, loading).then((res: any) => {
      if (res?.data) {
        title.value = '创建用户'
        UserDialogRef.value.open()
      } else {
        MsgAlert('提示', '社区版最多支持 2 个用户，如需拥有更多用户，请升级为专业版。')
      }
    })
  }
}

function deleteUserManage(row: any) {
  MsgConfirm(
    `是否删除用户：${row.username} ?`,
    `删除用户，该用户创建的资源（应用、知识库、模型）都会删除，请谨慎操作。`,
    {
      confirmButtonText: '删除',
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      loading.value = true
      userApi.delUserManage(row.id, loading).then(() => {
        MsgSuccess('删除成功')
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
