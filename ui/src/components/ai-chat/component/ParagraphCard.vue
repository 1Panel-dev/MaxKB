<template>
  <CardBox
    shadow="never"
    :title="data.title || '-'"
    class="paragraph-source-card cursor mb-8 paragraph-source-card-height"
    :class="data.is_active ? '' : 'disabled'"
    :showIcon="false"
  >
    <template #icon>
      <AppAvatar class="mr-12 avatar-light" :size="22"> {{ index + 1 + '' }}</AppAvatar>
    </template>
    <div class="active-button primary">{{ score?.toFixed(3) || data.similarity?.toFixed(3) }}</div>
    <template #description>
      <el-scrollbar height="150">
        <MdPreview ref="editorRef" editorId="preview-only" :modelValue="content" noImgZoomIn />
      </el-scrollbar>
    </template>
    <template #footer>
      <div class="footer-content flex-between">
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
        <div class="flex align-center item" style="line-height: 32px">
          <AppAvatar class="mr-8 avatar-blue" shape="square" :size="18">
            <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
          </AppAvatar>

          <span class="ellipsis-1 break-all" :title="data?.dataset_name">
            {{ data?.dataset_name }}</span
          >
        </div>
      </div>
    </template>
  </CardBox>
</template>
<script setup lang="ts">
import { getImgUrl, getNormalizedUrl } from '@/utils/utils'
import { computed } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    default: () => {}
  },
  content: {
    type: String,
    default: ''
  },
  index: {
    type: Number,
    default: 0
  },
  score: {
    type: Number,
    default: null
  }
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
.paragraph-source-card {
  .footer-content {
    .item {
      max-width: 50%;
    }
  }
}

.paragraph-source-card-height {
  height: 260px;
}

@media only screen and (max-width: 768px) {
  .paragraph-source-card-height {
    height: 285px;
  }
  .paragraph-source-card {
    .footer-content {
      display: block;

      .item {
        max-width: 100%;
      }
    }
  }
}
</style>
