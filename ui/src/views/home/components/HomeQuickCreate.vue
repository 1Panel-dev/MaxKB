<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { ModelProviderItem } from '@/api/types'
import ModelProviderApi from '@/api/admin/model-provider'
import ModelApi from '@/api/admin/workspace/model'
import ButtonCreateApplication from '@/views/application/components/ButtonCreateApplication.vue'
import ButtonCreateKnowledge from '@/views/knowledge/components/ButtonCreateKnowledge.vue'
import ButtonAddModel from '@/views/model/create-model/ButtonAddModel.vue'
import ButtonCreateTool from '@/views/tool/components/ButtonCreateTool.vue'
import perm from '@/permission'
const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ workspaceId: string }>()
const router = useRouter()

/* 任一资源可创建时展示快捷创建区域。 */
const showQuickCreate = computed(
  () => perm.application.workspace.create() || perm.knowledge.workspace.create() || perm.tool.workspace.create() || perm.model.workspace.create(),
)

/* 智能体快捷导入完成后进入列表页面。其他创建会随组件进入对应的详情页面 */
function handleCreateApplication() {
  return router.push({ name: 'workspace-application-list', params: { workspaceId: props.workspaceId } })
}

/* 知识库快捷导入完成后进入列表页面。其他创建会随组件进入对应的详情页面 */
function handleCreateKnowledge() {
  return router.push({ name: 'workspace-knowledge-list', params: { workspaceId: props.workspaceId } })
}

/* 工具快捷导入完成后进入列表页面。其他创建会随组件进入对应的详情页面 */
function handleCreateTool() {
  return router.push({ name: 'workspace-tools', params: { workspaceId: props.workspaceId } })
}

/* 模型创建完成后进入列表页面 */
function handleCreateModel() {
  return router.push({ name: 'workspace-model', params: { workspaceId: props.workspaceId } })
}

/* 模型供应商与复用创建入口 */
const providers = ref<ModelProviderItem[]>([])
const defaultProvider = computed<ModelProviderItem>(() => ({ name: t('model.categories.all'), provider: 'all', icon: '' }))
onMounted(() =>
  ModelProviderApi.getProviderList().then((result) => {
    providers.value = result
  }),
)
</script>
<template>
  <section v-if="showQuickCreate">
    <h4 class="mb-4 mt-4">{{ t('overview.quickCreate.title') }}</h4>
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <!-- 创建智能体 -->
      <ButtonCreateApplication
        v-if="perm.application.workspace.create()"
        trigger="hover"
        fit-trigger-width
        folder-id="default"
        popperClass="rounded-xl!"
        @refresh="handleCreateApplication"
      >
        <template #trigger>
          <el-card shadow="hover" class="h-full">
            <div class="flex-between gap-3">
              <MkIcon name="icon_creat-robot_colorful" :size="24" />
              <div class="min-w-0 flex-1">
                <h6>{{ t('overview.quickCreate.applicationTitle') }}</h6>
                <p class="text-sm text-N600">{{ t('overview.quickCreate.applicationDescription') }}</p>
              </div>
              <MkIcon name="icon_down_outlined" class="text-N600! transition-transform duration-200 in-aria-expanded:rotate-180" />
            </div>
          </el-card>
        </template>
      </ButtonCreateApplication>
      <!-- 创建知识库 -->
      <ButtonCreateKnowledge
        v-if="perm.knowledge.workspace.create()"
        trigger="hover"
        fit-trigger-width
        popper-class="rounded-xl!"
        folder-id="default"
        @refresh="handleCreateKnowledge"
      >
        <template #trigger>
          <el-card shadow="hover" class="h-full">
            <div class="flex-between gap-3">
              <MkIcon name="icon_creat-book_colorful" :size="24" />
              <div class="min-w-0 flex-1">
                <h6>{{ t('overview.quickCreate.knowledgeTitle') }}</h6>
                <p class="text-sm text-N600">{{ t('overview.quickCreate.knowledgeDescription') }}</p>
              </div>
              <MkIcon name="icon_down_outlined" class="text-N600! transition-transform duration-200 in-aria-expanded:rotate-180" />
            </div>
          </el-card>
        </template>
      </ButtonCreateKnowledge>
      <!-- 创建工具 -->
      <ButtonCreateTool
        v-if="perm.tool.workspace.create()"
        trigger="hover"
        fit-trigger-width
        popper-class="rounded-xl!"
        folder-id="default"
        @refresh="handleCreateTool"
      >
        <template #trigger>
          <el-card shadow="hover" class="h-full">
            <div class="flex-between gap-3">
              <MkIcon name="icon_creat-busy_colorful" :size="24" />
              <div class="min-w-0 flex-1">
                <h6>{{ t('tool.createTitle') }}</h6>
                <p class="text-sm text-N600">{{ t('overview.quickCreate.toolDescription') }}</p>
              </div>
              <MkIcon name="icon_down_outlined" class="text-N600! transition-transform duration-200 in-aria-expanded:rotate-180" />
            </div>
          </el-card>
        </template>
      </ButtonCreateTool>
      <!-- 添加模型 -->
      <ButtonAddModel
        v-if="perm.model.workspace.create()"
        :current-provider="defaultProvider"
        :providers="providers"
        :api="ModelApi"
        @refresh="handleCreateModel"
      >
        <template #default="{ open }">
          <!-- 打开模型创建入口 -->
          <el-card shadow="hover" class="h-full cursor-pointer" @click="open">
            <div class="flex-between gap-3">
              <MkIcon name="icon_creat-model_colorful" :size="24" />
              <div class="min-w-0 flex-1">
                <h6>{{ t('model.actions.add') }}</h6>
                <p class="text-sm text-N600">{{ t('overview.quickCreate.modelDescription') }}</p>
              </div>
            </div>
          </el-card>
        </template>
      </ButtonAddModel>
    </div>
  </section>
</template>
