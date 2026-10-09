<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import DocumentStrategyForm from '@/views/knowledge/create-knowledge/components/DocumentStrategyForm.vue'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'WebImportDocumentDrawer' })
const props = defineProps<{ api: typeof DocumentApi; knowledgeId: string }>()
const emit = defineEmits<{ refresh: []; closed: [] }>()

/* Web 地址与处理策略 */
const visible = ref(false)
const loading = ref(false)
const activeStep = ref(0)
const strategyMounted = ref(false)
const form = ref({ source_url: '', selector: '' })
const sourceUrls = computed(() => [
  ...new Set(
    form.value.source_url
      .split(/\r?\n/)
      .map((url) => url.trim())
      .filter(Boolean),
  ),
])
const formRef = ref<FormInstance>()
const strategyRef = useTemplateRef<InstanceType<typeof DocumentStrategyForm>>('strategyRef')
const rules: FormRules = {
  source_url: [{ required: true, whitespace: true, message: '请输入文档地址', trigger: 'blur' }],
}
function open() {
  visible.value = true
}
function handleNext() {
  if (loading.value) return
  return formRef.value
    ?.validate()
    .then(() => {
      strategyMounted.value = true
      activeStep.value = 1
    })
    .catch(() => {
      /* 表单展示校验错误。 */
    })
}
function handleSubmit() {
  if (loading.value || !strategyRef.value) return
  loading.value = true
  return strategyRef.value
    .validate()
    .then((valid) => {
      if (!valid || !strategyRef.value) return
      return props.api
        .postWebDocument(props.knowledgeId, {
          source_url_list: sourceUrls.value,
          selector: form.value.selector.trim() || 'body',
          doc_strategy: strategyRef.value.getStrategy(),
        })
        .then(() => {
          MsgSuccess('导入成功')
          visible.value = false
          emit('refresh')
        })
    })
    .catch(() => {
      /* 请求层统一提示错误，保留地址与策略。 */
    })
    .finally(() => {
      loading.value = false
    })
}
defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" direction="btt" @closed="emit('closed')">
    <template #header>
      <div class="flex w-full">
        <h4>导入文档</h4>
        <el-steps :active="activeStep" finish-status="success" class="absolute-center w-85!">
          <el-step title="基本信息" />
          <el-step title="文档处理策略" />
        </el-steps>
      </div>
    </template>
    <div v-loading="loading" class="mx-auto w-full max-w-200">
      <section v-show="activeStep === 0">
        <h4 class="mb-4 mk-title-decoration">基本信息</h4>
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" require-asterisk-position="right" @submit.prevent>
          <el-form-item label="文档地址" prop="source_url">
            <el-input v-model="form.source_url" type="textarea" :rows="5" placeholder="请输入文档地址，一行一个，地址不正确文档会导入失败。" />
          </el-form-item>
          <el-form-item label="选择器">
            <el-input v-model="form.selector" placeholder="默认为 body，可输入 .classname/#idname/tagname" />
          </el-form-item>
        </el-form>
      </section>
      <section v-if="strategyMounted" v-show="activeStep === 1">
        <h4 class="mb-4 mk-title-decoration">文档处理策略</h4>
        <DocumentStrategyForm ref="strategyRef" />
      </section>
    </div>
    <template #footer>
      <!-- 取消导入 -->
      <el-button :disabled="loading" @click="visible = false">取消</el-button>
      <!-- 返回基本信息 -->
      <el-button v-if="activeStep === 1" :disabled="loading" @click="activeStep = 0">上一步</el-button>
      <!-- 进入文档处理策略 -->
      <el-button v-if="activeStep === 0" type="primary" @click="handleNext">下一步</el-button>
      <!-- 提交 Web 文档导入 -->
      <el-button v-else type="primary" :loading="loading" @click="handleSubmit">开始导入</el-button>
    </template>
  </MkDrawer>
</template>
