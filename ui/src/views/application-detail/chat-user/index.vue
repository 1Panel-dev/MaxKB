<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ChatUserAuthorization, ChatUserAuthorizationGroup, ChatUserAuthorizationResource, Dict, OptionItem } from '@/api/types'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import type { CheckboxValueType } from 'element-plus'
import { LOGIN_METHOD, RESOURCE_TYPE } from '@/api/enums'
import { useApplicationDetailContext } from '../context'
import { LOGIN_METHOD_LABELS } from '@/constants'
import { MsgSuccess } from '@/utils/message'
import { isSystemResource } from '@/utils/resource-context'
import perm from '@/permission'

defineOptions({ name: 'ApplicationChatUserListView' })
defineProps<ResourceDetailPageProps>()
defineExpose({ hideHeader: true })

const { t } = useI18n({ useScope: 'global' })

type ApplicationChatUserPermissionMethod = 'chatUserEdit'
function applicationchatUserPermission(method: ApplicationChatUserPermissionMethod): boolean {
  if (isSystemResource()) return Boolean(perm.application.system[method]())
  return Boolean(perm.application.workspace[method](applicationId.value))
}

const { applicationId, resourceApi } = useApplicationDetailContext()
const resource = computed<ChatUserAuthorizationResource>(() => ({
  resource_id: applicationId.value,
  resource_type: RESOURCE_TYPE.APPLICATION,
}))

const loading = ref(false)

// 用户组查询与切换
const chatUserGroups = ref<ChatUserAuthorizationGroup[]>([])
const currentGroup = ref<ChatUserAuthorizationGroup>()

function loadChatUserGroups() {
  loading.value = true
  return resourceApi.chatUser
    .getUserGroupList(resource.value)
    .then((groups) => {
      chatUserGroups.value = groups
      currentGroup.value = groups[0]
      return loadChatUsers()
    })
    .finally(() => {
      loading.value = false
    })
}

// 仅刷新用户组列表及已授权人数，保留当前选中的用户组。
function refreshChatUserGroups() {
  return resourceApi.chatUser.getUserGroupList(resource.value).then((groups) => {
    const currentId = currentGroup.value?.id
    chatUserGroups.value = groups
    currentGroup.value = groups.find((group) => group.id === currentId) ?? groups[0]
  })
}

function handleSelectGroup(group: ChatUserAuthorizationGroup) {
  if (loading.value || currentGroup.value?.id === group.id) return
  currentGroup.value = group
  chatUsers.value = []
  savedAuthorization.value = {}
  paginationConfig.value.currentPage = 1
  paginationConfig.value.total = 0
  return refreshChatUsers()
}

// 用户筛选与分页，仅维护当前页的授权勾选
const chatUsers = ref<ChatUserAuthorization[]>([])
const savedAuthorization = ref<Record<string, boolean>>({})
const chatUserSearchQuery = ref<Dict<unknown>>()
const paginationConfig = ref({ currentPage: 1, pageSize: 20, total: 0 })
const searchFields = computed<OptionItem<string>[]>(() => [
  { label: t('user.name.label'), value: 'nick_name' },
  { label: t('user.username.label'), value: 'username' },
])

// 表头用户来源筛选
const selectedSource = ref<string | null>(null)
const userSourceLabels = computed<Record<string, string>>(() => ({
  ...LOGIN_METHOD_LABELS,
  [LOGIN_METHOD.LOCAL]: t('chatUser.source.local'),
  OAUTH2: LOGIN_METHOD_LABELS[LOGIN_METHOD.OAUTH2],
}))
const sourceOptions = computed<OptionItem<string>[]>(() =>
  Object.entries(LOGIN_METHOD_LABELS).map(([value, label]) => ({ label: userSourceLabels.value[value] ?? label, value })),
)
const chatUserQuery = computed<Dict<unknown>>(() => ({
  ...chatUserSearchQuery.value,
  ...(selectedSource.value !== null ? { source: selectedSource.value } : {}),
}))

function loadChatUsers() {
  if (!currentGroup.value) return Promise.resolve()
  return resourceApi.chatUser
    .getUserGroupUserList(resource.value, currentGroup.value.id, paginationConfig.value, chatUserQuery.value)
    .then((page) => {
      chatUsers.value = page.records
      savedAuthorization.value = Object.fromEntries(page.records.map(({ id, is_auth }) => [id, is_auth]))
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
  chatUserSearchQuery.value = query
  paginationConfig.value.currentPage = 1
  return refreshChatUsers()
}

function handleSourceChange() {
  paginationConfig.value.currentPage = 1
  return refreshChatUsers()
}

// 当前页批量授权与保存
const allChecked = computed(() => chatUsers.value.length > 0 && chatUsers.value.every((chatUser) => chatUser.is_auth))
const allIndeterminate = computed(() => !allChecked.value && chatUsers.value.some((chatUser) => chatUser.is_auth))
const authorizationDisabled = computed(() => loading.value || !currentGroup.value || currentGroup.value.is_auth)
const saveDisabled = computed(
  () => authorizationDisabled.value || !chatUsers.value.some(({ id, is_auth }) => savedAuthorization.value[id] !== is_auth),
)

function handleRowChange(value: CheckboxValueType, chatUser: ChatUserAuthorization) {
  if (authorizationDisabled.value) return
  chatUser.is_auth = value === true
}

function handleCheckAll(value: CheckboxValueType) {
  chatUsers.value.forEach((chatUser) => handleRowChange(value, chatUser))
}

function handleSave() {
  const group = currentGroup.value
  if (!group || saveDisabled.value) return
  const payload = chatUsers.value.map(({ id, is_auth }) => ({ chat_user_id: id, is_auth }))
  loading.value = true
  return resourceApi.chatUser
    .putUserGroupUser(resource.value, group.id, payload)
    .then(() => {
      // 先记住已保存结果，列表刷新失败时不重复提示未保存。
      savedAuthorization.value = Object.fromEntries(payload.map(({ chat_user_id, is_auth }) => [chat_user_id, is_auth]))
      MsgSuccess(t('common.messages.saveSuccess'))
      return loadChatUsers().then(refreshChatUserGroups)
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
  return resourceApi.chatUser
    .putUserGroupAuthorization(resource.value, [{ user_group_id: group.id, is_auth: isAuth }])
    .then(() => {
      group.is_auth = isAuth
      chatUsers.value = []
      savedAuthorization.value = {}
      MsgSuccess(t('common.messages.saveSuccess'))
      return loadChatUsers().then(refreshChatUserGroups)
    })
    .finally(() => {
      loading.value = false
    })
}

onMounted(() => loadChatUserGroups())
</script>

<template>
  <div v-loading="loading" :inert="loading" class="-mx-6 -mb-6 flex min-h-0 flex-1">
    <aside class="flex-column h-layout-content w-sidebar-expanded shrink-0 border-r">
      <div class="shrink-0 p-4">
        <h4>{{ t('authorization.byGroup') }}</h4>
      </div>
      <!-- 搜索并切换用户组 -->
      <MkSearchList :data="chatUserGroups" :default-active="currentGroup?.id" @click="handleSelectGroup">
        <template #default="{ row }">
          <span class="min-w-0 truncate" :title="row.name">{{ row.name }}</span>
          <span class="shrink-0 font-normal text-N500">
            （{{ row.is_auth ? t('authorization.autoAuthorization') : `${t('authorization.authorized')} ${row.authorized_count ?? 0}` }}）
          </span>
        </template>
      </MkSearchList>
    </aside>

    <section class="flex-column min-w-0 flex-1 px-6">
      <template v-if="currentGroup">
        <div class="flex-align-center min-w-0 shrink-0 gap-2 py-4">
          <h4 class="min-w-0 truncate" :title="currentGroup.name">{{ currentGroup.name }}</h4>
          <el-divider direction="vertical" />
          <span class="flex-align-center shrink-0 text-N500">
            <MkIcon name="icon_member_filled" class="mr-1" />
            {{ paginationConfig.total }}
          </span>
        </div>

        <div class="flex-between mb-4 flex-wrap gap-4">
          <div class="flex-align-center flex-wrap gap-5">
            <!-- 搜索对话用户 -->
            <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
            <!-- 设置用户组自动授权 -->
            <div class="flex-align-center shrink-0 gap-2">
              <span>{{ t('authorization.autoAuthorization') }}</span>
              <el-switch
                :disabled="!applicationchatUserPermission('chatUserEdit')"
                :model-value="currentGroup.is_auth"
                size="small"
                @change="handleAutoAuthorizationChange"
              />
            </div>
          </div>
          <!-- 保存对话用户授权 -->
          <el-button
            v-if="!currentGroup.is_auth && applicationchatUserPermission('chatUserEdit')"
            type="primary"
            :disabled="saveDisabled"
            @click="handleSave"
          >
            {{ t('common.actions.save') }}
          </el-button>
        </div>

        <MkTable
          v-model:pagination-config="paginationConfig"
          :data="chatUsers"
          :max-table-height="230"
          @size-change="refreshChatUsers"
          @current-change="refreshChatUsers"
        >
          <el-table-column prop="nick_name" :label="t('user.name.label')" show-overflow-tooltip />
          <el-table-column prop="username" :label="t('user.username.label')" show-overflow-tooltip />
          <el-table-column prop="source" :label="t('user.source.label')" show-overflow-tooltip>
            <template #header>
              <MkTableFilter
                mode="single"
                v-model="selectedSource"
                :label="t('user.source.label')"
                :options="sourceOptions"
                @change="handleSourceChange"
              />
            </template>
            <template #default="{ row }">{{ userSourceLabels[row.source] ?? row.source }}</template>
          </el-table-column>
          <el-table-column :width="140" align="center">
            <template #header>
              <!-- 批量设置当前页授权 -->
              <el-checkbox
                :model-value="allChecked"
                :indeterminate="allIndeterminate"
                :disabled="authorizationDisabled || !applicationchatUserPermission('chatUserEdit')"
                @change="handleCheckAll"
              >
                {{ t('authorization.authorize') }}
              </el-checkbox>
            </template>
            <template #default="{ row }">
              <!-- 设置对话用户授权 -->
              <el-checkbox
                :model-value="row.is_auth"
                :disabled="authorizationDisabled || !applicationchatUserPermission('chatUserEdit')"
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
