<template>
  <CardBox
    shadow="never"
    :title="index + 1 + '.' + data.title || '-'"
    class="paragraph-source-card cursor mb-8 paragraph-source-card-height"
    :style="{ height: cardHeight }"
    :class="data.is_active ? '' : 'disabled'"
    :showIcon="false"
  >
    <template #tag>
      <div class="color-primary">
        {{ score?.toFixed(3) || data.similarity?.toFixed(3) }}
      </div>
    </template>

    <!-- 章节路径显示 -->
    <div v-if="data?.section_path" class="section-path mb-8">
      <el-tag type="info" size="small" effect="plain" class="section-path-tag">
        <el-icon class="mr-4"><FolderOpened /></el-icon>
        <span class="ellipsis-1" :title="data.section_path">{{ data.section_path }}</span>
      </el-tag>
    </div>

    <el-scrollbar :height="scrollHeight">
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
import { FolderOpened } from '@element-plus/icons-vue'

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

// 根据是否有章节路径调整高度
const hasSectionPath = computed(() => !!props.data?.section_path)
const cardHeight = computed(() => {
  let baseHeight = props.data?.document_name?.trim() ? 300 : 260
  if (hasSectionPath.value) {
    baseHeight += 32 // 章节路径标签高度
  }
  return `${baseHeight}px`
})

const scrollHeight = computed(() => {
  return hasSectionPath.value ? 120 : 150
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
<style lang="scss" scoped>
.section-path {
  .section-path-tag {
    max-width: 100%;
    display: inline-flex;
    align-items: center;

    .ellipsis-1 {
      max-width: 200px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }
}
</style>
