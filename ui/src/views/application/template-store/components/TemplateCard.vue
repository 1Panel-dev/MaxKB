<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type { ApplicationStoreTemplate } from '@/api/types'
import { numberFormat } from '@/utils/number'
import TemplateStoreDetailDrawer from '../TemplateStoreDetailDrawer.vue'

defineOptions({ name: 'TemplateCard' })

const props = defineProps<{
  template: ApplicationStoreTemplate
}>()
const emit = defineEmits<{ use: [template: ApplicationStoreTemplate] }>()

/* 模板详情 */
const detailDrawerMounted = ref(false)
const detailDrawerRef = useTemplateRef<InstanceType<typeof TemplateStoreDetailDrawer>>('detailDrawerRef')

function handleOpenDetail() {
  detailDrawerMounted.value = true
  nextTick(() => detailDrawerRef.value?.open(props.template))
}

/* 使用模板交由模板中心统一处理。 */
function handleUseTemplate() {
  emit('use', props.template)
}
</script>

<template>
  <MkSourceCard :title="template.name">
    <template #icon><ApplicationIcon :icon="template.icon" :size="24" /></template>
    <p class="line-clamp-2" :title="template.desc || '-'">{{ template.desc || '-' }}</p>
    <template #footer="{ Action }">
      <span class="-mb-3 flex items-center gap-1 text-sm text-N600 group-hover:hidden group-focus-within:hidden">
        <template v-if="template.downloads !== undefined">
          <MkIcon name="icon_download_outlined" />
          {{ numberFormat(template.downloads) }}
        </template>
      </span>
      <component :is="Action" class="flex-1!">
        <div class="flex min-w-0 flex-1" @click.stop>
          <!-- 查看模板详情 -->
          <el-button class="flex-1!" plain @click="handleOpenDetail">详情</el-button>
          <!-- 使用模板 -->
          <el-button class="flex-1!" type="primary" @click="handleUseTemplate">使用</el-button>
        </div>
      </component>
    </template>
  </MkSourceCard>
  <TemplateStoreDetailDrawer v-if="detailDrawerMounted" ref="detailDrawerRef" @add="handleUseTemplate" @closed="detailDrawerMounted = false" />
</template>
