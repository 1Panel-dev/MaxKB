<template>
  <div class="function-lib-list-container p-24" style="padding-top: 16px">
    <div class="flex-between mb-16">
      <h4>{{ $t('views.functionLib.title') }}</h4>
      <div class="flex-between">
        <el-select
          v-model="selectUserId"
          class="mr-12"
          style="max-width: 240px; width: 150px"
          @change="searchHandle"
        >
          <el-option
            v-for="item in userOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <el-input
          v-model="searchValue"
          @change="searchHandle"
          :placeholder="$t('views.functionLib.searchBar.placeholder')"
          prefix-icon="Search"
          class="w-240"
          style="max-width: 240px"
          clearable
        />
      </div>
    </div>
    <div
      v-loading.fullscreen.lock="
        (paginationConfig.current_page === 1 && loading) || changeStateloading
      "
    >
      <InfiniteScroll
        :size="functionLibList.length"
        :total="paginationConfig.total"
        :page_size="paginationConfig.page_size"
        v-model:current_page="paginationConfig.current_page"
        @load="getList"
        :loading="loading"
      >
        <el-row :gutter="15">
          <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="6" class="mb-16">
            <CardAdd :title="$t('views.functionLib.createFunction')" @click="openCreateDialog()" />
          </el-col>
          <el-col
            :xs="24"
            :sm="12"
            :md="8"
            :lg="6"
            :xl="6"
            v-for="(item, index) in functionLibList"
            :key="index"
            class="mb-16"
          >
            <CardBox
              :title="item.name"
              :description="item.desc"
              class="function-lib-card"
              @click="openCreateDialog(item)"
              :class="item.permission_type === 'PUBLIC' && !canEdit(item) ? '' : 'cursor'"
            >
              <template #icon>
                <AppAvatar class="mr-12 avatar-green" shape="square" :size="32">
                  <img src="@/assets/icon_function_outlined.svg" style="width: 58%" alt="" />
                </AppAvatar>
              </template>
              <template #subTitle>
                <el-text class="color-secondary" size="small">
                  <auto-tooltip :content="item.username">
                    {{ $t('common.creator') }}: {{ item.username }}
                  </auto-tooltip>
                </el-text>
              </template>
              <div class="status-button">
                <el-tag
                  class="info-tag"
                  v-if="item.permission_type === 'PUBLIC'"
                  style="height: 22px"
                >
                  {{ $t('common.public') }}</el-tag
                >
                <el-tag
                  class="danger-tag"
                  v-else-if="item.permission_type === 'PRIVATE'"
                  style="height: 22px"
                >
                  {{ $t('common.private') }}</el-tag
                >
              </div>
              <template #footer>
                <div class="footer-content flex-between">
                  <div>
                    <el-tooltip effect="dark" :content="$t('common.copy')" placement="top">
                      <el-button text @click.stop="copyFunctionLib(item)">
                        <AppIcon iconName="app-copy"></AppIcon>
                      </el-button>
                    </el-tooltip>
                    <el-divider direction="vertical" />
                    <el-tooltip effect="dark" :content="$t('common.delete')" placement="top">
                      <el-button
                        :disabled="item.permission_type === 'PUBLIC' && !canEdit(item)"
                        text
                        @click.stop="deleteFunctionLib(item)"
                      >
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </el-tooltip>
                  </div>
                  <div @click.stop>
                    <el-switch
                      :disabled="item.permission_type === 'PUBLIC' && !canEdit(item)"
                      v-model="item.is_active"
                      @change="changeState($event, item)"
                      size="small"
                    />
                  </div>
                </div>
              </template>
            </CardBox>
          </el-col>
        </el-row>
      </InfiniteScroll>
    </div>
    <FunctionFormDrawer ref="FunctionFormDrawerRef" @refresh="refresh" :title="title" />
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { cloneDeep } from 'lodash'
import functionLibApi from '@/api/function-lib'
import FunctionFormDrawer from './component/FunctionFormDrawer.vue'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import useStore from '@/stores'
import applicationApi from '@/api/application'
import { t } from '@/locales'
const { user } = useStore()

const loading = ref(false)

const FunctionFormDrawerRef = ref()

const functionLibList = ref<any[]>([])

const paginationConfig = reactive({
  current_page: 1,
  page_size: 30,
  total: 0
})

const searchValue = ref('')
const title = ref('')
const changeStateloading = ref(false)

interface UserOption {
  label: string
  value: string
}

const userOptions = ref<UserOption[]>([])

const selectUserId = ref('all')

const canEdit = (row: any) => {
  return user.userInfo?.id === row?.user_id
}

function openCreateDialog(data?: any) {
  title.value = data ? t('views.functionLib.editFunction') : t('views.functionLib.createFunction')
  if (data) {
    if (data?.permission_type !== 'PUBLIC' || canEdit(data)) {
      FunctionFormDrawerRef.value.open(data)
    }
  } else {
    FunctionFormDrawerRef.value.open(data)
  }
}

function searchHandle() {
  if (user.userInfo) {
    localStorage.setItem(user.userInfo.id + 'function', selectUserId.value)
  }
  paginationConfig.total = 0
  paginationConfig.current_page = 1
  functionLibList.value = []
  getList()
}

function changeState(bool: Boolean, row: any) {
  if (!bool) {
    MsgConfirm(
      `${t('views.functionLib.disabled.confirmTitle')}${row.name} ?`,
      t('views.functionLib.disabled.confirmMessage'),
      {
        confirmButtonText: t('views.functionLib.setting.disabled'),
        confirmButtonClass: 'danger'
      }
    )
      .then(() => {
        const obj = {
          is_active: bool
        }
        functionLibApi.putFunctionLib(row.id, obj, changeStateloading).then((res) => {})
      })
      .catch(() => {
        row.is_active = true
      })
  } else {
    const obj = {
      is_active: bool
    }
    functionLibApi.putFunctionLib(row.id, obj, changeStateloading).then((res) => {})
  }
}

function deleteFunctionLib(row: any) {
  MsgConfirm(
    `${t('views.functionLib.delete.confirmTitle')}${row.name} ?`,
    t('views.functionLib.delete.confirmMessage'),
    {
      confirmButtonText: t('common.delete'),
      cancelButtonText: t('common.cancel'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      functionLibApi.delFunctionLib(row.id, loading).then(() => {
        const index = functionLibList.value.findIndex((v) => v.id === row.id)
        functionLibList.value.splice(index, 1)
        MsgSuccess(t('common.deleteSuccess'))
      })
    })
    .catch(() => {})
}

function copyFunctionLib(row: any) {
  title.value = t('views.functionLib.copyFunction')
  const obj = cloneDeep(row)
  delete obj['id']
  obj['name'] = obj['name'] + `  ${t('views.functionLib.functionForm.title.copy')}`
  FunctionFormDrawerRef.value.open(obj)
}

function getList() {
  const params = {
    ...(searchValue.value && { name: searchValue.value }),
    ...(selectUserId.value &&
      selectUserId.value !== 'all' && { select_user_id: selectUserId.value })
  }
  functionLibApi.getFunctionLib(paginationConfig, params, loading).then((res: any) => {
    res.data.records.forEach((item: any) => {
      if (user.userInfo && item.user_id === user.userInfo.id) {
        item.username = user.userInfo.username
      } else {
        item.username = userOptions.value.find((v) => v.value === item.user_id)?.label
      }
    })
    functionLibList.value = [...functionLibList.value, ...res.data.records]
    paginationConfig.total = res.data.total
  })
}

function refresh(data: any) {
  if (data) {
    const index = functionLibList.value.findIndex((v) => v.id === data.id)
    functionLibList.value.splice(index, 1, data)
  } else {
    paginationConfig.total = 0
    paginationConfig.current_page = 1
    functionLibList.value = []
    getList()
  }
}

function getUserList() {
  applicationApi.getUserList('FUNCTION', loading).then((res) => {
    if (res.data) {
      userOptions.value = res.data.map((item: any) => {
        return {
          label: item.username,
          value: item.id
        }
      })
      if (user.userInfo) {
        const selectUserIdValue = localStorage.getItem(user.userInfo.id + 'function')
        if (selectUserIdValue && userOptions.value.find((v) => v.value === selectUserIdValue)) {
          selectUserId.value = selectUserIdValue
        }
      }
      getList()
    }
  })
}

onMounted(() => {
  getUserList()
})
</script>
<style lang="scss" scoped>
.function-lib-list-container {
  .status-button {
    position: absolute;
    right: 12px;
    top: 15px;
    height: auto;
  }
}
</style>
