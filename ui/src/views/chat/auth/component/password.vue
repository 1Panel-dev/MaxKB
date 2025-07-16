<template>
  <el-form ref="FormRef" :model="form" @submit.prevent="validator">
    <el-form-item prop="value" :rules="rules.password">
      <el-input show-password v-model="form.password" />
    </el-form-item>
    <el-button class="w-full mt-8" type="primary" @click="validator" :loading="loading">
      {{ $t('common.confirm') }}</el-button
    >
  </el-form>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue'
import useStore from '@/stores'
import { t } from '@/locales'
import { useRoute, useRouter } from 'vue-router'
const FormRef = ref()

const { chatUser } = useStore()
const loading = ref<boolean>(false)
const router = useRouter()
const route = useRoute()

const auth = () => {
  return chatUser.passwordAuthentication(form.value.password).then((ok) => {
    router.push({ name: 'chat', params: { accessToken: chatUser.accessToken }, query: route.query })
  })
}
const validator_auth = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error(t('chat.passwordValidator.errorMessage1')))
  } else {
    auth().catch(() => {
      callback(new Error(t('chat.passwordValidator.errorMessage2')))
    })
  }
}
const validator = () => {
  FormRef.value.validate()
}

const rules = {
  password: [{ required: true, validator: validator_auth, trigger: 'manual' }],
}

const form = ref({
  password: '',
})
</script>
<style lang="scss">
.positioned-mask {
  top: var(--app-header-height);
  height: calc(100% - var(--app-header-height));
  .el-overlay-dialog {
    top: var(--app-header-height);
    height: calc(100% - var(--app-header-height));
  }
}
</style>
