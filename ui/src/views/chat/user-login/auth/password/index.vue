<template>
  <div>
    <el-form ref="FormRef" :model="form" @submit.prevent="validator">
      <el-form-item prop="value" :rules="rules">
        <el-input show-password v-model="form.value" />
      </el-form-item>
      <el-button class="w-full mt-8" type="primary" @click="validator" :loading="loading">
        {{ $t('common.confirm') }}</el-button
      >
    </el-form>
  </div>
</template>
<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRoute } from 'vue-router'
import useStore from '@/stores'
import { t } from '@/locales'
const route = useRoute()
const FormRef = ref()
const {
  params: { accessToken },
} = route as any
const { application } = useStore()
const loading = ref<boolean>(false)
const auth = () => {
  return application.asyncAppAuthentication(accessToken, loading, form.value).then(() => {})
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

const rules = reactive({
  value: [{ required: true, validator: validator_auth, trigger: 'manual' }],
})

const form = ref({
  type: 'password',
  value: '',
})
</script>
<style lang="scss" scoped></style>
