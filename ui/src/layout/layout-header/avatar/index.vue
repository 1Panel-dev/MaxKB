<template>
  <el-dropdown trigger="click" type="primary">
    <div class="flex-center cursor">
      <el-avatar :size="30">
        <img src="@/assets/user-icon.svg" style="width: 54%" alt=""/>
      </el-avatar>
      <span class="ml-8 color-text-primary ellipsis" :title="user.userInfo?.nick_name">{{ user.userInfo?.nick_name }}</span>
      <el-icon class="el-icon--right">
        <CaretBottom/>
      </el-icon>
    </div>

    <template #dropdown>
      <el-dropdown-menu class="avatar-dropdown">
        <div class="userInfo flex align-center">
          <div class="mr-12 flex align-center">
            <el-avatar :size="30">
              <img src="@/assets/user-icon.svg" style="width: 54%" alt=""/>
            </el-avatar>
          </div>
          <div style="width: 90%">
            <p class="bold mb-4" style="font-size: 14px">{{ user.userInfo?.nick_name }} <span class="color-secondary lighter">({{ user.userInfo?.username }})</span></p>
            <template v-if="user.userInfo?.role_name && user.userInfo.role_name.length > 0">
              <TagGroup
                size="small"
                :tags="role_list"
                v-if="hasPermission([EditionConst.IS_EE, EditionConst.IS_PE], 'OR')"
              />
            </template>
          </div>
        </div>
        <el-dropdown-item
          class="border-t"
          @click="router.push({ path: `/system/user` })"
          v-if="
            hasPermission(
              [
                RoleConst.EXTENDS_ADMIN,
                RoleConst.EXTENDS_WORKSPACE_MANAGE,
                RoleConst.ADMIN,
                RoleConst.WORKSPACE_MANAGE,
              ],
              'OR',
            )
          "
        >
          <div class="flex-between w-full">
            {{ $t('views.system.title') }}
          </div>
        </el-dropdown-item>
        <el-dropdown-item
          @click="openResetPassword"
          v-if="
            hasPermission(
              new ComplexPermission(
                [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE, RoleConst.USER],
                [PermissionConst.CHANGE_PASSWORD],
                [],
                'OR',
              ),
              'OR',
            )
          "
        >
          {{ $t('views.login.resetPassword') }}
        </el-dropdown-item>
        <div>
          <el-dropdown-item
            class="p-8"
            @click="openAPIKeyDialog"
            v-if="
              hasPermission(
                new ComplexPermission(
                  [RoleConst.ADMIN],
                  [PermissionConst.SYSTEM_API_KEY_EDIT],
                  [EditionConst.IS_EE, EditionConst.IS_PE],
                  'OR',
                ),
                'OR',
              )
            "
          >
            {{ $t('layout.apiKey') }}
          </el-dropdown-item>
        </div>
        <el-dropdown-item
          style="padding: 0"
          @click.stop
          v-if="
            hasPermission(
              new ComplexPermission(
                [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE, RoleConst.USER],
                [PermissionConst.SWITCH_LANGUAGE],
                [],
                'OR',
              ),
              'OR',
            )
          "
        >
          <el-dropdown class="w-full" trigger="hover" placement="left-start">
            <div class="flex-between w-full" style="line-height: 22px; padding: 12px 11px">
              <span> {{ $t('layout.language') }}</span>
              <el-icon>
                <ArrowRight/>
              </el-icon>
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
                    <Check/>
                  </el-icon>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-dropdown-item>
        <el-dropdown-item
          @click="openAbout"
          v-if="
              hasPermission(
                new ComplexPermission(
                  [RoleConst.ADMIN, RoleConst.USER, RoleConst.WORKSPACE_MANAGE],
                  [PermissionConst.ABOUT_READ],
                  [],
                  'OR',
                ),
                'OR',
              )
            "
        >
          {{ $t('layout.about.title') }}
        </el-dropdown-item>

        <el-dropdown-item class="border-t" @click="logout">
          {{ $t('layout.logout') }}
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
  <APIKeyDialog :user-id="user.userInfo?.id" ref="APIKeyDialogRef"/>
  <ResetPassword ref="resetPasswordRef"></ResetPassword>
  <AboutDialog ref="AboutDialogRef"></AboutDialog>

  <!-- <UserPwdDialog ref="UserPwdDialogRef" /> -->
</template>
<script setup lang="ts">
import {ref, onMounted, computed} from 'vue'
import useStore from '@/stores'
import { useRouter } from 'vue-router'
import {t} from "@/locales"
import ResetPassword from './ResetPassword.vue'
import AboutDialog from './AboutDialog.vue'
// import UserPwdDialog from '@/views/user-manage/component/UserPwdDialog.vue'
import APIKeyDialog from './APIKeyDialog.vue'
import {ComplexPermission} from '@/utils/permission/type'
import {langList} from '@/locales/index'
import {hasPermission} from '@/utils/permission'
import {PermissionConst, RoleConst, EditionConst} from '@/utils/permission/data'

const {user, login} = useStore()
const router = useRouter()

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
const m:any = {
  "系统管理员": 'layout.about.inner_admin',
  "工作空间管理员": 'layout.about.inner_wsm',
  "普通用户":'layout.about.inner_user'
}
const role_list = computed(() => {
  if (!user.userInfo) {
return []
  }
 return user.userInfo?.role_name?.map(name => {
    const inner = m[name]
    if (inner) {
      return t(inner)
    }
    return name
  })
})
const logout = () => {
  login.logout().then(() => {
    if (user?.userInfo?.source && ['CAS', 'OIDC', 'OAuth2'].includes(user.userInfo.source)) {
      router.push({name: 'login', query: {login_mode: 'manual'}})
    } else {
      router.push({name: 'login'})
    }
  })
}

onMounted(() => {
  if (user.userInfo?.is_edit_password) {
    resetPasswordRef.value?.open()
  }
})
</script>
<style lang="scss" scoped>
.avatar-dropdown {
  min-width: 210px;
  max-width: 400px;

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
