<template>
  <!-- 问题内容 -->
  <div class="question-content item-content mb-16 lighter">
    <div class="content p-12-16 border-r-8" :class="getClassName">
      <div class="text break-all pre-wrap">
        <div class="mb-8" v-if="document_list.length">
          <el-space wrap class="w-full media-file-width">
            <template v-for="(item, index) in document_list" :key="index">
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
            </template>
          </el-space>
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
          <el-space wrap>
            <template v-for="(item, index) in audio_list" :key="index">
              <div class="file cursor border-r-4" v-if="item.url">
                <audio
                  :src="item.url"
                  controls
                  style="width: 350px; height: 43px"
                  class="border-r-4"
                />
              </div>
            </template>
          </el-space>
        </div>
        <div class="mb-8" v-if="other_list.length">
          <el-space wrap class="w-full media-file-width">
            <template v-for="(item, index) in other_list" :key="index">
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
            </template>
          </el-space>
        </div>
        <span> {{ chatRecord.problem_text }}</span>
      </div>
    </div>
    <div class="avatar ml-8" v-if="showAvatar">
      <el-image
        v-if="application.user_avatar"
        :src="application.user_avatar"
        alt=""
        fit="cover"
        style="width: 28px; height: 28px; display: block"
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
import useStore from '@/stores'
const props = defineProps<{
  application: any
  chatRecord: chatType
  type: 'log' | 'ai-chat' | 'debug-ai-chat'
}>()

const { user } = useStore()

const showAvatar = computed(() => {
  return user.isEnterprise() ? props.application.show_user_avatar : true
})

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
const other_list = computed(() => {
  if (props.chatRecord?.upload_meta) {
    return props.chatRecord.upload_meta?.other_list || []
  }
  const startNode = props.chatRecord.execution_details?.find(
    (detail) => detail.type === 'start-node'
  )
  return startNode?.other_list || []
})
const getClassName = computed(() => {
  return document_list.value.length >= 2 || other_list.value.length >= 2
    ? 'media_2'
    : document_list.value.length
      ? `media_${document_list.value.length}`
      : other_list.value.length
        ? `media_${other_list.value.length}`
        : `media_0`
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
  padding-left: var(--padding-left);
  width: 100%;
  box-sizing: border-box;

  .content {
    background: #d6e2ff;
    padding-left: 16px;
    padding-right: 16px;
  }

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
  .media-file-width {
    :deep(.el-space__item) {
      min-width: 40% !important;
      flex-grow: 1;
    }
  }
  .media_2 {
    flex: 1;
  }
  .media_0 {
    flex: inherit;
  }
  .media_1 {
    width: 50%;
  }
}
@media only screen and (max-width: 768px) {
  .question-content {
    .media-file-width {
      :deep(.el-space__item) {
        min-width: 100% !important;
      }
    }
    .media_1 {
      width: 100%;
    }
  }
}
.debug-ai-chat {
  .question-content {
    .media-file-width {
      :deep(.el-space__item) {
        min-width: 100% !important;
      }
    }
    .media_1 {
      width: 100%;
    }
  }
}
</style>
