<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import type { CheckboxValueType } from 'element-plus'
import ChatUserApi from '@/api/admin/workspace/chat-user'
import { LOGIN_METHOD } from '@/api/enums'
import type { ChatUserAuthorization, ChatUserAuthorizationGroup, Dict, LoginMethod, OptionItem } from '@/api/types'
import { LOGIN_METHOD_LABELS } from '@/constants'
import MkSearchList from '@/components/mk-search-list/index.vue'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'ChatUserListView' })
defineProps<ResourceDetailPageProps>()
defineExpose({ hideHeader: true })

const route = useRoute()
const resource = computed(() => ({ resource_id: String(route.params.applicationId ?? ''), resource_type: 'application' }))
const loading = ref(false)

// 用户组查询与切换
const chatUserGroups = ref<ChatUserAuthorizationGroup[]>([])
const currentGroup = ref<ChatUserAuthorizationGroup>()

function loadChatUserGroups() {
  loading.value = true
  return ChatUserApi.getUserGroupList(resource.value)
    .then((groups) => {
      chatUserGroups.value = groups
      currentGroup.value = groups[0]
      return loadChatUsers()
    })
    .finally(() => {
      loading.value = false
    })
}

function handleSelectGroup(group: ChatUserAuthorizationGroup) {
  if (loading.value || currentGroup.value?.id === group.id) return
  currentGroup.value = group
  checkedUsers.value = {}
  chatUsers.value = []
  paginationConfig.value.currentPage = 1
  paginationConfig.value.total = 0
  return refreshChatUsers()
}

// 用户筛选与分页，保留当前用户组跨页的授权勾选
const chatUsers = ref<ChatUserAuthorization[]>([])
const chatUserQuery = ref<Dict<unknown>>()
const paginationConfig = ref({ currentPage: 1, pageSize: 20, total: 0 })
const checkedUsers = ref<Dict<boolean>>({})
const searchFields: OptionItem<string>[] = [
  { label: '用户名', value: 'username' },
  { label: '姓名', value: 'nick_name' },
  {
    label: '用户来源',
    value: 'source',
    options: Object.entries(LOGIN_METHOD_LABELS).map(([value, label]) => ({ value, label: value === LOGIN_METHOD.LOCAL ? '本地创建' : label })),
  },
]

function formatUserSource(source: string) {
  if (source === LOGIN_METHOD.LOCAL) return '本地创建'
  if (source === 'OAUTH2') return LOGIN_METHOD_LABELS[LOGIN_METHOD.OAUTH2]
  return LOGIN_METHOD_LABELS[source as LoginMethod] ?? source
}

function loadChatUsers() {
  if (!currentGroup.value) return Promise.resolve()
  return ChatUserApi.getUserGroupUserList(resource.value, currentGroup.value.id, paginationConfig.value, chatUserQuery.value).then((page) => {
    chatUsers.value = page.records.map((chatUser) => {
      const isAuth = checkedUsers.value[chatUser.id] ?? chatUser.is_auth
      checkedUsers.value[chatUser.id] = isAuth
      return { ...chatUser, is_auth: isAuth }
    })
    paginationConfig.value.total = page.total
  })
}

function refreshChatUsers() {
  loading.value = true
  return loadChatUsers().finally(() => {
    loading.value = false
  })
}

function handleSearchChange(query?: Dict<unknown>) {
  chatUserQuery.value = query
  paginationConfig.value.currentPage = 1
  return refreshChatUsers()
}

// 当前页批量授权与跨页保存
const allChecked = computed(() => chatUsers.value.length > 0 && chatUsers.value.every((chatUser) => chatUser.is_auth))
const allIndeterminate = computed(() => !allChecked.value && chatUsers.value.some((chatUser) => chatUser.is_auth))
const authorizationDisabled = computed(() => loading.value || !currentGroup.value || currentGroup.value.is_auth)

function handleRowChange(value: CheckboxValueType, chatUser: ChatUserAuthorization) {
  chatUser.is_auth = value === true
  checkedUsers.value[chatUser.id] = chatUser.is_auth
}

function handleCheckAll(value: CheckboxValueType) {
  chatUsers.value.forEach((chatUser) => handleRowChange(value, chatUser))
}

function handleSave() {
  const group = currentGroup.value
  if (!group || authorizationDisabled.value) return
  const userGroupId = group.id
  const payload = Object.entries(checkedUsers.value).map(([chat_user_id, is_auth]) => ({ chat_user_id, is_auth }))
  loading.value = true
  return ChatUserApi.putUserGroupUser(resource.value, userGroupId, payload)
    .then(() => {
      MsgSuccess('保存成功')
    })
    .finally(() => {
      loading.value = false
    })
}

// 自动授权成功后清空旧勾选，重新读取服务端授权状态
function handleAutoAuthorizationChange(value: string | number | boolean) {
  const group = currentGroup.value
  if (!group || loading.value) return
  loading.value = true
  const isAuth = value === true
  return ChatUserApi.putUserGroupAuthorization(resource.value, [{ user_group_id: group.id, is_auth: isAuth }])
    .then(() => {
      group.is_auth = isAuth
      checkedUsers.value = {}
      chatUsers.value = []
      return loadChatUsers().then(() => {
        MsgSuccess('保存成功')
      })
    })
    .finally(() => {
      loading.value = false
    })
}

onMounted(() => loadChatUserGroups())
</script>

<template>
  <div v-loading="loading" class="-mx-6 -mb-6 flex min-h-0 flex-1">
    <aside class="flex-column w-sidebar-expanded shrink-0 border-r">
      <div class="shrink-0 p-4">
        <h4>用户组</h4>
      </div>
      <!-- 搜索并切换用户组 -->
      <MkSearchList :data="chatUserGroups" :default-active="currentGroup?.id" @click="handleSelectGroup" />
    </aside>

    <section class="flex-column min-w-0 flex-1 pl-6">
      <template v-if="currentGroup">
        <div class="flex-between shrink-0 gap-4 py-4">
          <div class="flex-align-center min-w-0 flex-1 gap-2">
            <h4 class="min-w-0 truncate" :title="currentGroup.name">{{ currentGroup.name }}</h4>
            <el-divider direction="vertical" />
            <span class="flex-align-center shrink-0 text-N500">
              <MkIcon name="icon_member_filled" class="mr-1" />
              {{ paginationConfig.total }}
            </span>
          </div>
          <!-- 设置用户组自动授权 -->
          <div class="flex-align-center shrink-0 gap-2">
            <span class="text-N600">自动授权</span>
            <el-switch :model-value="currentGroup.is_auth" size="small" @change="handleAutoAuthorizationChange" />
          </div>
        </div>

        <div class="flex-between mb-4 gap-4">
          <!-- 保存对话用户授权 -->

          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
          <el-button type="primary" :disabled="authorizationDisabled" @click="handleSave">保存</el-button>
        </div>

        <MkTable
          v-model:pagination-config="paginationConfig"
          :data="chatUsers"
          :max-table-height="350"
          @size-change="refreshChatUsers"
          @current-change="refreshChatUsers"
        >
          <el-table-column prop="nick_name" label="姓名" show-overflow-tooltip />
          <el-table-column prop="username" label="用户名" show-overflow-tooltip />
          <el-table-column prop="source" label="用户来源" show-overflow-tooltip>
            <template #default="{ row }">{{ formatUserSource(row.source) }}</template>
          </el-table-column>
          <el-table-column :width="140" align="center">
            <template #header>
              <!-- 批量设置当前页授权 -->
              <el-checkbox :model-value="allChecked" :indeterminate="allIndeterminate" :disabled="authorizationDisabled" @change="handleCheckAll">
                授权
              </el-checkbox>
            </template>
            <template #default="{ row }">
              <!-- 设置对话用户授权 -->
              <el-checkbox
                :model-value="row.is_auth"
                :disabled="authorizationDisabled"
                @change="(value: CheckboxValueType) => handleRowChange(value, row)"
              />
            </template>
          </el-table-column>
        </MkTable>
      </template>
      <MkEmpty v-else-if="!loading" class="flex-1" />
    </section>
  </div>
</template>
