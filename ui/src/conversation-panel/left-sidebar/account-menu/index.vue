<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { Locale } from '@/locales/config'
import { QUOTA_TYPE } from '@/api/enums'
import ChatUserApi from '@/api/chat/chat-user'
import { useConversationListStore } from '../conversation-list/index'
import ApiKeyDialog from './ApiKeyDialog.vue'
import UserPwdDialog from './UserPwdDialog.vue'
import { LOCALE_OPTIONS } from '@/locales/config'
import { useStore } from '@/stores/chat'
import { formatTokenNumber } from '@/utils/number'

defineOptions({ name: 'ConversationAccountMenu' })

const { t } = useI18n({ useScope: 'global' })
const { account } = useConversationListStore()
const { auth, user } = useStore()
const router = useRouter()
const route = useRoute()

// 保存语言偏好后更新当前场景的界面与缓存。
const isChangingLanguage = ref(false)
const handleChangeLanguage = (language: Locale) => {
  if (isChangingLanguage.value || language === user.language) return
  isChangingLanguage.value = true
  return ChatUserApi.postCurrentUserLanguage(language)
    .then(() => {
      user.setLanguage(language)
    })
    .finally(() => {
      isChangingLanguage.value = false
    })
}

const menuVisible = ref(false)
const displayName = computed(() => account.value?.nickName || account.value?.username || t('chat.roles.user'))

// 配额尚未接入时保留空值展示，不将缺失数据表示为零用量。
const tokenPercentage = computed(() => {
  const quota = account.value?.token_quota
  if (!quota || quota.quota_type === QUOTA_TYPE.UNLIMITED || !quota.token_limit) return 0
  return Math.min(100, Math.max(0, (quota.used_tokens / quota.token_limit) * 100))
})

const userPwdDialogRef = useTemplateRef<InstanceType<typeof UserPwdDialog>>('userPwdDialogRef')
const apiKeyDialogRef = useTemplateRef<InstanceType<typeof ApiKeyDialog>>('apiKeyDialogRef')

// 退出对话账号后回到当前场景首页，不停留在上一用户的对话；由守卫决定匿名认证或跳转登录页。
// 必须先回到首页再退出：守卫签发匿名 token 时会立即重建对话面板，此时若仍在原地址，
// 面板会用匿名身份请求上一用户的智能体与会话，需要认证的智能体返回 403。
const handleLogout = async () => {
  try {
    await router.replace(
      route.meta.portal ? { name: 'portal-application-list' } : { name: 'chat-home', params: { accessToken: route.params.accessToken } },
    )
    await auth.logout()
    await router.replace({ path: router.currentRoute.value.fullPath, force: true })
  } catch {
    // 接口错误由请求层提示
  }
}

// 匿名用户主动登录，登录成功后回到当前地址；透传钉钉客户端入口参数
const goLogin = () => {
  const query = { redirect: route.fullPath, client: route.query.client, corpId: route.query.corpId }
  return router.push(
    route.meta.portal ? { name: 'portal-login', query } : { name: 'chat-login', params: { accessToken: route.params.accessToken }, query },
  )
}
</script>

<template>
  <MkDropdown v-if="account" class="w-full" trigger="click" placement="top-start" @visible-change="menuVisible = $event">
    <!-- 展开账户菜单 -->
    <div class="flex-align-center w-full cursor-pointer gap-2 rounded-md py-1 px-2 hover:bg-N900/10" :class="{ 'bg-N900/10': menuVisible }">
      <el-avatar :size="32" class="bg-primary-gradient!">
        <img src="@/assets/mk_icon_user_gradient.svg" alt="" style="width: 54%" />
      </el-avatar>
      <span class="truncate" :title="displayName">{{ displayName }}</span>
    </div>
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
          <div class="mb-1 flex-align-center">
            <span class="mr-3">Tokens</span>
            <span class="text-primary">{{ formatTokenNumber(account?.token_quota?.used_tokens ?? 0) }}</span>
            <span class="text-N500">
              /{{
                !account?.token_quota || account?.token_quota?.quota_type === QUOTA_TYPE.UNLIMITED
                  ? t('chatUser.quota.unlimited')
                  : formatTokenNumber(account?.token_quota?.token_limit)
              }}
            </span>
          </div>

          <el-progress
            v-if="account?.token_quota && account?.token_quota?.quota_type !== QUOTA_TYPE.UNLIMITED"
            :percentage="tokenPercentage"
            :status="tokenPercentage > 80 ? 'warning' : undefined"
            :show-text="false"
            :stroke-width="6"
          />
        </div>
        <el-divider />
        <MkDropdownMenu>
          <!-- 修改密码 -->
          <MkDropdownItem @click="userPwdDialogRef?.open()">
            <template #icon><MkIcon name="icon-key_outlined" /></template>
            <span>{{ t('auth.changePassword.title') }}</span>
          </MkDropdownItem>
          <!-- 管理 API Key -->
          <MkDropdownItem @click="apiKeyDialogRef?.open()">
            <template #icon><MkIcon name="icon_passkeys_outlined" /></template>
            <span>API Key</span>
          </MkDropdownItem>
          <!-- 切换账号界面语言 -->
          <MkDropdownItem @click.stop class="p-0!">
            <MkDropdown class="w-full" trigger="hover" placement="left-start">
              <div class="flex-between w-full gap-2 py-[5px] px-2">
                <div class="flex-align-center gap-2">
                  <MkIcon name="icon_internet_outlined" class="text-N600!" />
                  <span>{{ t('common.labels.language') }}</span>
                </div>

                <MkIcon name="icon_right_outlined" class="text-N500!" />
              </div>
              <template #dropdown>
                <MkDropdownMenu class="w-52">
                  <MkDropdownItem
                    v-for="language in LOCALE_OPTIONS"
                    :key="language.value"
                    selectable
                    :selected="user.language === language.value"
                    :disabled="isChangingLanguage"
                    @click="handleChangeLanguage(language.value)"
                  >
                    {{ language.label }}
                  </MkDropdownItem>
                </MkDropdownMenu>
              </template>
            </MkDropdown>
          </MkDropdownItem>
          <!-- 退出登录 -->
          <MkDropdownItem divided @click="handleLogout">
            <template #icon><MkIcon name="icon_logout_outlined" /></template>
            <span>{{ t('auth.logout.label') }}</span>
          </MkDropdownItem>
        </MkDropdownMenu>
      </div>
    </template>
  </MkDropdown>
  <!-- 匿名登陆 -->
  <el-button v-else type="primary" class="w-full" @click="goLogin">{{ t('auth.login.now') }}</el-button>
  <UserPwdDialog ref="userPwdDialogRef" />
  <ApiKeyDialog ref="apiKeyDialogRef" />
</template>

<style scoped lang="scss"></style>
