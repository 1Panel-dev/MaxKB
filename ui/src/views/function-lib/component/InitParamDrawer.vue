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
      <div v-if="form.init_field_list.length > 0">
        <DynamicsForm
          v-model="init_form_data"
          :model="init_form_data"
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
const showResult = ref(false)
const isSuccess = ref(false)
const result = ref('')
const init_form_data = ref<any>({})

const form = ref<any>({
  init_field_list: []
})

watch(debugVisible, (bool) => {
  if (!bool) {
    showResult.value = false
    isSuccess.value = false
    result.value = ''
    form.value = {
      init_field_list: []
    }
  }
})

const submit = async () => {
  dynamicsFormRef.value.validate().then(() => {
    form.value.init_field_list.forEach((item: any) => {
      item.value = init_form_data.value[item.field]
    })
    // console.log(init_form_data.value)
    functionLibApi.putFunctionLib(form.value?.id as string, form.value, loading)
      .then((res) => {
        MsgSuccess(t('common.editSuccess'))
        emit('refresh')
        debugVisible.value = false
      })
  })
}

const open = (data: any) => {
  if (data) {
    form.value = cloneDeep(data)
  }
  init_form_data.value = form.value.init_field_list
    .map((item: any) => {
      if (item.value) {
        return { [item.field]: item.value }
      }
      if (item.show_default_value === false) {
        return { [item.field]: undefined }
      }
      return { [item.field]: item.default_value }
    })
    .reduce((x: any, y: any) => ({ ...x, ...y }), {})
  debugVisible.value = true
}

defineExpose({
  open
})
</script>
<style lang="scss"></style>
