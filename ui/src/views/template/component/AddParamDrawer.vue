<template>
  <el-drawer
    v-model="drawer"
    :direction="direction"
    size="600"
    :destroy-on-close="true"
    :before-close="cancelClick"
  >
    <template #header>
      <h4>
        {{
          isEdit
            ? $t('views.template.templateForm.title.editParam')
            : $t('views.template.templateForm.title.addParam')
        }}
      </h4>
    </template>
    <template #default>
      <DynamicsFormConstructor
        v-model="currentItem"
        label-position="top"
        require-asterisk-position="right"
        ref="DynamicsFormConstructorRef"
      ></DynamicsFormConstructor>
    </template>
    <template #footer>
      <div style="flex: auto">
        <el-button @click="cancelClick">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="confirmClick()">{{
          isEdit ? $t('common.save') : $t('common.add')
        }}</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { DrawerProps } from 'element-plus'
import { cloneDeep } from 'lodash'
import DynamicsFormConstructor from '@/components/dynamics-form/constructor/index.vue'

const drawer = ref(false)
const direction = ref<DrawerProps['direction']>('rtl')
const isEdit = ref(false)
const DynamicsFormConstructorRef = ref<InstanceType<typeof DynamicsFormConstructor>>()

const currentItem = ref(null)
const currentIndex = ref(null)

const emit = defineEmits(['refresh'])

const open = (row: any, index: any) => {
  if (row) {
    currentItem.value = cloneDeep(row)
    currentIndex.value = index
    isEdit.value = true
  }
  drawer.value = true
}

function cancelClick() {
  drawer.value = false
  isEdit.value = false
  currentItem.value = null
  currentIndex.value = null
}

function confirmClick() {
  const formEl = DynamicsFormConstructorRef.value
  formEl?.validate().then((valid) => {
    if (valid) {
      emit('refresh', formEl?.getData(), currentIndex.value)
      drawer.value = false
      isEdit.value = false
      currentItem.value = null
      currentIndex.value = null
    }
  })
}

defineExpose({ open })
</script>

<style scoped lang="scss"></style>
