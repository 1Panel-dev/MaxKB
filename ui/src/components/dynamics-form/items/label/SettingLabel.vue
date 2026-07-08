<template>
  <div class="flex-between w-full my-required">
    <div>
      <span> {{ label.label }}<span class="color-danger">*</span></span>
    </div>

    <el-tooltip v-if="label.attrs?.tooltip" effect="dark" placement="right">
      <template #content
        ><div style="max-width: 200px">{{ label.attrs.tooltip }}</div></template
      >
      <AppIcon iconName="app-warning" class="app-warning-icon" style="flex-shrink: 0"></AppIcon>
    </el-tooltip>
    <el-button v-if="show(label)" type="primary" link @click="open()">
      <AppIcon iconName="app-setting"></AppIcon>
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
        :render_data="label.children ? label.children : []"
        label-position="top"
        v-model="form_data"
        require-asterisk-position="right"
        :model="form_data"
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
<script setup lang="ts">
import DynamicsForm from '@/components/dynamics-form/index.vue'
import { ref } from 'vue'
import { cloneDeep, get } from 'lodash'
const props = defineProps<{
  label: any
  modelValue?: any
  formValue: any
  view?: boolean
}>()
const emit = defineEmits(['update:modelValue'])
const dialogVisible = ref<boolean>(false)
const dynamicsFormRef = ref<InstanceType<typeof DynamicsForm>>()
const form_data = ref<any>(undefined)
const open = () => {
  if (props.modelValue) {
    form_data.value = cloneDeep(props.modelValue)
  }
  dialogVisible.value = true
}
const close = () => {
  dialogVisible.value = false
  form_data.value = undefined
}
/**
 * 当前 field是否展示
 * @param field
 */
const show = (field: any) => {
  if (field.relation_show_field_dict) {
    const keys = Object.keys(field.relation_show_field_dict)
    for (const index in keys) {
      const key = keys[index]
      const v = get(props.formValue, key)
      if (v && v !== undefined && v !== null) {
        const values = field.relation_show_field_dict[key]
        if (values && values.length > 0) {
          return values.includes(v)
        } else {
          return true
        }
      } else {
        return false
      }
    }
  }
  return true
}
const submit = () => {
  dynamicsFormRef.value?.validate().then(() => {
    dialogVisible.value = false
    emit('update:modelValue', form_data.value)
    form_data.value = undefined
  })
}
</script>
<style lang="scss" scoped></style>
