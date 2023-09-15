<template>
    <LoiginLayout>
        <div class="register-form-container">
            <div class="register-form-title">
                <div class="title">
                    <div class="logo"></div>
                    <div>智能客服</div>
                </div>
                <div class="sub-title">修改密码</div>
            </div>
            <el-form class="reset-password-form" ref="resetPasswordFormRef" :model="resetPasswordForm" :rules="rules">

                <el-form-item prop="password">
                    <el-input type="password" size="large" class="input-item" v-model="resetPasswordForm.password"
                        placeholder="请输入密码">

                        <template #prepend>
                            <el-button :icon="Lock" />
                        </template>
                    </el-input>
                </el-form-item>
                <el-form-item prop="re_password">
                    <el-input type="password" size="large" class="input-item" v-model="resetPasswordForm.re_password"
                        placeholder="请输入确认密码">
                        <template #prepend>
                            <el-button :icon="Lock" />
                        </template>
                    </el-input>
                </el-form-item>
            </el-form>
            <el-button type="primary" class="register-button" @click="resetPassword">确认修改</el-button>
            <div class="operate-container">
                <span class="register" @click="router.push('login')">&lt; 返回登陆</span>

            </div>
        </div>
    </LoiginLayout>
</template>
<script setup lang="ts">
import { ref, onMounted } from "vue"
import type { ResetPasswordRequest } from "@/api/user/type"
import { Lock } from '@element-plus/icons-vue'
import LoiginLayout from "@/components/layout/login-layout/index.vue"
import { useRouter, useRoute } from "vue-router"
import { ElMessage } from "element-plus"
import type { FormInstance, FormRules } from 'element-plus'
import UserApi from "@/api/user/index"
const router = useRouter()
const route = useRoute()
const resetPasswordForm = ref<ResetPasswordRequest>({
    password: '',
    re_password: '',
    email: '',
    code: ''
});

onMounted(() => {
    const code = route.params.code;
    const email = route.params.email;
    if (code && email) {
        resetPasswordForm.value.code = code as string;
        resetPasswordForm.value.email = email as string;
    } else {
        router.push('forgot_password')
    }
})


const rules = ref<FormRules<ResetPasswordRequest>>({

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
    re_password: [{
        required: true,
        message: '请输入确认密码',
        trigger: 'blur'
    },
    {
        min: 6,
        max: 30,
        message: "长度在 6 到 30 个字符",
        trigger: "blur",
    },
    {
        validator: (rule, value, callback) => {
            if (resetPasswordForm.value.password != resetPasswordForm.value.re_password) {
                callback(new Error('密码不一致'));
            } else {
                callback();
            }
        },
        trigger: 'blur'
    }],

})
const resetPasswordFormRef = ref<FormInstance>();
const loading = ref<boolean>(false);
const resetPassword = () => {
    resetPasswordFormRef.value?.validate()
        .then(() => UserApi.resetPassword(resetPasswordForm.value, loading))
        .then(() => {
            ElMessage.success("修改密码成功")
            router.push({ name: 'login' })
        })
}

</script>
<style lang="scss" scope>
.register-form-container {
    width: 420px;

    .code-input {
        width: 250px;
    }

    .send-email-button {
        margin-left: 12px;
        width: 158px;
    }

    .register-form-title {
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
            color: #101010;
            font-size: 18px;
        }
    }

    .operate-container {
        margin-top: 12px;
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

    .register-button {
        width: 100%;
        margin-top: 20px;
        height: 40px;
    }
}
</style>
