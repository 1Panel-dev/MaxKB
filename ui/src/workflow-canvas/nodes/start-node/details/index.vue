<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import ImageUploadCard from '@/components/mk-drag-upload/ImageUploadCard.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import { downloadByURL } from '@/utils/common'
import { getFileIconUrl } from '@/utils/icon'

defineOptions({ name: 'StartNodeDetail' })

const { t } = useI18n({ useScope: 'global' })

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
      <h6 class="mb-2">{{ t('execution.details.inputParams') }}</h6>
      <div class="space-y-2">
        <p>
          <span class="text-N600">{{ t('common.labels.question') }}：</span>
          {{ data.question || '-' }}
        </p>

        <p v-for="(f, i) in data.global_fields" :key="i">
          <span class="text-N600">{{ f.label }}：</span>
          {{ f.value }}
        </p>

        <div v-if="attachments.document.length > 0">
          <p class="mb-1 text-N600">{{ t('upload.types.document') }}：</p>
          <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <template v-for="(f, i) in attachments.document" :key="i">
              <!-- 下载文档附件 -->
              <el-card shadow="never" class="small cursor-pointer" @click="f.url && downloadByURL(f.url, f.name)">
                <div class="flex-align-center gap-2">
                  <img :src="getFileIconUrl(f?.name)" alt="" width="24" />
                  <span class="min-w-0 truncate" :title="f?.name">{{ f?.name }}</span>
                </div>
              </el-card>
            </template>
          </div>
        </div>

        <div v-if="attachments.image.length > 0">
          <p class="mb-1 text-N600">{{ t('upload.types.image') }}：</p>
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
          <p class="mb-1 text-N600">{{ t('upload.types.audio') }}：</p>
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
          <p class="mb-1 text-N600">{{ t('upload.types.video') }}：</p>
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
          <p class="mb-1 text-N600">{{ t('common.labels.other') }}：</p>
          <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <template v-for="(f, i) in attachments.other" :key="i">
              <!-- 下载其他附件 -->
              <el-card shadow="never" class="small cursor-pointer" @click="f.url && downloadByURL(f.url, f.name)">
                <div class="flex-align-center gap-2">
                  <img :src="getFileIconUrl(f?.name)" alt="" width="24" />
                  <span class="min-w-0 truncate" :title="f?.name">{{ f?.name }}</span>
                </div>
              </el-card>
            </template>
          </div>
        </div>
      </div>
    </div>
  </DetailContainer>
</template>
