<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from '@/stores/chat'
import { formatTokenNumber } from '@/utils/number'
import { QUOTA_TYPE } from '@/api/enums'
import { useConversationListStore } from '../conversation-list/index'
import UserPwdDialog from './UserPwdDialog.vue'
import ApiKeyDialog from './ApiKeyDialog.vue'

defineOptions({ name: 'ConversationAccountMenu' })

const { account } = useConversationListStore()
const { auth } = useStore()
const router = useRouter()

const menuVisible = ref(false)
const displayName = computed(() => account.value?.nickName || account.value?.username || '用户')

// 配额尚未接入时保留空值展示，不将缺失数据表示为零用量。
const tokenPercentage = computed(() => {
  return Math.min(100, Math.max(0, (account.value?.token_quota?.used_tokens / account.value?.token_quota?.total_tokens) * 100))
})

const userPwdDialogRef = useTemplateRef<InstanceType<typeof UserPwdDialog>>('userPwdDialogRef')
const apiKeyDialogRef = useTemplateRef<InstanceType<typeof ApiKeyDialog>>('apiKeyDialogRef')

// 退出对话账号后重新导航，由守卫处理后续认证。
const handleLogout = () => {
  return auth
    .logout()
    .then(() => router.replace({ path: router.currentRoute.value.fullPath, force: true }))
    .catch(() => {})
}
</script>

<template>
  <MkDropdown v-if="account" class="w-full" trigger="click" placement="top-start" @visible-change="menuVisible = $event">
    <!-- 展开账户菜单 -->
    <button
      type="button"
      class="flex-align-center w-full cursor-pointer gap-2 rounded-md py-1 px-2 hover:bg-N900/10"
      :class="{ 'bg-N900/10': menuVisible }"
    >
      <el-avatar :size="32" class="bg-primary-gradient!">
        <img src="@/assets/mk_icon_user_gradient.svg" alt="" style="width: 54%" />
      </el-avatar>
      <span class="truncate" :title="displayName">{{ displayName }}</span>
    </button>
    <template #dropdown>
      <div class="w-60">
        <div class="p-3">
          <div class="mb-2 flex-align-center gap-2">
            <el-avatar :size="40" class="shrink-0 bg-primary-gradient!">
              <img src="@/assets/mk_icon_user_gradient.svg" alt="" style="width: 54%" />
            </el-avatar>
            <div class="min-w-0">
              <h4 class="truncate" :title="displayName">{{ displayName }}</h4>
              <div class="truncate text-N600" :title="account?.username">{{ account?.username || '-' }}</div>
            </div>
          </div>
          <template v-if="account?.token_quota">
            <div class="mb-1 flex-align-center">
              <span class="mr-3">Tokens</span>
              <span class="text-primary">{{ formatTokenNumber(account?.token_quota?.used_tokens) }}</span>
              <span class="text-N500">
                /{{ account?.token_quota?.quota_type === QUOTA_TYPE.UNLIMITED ? '不限' : formatTokenNumber(account?.token_quota?.total_tokens) }}
              </span>
            </div>

            <el-progress
              v-if="account?.token_quota?.quota_type !== QUOTA_TYPE.UNLIMITED"
              :percentage="tokenPercentage"
              :status="tokenPercentage > 80 ? 'warning' : undefined"
              :show-text="false"
              :stroke-width="6"
            />
          </template>
        </div>
        <el-divider />
        <MkDropdownMenu>
          <!-- 修改密码 -->
          <MkDropdownItem @click="userPwdDialogRef?.open()">
            <template #icon><MkIcon name="icon-key_outlined" /></template>
            <span>修改密码</span>
          </MkDropdownItem>
          <!-- 管理 API Key -->
          <MkDropdownItem @click="apiKeyDialogRef?.open()">
            <template #icon><MkIcon name="icon_passkeys_outlined" /></template>
            <span>API Key</span>
          </MkDropdownItem>
          <!-- 退出登录 -->
          <MkDropdownItem divided @click="handleLogout">
            <template #icon><MkIcon name="icon_logout_outlined" /></template>
            <span>退出登录</span>
          </MkDropdownItem>
        </MkDropdownMenu>
      </div>
    </template>
  </MkDropdown>
  <!-- 匿名登陆 -->
  <el-button v-else type="primary" class="w-full">立即登录</el-button>
  <UserPwdDialog ref="userPwdDialogRef" />
  <ApiKeyDialog ref="apiKeyDialogRef" />
</template>

<style scoped lang="scss"></style>
