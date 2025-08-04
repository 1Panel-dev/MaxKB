<template>
  <el-drawer v-model="show" :with-header="false" class="user-center-drawer" size="100%">
    <div class="flex-center navigation mb-8">
      <el-icon size="16" @click="show = false">
        <ArrowLeftBold />
      </el-icon>
      <h4 class="medium">{{ $t('chat.mine') }}</h4>
    </div>
    <div class="card-item info p-16">
      <el-avatar :size="64">
        <img src="@/assets/user-icon.svg" style="width: 54%" alt="" />
      </el-avatar>
      <h2 class="mt-12 mb-4">{{ chatUser.chatUserProfile?.nick_name }}</h2>
      <div class="color-secondary lighter">
        {{ `${$t('common.username')}: ${chatUser.chatUserProfile?.username}` }}
      </div>
    </div>

    <div
      class="card-item reset-password flex-between"
      v-if="chatUser.chatUserProfile?.source === 'LOCAL'"
      @click="resetPassword"
    >
      <div class="flex align-center">
        <AppIcon iconName="app-key" class="mr-12"></AppIcon>
        <h4 class="lighter">{{ $t('views.login.resetPassword') }}</h4>
      </div>
      <el-icon size="16">
        <ArrowRight />
      </el-icon>
    </div>

    <div
      v-if="chatUser.chatUserProfile?.source === 'LOCAL'"
      class="card-item logout"
      @click="logout"
    >
      <h4 class="lighter">{{ $t('layout.logout') }}</h4>
    </div>

    <ResetPasswordDrawer v-model:show="resetPasswordDrawerShow" />
  </el-drawer>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import useStore from '@/stores'
import { MsgConfirm } from '@/utils/message'
import { t } from '@/locales'
import { useRouter } from 'vue-router'
import ResetPasswordDrawer from './ResetPasswordDrawer.vue'

const router = useRouter()
const { chatUser } = useStore()

const show = defineModel<boolean>('show', {
  required: true,
})

const resetPasswordDrawerShow = ref(false)
function resetPassword() {
  resetPasswordDrawerShow.value = true
}

function logout() {
  MsgConfirm(t('layout.logout'), t('chat.logoutContent'), {
    confirmButtonText: t('layout.logout'),
    confirmButtonClass: 'danger',
  }).then(() => {
    chatUser.logout().then(() => {
      router.push({ name: 'login' })
    })
  })
}
</script>

<style lang="scss">
.user-center-drawer {
  .el-drawer__body {
    padding: 16px;
    padding-top: 0;
    background:
      linear-gradient(187.61deg, rgba(235, 241, 255, 0.2) 39.6%, rgba(231, 249, 255, 0.2) 94.3%),
      #eff0f1;

    .navigation {
      height: 44px;
      position: relative;

      i {
        position: absolute;
        left: 0;
      }
    }

    .card-item {
      background-color: #ffffff;
      border-radius: 8px;
      margin-bottom: 16px;

      &.info {
        display: flex;
        flex-direction: column;
        align-items: center;
      }

      &.logout,
      &.reset-password {
        padding: 13px 16px;
      }

      &.logout {
        color: #f54a45;
        display: flex;
        justify-content: center;
      }
    }
  }
}
</style>
