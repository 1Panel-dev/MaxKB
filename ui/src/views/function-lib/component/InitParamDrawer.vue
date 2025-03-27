<template>
  <el-drawer v-model="debugVisible" size="60%" :append-to-body="true">
    <template #header>
      <div class="flex align-center" style="margin-left: -8px">
        <el-button class="cursor mr-4" link @click.prevent="debugVisible = false">
          <el-icon :size="20">
            <Back />
          </el-icon>
        </el-button>
        <h4>{{ $t('common.param.initParam') }}</h4>
      </div>
    </template>
    <div>
      <div v-if="form.init_field_list?.length > 0">
        <DynamicsForm
          v-model="form.init_params"
          :model="form.init_params"
          label-position="top"
          require-asterisk-position="right"
          :render_data="form.init_field_list"
          ref="dynamicsFormRef"
        >
        </DynamicsForm>
      </div>

    </div>
    <template #footer>
      <div>
        <el-button type="primary" @click="submit()" :loading="loading">
          {{ $t('common.save') }}
        </el-button
        >
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import functionLibApi from '@/api/function-lib'
import DynamicsForm from '@/components/dynamics-form/index.vue'
import { MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
import { cloneDeep } from 'lodash'

const emit = defineEmits(['refresh'])

const dynamicsFormRef = ref()
const loading = ref(false)
const debugVisible = ref(false)

const form = ref<any>({
  init_params: {}
})

watch(debugVisible, (bool) => {
  if (!bool) {
    form.value = {
      init_params: {},
      is_active: false
    }
  }
})

const submit = async () => {
  dynamicsFormRef.value.validate().then(() => {
    functionLibApi.putFunctionLib(form.value?.id as string, form.value, loading)
      .then((res) => {
        MsgSuccess(t('common.editSuccess'))
        emit('refresh')
        debugVisible.value = false
      })
  })
}

const open = (data: any, is_active: boolean) => {
  if (data) {
    form.value = cloneDeep(data)
    form.value.is_active = is_active
  }
  const init_params = form.value.init_field_list
    .map((item: any) => {
      if (item.show_default_value === false) {
        return { [item.field]: undefined }
      }
      return { [item.field]: item.default_value }
    })
    .reduce((x: any, y: any) => ({ ...x, ...y }), {})
  form.value.init_params = { ...init_params, ...form.value.init_params }
  debugVisible.value = true
}

defineExpose({
  open
})
</script>
<style lang="scss"></style>
