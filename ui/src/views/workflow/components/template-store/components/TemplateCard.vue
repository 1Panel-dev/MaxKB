<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type { WorkflowStoreTemplate } from '@/api/types'
import { numberFormat } from '@/utils/number'
import { resetUrl } from '@/utils/icon'
import TemplateStoreDetailDrawer from '../TemplateStoreDetailDrawer.vue'

defineOptions({ name: 'TemplateCard' })

const props = defineProps<{
  resource: 'application' | 'knowledge' | 'tool'
  disabled?: boolean
  template: WorkflowStoreTemplate
}>()
const emit = defineEmits<{ use: [template: WorkflowStoreTemplate] }>()

/* 模板详情 */
const detailDrawerMounted = ref(false)
const detailDrawerRef = useTemplateRef<InstanceType<typeof TemplateStoreDetailDrawer>>('detailDrawerRef')

function handleOpenDetail() {
  detailDrawerMounted.value = true
  nextTick(() => detailDrawerRef.value?.open(props.template))
}

/* 使用模板交由模板中心统一处理。 */
function handleUseTemplate() {
  if (!props.disabled) emit('use', props.template)
}
</script>

<template>
  <MkSourceCard :title="template.name">
    <template #icon>
      <el-avatar class="bg-transparent!" shape="square" :size="24">
        <img :src="resetUrl(template.icon, true)" alt="" />
      </el-avatar>
    </template>
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
          <el-button class="flex-1!" type="primary" :disabled="disabled" @click="handleUseTemplate">使用</el-button>
        </div>
      </component>
    </template>
  </MkSourceCard>
  <TemplateStoreDetailDrawer
    v-if="detailDrawerMounted"
    ref="detailDrawerRef"
    :resource="resource"
    :disabled="disabled"
    @use="handleUseTemplate"
    @closed="detailDrawerMounted = false"
  />
</template>
