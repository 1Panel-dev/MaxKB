<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import MkAudio from '@/components/global/mk-media-preview/MkAudio.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import { getFileIconUrl } from '@/utils/icon'

defineOptions({ name: 'SpeechToTextNodeDetail' })
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
      <h6 class="mb-2">{{ t('workflow.executionResult.inputParams') }}</h6>
      <div>
        <div v-if="data.audio_list?.length > 0">
          <p class="mb-2 text-N600">{{ t('workflow.audioFile.label') }}：</p>
          <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <!-- 点击卡片播放输入音频 -->
            <MkAudio
              v-for="(file, index) in data.audio_list"
              :key="index"
              :src="file.url"
              :name="file.name || t('upload.types.audio')"
              class="min-w-0"
            >
              <el-card shadow="never" class="small cursor-pointer">
                <div class="flex-align-center gap-2">
                  <img :src="getFileIconUrl(file.name || 'audio.mp3')" alt="" width="24" class="shrink-0" />
                  <span class="min-w-0 truncate" :title="file.name || t('upload.types.audio')">{{ file.name || t('upload.types.audio') }}</span>
                </div>
              </el-card>
            </MkAudio>
          </div>
        </div>
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.executionResult.outputParams') }}</h6>
      <div class="space-y-2">
        <template v-for="(file_content, index) in data.content" :key="index">
          <el-card shadow="never">
            <MdPreview v-if="file_content" :model-value="file_content" noImgZoomIn />
            <template v-else>-</template>
          </el-card>
        </template>
      </div>
    </div>
  </DetailContainer>
</template>
