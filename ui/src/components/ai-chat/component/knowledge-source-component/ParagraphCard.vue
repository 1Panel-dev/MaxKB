<template>
  <CardBox
    shadow="never"
    :title="index + 1 + '.' + data.title || '-'"
    class="paragraph-source-card cursor mb-8 paragraph-source-card-height"
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
      <el-card shadow="never" style="--el-card-padding: 8px" class="w-full mb-12">
        <el-text class="flex align-center item">
          <img :src="getImgUrl(data?.document_name?.trim())" alt="" width="20" class="mr-4" />

          <template v-if="meta?.source_url">
            <a
              :href="getNormalizedUrl(meta?.source_url)"
              target="_blank"
              class="ellipsis-1 break-all"
              :title="data?.document_name?.trim()"
            >
              {{ data?.document_name?.trim() }}
            </a>
          </template>
          <template v-else>
            <span class="ellipsis-1 break-all" :title="data?.document_name?.trim()">
              {{ data?.document_name?.trim() }}
            </span>
          </template>
        </el-text>
      </el-card>
      <div class="flex align-center border-t" style="padding: 12px 0 8px">
        <el-avatar class="mr-8 avatar-blue" shape="square" :size="18">
          <img src="@/assets/knowledge/icon_document.svg" style="width: 58%" alt="" />
        </el-avatar>
        <span class="ellipsis-1 break-all" :title="data?.knowledge_name">
          {{ data?.knowledge_name || '-' }}
        </span>
      </div>
    </template>
  </CardBox>
</template>
<script setup lang="ts">
import { getImgUrl, getNormalizedUrl } from '@/utils/common'
import { computed } from 'vue'

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
</script>
<style lang="scss" scoped>
.paragraph-source-card-height {
  height: 300px;
}

// @media only screen and (max-width: 768px) {
//   .paragraph-source-card-height {
//     height: 285px;
//   }
// }
</style>
