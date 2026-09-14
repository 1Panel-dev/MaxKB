<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import type { UploadFile, UploadInstance } from 'element-plus'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import { KNOWLEDGE_TYPE } from '@/api/enums'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'
import CreateBaseKnowledgeDialog from './BaseKnowledgeDialog.vue'
import CreateWebKnowledgeDialog from './WebKnowledgeDialog.vue'
import CreateLarkKnowledgeDialog from './LarkKnowledgeDialog.vue'
import CreateWorkflowKnowledgeDialog from './WorkflowKnowledgeDialog.vue'

defineOptions({ name: 'CreateKnowledgeDropdown' })

const props = defineProps<{ folderId: string }>()
const { auth } = useStore()

defineSlots<{
  /** 创建菜单触发器，只能渲染一个有效根节点 */
  trigger?(): unknown
}>()

const emit = defineEmits<{ refresh: [] }>()

/* 各类型知识库创建 */
const createBaseKnowledgeDialogRef = useTemplateRef<InstanceType<typeof CreateBaseKnowledgeDialog>>('createBaseKnowledgeDialogRef')
const createWebKnowledgeDialogRef = useTemplateRef<InstanceType<typeof CreateWebKnowledgeDialog>>('createWebKnowledgeDialogRef')
const createLarkKnowledgeDialogRef = useTemplateRef<InstanceType<typeof CreateLarkKnowledgeDialog>>('createLarkKnowledgeDialogRef')

const createWorkflowKnowledgeDialogRef = useTemplateRef<InstanceType<typeof CreateWorkflowKnowledgeDialog>>('createWorkflowKnowledgeDialogRef')

function handleCreateBaseKnowledge() {
  createBaseKnowledgeDialogRef.value?.open()
}

function handleCreateWebKnowledge() {
  createWebKnowledgeDialogRef.value?.open()
}

function handleCreateLarkKnowledge() {
  createLarkKnowledgeDialogRef.value?.open()
}

function handleCreateWorkflowKnowledge() {
  createWorkflowKnowledgeDialogRef.value?.open()
}

/* 导入创建 */
const importUploadRef = ref<UploadInstance>()
const importing = ref(false)

function handleImportCreate(file: UploadFile) {
  if (!file.raw || importing.value) return
  importing.value = true
  return KnowledgeApi.postKnowledgeImport(file.raw, props.folderId)
    .then(() => {
      // 先刷新新资源权限，再通知列表加载导入的知识库。
      return auth.loadAuthBaseProfile().then(() => {
        MsgSuccess('导入成功')
        emit('refresh')
      })
    })
    .finally(() => {
      importing.value = false
      importUploadRef.value?.clearFiles()
    })
}
</script>

<template>
  <MkDropdown trigger="click" placement="bottom-end" persistent>
    <slot name="trigger">
      <!-- 创建知识库 -->
      <el-button type="primary">
        <span class="mr-1">创建</span>
        <MkIcon name="icon_down_outlined" :size="14" />
      </el-button>
    </slot>
    <template #dropdown>
      <MkDropdownMenu class="w-77!">
        <!-- 创建通用知识库 -->
        <MkDropdownItem class="py-2!" @click="handleCreateBaseKnowledge">
          <template #icon><KnowledgeIcon :type="KNOWLEDGE_TYPE.BASE" /></template>
          <div class="min-w-0">
            <p>通用知识库</p>
            <p class="text-sm text-N500 whitespace-normal">通过上传文件或手动录入构建知识库</p>
          </div>
        </MkDropdownItem>
        <!-- 创建 Web 知识库 -->
        <MkDropdownItem class="py-2!">
          <template #icon><KnowledgeIcon :type="KNOWLEDGE_TYPE.WEB" /></template>
          <div class="min-w-0">
            <p>Web 知识库</p>
            <p class="text-sm text-N500 whitespace-normal">通过网站链接构建知识库</p>
          </div>
        </MkDropdownItem>
        <!-- 创建飞书知识库 -->
        <MkDropdownItem class="py-2!" @click="handleCreateLarkKnowledge">
          <template #icon><KnowledgeIcon :type="KNOWLEDGE_TYPE.LARK" /></template>
          <div class="min-w-0">
            <p>飞书知识库</p>
            <p class="text-sm text-N500 whitespace-normal">通过飞书文档构建知识库</p>
          </div>
        </MkDropdownItem>
        <!-- 创建工作流知识库 -->
        <MkDropdownItem class="py-2!" @click="handleCreateWorkflowKnowledge">
          <template #icon><KnowledgeIcon :type="KNOWLEDGE_TYPE.WORKFLOW" /></template>
          <div class="min-w-0">
            <p>工作流知识库</p>
            <p class="text-sm text-N500 whitespace-normal">通过自定义工作流方式构建知识库</p>
          </div>
        </MkDropdownItem>
        <!-- 导入创建 -->
        <el-upload
          ref="importUploadRef"
          action="#"
          :auto-upload="false"
          class="mk-import-button"
          :limit="1"
          :on-change="handleImportCreate"
          :show-file-list="false"
        >
          <MkDropdownItem class="w-full py-2!">
            <template #icon>
              <img class="size-6" src="@/assets/mk_icon_import.svg" alt="" />
            </template>
            <span>导入创建</span>
          </MkDropdownItem>
        </el-upload>
      </MkDropdownMenu>
    </template>
  </MkDropdown>

  <CreateBaseKnowledgeDialog ref="createBaseKnowledgeDialogRef" :folder-id="folderId" @refresh="emit('refresh')" />
  <CreateWebKnowledgeDialog ref="createWebKnowledgeDialogRef" :folder-id="folderId" @refresh="emit('refresh')" />
  <CreateLarkKnowledgeDialog ref="createLarkKnowledgeDialogRef" :folder-id="folderId" @refresh="emit('refresh')" />
  <CreateWorkflowKnowledgeDialog ref="createWorkflowKnowledgeDialogRef" :folder-id="folderId" @refresh="emit('refresh')" />
</template>
