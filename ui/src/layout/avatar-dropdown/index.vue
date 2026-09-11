<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import LoginApi from '@/api/admin/auth/login'
import { LOGIN_METHOD } from '@/api/enums'
import { useStore } from '@/stores'
import ChangePasswordDialog from './ChangePasswordDialog.vue'

defineOptions({ name: 'AvatarDropdown' })

type Language = 'en' | 'zh-CN' | 'zh-TW'

const currentLanguage = ref<Language>('zh-CN')
const router = useRouter()
const { auth, user, theme } = useStore()
const languages: Array<{ label: string; value: Language }> = [
  { label: 'English', value: 'en' },
  { label: '简体中文', value: 'zh-CN' },
  { label: '繁體中文', value: 'zh-TW' },
]

// 修改当前账号密码。
const changePasswordDialogRef = ref<InstanceType<typeof ChangePasswordDialog>>()

function handleOpenChangePassword() {
  changePasswordDialogRef.value?.open()
}

function handleLogout() {
  const loginMode = user.userInfo?.source
  LoginApi.postLogout().then(() => {
    auth.clearToken()
    router.push(
      loginMode && ([LOGIN_METHOD.CAS, LOGIN_METHOD.OIDC, LOGIN_METHOD.OAUTH2] as string[]).includes(loginMode)
        ? { name: 'login', query: { login_mode: 'manual' } }
        : { name: 'login' },
    )
  })
}

function toUrl(url?: string) {
  if (!url) return
  window.open(url, '_blank')
}
</script>

<template>
  <MkDropdown ref="dropdownRef" trigger="click" placement="bottom-end">
    <el-avatar :size="32" class="cursor-pointer bg-primary-gradient!">
      <img src="@/assets/mk_icon_user_gradient.svg" alt="" style="width: 54%" />
    </el-avatar>

    <template #dropdown>
      <div class="w-52">
        <div class="flex items-start gap-2 p-3">
          <el-avatar :size="40" class="bg-primary-gradient! mt-1">
            <img src="@/assets/mk_icon_user_gradient.svg" alt="" style="width: 54%" />
          </el-avatar>
          <div>
            <div class="font-medium text-lg">{{ user.userInfo?.nick_name }}</div>
            <div class="text-N600">{{ user.userInfo?.username }}</div>
            <MkTagGroup v-if="user.userInfo?.role_name?.length" :tags="user.userInfo?.role_name" size="small" class="mt-2" type="primary" />
          </div>
        </div>
        <el-divider />
        <MkDropdownMenu>
          <!-- 修改密码 -->
          <MkDropdownItem @click="handleOpenChangePassword">
            <template #icon><MkIcon name="icon-key_outlined" /></template>
            <span>修改密码</span>
          </MkDropdownItem>
          <!-- // TODO API Key -->
          <MkDropdownItem>
            <template #icon><MkIcon name="icon_passkeys_outlined" /></template>
            <span>API Key</span>
          </MkDropdownItem>
          <!-- // TODO 语言 -->
          <MkDropdownItem @click.stop class="p-0!">
            <MkDropdown class="w-full" trigger="hover" placement="left-start">
              <div class="flex-between w-full gap-2 p-2">
                <div class="flex items-center gap-2">
                  <MkIcon name="icon_translate_outlined" class="text-N600!" />
                  <span>语言</span>
                </div>

                <MkIcon name="icon_right_outlined" class="text-N500!" />
              </div>
              <template #dropdown>
                <MkDropdownMenu class="w-52">
                  <MkDropdownItem
                    v-for="language in languages"
                    :key="language.value"
                    selectable
                    :selected="currentLanguage === language.value"
                    @click="currentLanguage = language.value"
                  >
                    {{ language.label }}
                  </MkDropdownItem>
                </MkDropdownMenu>
              </template>
            </MkDropdown>
          </MkDropdownItem>
          <MkDropdownItem divided @click="toUrl(theme.themeInfo?.projectUrl)" v-if="theme.themeInfo?.showProject">
            <template #icon><MkIcon name="icon_github_filled" /></template>
            <span>项目地址</span>
          </MkDropdownItem>
          <MkDropdownItem @click="toUrl(theme.themeInfo?.userManualUrl)" v-if="theme.themeInfo?.showUserManual">
            <template #icon><MkIcon name="icon_add-dictionary_outlined" /></template>
            <span>用户手册</span>
          </MkDropdownItem>
          <MkDropdownItem @click="toUrl(theme.themeInfo?.forumUrl)" v-if="theme.themeInfo?.showForum">
            <template #icon><MkIcon name="icon-maybe_outlined" /></template>
            <span>论坛求助</span>
          </MkDropdownItem>
          <!-- // TODO 关于 -->
          <MkDropdownItem>
            <template #icon><MkIcon name="icon_info_outlined" /></template>
            <span>关于</span>
          </MkDropdownItem>
          <MkDropdownItem divided @click="handleLogout">
            <template #icon><MkIcon name="icon_logout_outlined" /></template>
            <span>退出登录</span>
          </MkDropdownItem>
        </MkDropdownMenu>
      </div>
    </template>
  </MkDropdown>
  <ChangePasswordDialog ref="changePasswordDialogRef" />
</template>
