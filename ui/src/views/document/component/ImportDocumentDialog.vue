<template>
  <el-dialog
    title="导入文档"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
  >
    <el-form
      label-position="top"
      ref="webFormRef"
      :rules="rules"
      :model="form"
      require-asterisk-position="right"
    >
      <el-form-item label="文档地址" prop="source_url" v-if="isImport">
        <el-input
          v-model="form.source_url"
          placeholder="请输入文档地址，一行一个，地址不正确文档会导入失败。"
          :rows="10"
          type="textarea"
        />
      </el-form-item>
      <el-form-item v-else label="文档地址" prop="source_url">
        <el-input v-model="form.source_url" placeholder="请输入文档地址" />
      </el-form-item>
      <el-form-item label="选择器">
        <el-input
          v-model="form.selector"
          placeholder="默认为 body，可输入 .classname/#idname/tagname"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button type="primary" @click="submit" :loading="loading"> 确定 </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useRoute } from 'vue-router'
import documentApi from '@/api/document'
import { MsgSuccess } from '@/utils/message'

const route = useRoute()
const {
  params: { id }
} = route as any

const emit = defineEmits(['refresh'])
const loading = ref<boolean>(false)
const isImport = ref<boolean>(false)
const form = ref<any>({
  source_url: '',
  selector: ''
})
const documentId = ref('')

const rules = reactive({
  source_url: [{ required: true, message: '请输入 Web 根地址', trigger: 'blur' }]
})

const dialogVisible = ref<boolean>(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      source_url: '',
      selector: ''
    }
    isImport.value = false
  }
})

const open = (row: any) => {
  if (row) {
    documentId.value = row.id
    form.value = row.meta
    isImport.value = false
  } else {
    isImport.value = true
  }
  dialogVisible.value = true
}

const submit = () => {
  if (isImport.value) {
    const obj = {
      source_url_list: form.value.source_url.split('\n'),
      selector: form.value.selector
    }
    documentApi.postWebDocument(id, obj, loading).then((res: any) => {
      MsgSuccess('导入成功')
      emit('refresh')
      dialogVisible.value = false
    })
  } else {
    const obj = {
      meta: form.value
    }
    documentApi.putDocument(id, documentId.value, obj, loading).then((res) => {
      MsgSuccess('设置成功')
      emit('refresh')
      dialogVisible.value = false
    })
  }
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
