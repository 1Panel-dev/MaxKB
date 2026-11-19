<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { CommonUserOption } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import CommonSystemApi from '@/api/admin/system/common'
import UserGroupsApi from '@/api/admin/system/user-groups'
import { MsgSuccess } from '@/utils/message'

const props = defineProps<{ workspaceId: string; currentGroup?: { id: string; name: string } }>()
const emit = defineEmits<{ refresh: [] }>()
const { t } = useI18n({ useScope: 'global' })

const visible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const formRules = computed<FormRules>(() => ({
  userIds: [{ required: true, message: t('system.member.requiredMessage'), trigger: 'change' }],
}))
const memberForm = reactive<{ userIds: string[] }>({ userIds: [] })

/* 成员选项 */
const optionsLoading = ref(false)
const userOptions = ref<CommonUserOption[]>([])
const allUserOptions = ref<CommonUserOption[]>([])
let searchTimer: ReturnType<typeof setTimeout> | null = null
function loadUserOptions(query = '') {
  const keyword = query.trim()
  optionsLoading.value = true
  CommonSystemApi.getWorkspaceMembers(props.workspaceId, keyword ? { nick_name: keyword } : undefined)
    .then((users) => {
      userOptions.value = users
      if (!keyword) allUserOptions.value = users
    })
    .finally(() => {
      optionsLoading.value = false
    })
}

function handleRemoteSearch(query: string) {
  if (searchTimer) {
    clearTimeout(searchTimer)
    searchTimer = null
  }
  const keyword = query.trim()
  if (!keyword) {
    // Select 聚焦会触发空关键词搜索，复用首次列表以避免加载态导致下拉浮层重绘。
    userOptions.value = allUserOptions.value
    return
  }
  searchTimer = setTimeout(() => {
    searchTimer = null
    loadUserOptions(keyword)
  }, 300)
}

function submit() {
  const groupId = props.currentGroup?.id
  if (!groupId) return

  formRef.value?.validate((valid) => {
    if (!valid) return

    loading.value = true
    UserGroupsApi.postSystemUserGroupMembers(props.workspaceId, groupId, memberForm.userIds)
      .then(() => {
        MsgSuccess(t('common.messages.addSuccess'))
        emit('refresh')
        visible.value = false
      })
      .finally(() => {
        loading.value = false
      })
  })
}

function open() {
  visible.value = true
  loadUserOptions()
}

function resetData() {
  memberForm.userIds = []
  loading.value = false
  optionsLoading.value = false
  userOptions.value = []
  allUserOptions.value = []
  formRef.value?.clearValidate()
  if (searchTimer) {
    clearTimeout(searchTimer)
    searchTimer = null
  }
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" :title="t('system.member.add')" @closed="resetData">
    <el-form
      ref="formRef"
      :model="memberForm"
      :rules="formRules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="`${t('user.username.label')}/${t('user.name.label')}`" prop="userIds">
        <el-select
          v-model="memberForm.userIds"
          class="w-full"
          filterable
          remote
          reserve-keyword
          multiple
          :remote-method="handleRemoteSearch"
          :loading="optionsLoading"
          :placeholder="t('user.placeholder')"
        >
          <el-option v-for="user in userOptions" :key="user.id" :label="user.nick_name" :value="user.id" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消添加成员 -->
      <el-button plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 添加成员 -->
      <el-button type="primary" :loading="loading" @click="submit">{{ t('common.actions.add') }}</el-button>
    </template>
  </MkDialog>
</template>
