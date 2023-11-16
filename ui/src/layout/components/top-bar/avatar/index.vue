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
      <el-dropdown-menu>
        <el-dropdown-item @click="openResetPassword">
          <AppIcon iconName="Lock"></AppIcon><span style="margin-left: 5px">修改密码</span>
        </el-dropdown-item>
        <el-dropdown-item @click="logout">
          <AppIcon iconName="app-exit"></AppIcon><span style="margin-left: 5px">退出</span>
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
  <ResetPassword ref="resetPasswordRef"></ResetPassword>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import useStore from '@/stores'
import { useRouter } from 'vue-router'
import ResetPassword from './ResetPasssword.vue'
const { user } = useStore()
const router = useRouter()

const resetPasswordRef = ref<InstanceType<typeof ResetPassword>>()

const openResetPassword = () => {
  resetPasswordRef.value?.open()
}

const logout = () => {
  user.logout().then(() => {
    router.push({ name: 'login' })
  })
}
</script>
<style lang="scss" scoped></style>
