<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import type { FormInstance, FormRules } from 'element-plus'
import DocumentStrategyForm from '@/views/knowledge/create-knowledge/components/DocumentStrategyForm.vue'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'WebImportDocumentDrawer' })
const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{ api: ReturnType<typeof useKnowledgeDetailContext>['resourceApi']['document']; knowledgeId: string }>()
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
const rules = computed<FormRules<typeof form.value>>(() => ({
  source_url: [{ required: true, whitespace: true, message: t('knowledge.document.sourceUrl.requiredMessage'), trigger: 'blur' }],
}))
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
        .postWebDocument?.(props.knowledgeId, {
          source_url_list: sourceUrls.value,
          selector: form.value.selector.trim() || 'body',
          doc_strategy: strategyRef.value.getStrategy(),
        })
        .then(() => {
          MsgSuccess(t('common.messages.importSuccess'))
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
        <h4>{{ t('knowledge.document.import.title') }}</h4>
        <el-steps :active="activeStep" finish-status="success" class="absolute-center w-85!">
          <el-step :title="t('common.labels.basicInfo')" />
          <el-step :title="t('knowledge.documentStrategy.title')" />
        </el-steps>
      </div>
    </template>
    <div v-loading="loading" class="mx-auto w-full max-w-200">
      <section v-show="activeStep === 0">
        <h4 class="mb-4 mk-title-decoration">{{ t('common.labels.basicInfo') }}</h4>
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          :validate-on-rule-change="false"
          label-position="top"
          require-asterisk-position="right"
          @submit.prevent
        >
          <el-form-item :label="t('knowledge.document.sourceUrl.label')" prop="source_url">
            <el-input v-model="form.source_url" type="textarea" :rows="5" :placeholder="t('knowledge.document.sourceUrl.placeholder')" />
          </el-form-item>
          <el-form-item :label="t('knowledge.fields.selector.label')">
            <el-input v-model="form.selector" :placeholder="t('knowledge.fields.selector.placeholder')" />
          </el-form-item>
        </el-form>
      </section>
      <section v-if="strategyMounted" v-show="activeStep === 1">
        <h4 class="mb-4 mk-title-decoration">{{ t('knowledge.documentStrategy.title') }}</h4>
        <DocumentStrategyForm ref="strategyRef" />
      </section>
    </div>
    <template #footer>
      <!-- 取消导入 -->
      <el-button plain :disabled="loading" @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 返回基本信息 -->
      <el-button plain v-if="activeStep === 1" :disabled="loading" @click="activeStep = 0">{{ t('common.actions.previous') }}</el-button>
      <!-- 进入文档处理策略 -->
      <el-button v-if="activeStep === 0" type="primary" @click="handleNext">{{ t('common.actions.next') }}</el-button>
      <!-- 提交 Web 文档导入 -->
      <el-button v-else type="primary" :loading="loading" @click="handleSubmit">{{ t('knowledge.document.import.start') }}</el-button>
    </template>
  </MkDrawer>
</template>
