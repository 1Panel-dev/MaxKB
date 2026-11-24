<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ToolStoreItem } from '@/api/types'
import { numberFormat } from '@/utils/number'

defineOptions({ name: 'ToolStoreDetailDrawer' })

const { t } = useI18n({ useScope: 'global' })
const props = withDefaults(defineProps<{ showAdd?: boolean }>(), { showAdd: true })

const emit = defineEmits<{ add: [tool: ToolStoreItem]; closed: [] }>()

const visible = ref(false)
const detailContent = ref('')
const toolDetail = ref<ToolStoreItem>()

function handleAdd() {
  if (!toolDetail.value) return
  emit('add', toolDetail.value)
  visible.value = false
}

function open(tool: ToolStoreItem, content?: string) {
  toolDetail.value = tool
  detailContent.value = content || tool.readMe || tool.desc || ''
  visible.value = true
}

function resetData() {
  detailContent.value = ''
  toolDetail.value = undefined
  emit('closed')
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" :title="t('common.labels.details')" close-on-click-modal close-on-press-escape size="60%" @closed="resetData">
    <template v-if="toolDetail">
      <div class="border-b pb-6 mb-3">
        <div class="flex-between gap-4">
          <div class="flex-align-center min-w-0 gap-4">
            <ToolIcon :icon="toolDetail.icon" :size="60" :type="toolDetail.tool_type" />
            <div class="min-w-0">
              <h3 class="truncate" :title="toolDetail.name">{{ toolDetail.name }}</h3>
              <span class="flex-align-center gap-1 text-N600">
                <MkIcon v-if="toolDetail.downloads !== undefined" name="icon_download_outlined" />
                {{ toolDetail.downloads && numberFormat(toolDetail.downloads) }}
              </span>
            </div>
          </div>
          <el-button v-if="props.showAdd" type="primary" @click="handleAdd">{{ t('tool.store.apply') }}</el-button>
        </div>
        <p class="mt-3 text-N600">{{ toolDetail.desc }}</p>
      </div>

      <MdPreview :modelValue="detailContent || t('common.empty.noDetails')" />
    </template>
  </MkDrawer>
</template>

<style scoped lang="scss"></style>
