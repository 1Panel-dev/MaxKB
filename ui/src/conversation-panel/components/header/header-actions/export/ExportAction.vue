<script setup lang="ts">
import { inject, onBeforeUnmount, ref } from 'vue'
import type { Options } from '@popperjs/core'
import MkDropdown from '@/components/global/mk-dropdown/index.vue'
import ExportPreviewDialog from './ExportPreviewDialog.vue'
import { useConversationExport } from './use-conversation-export.ts'
import { EXPORT_MESSAGE_ELEMENT_KEY } from './context.ts'
import { MsgError } from '@/utils/message'

withDefaults(defineProps<{ display?: 'button' | 'menu' }>(), { display: 'button' })
defineOptions({ inheritAttrs: false })
const { disabled, loading, fileName, exportText } = useConversationExport()
const getMessageElement = inject(EXPORT_MESSAGE_ELEMENT_KEY, () => null)
const dropdownRef = ref<InstanceType<typeof MkDropdown>>()
const submenuOpen = ref(false)
// 优先向左展开，空间不足时仅回退到右侧，避免子菜单挤到主菜单下方。
const submenuOptions: Partial<Options> = {
  modifiers: [{ name: 'flip', options: { fallbackPlacements: ['right-start'] } }],
}
function selectFormat(format: 'markdown' | 'html' | 'pdf') {
  dropdownRef.value?.handleClose()
  if (format === 'pdf') void previewPdf()
  else void exportText(format)
}
const previewRef = ref<InstanceType<typeof ExportPreviewDialog>>()
let disposed = false
onBeforeUnmount(() => {
  disposed = true
})

async function previewPdf() {
  if (disabled.value) return
  const element = getMessageElement()
  if (!element) return
  const name = fileName()
  loading.value = true
  try {
    const { captureMessages } = await import('./capture.ts')
    const canvas = await captureMessages(element)
    if (!disposed) previewRef.value?.open(canvas, name)
  } catch {
    if (!disposed) MsgError('导出预览失败，请等待内容加载完成后重试')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="inline-flex" :class="{ 'w-full': display === 'menu' }">
    <MkDropdown
      ref="dropdownRef"
      :disabled="disabled"
      :trigger="display === 'menu' ? ['hover', 'click'] : 'click'"
      :placement="display === 'menu' ? 'left-start' : 'bottom-end'"
      :popper-options="display === 'menu' ? submenuOptions : undefined"
      :hide-on-click="false"
      class="w-full"
      @visible-change="submenuOpen = $event"
    >
      <!-- 导出子菜单：沿用菜单项外观，展开时保留当前行高亮 -->
      <span v-if="display === 'menu'" class="inline-flex w-full">
        <MkDropdownItem
          :disabled="disabled"
          class="export-menu-trigger min-w-32! [&.is-disabled_.mk-icon]:text-N400!"
          :class="{ 'is-open': submenuOpen }"
        >
          <template #icon><MkIcon name="icon_export_outlined" /></template>
          <span class="flex-1">导出</span>
          <MkIcon name="icon_right_outlined" class="text-N500" />
        </MkDropdownItem>
      </span>
      <!-- 桌面端导出图标入口 -->
      <span v-else class="inline-flex">
        <MkTooltip content="导出">
          <el-button text :disabled="disabled" :loading="loading" class="[&_.mk-icon]:text-N900! [&.is-disabled_.mk-icon]:text-N400!">
            <MkIcon name="icon_export_outlined" :size="18" />
          </el-button>
        </MkTooltip>
      </span>
      <template #dropdown>
        <MkDropdownMenu>
          <!-- 导出 Markdown -->
          <MkDropdownItem :disabled="disabled" @click="selectFormat('markdown')">导出 Markdown</MkDropdownItem>
          <!-- 导出 HTML -->
          <MkDropdownItem :disabled="disabled" @click="selectFormat('html')">导出 HTML</MkDropdownItem>
          <!-- 预览并导出 PDF -->
          <MkDropdownItem :disabled="disabled" @click="selectFormat('pdf')">导出 PDF</MkDropdownItem>
        </MkDropdownMenu>
      </template>
    </MkDropdown>
    <ExportPreviewDialog ref="previewRef" />
  </div>
</template>

<style scoped lang="scss">
.export-menu-trigger.is-open {
  background-color: var(--mk-N900-transparent-10);
}
</style>
