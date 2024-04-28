<template>
  <el-dialog
    title="设置"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    width="400"
  >
    <el-form
      label-position="top"
      ref="webFormRef"
      :rules="rules"
      :model="form"
      require-asterisk-position="right"
    >
      <el-form-item>
        <template #label>
          <div class="flex align-center">
            <span class="mr-4">命中处理方式</span>
            <el-tooltip
              effect="dark"
              content="用户提问时，命中文档下的分段时按照设置的方式进行处理。"
              placement="right"
            >
              <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
            </el-tooltip>
          </div>
        </template>
        <el-radio-group v-model="form.hit_handling_method">
          <template v-for="(value, key) of hitHandlingMethod" :key="key">
            <el-radio :value="key">{{ value }}</el-radio>
          </template>
        </el-radio-group>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button type="primary" @click="submit(webFormRef)" :loading="loading"> 确定 </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import documentApi from '@/api/document'
import { MsgSuccess } from '@/utils/message'
import { hitHandlingMethod } from '../utils'

const route = useRoute()
const {
  params: { id }
} = route as any

const emit = defineEmits(['refresh'])
const webFormRef = ref()
const loading = ref<boolean>(false)
const documentList = ref<Array<string>>([])
const form = ref<any>({
  hit_handling_method: 'optimization'
})

const rules = reactive({
  source_url: [{ required: true, message: '请输入文档地址', trigger: 'blur' }]
})

const dialogVisible = ref<boolean>(false)

const open = (list: Array<string>) => {
  documentList.value = list
  dialogVisible.value = true
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      const obj = {
        hit_handling_method: form.value.hit_handling_method,
        id_list: documentList.value
      }
      documentApi.batchEditHitHandling(id, obj, loading).then((res: any) => {
        MsgSuccess('设置成功')
        emit('refresh')
        dialogVisible.value = false
      })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
