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
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit()" :loading="loading">
          {{ $t('common.modify') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import DynamicsFormConstructor from '@/components/dynamics-form/constructor/index.vue'
import { t } from '@/locales'
const props = withDefaults(
  defineProps<{ title?: string; editFormField: (form_data: any, index: number) => void }>(),
  { title: t('views.template.templateForm.title.editParam') }
)
const dialogVisible = ref<boolean>(false)
const dynamicsFormConstructorRef = ref<InstanceType<typeof DynamicsFormConstructor>>()
const emit = defineEmits(['submit'])
const dynamicsFormData = ref<any>({})
const currentIndex = ref<number>(0)
const loading = ref<boolean>(false)
const open = (form_data: any, index: number) => {
  dialogVisible.value = true
  dynamicsFormData.value = form_data
  currentIndex.value = index
}
const close = () => {
  dialogVisible.value = false
  dynamicsFormData.value = {}
}
const submit = () => {
  dynamicsFormConstructorRef.value?.validate().then(() => {
    props.editFormField(dynamicsFormConstructorRef.value?.getData(), currentIndex.value)
    close()
  })
}
defineExpose({ close, open })
</script>
<style lang="scss" scoped></style>
