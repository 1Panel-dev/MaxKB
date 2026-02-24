<template>
  <div>
    <div class="flex-between mt-8">
      <div>
        <el-text type="info">
          <span class="ml-4">{{ datetimeFormat(data.create_time) }}</span>
        </el-text>
      </div>
      <div>
        <el-tooltip effect="dark" :content="$t('common.copy')" placement="top">
          <el-button text @click="copyClick(data?.answer_text)">
            <AppIcon iconName="app-copy" class="color-secondary"></AppIcon>
          </el-button>
        </el-tooltip>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { copyClick } from '@/utils/clipboard'

import { datetimeFormat } from '@/utils/time'

import { useRoute } from 'vue-router'

const route = useRoute()
const {
  params: { id },
} = route as any

const props = defineProps({
  data: {
    type: Object,
    default: () => {},
  },
})
</script>
<style lang="scss" scoped></style>
