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
          <el-button text @click="copy(data)">
            <AppIcon iconName="app-copy" class="color-secondary"></AppIcon>
          </el-button>
        </el-tooltip>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
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

function removeFormRander(text: string) {
  return text.replace(/<form_rander>.*?<\/form_rander>/gs, '').trim()
}
const copy = (data: any) => {
  try {
    const text = data.answer_text_list
      .map((item: Array<any>) => item.map((i) => i.content).join('\n'))
      .join('\n\n')
    copyClick(removeFormRander(text))
  } catch (e: any) {
    copyClick(removeFormRander(data?.answer_text.trim()))
  }
}
</script>
<style lang="scss" scoped></style>
