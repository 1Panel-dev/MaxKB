<template>
  <ContentContainer>
    <template #header>
      <div>
        <h2>{{ $t('views.chatUser.title') }}</h2>
        <div class="color-secondary">{{ resource.resource_type === SourceTypeEnum.APPLICATION ?
          $t('views.chatUser.applicationTitleTip') : $t('views.chatUser.knowledgeTitleTip') }}</div>
      </div>
    </template>
    <el-card style="--el-card-padding: 0" class="user-card">
      <div class="flex h-full">
        <div class="user-left border-r p-16">
          <div class="user-left_title">
            <h4 class="medium">{{ $t('views.chatUser.group.title') }}</h4>
          </div>
          <div class="p-8">
            <el-input v-model="filterText" :placeholder="$t('common.search')" prefix-icon="Search" clearable />
          </div>
          <div class="list-height-left">
            <el-scrollbar v-loading="loading">
              <common-list :data="filterList" @click="clickUserGroup" :default-active="current?.id">
                <template #default="{ row }">
                  <span>{{ row.name }}</span>
                </template>
                <template #empty>
                  <span></span>
                </template>
              </common-list>
            </el-scrollbar>
          </div>
        </div>

        <!-- 右边 -->
        <div class="user-right" v-loading="rightLoading">
          <div class="flex-between">
            <div class="flex align-center">
              <h4 class="medium">{{ current?.name }}</h4>
              <el-divider direction="vertical" class="mr-8 ml-8" />
              <AppIcon iconName="app-workspace" style="font-size: 16px" class="color-input-placeholder"></AppIcon>
              <span class="color-input-placeholder ml-4">
                {{ paginationConfig.total }}
              </span>
            </div>
            <el-button type="primary" :disabled="current?.is_auth" @click="handleSave"
              v-if="permissionPrecise.chat_user_edit(id)"
            >
              {{ t('common.save') }}
            </el-button>
          </div>

          <div class="flex-between mb-16" style="margin-top: 18px;">
            <div class="flex complex-search">
              <el-select class="complex-search__left" v-model="searchType" style="width: 120px">
                <el-option :label="$t('views.login.loginForm.username.label')" value="name" />
              </el-select>
              <el-input v-if="searchType === 'name'" v-model="searchForm.name" @change="getList"
                :placeholder="$t('common.inputPlaceholder')" style="width: 220px" clearable />
            </div>
            <div class="flex align-center"
              v-if="permissionPrecise.chat_user_edit(id)"
            >
              <div class="color-secondary mr-8">{{ $t('views.chatUser.autoAuthorization') }}</div>
              <el-switch size="small" :model-value="current?.is_auth" @click="changeAuth"
                :loading="loading"
                ></el-switch>
            </div>
          </div>

          <app-table :data="tableData" :pagination-config="paginationConfig" @sizeChange="handleSizeChange"
            @changePage="getList">
            <el-table-column prop="nick_name" :label="$t('views.userManage.userForm.nick_name.label')" />
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
            <el-table-column :width="140" align="center">
              <template #header>
                <el-checkbox :model-value="allChecked" :indeterminate="allIndeterminate" :disabled="current?.is_auth"
                  @change="handleCheckAll">{{ $t('views.chatUser.authorization')
                  }}</el-checkbox>
              </template>
              <template #default="{ row }">
                <el-checkbox v-model="row.is_auth" :indeterminate="row.indeterminate" :disabled="current?.is_auth"
                  @change="(value: boolean) => handleRowChange(value, row)" />
              </template>
            </el-table-column>
          </app-table>
        </div>
      </div>
    </el-card>
  </ContentContainer>
</template>

<script lang="ts" setup>
import { onMounted, ref, watch, reactive, computed } from 'vue'
import ChatUserApi from '@/api/chat-user/chat-user'
import { t } from '@/locales'
import type { ChatUserGroupItem, ChatUserGroupUserItem } from '@/api/type/workspaceChatUser'
import { useRoute } from 'vue-router'
import { SourceTypeEnum } from '@/enums/common'
import { MsgSuccess } from '@/utils/message'
import permissionMap from '@/permission'

const route = useRoute()

const apiType = computed<'workspace'>(() => {
    return 'workspace'
})
const permissionPrecise = computed(() => {
  return permissionMap['application'][apiType.value]
})

const {
  params: { id },
} = route as any

const resource = reactive({ resource_id: route.params.id as string, resource_type: route.meta.resourceType as string })

const filterText = ref('')
const loading = ref(false)
const list = ref<ChatUserGroupItem[]>([])
const filterList = ref<ChatUserGroupItem[]>([]) // 搜索过滤后列表
const current = ref<ChatUserGroupItem>()

async function getUserGroupList() {
  try {
    const res = await ChatUserApi.getUserGroupList(resource, loading)
    list.value = res.data
    filterList.value = filter(list.value, filterText.value)
  } catch (error) {
    console.error(error)
  }
}

onMounted(async () => {
  await getUserGroupList()
  current.value = list.value[0]
})

function filter(list: ChatUserGroupItem[], filterText: string) {
  if (!filterText.length) {
    return list
  }
  return list.filter((v: ChatUserGroupItem) =>
    v.name.toLowerCase().includes(filterText.toLowerCase()),
  )
}

watch(filterText, (val: string) => {
  filterList.value = filter(list.value, val)
})

function clickUserGroup(item: ChatUserGroupItem) {
  current.value = item
}

async function changeAuth() {
  const params = [{ user_group_id: current.value?.id as string, is_auth: !current.value?.is_auth }]
  try {
    await ChatUserApi.editUserGroupList(resource, params, loading)
    await getUserGroupList()
    current.value = { name: current.value?.name as string, id: current.value?.id as string, is_auth: !current.value?.is_auth }
    getList()
  } catch (error) {
    console.error(error)
  }
}

const rightLoading = ref(false)

const searchType = ref('name')
const searchForm = ref<Record<string, any>>({
  name: '',
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
    const res = await ChatUserApi.getUserGroupUserList(resource, current.value?.id, paginationConfig, searchForm.value.name, rightLoading)
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

watch(() => current.value?.id, () => {
  getList()
})

const allChecked = computed(() =>
  tableData.value.length > 0 && tableData.value.every((item: ChatUserGroupUserItem) => item.is_auth)
);

const allIndeterminate = computed(() =>
  !allChecked.value && tableData.value.some((item: ChatUserGroupUserItem) => item.is_auth)
);

const handleCheckAll = (checked: boolean) => {
  tableData.value.forEach((item: ChatUserGroupUserItem) => {
    item.is_auth = checked;
  });
};

const handleRowChange = (value: boolean, row: ChatUserGroupUserItem) => {
  row.is_auth = value;
};

async function handleSave() {
  try {
    const params = tableData.value.map(item => ({ chat_user_id: item.id, is_auth: item.is_auth }))
    await ChatUserApi.putUserGroupUser(resource, current.value?.id as string, params, rightLoading)
    MsgSuccess(t('common.saveSuccess'))
  } catch (error) {
    console.error(error)
  }
}
</script>

<style lang="scss" scoped>
.content-container {
  height: 100%;
  display: flex;
  flex-direction: column;

  :deep(.content-container__main) {
    flex: 1;
    overflow: hidden;
  }
}

:deep(.user-card) {
  height: 100%;
  overflow: hidden;
}

.user-left {
  box-sizing: border-box;
  width: var(--setting-left-width);
  min-width: var(--setting-left-width);

  .user-left_title {
    padding: 8px;
  }

  .list-height-left {
    height: calc(100vh - 271px);

    :deep(.common-list li) {
      padding-right: 4px;
      padding-left: 8px;
    }
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
