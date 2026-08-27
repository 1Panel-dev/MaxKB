<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { Setting } from '@element-plus/icons-vue'
import DynamicsForm from '@/components/mk-dynamics-form/index.vue'
import { ref } from 'vue'
import { cloneDeep } from 'lodash'
const props = defineProps<{
  label: DynamicFormValue
  modelValue?: DynamicFormValue
  formValue: DynamicFormValue
  view?: boolean
}>()
const emit = defineEmits(['update:modelValue'])
const dialogVisible = ref<boolean>(false)
const dynamicsFormRef = ref<InstanceType<typeof DynamicsForm>>()
const formData = ref<DynamicFormValue>(undefined)
const open = () => {
  if (props.modelValue) {
    formData.value = cloneDeep(props.modelValue)
  }
  dialogVisible.value = true
}
const close = () => {
  dialogVisible.value = false
  formData.value = undefined
}
const submit = () => {
  dynamicsFormRef.value?.validate().then(() => {
    dialogVisible.value = false
    emit('update:modelValue', formData.value)
    formData.value = undefined
  })
}
</script>

<template>
  <div class="flex-between w-full my-required">
    <div>
      <span> {{ label.label }}<span class="color-danger">*</span></span>
    </div>

    <el-tooltip v-if="label.attrs?.tooltip" effect="dark" placement="right">
      <template #content
        ><div style="max-width: 200px">{{ label.attrs.tooltip }}</div></template
      >
      <MkIcon name="icon_warning_filled" class="app-warning-icon" style="flex-shrink: 0"></MkIcon>
    </el-tooltip>
    <el-button type="primary" link @click="open()">
      <MkIcon :icon="Setting"></MkIcon>
    </el-button>
    <el-dialog
      destroy-on-close
      v-model="dialogVisible"
      title="Tips"
      width="500"
      :before-close="close"
    >
      <DynamicsForm
        :read-only="view"
        ref="dynamicsFormRef"
        :render-data="label.children ? label.children : []"
        label-position="top"
        v-model="formData"
        require-asterisk-position="right"
        :model="formData"
      ></DynamicsForm>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="close">取消</el-button>
          <el-button type="primary" @click="submit"> 确定 </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>
