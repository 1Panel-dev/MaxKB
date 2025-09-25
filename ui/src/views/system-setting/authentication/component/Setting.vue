<template>
  <div class="authentication-setting__main main-calc-height">
    <el-scrollbar>
      <div class="form-container p-24" v-loading="loading">
        <el-form ref="authFormRef" :model="form" label-position="top"
                 require-asterisk-position="right" @submit.prevent>
          <!-- 登录方式选择框 -->
          <el-form-item
            :label="$t('views.system.default_login')"
            :rules="[
              {
                required: true,
                message: $t('views.applicationOverview.appInfo.LimitDialog.loginMethodRequired'),
                trigger: 'change',
              },
            ]"
            prop="default_value"
            style="padding-top: 16px"
          >
            <el-radio-group v-model="form.default_value" class="radio-group">
              <el-radio
                v-for="method in loginMethods"
                :key="method.value"
                :label="method.value"
                class="radio-item"
              >
                {{ method.label }}
              </el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item
            :label="$t('views.system.display_code')"
            :rules="[
              {
                required: true,
                message: $t('views.applicationOverview.appInfo.LimitDialog.displayCodeRequired'),
                trigger: 'change',
              },
            ]"
            prop="max_attempts"
          >
            <span style="font-size: 13px;">
      {{ $t('views.system.loginFailed') }}
    </span>
            <el-input-number
              style="margin-left: 8px;"
              v-model="form.max_attempts"
              :min="-1"
              :max="10"
              :step="1"
              controls-position="right"
            />
            <span style="margin-left: 8px; font-size: 13px;">
      {{ $t('views.system.loginFailedMessage') }}
    </span>
            <span style="margin-left: 8px; color: #909399; font-size: 12px;">
      ({{ $t('views.system.display_codeTip') }})
    </span>
          </el-form-item>
        </el-form>
        <div style="margin-top:16px;">
            <span
              v-hasPermission="
                new ComplexPermission([RoleConst.ADMIN], [PermissionConst.LOGIN_AUTH_EDIT], [], 'OR')
              "
              class="mr-12"
            >
              <el-button @click="submit(authFormRef)" type="primary" :disabled="loading">
                {{ $t('common.save') }}
              </el-button>
            </span>
        </div>
      </div>
    </el-scrollbar>
  </div>
</template>

<script setup lang="ts">
import {ref, onMounted, reactive} from "vue";
import {ComplexPermission} from "@/utils/permission/type";
import {PermissionConst, RoleConst} from "@/utils/permission/data";
import type {FormInstance, FormRules} from 'element-plus';
import {t} from "@/locales";
import authApi from "@/api/system-settings/auth-setting.ts";
import {MsgSuccess} from "@/utils/message.ts";

const loginMethods = ref<Array<{ label: string; value: string }>>([]);
const loading = ref(false);
const authFormRef = ref<FormInstance>();


const form = ref<any>({
  default_value: 'LOCAL',
  max_attempts: 1,
})

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return;
  await formEl.validate((valid, fields) => {
    if (valid) {
      const params = {
        default_value: form.value.default_value,
        max_attempts: form.value.max_attempts,
      };
      authApi.putLoginSetting(params, loading).then((res) => {
        MsgSuccess(t('common.saveSuccess'))
      })
    } else {
      console.log('error submit!', fields);
    }
  });
};


onMounted(() => {
  authApi.getLoginSetting().then((res) => {
    if (Object.keys(res.data).length > 0) {
      form.value = res.data;
      loginMethods.value = res.data.auth_types
    }
  })
});
</script>

<style scoped>
.radio-group {
  display: flex;
  flex-wrap: wrap;
  flex-direction: row;
}
</style>
