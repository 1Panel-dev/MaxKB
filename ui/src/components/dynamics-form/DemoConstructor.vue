<template>
  <el-row :gutter="12">
    <el-col :span="12">
      <el-card shadow="never">
        <DynamicsFormConstructor
          v-model="item"
          label-position="top"
          require-asterisk-position="right"
          ref="DynamicsFormConstructorRef"
        ></DynamicsFormConstructor>
        <el-button @click="add_field">添加</el-button>
      </el-card></el-col
    >
    <el-col :span="12">
      <el-card shadow="never">
        <DynamicsForm
          label-position="top"
          require-asterisk-position="right"
          v-model="form_data"
          :model="form_data"
          :render_data="form_item_list"
          ref="dynamicsFormRef"
        >
        </DynamicsForm>
        <el-button @click="validate">校验</el-button>
      </el-card></el-col
    >
  </el-row>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import DynamicsFormConstructor from '@/components/dynamics-form/constructor/index.vue'
import DynamicsForm from '@/components/dynamics-form/index.vue'
const DynamicsFormConstructorRef = ref<InstanceType<typeof DynamicsFormConstructor>>()

const form_item_list = ref<Array<any>>([])
const add_field = () => {
  if (DynamicsFormConstructorRef.value) {
    DynamicsFormConstructorRef.value.validate().then(() => {
      form_item_list.value.push(DynamicsFormConstructorRef.value?.getData())
    })
  }
}

const form_data = ref({})
const item = ref({})
const dynamicsFormRef = ref<InstanceType<typeof DynamicsForm>>()
const validate = () => {
  dynamicsFormRef.value
    ?.validate()
    .then((ok) => {})
    .catch((e) => {})
}
</script>
<style lang="scss"></style>
