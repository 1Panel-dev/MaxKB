<template>
    <LoiginLayout v-loading="loading">
        <div class="login-form-container">
            <div class="login-form-title">
                <div class="title">
                    <div class="logo"></div>
                    <div>智能客服</div>
                </div>
                <div class="sub-title">欢迎使用智能客服管理平台</div>
            </div>
            <el-form class="login-form" :rules="rules" :model="loginForm" ref="loginFormRef">
                <el-form-item>
                    <el-input size="large" class="input-item" v-model="loginForm.username" placeholder="请输入用户名">
                        <template #prepend>
                            <el-button :icon="UserFilled" />
                        </template>
                    </el-input>

                </el-form-item>
                <el-form-item>
                    <el-input type="password" size="large" class="input-item" v-model="loginForm.password"
                        placeholder="请输入密码">

                        <template #prepend>
                            <el-button :icon="Lock" />
                        </template>
                    </el-input>
                </el-form-item>
            </el-form>
            <div class="operate-container">
                <span class="register" @click="router.push('register')">注册</span>
                <span class="forgot-password" @click="router.push('forgot_password')">忘记密码</span>
            </div>
            <el-button type="primary" class="login-button" @click="login">登录</el-button>
        </div>
    </LoiginLayout>
</template>
<script setup lang="ts">
import { ref } from "vue"
import type { LoginRequest } from "@/api/user/type"
import { UserFilled, Lock } from '@element-plus/icons-vue'
import LoiginLayout from "@/components/layout/login-layout/index.vue"
import { useRouter } from "vue-router"
import type { FormInstance, FormRules } from 'element-plus'
import { useUserStore } from "@/stores/user"

const loading = ref<boolean>(false);
const userStore = useUserStore();
const router = useRouter()
const loginForm = ref<LoginRequest>({
    username: '',
    password: ''
});


const rules = ref<FormRules<LoginRequest>>({
    username: [
        {
            required: true,
            message: "请输入用户名",
            trigger: "blur",
        },
    ],
    password: [
        {
            required: true,
            message: "请输入密码",
            trigger: "blur",
        },
        {
            min: 6,
            max: 30,
            message: "长度在 6 到 30 个字符",
            trigger: "blur",
        },
    ],
})
const loginFormRef = ref<FormInstance>()

const login = () => {
    loginFormRef.value?.validate().then(() => {
        loading.value = true
        userStore.login(loginForm.value.username, loginForm.value.password)
            .then(() => { router.push({ name: 'home' }) })
            .finally(() => loading.value = false)
    })
}

</script>
<style lang="scss" scope>
.login-form-container {
    width: 420px;


    .login-form-title {
        width: 100%;
        margin-bottom: 30px;

        .title {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;

            .logo {
                background-image: url('@/assets/logo.png');
                background-size: 100% 100%;
                width: 48px;
                height: 48px;
            }

            font-size: 28px;
            font-weight: 900;
            color: #101010;
            height: 60px;

        }

        .sub-title {
            display: flex;
            align-items: center;
            justify-content: center;
            color: #101010;
            font-size: 18px;
        }




    }

    .operate-container {
        color: rgba(51, 112, 255, 1);
        display: flex;
        justify-content: space-between;

        .register {
            cursor: pointer;
        }

        .forgot-password {
            cursor: pointer;
        }
    }

    .login-button {
        width: 100%;
        margin-top: 20px;
        height: 40px;
    }
}
</style>
