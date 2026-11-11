<script setup lang="ts">
import { getFileIconUrl } from '@/utils/icon'
import { useRightSidebarStore } from '../index'
import DocumentPreview from './document-preview/index.vue'

defineOptions({ name: 'KnowledgeSource' })

const { knowledgeSource, closeRightSide } = useRightSidebarStore()
const { previewDocument, sourceParagraphs, count, openDocument } = knowledgeSource
</script>

<template>
  <!-- 右侧内容区:知识来源。数据来自 view 层(消息区点击「知识来源」写入) -->
  <div class="knowledge-source-panel relative h-full">
    <!-- 分段列表预览文档时仅隐藏不卸载，返回后保留滚动位置 -->
    <div class="flex-column h-full" :class="{ invisible: previewDocument }">
      <div class="flex-between shrink-0 px-6 py-4 border-b">
        <h4>知识来源 ({{ count }})</h4>
        <!-- 关闭知识来源 -->
        <el-button text @click="closeRightSide()">
          <MkIcon name="icon_close_outlined" size="18" />
        </el-button>
      </div>
      <el-scrollbar class="min-h-0 flex-1" view-class="p-6">
        <div v-if="count" class="space-y-4">
          <template v-for="paragraph in sourceParagraphs" :key="paragraph.key">
            <MkResourceCard :title="paragraph.title" disabled>
              <template #title="{ title }">
                <span class="flex-align-center min-w-0 gap-2">
                  <h4 class="shrink-0">{{ `#${paragraph.order}` }}</h4>
                  <el-divider direction="vertical" />
                  <h4 class="min-w-0 truncate" :title="title">{{ title }}</h4>
                </span>
              </template>
              <template #tag>
                <div class="flex-align-center gap-2">
                  <el-tag size="small" type="info">{{ paragraph.vectorLabel }}</el-tag>
                  <h6 v-if="paragraph.similarity" class="shrink-0 text-primary">{{ paragraph.similarity }}</h6>
                </div>
              </template>

              <MdPreview :model-value="paragraph.content" no-img-zoom-in />

              <!-- 放大预览召回图片 -->
              <el-image
                v-if="paragraph.imageUrl"
                :src="paragraph.imageUrl"
                :alt="paragraph.title"
                fit="cover"
                class="mt-2 w-full rounded-lg"
                :preview-src-list="[paragraph.imageUrl]"
                preview-teleported
              />

              <!-- 打开来源文档：PDF 在知识来源内预览，其他文件下载，网页来源打开原网址 -->
              <el-card v-if="paragraph.documentName" shadow="never" class="small mt-2 cursor-pointer" @click="openDocument(paragraph)">
                <div class="flex-align-center gap-2">
                  <img :src="getFileIconUrl(paragraph.documentName)" alt="" width="24" />
                  <span class="min-w-0 truncate" :title="paragraph.documentName">{{ paragraph.documentName }}</span>
                </div>
              </el-card>

              <template #footer>
                <div class="flex-align-center w-full gap-2 border-t pt-2">
                  <KnowledgeIcon :type="paragraph.knowledgeType" :size="16" class="small" />
                  <span class="truncate text-N600" :title="paragraph.knowledgeName">{{ paragraph.knowledgeName }}</span>
                </div>
              </template>
            </MkResourceCard>
          </template>
        </div>
        <el-empty v-else description="暂无知识来源" :image-size="80" />
      </el-scrollbar>
    </div>
    <!-- 预览 PDF 来源文档，覆盖在分段列表之上 -->
    <DocumentPreview v-if="previewDocument" class="absolute inset-0 bg-white" />
  </div>
</template>
