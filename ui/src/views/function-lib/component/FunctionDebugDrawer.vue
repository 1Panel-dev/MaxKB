<template>
  <el-drawer v-model="dubugVisible" size="60%" :append-to-body="true">
    <template #header>
      <div class="flex align-center" style="margin-left: -8px">
        <el-button class="cursor mr-4" link @click.prevent="dubugVisible = false">
          <el-icon :size="20">
            <Back />
          </el-icon>
        </el-button>
        <h4>调试</h4>
      </div>
    </template>
    <div>
      <h4 class="title-decoration-1 mb-16">输入变量</h4>
      <el-card shadow="never" class="card-never" style="--el-card-padding: 12px">
        <el-form
          ref="FormRef"
          :model="form"
          :rules="rules"
          label-position="top"
          require-asterisk-position="right"
          hide-required-asterisk
          v-loading="loading"
        >
          <template v-for="(item, index) in form.debug_field_list" :key="index">
            <el-form-item
              :label="item.name"
              :rules="{
                required: item.is_required,
                message: '请输入变量值',
                trigger: 'blur'
              }"
            >
              <template #label>
                <div class="flex">
                  <span>{{ item.name }} <span class="danger" v-if="item.is_required">*</span></span>
                  <el-tag type="info" class="info-tag ml-4">{{ item.type }}</el-tag>
                </div>
              </template>
              <el-input v-model="item.value" placeholder="请输入变量值" />
            </el-form-item>
          </template>
        </el-form>
      </el-card>
      <el-button type="primary" class="mt-16"> 运行 </el-button>

      <h4 class="title-decoration-1 mb-16 mt-16">运行结果</h4>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import functionLibApi from '@/api/function-lib'
import type { FormInstance } from 'element-plus'
import { MsgSuccess } from '@/utils/message'
import { cloneDeep } from 'lodash'

const emit = defineEmits(['refresh'])
const FormRef = ref()
const loading = ref(false)
const dubugVisible = ref(false)
const showEditor = ref(false)

const form = ref<any>({
  debug_field_list: []
})

watch(dubugVisible, (bool) => {
  if (!bool) {
    showEditor.value = true
    form.value = {
      debug_field_list: []
    }
  }
})

const rules = reactive({
  name: [{ required: true, message: '请输入函数名称', trigger: 'blur' }]
})

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid: any) => {
    if (valid) {
      functionLibApi.postFunctionLibDebug(form.value?.id, form.value, loading).then((res) => {
        MsgSuccess('创建成功')
        emit('refresh')
        dubugVisible.value = false
      })
    }
  })
}

const open = (list: any) => {
  if (list) {
    list.forEach((item: any) => {
      form.value.debug_field_list.push({
        value: '',
        ...item
      })
    })
  }
  dubugVisible.value = true
}

defineExpose({
  open
})
</script>
<style lang="scss"></style>
