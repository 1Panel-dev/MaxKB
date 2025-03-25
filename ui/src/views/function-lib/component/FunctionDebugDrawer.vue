<template>
  <el-drawer v-model="debugVisible" size="60%" :append-to-body="true">
    <template #header>
      <div class="flex align-center" style="margin-left: -8px">
        <el-button class="cursor mr-4" link @click.prevent="debugVisible = false">
          <el-icon :size="20">
            <Back />
          </el-icon>
        </el-button>
        <h4>{{ $t('common.debug') }}</h4>
      </div>
    </template>
    <div>
      <div v-if="form.init_field_list.length > 0">
        <h4 class="title-decoration-1 mb-16">
          {{ $t('common.param.initParam') }}
        </h4>
        <el-card shadow="never" class="card-never" style="--el-card-padding: 12px">
          <DynamicsForm
            v-model="form.init_params"
            :model="form.init_params"
            label-position="top"
            require-asterisk-position="right"
            :render_data="form.init_field_list"
            ref="dynamicsFormRef"
          >
          </DynamicsForm>
        </el-card>
      </div>
      <div v-if="form.debug_field_list.length > 0" class="mb-16">
        <h4 class="title-decoration-1 mb-16">
          {{ $t('common.param.inputParam') }}
        </h4>
        <el-card shadow="never" class="card-never" style="--el-card-padding: 12px">
          <el-form
            ref="FormRef"
            :model="form"
            label-position="top"
            require-asterisk-position="right"
            hide-required-asterisk
            v-loading="loading"
            @submit.prevent
          >
            <template v-for="(item, index) in form.debug_field_list" :key="index">
              <el-form-item
                :label="item.name"
                :prop="'debug_field_list.' + index + '.value'"
                :rules="{
                  required: item.is_required,
                  message: $t('views.functionLib.functionForm.form.param.inputPlaceholder'),
                  trigger: 'blur'
                }"
              >
                <template #label>
                  <div class="flex">
                    <span
                    >{{ item.name }} <span class="danger" v-if="item.is_required">*</span></span
                    >
                    <el-tag type="info" class="info-tag ml-4">{{ item.type }}</el-tag>
                  </div>
                </template>
                <el-input
                  v-model="item.value"
                  :placeholder="$t('views.functionLib.functionForm.form.param.inputPlaceholder')"
                />
              </el-form-item>
            </template>
          </el-form>
        </el-card>
      </div>

      <el-button type="primary" @click="submit(FormRef)" :loading="loading">
        {{ $t('views.functionLib.functionForm.form.debug.run') }}
      </el-button>
      <div v-if="showResult" class="mt-8">
        <h4 class="title-decoration-1 mb-16 mt-16">
          {{ $t('views.functionLib.functionForm.form.debug.runResult') }}
        </h4>
        <div class="mb-16">
          <el-alert
            v-if="isSuccess"
            :title="$t('views.functionLib.functionForm.form.debug.runSuccess')"
            type="success"
            show-icon
            :closable="false"
          />
          <el-alert
            v-else
            :title="$t('views.functionLib.functionForm.form.debug.runFailed')"
            type="error"
            show-icon
            :closable="false"
          />
        </div>

        <p class="lighter mb-8">{{ $t('views.functionLib.functionForm.form.debug.output') }}</p>

        <el-card
          :class="isSuccess ? '' : 'danger'"
          class="pre-wrap"
          shadow="never"
          style="max-height: 350px; overflow: scroll"
        >
          {{ String(result) == '0' ? 0 : result || '-' }}
        </el-card>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import functionLibApi from '@/api/function-lib'
import type { FormInstance } from 'element-plus'
import DynamicsForm from '@/components/dynamics-form/index.vue'

const FormRef = ref()
const dynamicsFormRef = ref()
const loading = ref(false)
const debugVisible = ref(false)
const showResult = ref(false)
const isSuccess = ref(false)
const result = ref('')

const form = ref<any>({
  debug_field_list: [],
  code: '',
  input_field_list: [],
  init_field_list: [],
  init_params: {}
})

watch(debugVisible, (bool) => {
  if (!bool) {
    showResult.value = false
    isSuccess.value = false
    result.value = ''
    form.value = {
      debug_field_list: [],
      code: '',
      input_field_list: [],
      init_field_list: [],
      init_params: {}
    }
  }
})

const submit = async (formEl: FormInstance | undefined) => {
  const validate = formEl ? formEl.validate() : Promise.resolve()
  Promise.all([dynamicsFormRef.value?.validate(), validate]).then(() => {
    functionLibApi.postFunctionLibDebug(form.value, loading).then((res) => {
      if (res.code === 500) {
        showResult.value = true
        isSuccess.value = false
        result.value = res.message
      } else {
        showResult.value = true
        isSuccess.value = true
        result.value = res.data
      }
    })
  })
}

const open = (data: any) => {
  if (data.input_field_list.length > 0) {
    data.input_field_list.forEach((item: any) => {
      form.value.debug_field_list.push({
        value: '',
        ...item
      })
    })
  }
  form.value.code = data.code
  form.value.input_field_list = data.input_field_list
  form.value.init_field_list = data.init_field_list
  debugVisible.value = true
}

defineExpose({
  open
})
</script>
<style lang="scss"></style>
