<script setup lang="ts">
import { computed } from 'vue'
import ImageUploadCard from '@/components/mk-drag-upload/ImageUploadCard.vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import { getFileIconUrl } from '@/utils/icon'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'StartNodeDetail' })

const props = defineProps<{
  data: ExecutionNodeDetail
}>()

interface StartAttachment {
  name: string
  url: string
  size?: number
}

// 开始节点附件兼容 v3 字段和 v2 的 _list 字段。
const attachments = computed<Record<'document' | 'image' | 'audio' | 'video' | 'other', StartAttachment[]>>(() => ({
  document: props.data.document ?? props.data.document_list ?? [],
  image: props.data.image ?? props.data.image_list ?? [],
  audio: props.data.audio ?? props.data.audio_list ?? [],
  video: props.data.video ?? props.data.video_list ?? [],
  other: props.data.other ?? props.data.other_list ?? [],
}))
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" />
    </template>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">输入参数</h6>
      <div class="space-y-2">
        <p>
          <span class="text-N600">问题：</span>
          {{ data.question || '-' }}
        </p>

        <p v-for="(f, i) in data.global_fields" :key="i">
          <span class="text-N600">{{ f.label }}：</span>
          {{ f.value }}
        </p>

        <div v-if="attachments.document.length > 0">
          <p class="mb-1 text-N600">文档：</p>
          <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <template v-for="(f, i) in attachments.document" :key="i">
              <!-- 在新标签页打开或下载附件 -->
              <a :href="f.url || undefined" target="_blank" rel="noopener noreferrer" :download="f.name" class="block min-w-0">
                <el-card shadow="never" class="small cursor-pointer">
                  <div class="flex-align-center gap-2">
                    <img :src="getFileIconUrl(f?.name)" alt="" width="24" />
                    <span class="min-w-0 truncate" :title="f?.name">{{ f?.name }}</span>
                  </div>
                </el-card>
              </a>
            </template>
          </div>
        </div>

        <div v-if="attachments.image.length > 0">
          <p class="mb-1 text-N600">图片：</p>
          <div class="flex flex-wrap gap-2">
            <template v-for="(file, index) in attachments.image" :key="index">
              <!-- 查看图片 -->
              <ImageUploadCard
                :file="{ ...file, status: 'success' }"
                :src="file.url"
                :size="58"
                :show-remove="false"
                :preview-src-list="attachments.image.map((image) => image.url)"
                :initial-index="index"
              />
            </template>
          </div>
        </div>

        <div v-if="attachments.audio.length > 0">
          <p class="mb-1 text-N600">音频：</p>
          <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <template v-for="(file, index) in attachments.audio" :key="index">
              <!-- 播放音频 -->
              <MkAudio :src="file.url" :name="file.name">
                <el-card shadow="never" class="small cursor-pointer">
                  <div class="flex-align-center gap-2">
                    <img :src="getFileIconUrl(file?.name)" alt="" width="24" />
                    <span class="min-w-0 truncate" :title="file?.name">{{ file?.name }}</span>
                  </div>
                </el-card>
              </MkAudio>
            </template>
          </div>
        </div>

        <div v-if="attachments.video.length > 0">
          <p class="mb-1 text-N600">视频：</p>
          <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <template v-for="(file, index) in attachments.video" :key="index">
              <!-- 播放视频 -->
              <MkVideo :src="file.url" :name="file.name">
                <el-card shadow="never" class="small cursor-pointer">
                  <div class="flex-align-center gap-2">
                    <img :src="getFileIconUrl(file?.name)" alt="" width="24" />
                    <span class="min-w-0 truncate" :title="file?.name">{{ file?.name }}</span>
                  </div>
                </el-card>
              </MkVideo>
            </template>
          </div>
        </div>

        <div v-if="attachments.other.length > 0">
          <p class="mb-1 text-N600">其他：</p>
          <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <template v-for="(f, i) in attachments.other" :key="i">
              <!-- 在新标签页打开或下载附件 -->
              <a :href="f.url || undefined" target="_blank" rel="noopener noreferrer" :download="f.name" class="block min-w-0">
                <el-card shadow="never" class="small cursor-pointer">
                  <div class="flex-align-center gap-2">
                    <img :src="getFileIconUrl(f?.name)" alt="" width="24" />
                    <span class="min-w-0 truncate" :title="f?.name">{{ f?.name }}</span>
                  </div>
                </el-card>
              </a>
            </template>
          </div>
        </div>
      </div>
    </div>
  </DetailContainer>
</template>
