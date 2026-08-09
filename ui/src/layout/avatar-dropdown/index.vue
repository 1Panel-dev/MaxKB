<script setup lang="ts">
import { ref } from 'vue'
import { Setting } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import LoginApi from '@/api/admin/auth/login'
import { useStore } from '@/stores'

defineOptions({ name: 'AvatarDropdown' })

type Language = 'en' | 'zh-CN' | 'zh-TW'

const currentLanguage = ref<Language>('zh-CN')
const router = useRouter()
const { auth, user } = useStore()
const languages: Array<{ label: string; value: Language }> = [
  { label: 'English', value: 'en' },
  { label: '简体中文', value: 'zh-CN' },
  { label: '繁體中文', value: 'zh-TW' },
]

function handleLogout() {
  const loginMode = user.userInfo?.source
  LoginApi.postLogout().then(() => {
    auth.clearToken()
    router.push(
      loginMode && ['CAS', 'OIDC', 'OAuth2'].includes(loginMode)
        ? { name: 'login', query: { login_mode: 'manual' } }
        : { name: 'login' },
    )
  })
}
</script>

<template>
  <MkDropdown ref="dropdownRef" trigger="click" placement="bottom-end">
    <el-avatar :size="32" class="cursor-pointer bg-primary-gradient!">
      <img src="@/assets/mk-icon-user-gradient.svg" alt="" class="w-[54%]!" />
    </el-avatar>

    <template #dropdown>
      <div class="w-52">
        <div class="flex items-center gap-2 p-3">
          <el-avatar :size="40" class="bg-primary-gradient!">
            <img src="@/assets/mk-icon-user-gradient.svg" alt="" class="w-[54%]!" />
          </el-avatar>
          <div>
            <div class="font-medium text-lg">{{ user.userInfo?.nick_name }}</div>
            <div class="text-N600">{{ user.userInfo?.username }}</div>
          </div>
        </div>
        <el-divider />
        <MkDropdownMenu>
          <MkDropdownItem :icon="Setting">修改密码</MkDropdownItem>
          <MkDropdownItem @click.stop class="p-0!">
            <MkDropdown class="w-full" trigger="hover" placement="left-start">
              <div class="flex-between w-full gap-2 p-2">
                <div class="flex items-center gap-2">
                  <MkIcon :icon="Setting" class="text-N600!" />
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
          <MkDropdownItem divided :icon="Setting" @click="handleLogout">退出登录</MkDropdownItem>
        </MkDropdownMenu>
      </div>
    </template>
  </MkDropdown>
</template>
