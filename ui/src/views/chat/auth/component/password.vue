<template>
  <el-dialog
    :modelValue="show"
    modal-class="positioned-mask"
    width="300"
    :title="$t('chat.passwordValidator.title')"
    custom-class="no-close-button"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
    top="25vh"
    center
    :modal="true"
  >
    <el-form ref="FormRef" :model="form" @submit.prevent="validator">
      <el-form-item prop="value" :rules="rules.value">
        <el-input show-password v-model="form.value" />
      </el-form-item>
      <el-button class="w-full mt-8" type="primary" @click="validator" :loading="loading">
        {{ $t('common.confirm') }}</el-button
      >
    </el-form>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import useStore from '@/stores'
import { t } from '@/locales'
const route = useRoute()
const FormRef = ref()
const {
  params: { accessToken }
} = route as any
const { application } = useStore()
const props = defineProps<{ applicationProfile: any; modelValue: boolean }>()
const loading = ref<boolean>(false)
const show = computed(() => {
  if (props.applicationProfile) {
    if (props.modelValue) {
      return false
    }
    return props.applicationProfile.authentication
  }
  return false
})
const emit = defineEmits(['update:modelValue'])
const auth = () => {
  return application.asyncAppAuthentication(accessToken, loading, form.value).then(() => {
    emit('update:modelValue', true)
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
  value: [{ required: true, validator: validator_auth, trigger: 'manual' }]
}

const form = ref({
  type: 'password',
  value: ''
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
