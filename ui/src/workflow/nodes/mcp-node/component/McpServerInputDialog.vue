<template>
  <el-dialog
    width="600"
    title="设置变量"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :append-to-body="true"
  >
    <el-form label-position="top" ref="formRef" :model="form" require-asterisk-position="right">
      <el-form-item v-for="item in input_field_list" :label="item" :key="item" :prop="item"
                    :rules="{ required: true, message: $t('dynamicsForm.tip.requiredMessage'), trigger: 'blur' }">
        <el-input v-model="form[item]"></el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit(formRef)" :loading="loading">
          {{ $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { FormInstance } from 'element-plus'

const emit = defineEmits<{
  (e: 'refresh', value: any): void;
}>();

const dialogVisible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const form = ref<any>({})

const input_field_list = ref<string[]>([])

function open(vars: string[]) {
  dialogVisible.value = true
  input_field_list.value = vars
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      emit('refresh', form.value)
      dialogVisible.value = false
    }
  })
}


defineExpose({open})
</script>
<style scoped lang="scss">

</style>
