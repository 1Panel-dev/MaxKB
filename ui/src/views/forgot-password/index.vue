<template>
    <LoiginLayout>
        <div class="register-form-container">
            <div class="register-form-title">
                <div class="title">
                    <div class="logo"></div>
                    <div>智能客服</div>
                </div>
                <div class="sub-title">忘记密码</div>
            </div>
            <el-form class="register-form" ref="resetPasswordFormRef" :model="CheckEmailForm" :rules="rules">

                <el-form-item prop="email">
                    <el-input size="large" class="input-item" v-model="CheckEmailForm.email" placeholder="请输入邮箱">

                        <template #prepend>
                            <el-button :icon="UserFilled" />
                        </template>
                    </el-input>
                </el-form-item>
                <el-form-item prop="code">
                    <el-input size="large" class="code-input" v-model="CheckEmailForm.code" placeholder="请输入验证码">

                        <template #prepend>
                            <el-button :icon="Key" />
                        </template>
                    </el-input>
                    <el-button size="large" class="send-email-button" @click="sendEmail"
                        :loading="loading">获取验证码</el-button>
                </el-form-item>
            </el-form>
            <el-button type="primary" class="register-button" @click="checkCode">立即验证</el-button>
            <div class="operate-container">
                <span class="register" @click="router.push('login')">&lt; 返回登陆</span>

            </div>
        </div>
    </LoiginLayout>
</template>
<script setup lang="ts">
import { ref } from "vue"
import { UserFilled, Key } from '@element-plus/icons-vue'
import type {
    CheckCodeRequest
} from "@/api/user/type"
import LoiginLayout from "@/components/layout/login-layout/index.vue"
import { useRouter } from "vue-router"
import type { FormInstance, FormRules } from 'element-plus'
import UserApi from "@/api/user/index"
import { ElMessage } from "element-plus"

const router = useRouter()
const CheckEmailForm = ref<CheckCodeRequest>({
    email: "",
    code: "",
    type: 'reset_password'
});

const resetPasswordFormRef = ref<FormInstance>()
const rules = ref<FormRules<CheckCodeRequest>>({
    email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        {
            validator: (rule, value, callback) => {
                const emailRegExp = /^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$/
                if ((!emailRegExp.test(value) && value != '')) {
                    callback(new Error('请输入有效邮箱格式！'));
                } else {
                    callback();
                }
            },
            trigger: 'blur'
        }
    ],
    code: [
        { required: true, message: '请输入验证码' }
    ]

})
const loading = ref<boolean>(false)

const checkCode = () => {
    resetPasswordFormRef.value?.validate()
        .then(() => UserApi.checkCode(CheckEmailForm.value, loading))
        .then(() => router.push({ name: 'reset_password', params: CheckEmailForm.value }))
}
/**
 * 发送验证码
 */
const sendEmail = () => {
    resetPasswordFormRef.value?.validateField("email", (v: boolean) => {
        if (v) {
            UserApi.sendEmit(CheckEmailForm.value.email, "reset_password", loading)
                .then(() => {
                    ElMessage.success("发送验证码成功")
                })

        }
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
