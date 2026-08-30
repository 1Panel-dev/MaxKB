<script setup lang="ts">
import { computed, nextTick, ref, useTemplateRef } from 'vue'
import type { ToolStoreItem } from '@/api/types'
import MkSourceCard from '@/components/mk-source-card/index.vue'
import { resetUrl } from '@/utils/icon'
import { numberFormat } from '@/utils/number'
import StoreToolFormDialog from '../../tool-form/StoreToolFormDialog.vue'
import ToolStoreDetailDrawer from '../ToolStoreDetailDrawer.vue'

defineOptions({ name: 'ToolStoreCard' })

const props = defineProps<{ categoryTitle: string; folderId: string; tool: ToolStoreItem }>()

const emit = defineEmits<{ refresh: [] }>()

const toolTypeLabel = computed(() => (props.tool.label === 'data_source' ? '数据源' : '工具'))

/* 商店详情 */
const detailDrawerMounted = ref(false)
const detailDrawerRef = useTemplateRef<InstanceType<typeof ToolStoreDetailDrawer>>('detailDrawerRef')

function openDetailDrawer(content?: string) {
  detailDrawerMounted.value = true
  nextTick(() => detailDrawerRef.value?.open(props.tool, content))
}

function handleOpenDetail() {
  if (props.tool.source !== 'internal' || !props.tool.icon?.includes('icon.png')) {
    openDetailDrawer()
    return
  }

  const detailUrl = resetUrl(props.tool.icon.replace('icon.png', 'detail.md'))
  fetch(detailUrl)
    .then((response) => (response.ok ? response.text() : Promise.reject(response)))
    .then((content) => openDetailDrawer(content))
    .catch(() => openDetailDrawer())
}

/* 添加商店工具 */
const storeToolFormDialogMounted = ref(false)
const storeToolFormDialogRef = useTemplateRef<InstanceType<typeof StoreToolFormDialog>>('storeToolFormDialogRef')

function handleOpenAdd(tool = props.tool) {
  storeToolFormDialogMounted.value = true
  nextTick(() => storeToolFormDialogRef.value?.open(tool))
}
</script>

<template>
  <MkSourceCard :title="tool.name">
    <template #icon>
      <ToolIcon :icon="tool.icon" :size="32" :type="tool.tool_type" />
    </template>
    <template #title="{ title }">
      <h6 class="min-w-0 truncate" :title="title">{{ title }}</h6>
      <el-tag v-if="tool.version" size="small" type="info" effect="plain">{{ tool.version }}</el-tag>
    </template>
    <template #subtitle>{{ categoryTitle }}</template>
    <template #tag>
      <el-tag size="small" type="info">{{ toolTypeLabel }}</el-tag>
    </template>

    <p class="line-clamp-2" :title="tool.desc ?? undefined">{{ tool.desc || '-' }}</p>

    <template #footer="{ Action }">
      <span class="-mb-3 flex items-center gap-1 text-sm text-N600 group-hover:hidden group-focus-within:hidden">
        <MkIcon v-if="tool.downloads !== undefined" name="icon_download_outlined" />
        {{ tool.downloads && numberFormat(tool.downloads) }}
      </span>

      <component :is="Action" class="flex-1!">
        <div class="flex min-w-0 flex-1" @click.stop>
          <el-button class="flex-1!" plain @click="handleOpenDetail">详情</el-button>
          <el-button class="flex-1!" type="primary" @click="handleOpenAdd()"> 应用 </el-button>
        </div>
      </component>
    </template>
  </MkSourceCard>

  <ToolStoreDetailDrawer v-if="detailDrawerMounted" ref="detailDrawerRef" @add="handleOpenAdd" @closed="detailDrawerMounted = false" />
  <StoreToolFormDialog
    v-if="storeToolFormDialogMounted"
    ref="storeToolFormDialogRef"
    @closed="storeToolFormDialogMounted = false"
    @refresh="emit('refresh')"
    :folderId="folderId"
  />
</template>
