<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import { getFileIconUrl } from '@/utils/icon'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'ApplicationNodeDetail' })

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

        <div v-if="data.document_list?.length > 0">
          <p class="mb-1 text-N600">文档：</p>
          <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <template v-for="(f, i) in data.document_list" :key="i">
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

        <div v-if="data.image_list?.length > 0">
          <p class="mb-1 text-N600">图片：</p>
          <div class="flex flex-wrap gap-2">
            <el-image
              class="size-8"
              v-for="(f, i) in data.image_list"
              :key="i"
              :src="f.url"
              fit="cover"
              :preview-src-list="data.image_list.map((img: any) => img.url)"
              :scale="0.8"
              :initial-index="i"
            />
          </div>
        </div>

        <div v-if="data.audio_list?.length > 0">
          <p class="mb-1 text-N600">音频：</p>
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
          <p class="mb-1 text-N600">视频：</p>
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
          <p class="mb-1 text-N600">其他：</p>
          <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <template v-for="(f, i) in data.other_list" :key="i">
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

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">输出参数</h6>
      <div class="space-y-2">
        <MdPreview v-if="data.answer" :model-value="data.answer" noImgZoomIn />
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>
