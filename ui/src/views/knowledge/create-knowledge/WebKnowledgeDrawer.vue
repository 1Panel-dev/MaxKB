<script setup lang="ts">
import { ref, useTemplateRef, reactive } from 'vue'
import { KNOWLEDGE_TYPE_MAP } from '@/constants/knowledge'
import { useRoute, useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import type SystemSharedKnowledgeApi from '@/api/admin/system/shared-resources/knowledge/knowledge'
import { KNOWLEDGE_TYPE } from '@/api/enums'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'
import DocumentStrategyForm from './components/DocumentStrategyForm.vue'
import KnowledgeBaseForm from './components/KnowledgeBaseForm.vue'

defineOptions({ name: 'CreateWebKnowledgeDrawer' })
const props = defineProps<{ api: typeof KnowledgeApi | typeof SystemSharedKnowledgeApi; folderId: string }>()
const emit = defineEmits<{ refresh: [] }>()
const { auth } = useStore()
const route = useRoute()
const router = useRouter()

/* 创建表单 */
const baseFormRef = useTemplateRef<InstanceType<typeof KnowledgeBaseForm>>('baseFormRef')
const drawerVisible = ref(false)
const loading = ref(false)
const activeStep = ref(0)
const strategyFormRef = useTemplateRef<InstanceType<typeof DocumentStrategyForm>>('strategyFormRef')
const knowledgeFormRef = ref<FormInstance>()
const knowledgeForm = reactive({ source_url: '', selector: '' })
const knowledgeFormRules: FormRules<typeof knowledgeForm> = {
  source_url: [{ required: true, whitespace: true, message: '请输入 Web 根地址', trigger: 'blur' }],
}

function resetData() {
  baseFormRef.value?.reset()
  Object.assign(knowledgeForm, { source_url: '', selector: '' })
  knowledgeFormRef.value?.clearValidate()
  loading.value = false
  activeStep.value = 0
}

function open() {
  drawerVisible.value = true
}

function handleNext() {
  if (loading.value) return
  loading.value = true
  return Promise.all([baseFormRef.value?.validate(), knowledgeFormRef.value?.validate().catch(() => false)])
    .then((results) => {
      if (results.every(Boolean)) activeStep.value = 1
    })
    .finally(() => {
      loading.value = false
    })
}

/* 校验并创建，成功后刷新资料并进入文档列表 */
function submit() {
  if (loading.value) return
  loading.value = true
  return Promise.all([baseFormRef.value?.validate(), knowledgeFormRef.value?.validate().catch(() => false), strategyFormRef.value?.validate()])
    .then((validationResults) => {
      if (!validationResults.every(Boolean) || !baseFormRef.value) return
      const baseForm = baseFormRef.value.form
      return props.api.postWebKnowledge({
          name: baseForm.name.trim(),
          desc: baseForm.desc.trim(),
          embedding_model_id: baseForm.embedding_model_id,
          folder_id: props.folderId,
          type: KNOWLEDGE_TYPE.WEB,
          source_url: knowledgeForm.source_url.trim(),
          selector: knowledgeForm.selector.trim(),
          doc_strategy: strategyFormRef.value?.getStrategy(),
        }).then((knowledge) => {
          return auth.loadAuthBaseProfile().then(() => {
            MsgSuccess('创建成功')
            drawerVisible.value = false
            emit('refresh')
            return router.push({
              name: 'workspace-knowledge-document-list',
              params: { knowledgeId: knowledge.id, type: KNOWLEDGE_TYPE_MAP[knowledge.type], workspaceId: route.params.workspaceId },
            })
          })
        })
    })
    .finally(() => {
      loading.value = false
    })
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="drawerVisible" direction="btt" content-class="h-full p-0!" @closed="resetData">
    <template #header>
      <div class="flex w-full">
        <h4>创建 Web 知识库</h4>
        <el-steps :active="activeStep" finish-status="success" class="absolute-center w-85!">
          <el-step title="基本信息" />
          <el-step title="文档处理策略" />
        </el-steps>
      </div>
    </template>
    <MkViewLayout title="" :loading="loading">
      <template #default="{ Footer }">
        <div class="mx-auto w-full max-w-200 pt-6">
          <section v-show="activeStep === 0">
            <h4 class="mb-5 border-l-2 border-primary pl-2">基本信息</h4>
            <KnowledgeBaseForm ref="baseFormRef" />
            <el-form
              class="mt-4"
              ref="knowledgeFormRef"
              :model="knowledgeForm"
              :rules="knowledgeFormRules"
              label-position="top"
              require-asterisk-position="right"
              @submit.prevent
            >
              <el-form-item label="Web 根地址" prop="source_url">
                <el-input
                  v-model="knowledgeForm.source_url"
                  placeholder="请输入 Web 根地址"
                  @blur="knowledgeForm.source_url = knowledgeForm.source_url.trim()"
                />
              </el-form-item>
              <el-form-item label="选择器" prop="selector">
                <el-input
                  v-model="knowledgeForm.selector"
                  placeholder="默认为 body，可输入 .classname/#idname/tagname"
                  @blur="knowledgeForm.selector = knowledgeForm.selector.trim()"
                />
              </el-form-item>
            </el-form>
          </section>
          <section v-show="activeStep === 1">
            <h4 class="mb-5 mk-title-decoration">文档处理策略</h4>
            <DocumentStrategyForm ref="strategyFormRef" />
          </section>
        </div>
        <component :is="Footer">
          <!-- 取消创建 -->
          <el-button plain :disabled="loading" @click="drawerVisible = false">取消</el-button>
          <!-- 返回基本信息 -->
          <el-button v-if="activeStep === 1" plain :disabled="loading" @click="activeStep = 0">上一步</el-button>
          <!-- 校验基本信息并进入策略配置 -->
          <el-button v-if="activeStep === 0" type="primary" :loading="loading" @click="handleNext">下一步</el-button>
          <!-- 创建知识库 -->
          <el-button v-else type="primary" :loading="loading" @click="submit">创建</el-button>
        </component>
      </template>
    </MkViewLayout>
  </MkDrawer>
</template>
