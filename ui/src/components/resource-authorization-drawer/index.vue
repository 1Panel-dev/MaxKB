<template>
  <el-drawer
    v-model="drawerVisible"
    :title="$t('views.system.resourceAuthorization.title')"
    size="60%"
    :append-to-body="true"
    :modal="false"
  >
    <div class="flex-between mb-16">
      <el-button
        type="primary"
        :disabled="multipleSelection.length === 0"
        @click="openMulConfigureDialog"
        >{{ $t('views.system.resourceAuthorization.setting.configure') }}</el-button
      >

      <div class="flex-between complex-search">
        <el-select
          class="complex-search__left"
          v-model="searchType"
          style="width: 100px"
          @change="search_type_change"
        >
          <el-option :label="$t('views.userManage.userForm.nick_name.label')" value="nick_name" />
          <el-option :label="$t('views.login.loginForm.username.label')" value="username" />
          <el-option
            :label="$t('views.model.modelForm.permissionType.label')"
            value="publish_status"
          />
        </el-select>
        <el-input
          v-if="searchType === 'nick_name'"
          v-model="searchForm.nick_name"
          @change="searchHandle"
          :placeholder="$t('common.search')"
          style="width: 220px"
          clearable
        />
        <el-input
          v-if="searchType === 'username'"
          v-model="searchForm.username"
          @change="searchHandle"
          :placeholder="$t('common.search')"
          style="width: 220px"
          clearable
        />

        <el-select
          v-else-if="searchType === 'publish_status'"
          v-model="searchForm.publish_status"
          @change="searchHandle"
          filterable
          clearable
          multiple
          collapse-tags
          collapse-tags-tooltip
          style="width: 220px"
        >
          <template v-for="(item, index) in permissionOptions" :key="index">
            <el-option :label="item.label" :value="item.value" />
          </template>
        </el-select>
      </div>
    </div>

    <app-table
      ref="multipleTableRef"
      class="mt-16"
      :data="permissionData"
      :pagination-config="paginationConfig"
      @sizeChange="handleSizeChange"
      @changePage="getPermissionList"
      @selection-change="handleSelectionChange"
      :maxTableHeight="200"
      :row-key="(row: any) => row.id"
      v-loading="loading"
    >
      <el-table-column type="selection" width="55" :reserve-selection="true" />
      <el-table-column
        prop="nick_name"
        :label="$t('views.userManage.userForm.nick_name.label')"
        min-width="120"
        show-overflow-tooltip
      />
      <el-table-column
        prop="username"
        min-width="120"
        show-overflow-tooltip
        :label="$t('views.login.loginForm.username.label')"
      />
      <!-- <el-table-column prop="role_name" :label="$t('views.role.member.role')" width="210">
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
      </el-table-column> -->
      <el-table-column :label="$t('common.operation')" align="left" width="340">
        <template #default="{ row }">
          <el-radio-group
            v-model="row.permission"
            @change="(val: any) => permissionsHandle(val, row)"
          >
            <template v-for="(item, index) in permissionOptions" :key="index">
              <el-radio :value="item.value" class="mr-16">{{ item.label }}</el-radio>
            </template>
          </el-radio-group>
        </template>
      </el-table-column>
    </app-table>

    <!-- 批量配置 弹出层 -->
    <el-dialog
      v-model="dialogVisible"
      :title="$t('views.system.resourceAuthorization.setting.configure')"
      destroy-on-close
      @close="closeDialog"
    >
      <el-radio-group v-model="radioPermission" class="radio-block">
        <template v-for="(item, index) in permissionOptions" :key="index">
          <el-radio :value="item.value" class="mr-16">
            <p class="color-text-primary lighter">{{ item.label }}</p>
            <el-text class="color-secondary lighter">{{ item.desc }}</el-text>
          </el-radio>
        </template>
      </el-radio-group>
      <template #footer>
        <div class="dialog-footer mt-24">
          <el-button @click="closeDialog"> {{ $t('common.cancel') }}</el-button>
          <el-button type="primary" @click="submitDialog"> {{ $t('common.confirm') }}</el-button>
        </div>
      </template>
    </el-dialog>
  </el-drawer>
</template>
<script setup lang="ts">
import { ref, onMounted, watch, computed, reactive } from 'vue'
import { permissionOptions } from '@/views/system/resource-authorization/constant'
import AuthorizationApi from '@/api/system/resource-authorization'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { t } from '@/locales'
import useStore from '@/stores'
const { user } = useStore()
const props = defineProps<{
  type: string
}>()

const drawerVisible = ref(false)
const multipleTableRef = ref()

watch(drawerVisible, (bool) => {
  if (!bool) {
    targetId.value = ''
    searchType.value = 'nick_name'
    searchForm.value = { nick_name: '', username: '', permission: undefined }
    permissionData.value = []
    paginationConfig.current_page = 1
    paginationConfig.total = 0
    multipleSelection.value = []
    multipleTableRef.value?.clearSelection()
  }
})

const loading = ref(false)
const targetId = ref('')
const permissionData = ref<any[]>([])
const searchType = ref('nick_name')
const searchForm = ref<any>({
  nick_name: '',
  username: '',
  permission: undefined,
})

const search_type_change = () => {
  searchForm.value = { nick_name: '', username: '', permission: undefined }
}

const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0,
})

function handleSizeChange() {
  paginationConfig.current_page = 1
  getPermissionList()
}
function searchHandle() {
  paginationConfig.current_page = 1
  getPermissionList()
}

const multipleSelection = ref<any[]>([])

const handleSelectionChange = (val: any[]) => {
  multipleSelection.value = val
}

const dialogVisible = ref(false)
const radioPermission = ref('')
function openMulConfigureDialog() {
  if (multipleSelection.value.length === 0) {
    return
  }
  dialogVisible.value = true
}
function submitDialog() {
  if (multipleSelection.value.length === 0 || !radioPermission.value) {
    return
  }
  const obj = multipleSelection.value.map((item) => ({
    user_id: item.id,
    permission: radioPermission.value,
  }))
  submitPermissions(obj)
  closeDialog()
}
function closeDialog() {
  dialogVisible.value = false
  radioPermission.value = ''
  multipleSelection.value = []
  multipleTableRef.value?.clearSelection()
}

function permissionsHandle(val: any, row: any) {
  const obj = [
    {
      user_id: row.id,
      permission: val,
    },
  ]
  submitPermissions(obj)
}

function submitPermissions(obj: any) {
  const workspaceId = user.getWorkspaceId() || 'default'
  AuthorizationApi.putWorkspaceResourceAuthorization(
    workspaceId,
    targetId.value,
    props.type,
    obj,
    loading,
  ).then(() => {
    MsgSuccess(t('common.submitSuccess'))
    getPermissionList()
  })
}
const getPermissionList = () => {
  const workspaceId = user.getWorkspaceId() || 'default'
  const params: any = {}
  if (searchForm.value[searchType.value]) {
    params[searchType.value] = searchForm.value[searchType.value]
  }
  AuthorizationApi.getWorkspaceResourceAuthorization(
    workspaceId,
    targetId.value,
    props.type,
    paginationConfig,
    params,
    loading,
  ).then((res) => {
    permissionData.value = res.data.records || []
    paginationConfig.total = res.data.total || 0
  })
}

const open = (id: string) => {
  targetId.value = id
  drawerVisible.value = true
  getPermissionList()
}
defineExpose({
  open,
})
</script>
<style lang="scss" scoped></style>
