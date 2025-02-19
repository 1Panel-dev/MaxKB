<template>
  <!-- 问题内容 -->
  <div class="question-content item-content mb-16 lighter">
    <div class="content mr-16">
      <div class="text break-all pre-wrap">
        <div class="mb-8" v-if="document_list.length">
          <el-row :gutter="10">
            <el-col
              v-for="(item, index) in document_list"
              :key="index"
              :xs="24"
              :sm="props.type === 'debug-ai-chat' ? 24 : 12"
              :md="props.type === 'debug-ai-chat' ? 24 : 12"
              :lg="props.type === 'debug-ai-chat' ? 24 : 12"
              :xl="props.type === 'debug-ai-chat' ? 24 : 12"
              class="mb-8 w-full"
            >
              <el-card shadow="never" style="--el-card-padding: 8px" class="download-file cursor">
                <div class="download-button flex align-center" @click="downloadFile(item)">
                  <el-icon class="mr-4">
                    <Download />
                  </el-icon>
                  {{ $t('chat.download') }}
                </div>
                <div class="show flex align-center">
                  <img :src="getImgUrl(item && item?.name)" alt="" width="24" />
                  <div class="ml-4 ellipsis-1" :title="item && item?.name">
                    {{ item && item?.name }}
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
        <div class="mb-8" v-if="image_list.length">
          <el-space wrap>
            <template v-for="(item, index) in image_list" :key="index">
              <div class="file cursor border-r-4" v-if="item.url">
                <el-image
                  :src="item.url"
                  :zoom-rate="1.2"
                  :max-scale="7"
                  :min-scale="0.2"
                  :preview-src-list="getAttrsArray(image_list, 'url')"
                  :initial-index="index"
                  alt=""
                  fit="cover"
                  style="width: 170px; height: 170px; display: block"
                  class="border-r-4"
                />
              </div>
            </template>
          </el-space>
        </div>
        <div class="mb-8" v-if="audio_list.length">
          <el-row :gutter="10">
            <el-col
              v-for="(item, index) in audio_list"
              :key="index"
              :xs="24"
              :sm="props.type === 'debug-ai-chat' ? 24 : 12"
              :md="props.type === 'debug-ai-chat' ? 24 : 12"
              :lg="props.type === 'debug-ai-chat' ? 24 : 12"
              :xl="props.type === 'debug-ai-chat' ? 24 : 12"
              class="mb-8"
            >
              <div class="file cursor border-r-4" v-if="item.url">
                <audio
                  :src="item.url"
                  controls
                  style="width: 350px; height: 43px"
                  class="border-r-4"
                />
              </div>
            </el-col>
          </el-row>
        </div>
        {{ chatRecord.problem_text }}
      </div>
    </div>
    <div class="avatar">
      <el-image
        v-if="application.user_avatar"
        :src="application.user_avatar"
        alt=""
        fit="cover"
        style="width: 32px; height: 32px; display: block"
      />
      <AppAvatar v-else>
        <img src="@/assets/user-icon.svg" style="width: 50%" alt="" />
      </AppAvatar>
    </div>
  </div>
</template>
<script setup lang="ts">
import { type chatType } from '@/api/type/application'
import { getImgUrl, getAttrsArray, downloadByURL } from '@/utils/utils'
import { onMounted, computed } from 'vue'

const props = defineProps<{
  application: any
  chatRecord: chatType
  type: 'log' | 'ai-chat' | 'debug-ai-chat'
}>()
const document_list = computed(() => {
  if (props.chatRecord?.upload_meta) {
    return props.chatRecord.upload_meta?.document_list || []
  }
  const startNode = props.chatRecord.execution_details?.find(
    (detail) => detail.type === 'start-node'
  )
  return startNode?.document_list || []
})
const image_list = computed(() => {
  if (props.chatRecord?.upload_meta) {
    return props.chatRecord.upload_meta?.image_list || []
  }
  const startNode = props.chatRecord.execution_details?.find(
    (detail) => detail.type === 'start-node'
  )
  return startNode?.image_list || []
})
const audio_list = computed(() => {
  if (props.chatRecord?.upload_meta) {
    return props.chatRecord.upload_meta?.audio_list || []
  }
  const startNode = props.chatRecord.execution_details?.find(
    (detail) => detail.type === 'start-node'
  )
  return startNode?.audio_list || []
})

function downloadFile(item: any) {
  downloadByURL(item.url, item.name)
}

onMounted(() => {})
</script>
<style lang="scss" scoped>
.question-content {
  display: flex;
  justify-content: flex-end;

  .download-file {
    height: 43px;

    &:hover {
      color: var(--el-color-primary);
      border: 1px solid var(--el-color-primary);

      .download-button {
        display: block;
        text-align: center;
        line-height: 26px;
      }

      .show {
        display: none;
      }
    }

    .download-button {
      display: none;
    }
  }
}
</style>
