<script setup lang="ts">
import { computed, reactive, ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import type { ChatContent } from '@/api/types'
import ScrollDiff from './components/ScrollDiff.vue'
import { parsePatch } from './patch/parsePatch'
import type { PatchFileStatus } from './patch/patchTypes'
import { extractPartialJsonField } from './extract-partial-json'
import { Scroll } from '@/conversation-panel/core/scroll'

defineOptions({ name: 'ConversationPatchContent' })

const props = defineProps<{ content: ChatContent; loading: boolean }>()
const expanded = defineModel<boolean>('expanded', { required: true })

const multiScrollRef = ref<HTMLElement>()
let multiScroll: Scroll | null = null

function initScroll() {
  multiScroll?.destroy()
  if (multiScrollRef.value) {
    multiScroll = new Scroll(multiScrollRef.value)
    multiScroll.forceBottom()
  }
}

onMounted(() => {
  if (expanded.value) initScroll()
})

watch(
  [expanded, multiScrollRef],
  () => {
    if (expanded.value && multiScrollRef.value) {
      initScroll()
    } else {
      multiScroll?.destroy()
      multiScroll = null
    }
  },
  { flush: 'post' },
)

onBeforeUnmount(() => multiScroll?.destroy())

const patchDiff = computed(() => {
  const raw = props.content.arguments
  if (!raw) return ''
  try {
    return extractPartialJsonField(raw, 'patch')
  } catch {
    return raw
  }
})

watch(patchDiff, () => {
  nextTick(() => multiScroll?.scrollBottom())
})

const files = computed(() => (patchDiff.value ? parsePatch(patchDiff.value) : []))
const singleFile = computed(() => (files.value.length === 1 ? files.value[0] : null))

const singleTitle = computed(() => {
  if (!singleFile.value) return 'apply patch'
  return `${verb(singleFile.value.status)} ${singleFile.value.newPath || singleFile.value.oldPath}`
})

const summary = computed(() =>
  files.value.reduce(
    (acc, f) => {
      acc.additions += f.additions
      acc.deletions += f.deletions
      return acc
    },
    { additions: 0, deletions: 0 },
  ),
)

// 多文件分别保留展开状态，默认收起。
const fileExpanded = reactive<Record<number, boolean>>({})
const patchTitle = computed(() => (files.value.length > 1 ? `Edit ${files.value.length} files` : singleTitle.value))
const patchStats = computed(() => singleFile.value ?? summary.value)

function verb(status: PatchFileStatus) {
  const map: Record<PatchFileStatus, string> = {
    add: 'Create',
    modify: 'Edit',
    delete: 'Delete',
    rename: 'Rename',
    copy: 'Copy',
    mode: 'Mode',
    binary: 'Binary',
    unknown: 'Unknown',
  }
  return map[status] ?? 'Edit'
}
</script>

<template>
  <!-- 展开或收起文件差异 -->
  <MkCollapse class="w-full" v-model:expanded="expanded" indicator-position="after" trigger-class="group text-N500! mb-2 w-fit hover:text-N900!">
    <template #indicator="{ expanded }">
      <MkIcon
        name="icon_right_outlined"
        :size="12"
        class="transition-transform text-N500! group-hover:text-N900!"
        :class="{ 'rotate-90': expanded }"
      />
    </template>
    <template #label>
      <span v-if="loading" class="mk-conversation-loading" />
      <svg class="shrink-0" viewBox="0 0 16 16" width="16" height="16" fill="none">
        <path d="M2 3.5h12M2 8h12M2 12.5h8" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" />
      </svg>
      <span class="min-w-0 max-w-[300px] truncate" :title="patchTitle">{{ patchTitle }}</span>
      <span v-if="patchStats.additions" class="tc-stat add">+{{ patchStats.additions }}</span>
      <span v-if="patchStats.deletions" class="tc-stat del">-{{ patchStats.deletions }}</span>
    </template>
    <ScrollDiff v-if="expanded && singleFile" :file="singleFile" />
    <div v-else-if="expanded && files.length > 1" ref="multiScrollRef" class="tc-files tc-scroll-files">
      <template v-for="(file, index) in files" :key="`${file.status}:${file.newPath}:${index}`">
        <!-- 展开或收起单个文件差异 -->
        <MkCollapse
          v-model:expanded="fileExpanded[index]"
          :default-expanded="false"
          class="py-0.5"
          indicator-position="after"
          trigger-class="group text-N500! mb-2 w-fit max-w-full hover:text-N900!"
        >
          <template #indicator="{ expanded }">
            <MkIcon
              name="icon_right_outlined"
              :size="12"
              class="transition-transform text-N500! group-hover:text-N900!"
              :class="{ 'rotate-90': expanded }"
            />
          </template>
          <template #label>
            <span class="shrink-0 text-xs font-semibold">{{ verb(file.status) }}</span>
            <span class="min-w-0 max-w-[300px] truncate font-mono text-xs text-N600" :title="file.newPath || file.oldPath">
              {{ file.newPath || file.oldPath }}
            </span>
            <span v-if="file.additions" class="tc-stat add">+{{ file.additions }}</span>
            <span v-if="file.deletions" class="tc-stat del">-{{ file.deletions }}</span>
          </template>
          <ScrollDiff v-if="fileExpanded[index]" :file="file" />
        </MkCollapse>
      </template>
    </div>
  </MkCollapse>
</template>

<style scoped>
.tc-stat {
  flex-shrink: 0;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 11px;
}
.tc-stat.add {
  color: var(--el-color-success-dark-2);
}
.tc-stat.del {
  color: var(--mk-danger);
}
.tc-scroll-files {
  max-height: 400px;
  overflow-y: auto;
}
.tc-files {
  background: var(--mk-N100);
  border-radius: 6px;
  padding: 6px 10px;
}
</style>
