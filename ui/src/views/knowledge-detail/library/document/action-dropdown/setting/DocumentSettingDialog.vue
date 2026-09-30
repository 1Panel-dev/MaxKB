<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import type { FormInstance } from 'element-plus'
import { DOCUMENT_HIT_HANDLING } from '@/api/enums'
import type { DocumentItem, DocumentSettingPayload } from '@/api/types'
import { KNOWLEDGE_TYPE_KEY } from '@/constants/knowledge'
import { DOCUMENT_HIT_HANDLING_LABELS } from '@/constants/document'
import { cloneDeep } from 'lodash'

defineOptions({ name: 'DocumentSettingDialog' })
const props = defineProps<{ loading: boolean; batch?: boolean }>()
const emit = defineEmits<{ submit: [data: DocumentSettingPayload]; closed: [] }>()
const route = useRoute()
const knowledgeType = computed(() => route.params.type)
const visible = ref(false)
const formRef = ref<FormInstance>()
const document = ref<DocumentItem>()
const form = ref({
  hit_handling_method: DOCUMENT_HIT_HANDLING.OPTIMIZATION as DocumentSettingPayload['hit_handling_method'],
  directly_return_similarity: 0.9,
  source_url: '',
  selector: '',
  allow_download: true,
})

// 单项设置回填文档，批量设置使用默认值。
function open(current?: DocumentItem) {
  document.value = current ? cloneDeep(current) : undefined
  form.value = {
    hit_handling_method: current?.hit_handling_method ?? DOCUMENT_HIT_HANDLING.OPTIMIZATION,
    directly_return_similarity: current?.directly_return_similarity ?? 0.9,
    source_url: String(current?.meta?.source_url ?? ''),
    selector: String(current?.meta?.selector ?? ''),
    allow_download: current?.meta?.allow_download !== false,
  }
  visible.value = true
}

async function handleSubmit() {
  if (props.loading || !(await formRef.value?.validate().catch(() => false))) return
  const data: DocumentSettingPayload = {
    hit_handling_method: form.value.hit_handling_method,
    directly_return_similarity: form.value.directly_return_similarity,
  }
  if (document.value) {
    data.meta = { ...document.value.meta, allow_download: form.value.allow_download }
    if (knowledgeType.value === KNOWLEDGE_TYPE_KEY.WEB) {
      data.meta.source_url = form.value.source_url.trim()
      data.meta.selector = form.value.selector
    }
  } else {
    data.allow_download = form.value.allow_download
  }
  emit('submit', data)
}

function close() {
  visible.value = false
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog v-model="visible" title="文档设置" @closed="emit('closed')">
    <el-form ref="formRef" :model="form" label-position="top" require-asterisk-position="right" @submit.prevent>
      <template v-if="!batch && knowledgeType === KNOWLEDGE_TYPE_KEY.WEB">
        <el-form-item label="文档地址" prop="source_url" :rules="[{ required: true, whitespace: true, message: '请输入文档地址', trigger: 'blur' }]">
          <el-input v-model="form.source_url" />
        </el-form-item>
        <el-form-item label="选择器"><el-input v-model="form.selector" placeholder="默认为 body，可输入 .classname/#idname/tagname"/></el-form-item>
      </template>
      <el-form-item label="召回处理">
        <el-radio-group v-model="form.hit_handling_method">
          <template v-for="(label, value) in DOCUMENT_HIT_HANDLING_LABELS" :key="value">
            <el-radio :value="value">{{ label }}</el-radio>
          </template>
        </el-radio-group>
      </el-form-item>
      <el-form-item v-if="form.hit_handling_method === DOCUMENT_HIT_HANDLING.DIRECTLY_RETURN" label="相似度阈值">
        <el-input-number
          v-model="form.directly_return_similarity"
          :min="0"
          :max="1"
          :precision="3"
          :step="0.1"
          :value-on-clear="0"
          controls-position="right"
          align="left"
        />
      </el-form-item>
      <el-checkbox v-model="form.allow_download">{{ knowledgeType === KNOWLEDGE_TYPE_KEY.WEB ? '允许预览' : '允许下载' }}</el-checkbox>
    </el-form>
    <template #footer>
      <!-- 取消文档设置 -->
      <el-button :disabled="loading" @click="visible = false">取消</el-button>
      <!-- 保存文档设置 -->
      <el-button type="primary" :loading="loading" @click="handleSubmit">确认</el-button>
    </template>
  </MkDialog>
</template>
