<template>
  <div v-if="userInputFieldList.length > 0" class="mb-16">
    <h4 class="title-decoration-1 mb-16">
      {{ $t('common.param.inputParam') }}
    </h4>
    <el-card shadow="never" class="card-never" style="--el-card-padding: 12px">
      <el-form
        ref="formRef"
        :model="userInputForm"
        label-position="top"
        require-asterisk-position="right"
        hide-required-asterisk
        @submit.prevent
      >
        <template v-for="(item, index) in userInputFieldList" :key="index">
          <el-form-item
            :label="item.label"
            :prop="item.field"
            :rules="{
              required: item.is_required,
              message: $t('views.tool.form.param.inputPlaceholder'),
              trigger: 'blur',
            }"
          >
            <template #label>
              <div class="flex">
                <span
                  >{{ item.label }}
                  <span class="color-danger" v-if="item.is_required">*</span></span
                >
                <el-tag type="info" class="info-tag ml-4">{{ item.type }}</el-tag>
              </div>
            </template>
            <el-input
              v-if="['string'].includes(item.type)"
              v-model="userInputForm[item.field]"
              :placeholder="$t('views.tool.form.param.inputPlaceholder')"
            />
            <JsonInput
              v-if="['array', 'dict'].includes(item.type)"
              v-model="userInputForm[item.field]"
            />
            <el-input-number
              v-if="['int', 'float'].includes(item.type)"
              v-model="userInputForm[item.field]"
            />
            <el-switch
              v-if="['boolean'].includes(item.type)"
              v-model="userInputForm[item.field]"
              :active-value="true"
              :inactive-value="false"
            />
          </el-form-item>
        </template>
      </el-form>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import JsonInput from '@/components/dynamics-form/items/JsonInput.vue'
import { FormInstance } from 'element-plus'
const props = defineProps<{
  workflow: any
}>()
const userInputFieldList = computed(() => {
  return (
    props.workflow?.nodes?.find((node: any) => node.id === 'tool-base-node')?.properties
      ?.user_input_field_list || []
  )
})
const formRef = ref<FormInstance>()
const userInputForm = ref<any>({})
const validate = () => {
  return formRef.value?.validate()
}
const getData = () => {
  return userInputForm.value
}
defineExpose({ validate, getData })
</script>
<style lang="scss" scoped></style>
