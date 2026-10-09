<script setup lang="ts">
import { computed, ref } from 'vue'
import { formatTokenNumber } from '@/utils/number'
import { MsgInfo } from '@/utils/message'
import { useConversationListStore } from './index'

defineOptions({ name: 'ConversationAccountMenu' })

const props = defineProps<{ usedTokens?: number; totalTokens?: number }>()
const { account } = useConversationListStore()
const menuVisible = ref(false)
const displayName = computed(() => account.value?.nickName || account.value?.username || '用户')

// 配额尚未接入时保留空值展示，不将缺失数据表示为零用量。
const tokenPercentage = computed(() => {
  const { usedTokens, totalTokens } = props
  if (usedTokens === undefined || totalTokens === undefined || !Number.isFinite(usedTokens) || !Number.isFinite(totalTokens) || totalTokens <= 0) {
    return 0
  }
  return Math.min(100, Math.max(0, (usedTokens / totalTokens) * 100))
})

// 账户接口后续接入，当前仅提供菜单布局与明确的操作反馈。
const handleAccountAction = (action: string) => MsgInfo(`${action}功能暂未接入`)
</script>

<template>
  <MkDropdown class="w-full" trigger="click" placement="top-start" @visible-change="menuVisible = $event">
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
          <div class="mb-1 flex-align-center gap-3">
            <span>Tokens</span>
            <!-- // TODO UI后期加 超过80%变黄 -->
            <span class="text-primary">{{ formatTokenNumber(usedTokens) }}</span>
            /
            <span class="text-N500">{{ formatTokenNumber(totalTokens) }}</span>
          </div>
          <el-progress :percentage="tokenPercentage" :show-text="false" :stroke-width="6" />
        </div>
        <el-divider />
        <MkDropdownMenu>
          <!-- 修改密码 -->
          <MkDropdownItem @click="handleAccountAction('修改密码')">
            <template #icon><MkIcon name="icon-key_outlined" /></template>
            <span>修改密码</span>
          </MkDropdownItem>
          <!-- 管理 API Key -->
          <MkDropdownItem @click="handleAccountAction('API Key')">
            <template #icon><MkIcon name="icon_passkeys_outlined" /></template>
            <span>API Key</span>
          </MkDropdownItem>
          <!-- 退出登录 -->
          <MkDropdownItem divided @click="handleAccountAction('退出登录')">
            <template #icon><MkIcon name="icon_logout_outlined" /></template>
            <span>退出登录</span>
          </MkDropdownItem>
        </MkDropdownMenu>
      </div>
    </template>
  </MkDropdown>
</template>

<style scoped lang="scss"></style>
