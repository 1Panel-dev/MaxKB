<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import { downloadByURL } from '@/utils/common'
import { getFileIconUrl } from '@/utils/icon'

defineOptions({ name: 'ApplicationNodeDetail' })

const { t } = useI18n({ useScope: 'global' })

defineProps<{
  data: ExecutionNodeDetail
}>()
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

        <div v-if="data.document_list?.length > 0">
          <p class="mb-1 text-N600">{{ t('workflow.document.label') }}：</p>
          <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <template v-for="(f, i) in data.document_list" :key="i">
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

        <div v-if="data.image_list?.length > 0">
          <p class="mb-1 text-N600">{{ t('upload.types.image') }}：</p>
          <div class="flex flex-wrap gap-2">
            <template v-for="(imageItem, qIndex) in data?.image_list" :key="qIndex">
              <ImageUploadCard
                :file="{ name: t('upload.types.image'), status: 'success' }"
                :src="imageItem.url || imageItem"
                :size="58"
                :show-remove="false"
                :preview-src-list="[imageItem.url || imageItem]"
              />
            </template>
          </div>
        </div>

        <div v-if="data.audio_list?.length > 0">
          <p class="mb-1 text-N600">{{ t('upload.types.audio') }}：</p>
          <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <template v-for="(file, index) in data.audio_list" :key="index">
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

        <div v-if="data.video_list?.length > 0">
          <p class="mb-1 text-N600">{{ t('upload.types.video') }}：</p>
          <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <template v-for="(file, index) in data.video_list" :key="index">
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

        <div v-if="data.other_list?.length > 0">
          <p class="mb-1 text-N600">{{ t('common.labels.other') }}：</p>
          <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <template v-for="(f, i) in data.other_list" :key="i">
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

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('execution.details.outputParams') }}</h6>
      <div class="space-y-2">
        <MdPreview v-if="data.answer" :model-value="data.answer" noImgZoomIn />
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>
