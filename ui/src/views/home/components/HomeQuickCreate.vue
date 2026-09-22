<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import type { ModelProviderItem } from '@/api/types'
import ModelProviderApi from '@/api/admin/model-provider'
import ModelApi from '@/api/admin/workspace/model'
import ButtonCreateApplication from '@/views/application/components/ButtonCreateApplication.vue'
import ButtonCreateKnowledge from '@/views/knowledge/components/ButtonCreateKnowledge.vue'
import ButtonCreateTool from '@/views/tool/components/ButtonCreateTool.vue'
import ButtonAddModel from '@/views/model/create-model/ButtonAddModel.vue'
const props = defineProps<{ workspaceId: string }>()
const router = useRouter()

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
const defaultProvider: ModelProviderItem = { name: '全部模型', provider: 'all', icon: '' }
onMounted(() =>
  ModelProviderApi.getProviderList().then((result) => {
    providers.value = result
  }),
)
</script>
<template>
  <section>
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <!-- 创建智能体 -->
      <ButtonCreateApplication trigger="hover" fit-trigger-width folder-id="default" popperClass="rounded-xl!" @refresh="handleCreateApplication">
        <template #trigger>
          <el-card shadow="hover">
            <div class="flex-between gap-3">
              <MkIcon name="icon_creat-robot_colorful" :size="24" />
              <div class="min-w-0 flex-1">
                <h6>创建智能体</h6>
                <p class="text-sm text-N600">从模板或空白创建</p>
              </div>
              <MkIcon name="icon_down_outlined" />
            </div>
          </el-card>
        </template>
      </ButtonCreateApplication>
      <!-- 创建知识库 -->
      <ButtonCreateKnowledge trigger="hover" fit-trigger-width popper-class="rounded-xl!" :folder-id="workspaceId" @refresh="handleCreateKnowledge">
        <template #trigger>
          <el-card shadow="hover">
            <div class="flex-between gap-3">
              <MkIcon name="icon_creat-book_colorful" :size="24" />
              <div class="min-w-0 flex-1">
                <h6>创建知识库</h6>
                <p class="text-sm text-N600">上传文档或 web 站点</p>
              </div>
              <MkIcon name="icon_down_outlined" />
            </div>
          </el-card>
        </template>
      </ButtonCreateKnowledge>
      <!-- 创建工具 -->
      <ButtonCreateTool trigger="hover" fit-trigger-width popper-class="rounded-xl!" :folder-id="workspaceId" @refresh="handleCreateTool">
        <template #trigger>
          <el-card shadow="hover">
            <div class="flex-between gap-3">
              <MkIcon name="icon_creat-busy_colorful" :size="24" />
              <div class="min-w-0 flex-1">
                <h6>创建工具</h6>
                <p class="text-sm text-N600">脚本工具或工作流工具</p>
              </div>
              <MkIcon name="icon_down_outlined" />
            </div>
          </el-card>
        </template>
      </ButtonCreateTool>
      <!-- 添加模型 -->
      <ButtonAddModel :current-provider="defaultProvider" :providers="providers" :api="ModelApi" @refresh="handleCreateModel">
        <template #default="{ open }">
          <!-- 打开模型创建入口 -->
          <el-card shadow="hover" class="cursor-pointer" @click="open">
            <div class="flex-between gap-3">
              <MkIcon name="icon_creat-model_colorful" :size="24" />
              <div class="min-w-0 flex-1">
                <h6>添加模型</h6>
                <p class="text-sm text-N600">配置大语言/向量等模型</p>
              </div>
            </div>
          </el-card>
        </template>
      </ButtonAddModel>
    </div>
  </section>
</template>
