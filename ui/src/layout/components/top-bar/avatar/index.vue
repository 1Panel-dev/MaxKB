<template>
  <el-dropdown trigger="click" type="primary">
    <AppAvatar :name="user.userInfo?.username" />
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
