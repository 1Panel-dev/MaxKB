<template >
    <el-dropdown trigger="click" size="small" type="primary">
        <el-avatar> {{ firstUserName }} </el-avatar>
        <template #dropdown>
            <el-dropdown-menu>
                <el-dropdown-item @click="openResetPassword">
                    <AppIcon iconName="password"></AppIcon><span style="margin-left:5px">修改密码</span>
                </el-dropdown-item>
                <el-dropdown-item @click="logout">
                    <AppIcon iconName="exit"></AppIcon><span style="margin-left:5px">退出</span>
                </el-dropdown-item>
            </el-dropdown-menu>
        </template>
    </el-dropdown>
    <ResetPassword ref="resetPasswordRef"></ResetPassword>
</template>
<script setup lang="ts">
import { computed, ref } from "vue";
import { useUserStore } from '@/stores/user';
import { useRouter } from "vue-router";
import AppIcon from "@/components/icons/AppIcon.vue"
import ResetPassword from "@/components/layout/top-bar/components/avatar/ResetPasssword.vue"
const userStore = useUserStore()
const router = useRouter()
const firstUserName = computed(() => {
    return userStore.userInfo?.username?.substring(0, 1)
})
const resetPasswordRef = ref<InstanceType<typeof ResetPassword>>();

const openResetPassword = () => {
    resetPasswordRef.value?.open()
}

const logout = () => {
    userStore.logout().then(() => {
        router.push({ name: "login" })
    })
}
</script>
<style lang="scss" scoped>
.el-avatar {
    --el-avatar-size: 30px;
    --el-avatar-bg-color: var(--app-base-action-text-color);
    cursor: pointer;
}

.el-dropdown-menu--small {
    padding: 10px 0;
}
</style>