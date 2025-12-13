<template>
  <CardBox
    shadow="never"
    :title="index + 1 + '.' + data.title || '-'"
    class="paragraph-source-card cursor mb-8 paragraph-source-card-height"
    :style="{ height: data?.document_name?.trim() ? '300px' : '260px' }"
    :class="data.is_active ? '' : 'disabled'"
    :showIcon="false"
  >
    <template #tag>
      <div class="color-primary">
        {{ score?.toFixed(3) || data.similarity?.toFixed(3) }}
      </div>
    </template>

    <el-scrollbar height="150">
      <MdPreview ref="editorRef" editorId="preview-only" :modelValue="content" noImgZoomIn />
    </el-scrollbar>

    <template #footer>
      <slot name="footer">
        <el-card
          shadow="never"
          style="--el-card-padding: 8px"
          class="w-full mb-12"
          v-if="data?.document_name?.trim()"
        >
          <el-text class="flex align-center item">
            <img :src="getImgUrl(data?.document_name?.trim())" alt="" width="20" class="mr-4" />
            <div class="ml-8">
              <div class="ml-4" v-if="data?.meta?.source_file_id || data?.meta?.source_url">
                <a
                  :href="getFileUrl(data?.meta?.source_file_id) || data?.meta?.source_url"
                  target="_blank"
                  class="ellipsis-1"
                  :title="data?.document_name?.trim()"
                >
                  <span :title="data?.document_name?.trim()">{{ data?.document_name }}</span>
                </a>
              </div>
              <div v-else @click="infoMessage(data)">
                <span class="ellipsis-1 break-all" :title="data?.document_name?.trim()">
                  {{ data?.document_name?.trim() }}
                </span>
              </div>
            </div>
          </el-text>
        </el-card>
        <div class="flex align-center border-t" style="padding: 12px 0 8px">
          <KnowledgeIcon :type="data?.knowledge_type" :size="18" class="mr-8" />
          <span class="ellipsis-1 break-all" :title="data?.knowledge_name">
            {{ data?.knowledge_name || '-' }}
          </span>
        </div>
      </slot>
    </template>
  </CardBox>
</template>
<script setup lang="ts">
import { getImgUrl, getFileUrl } from '@/utils/common'
import { computed } from 'vue'
import { MsgInfo } from '@/utils/message'
import { t } from '@/locales'
const props = defineProps({
  data: {
    type: Object,
    default: () => {},
  },
  content: {
    type: String,
    default: '',
  },
  index: {
    type: Number,
    default: 0,
  },
  score: {
    type: Number,
    default: null,
  },
})
const isMetaObject = computed(() => typeof props.data.meta === 'object')
const parsedMeta = computed(() => {
  try {
    return JSON.parse(props.data.meta)
  } catch (e) {
    return {}
  }
})

const meta = computed(() => (isMetaObject.value ? props.data.meta : parsedMeta.value))
function infoMessage(data: any) {
  if (data?.meta?.allow_download === false) {
    MsgInfo(t('chat.noPermissionDownload'))
  } else {
    MsgInfo(t('chat.noDocument'))
  }
}
</script>
<style lang="scss" scoped></style>
