<template>
  <el-dialog
    :title="title"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="close"
    append-to-body
  >
    <DynamicsFormConstructor
      v-model="dynamicsFormData"
      label-position="top"
      require-asterisk-position="right"
      ref="dynamicsFormConstructorRef"
    ></DynamicsFormConstructor>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{$t('common.cancel')}} </el-button>
        <el-button type="primary" @click="submit()" :loading="loading"> {{$t('common.add')}} </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import DynamicsFormConstructor from '@/components/dynamics-form/constructor/index.vue'
import { t } from '@/locales'
const props = withDefaults(
  defineProps<{ title?: string; addFormField: (form_data: any) => void }>(),
  { title: t('views.template.templateForm.title.addParam') }
)
const dialogVisible = ref<boolean>(false)
const dynamicsFormConstructorRef = ref<InstanceType<typeof DynamicsFormConstructor>>()
const emit = defineEmits(['submit'])
const dynamicsFormData = ref<any>({})
const loading = ref<boolean>(false)
const open = () => {
  dialogVisible.value = true
}
const close = () => {
  dialogVisible.value = false
  dynamicsFormData.value = {}
}
const submit = () => {
  dynamicsFormConstructorRef.value?.validate().then(() => {
    props.addFormField(dynamicsFormConstructorRef.value?.getData())
    close()
  })
}
defineExpose({ close, open })
</script>
<style lang="scss" scoped></style>
