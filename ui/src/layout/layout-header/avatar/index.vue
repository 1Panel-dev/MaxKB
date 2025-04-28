<template>
  <el-dropdown trigger="click" type="primary">
    <div class="flex-center cursor">
      <AppAvatar>
        <img src="@/assets/user-icon.svg" style="width: 54%" alt="" />
      </AppAvatar>
      <span class="ml-8">{{ user.userInfo?.username }}</span>
      <el-icon class="el-icon--right">
        <CaretBottom />
      </el-icon>
    </div>

    <template #dropdown>
      <el-dropdown-menu class="avatar-dropdown">
        <div class="userInfo">
          <p class="bold mb-4" style="font-size: 14px">{{ user.userInfo?.username }}</p>
          <p>
            <el-text type="info">
              {{ user.userInfo?.email }}
            </el-text>
          </p>
        </div>
        <el-dropdown-item class="border-t p-8" @click="openResetPassword">
          {{ $t('views.login.resetPassword') }}
        </el-dropdown-item>
        <div v-hasPermission="new ComplexPermission([], ['x-pack'], 'OR')">
          <el-dropdown-item class="border-t p-8" @click="openAPIKeyDialog">
            {{ $t('layout.apiKey') }}
          </el-dropdown-item>
        </div>
        <el-dropdown-item class="border-t" style="padding: 0" @click.stop>
          <el-dropdown class="w-full" trigger="hover" placement="left-start">
            <div class="flex-between w-full" style="line-height: 22px; padding: 12px 11px">
              <span> {{ $t('layout.language') }}</span>
              <el-icon><ArrowRight /></el-icon>
            </div>

            <template #dropdown>
              <el-dropdown-menu style="width: 180px">
                <el-dropdown-item
                  v-for="(lang, index) in langList"
                  :key="index"
                  :value="lang.value"
                  @click="changeLang(lang.value)"
                  class="flex-between"
                >
                  <span :class="lang.value === user.userInfo?.language ? 'primary' : ''">{{
                    lang.label
                  }}</span>

                  <el-icon
                    :class="lang.value === user.userInfo?.language ? 'primary' : ''"
                    v-if="lang.value === user.userInfo?.language"
                  >
                    <Check />
                  </el-icon>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-dropdown-item>
        <el-dropdown-item class="border-t" @click="openAbout">
          {{ $t('layout.about.title') }}
        </el-dropdown-item>

        <el-dropdown-item class="border-t" @click="logout">
          {{ $t('layout.logout') }}
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
  <ResetPassword ref="resetPasswordRef"></ResetPassword>
  <AboutDialog ref="AboutDialogRef"></AboutDialog>
  <APIKeyDialog :user-id="user.userInfo?.id" ref="APIKeyDialogRef" />
  <UserPwdDialog ref="UserPwdDialogRef" />
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import useStore from '@/stores'
import { useRouter } from 'vue-router'
import ResetPassword from './ResetPassword.vue'
import AboutDialog from './AboutDialog.vue'
import UserPwdDialog from '@/views/user-manage/component/UserPwdDialog.vue'
import APIKeyDialog from './APIKeyDialog.vue'
import { ComplexPermission } from '@/utils/permission/type'
import { langList } from '@/locales/index'
import { useLocale } from '@/locales/useLocale'
const { user } = useStore()
const router = useRouter()

const UserPwdDialogRef = ref()
const AboutDialogRef = ref()
const APIKeyDialogRef = ref()
const resetPasswordRef = ref<InstanceType<typeof ResetPassword>>()

// const { changeLocale } = useLocale()
const changeLang = (lang: string) => {
  user.postUserLanguage(lang)
  // changeLocale(lang)
}
const openAbout = () => {
  AboutDialogRef.value?.open()
}

function openAPIKeyDialog() {
  APIKeyDialogRef.value.open()
}

const openResetPassword = () => {
  resetPasswordRef.value?.open()
}

const logout = () => {
  user.logout().then(() => {
    router.push({ name: 'login' })
  })
}

onMounted(() => {
  if (user.userInfo?.is_edit_password) {
    UserPwdDialogRef.value.open(user.userInfo)
  }
})
</script>
<style lang="scss" scoped>
.avatar-dropdown {
  min-width: 210px;

  .userInfo {
    padding: 12px 11px;
  }

  :deep(.el-dropdown-menu__item) {
    padding: 12px 11px;
    &:hover {
      background: var(--app-text-color-light-1);
    }
  }
}
</style>
