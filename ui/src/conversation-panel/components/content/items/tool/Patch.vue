<template>
  <div class="tool-call">
    <!-- 单文件 -->
    <template v-if="files.length <= 1">
      <button class="tc-head" @click="expanded = !expanded">
        <svg class="tc-chevron" :class="{ open: expanded }" viewBox="0 0 16 16" fill="none">
          <path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        <span class="tc-icon" :class="{ spin: loading }">
          <Loading v-if="loading" :size="14" />
          <svg v-else viewBox="0 0 16 16" width="16" height="16" fill="none">
            <path d="M2 3.5h12M2 8h12M2 12.5h8" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" />
          </svg>
        </span>
        <span class="tc-name">{{ singleTitle }}</span>
        <template v-if="singleFile">
          <span class="tc-stat add" v-if="singleFile.additions">+{{ singleFile.additions }}</span>
          <span class="tc-stat del" v-if="singleFile.deletions">-{{ singleFile.deletions }}</span>
        </template>
      </button>
      <Transition enter-active-class="tc-expand-enter" leave-active-class="tc-expand-leave">
        <div v-if="expanded && singleFile" class="tc-body">
          <ScrollDiff :file="singleFile" />
        </div>
      </Transition>
    </template>

    <!-- 多文件：汇总 + 每个文件独立展开 -->
    <template v-else>
      <button class="tc-head" @click="expanded = !expanded">
        <svg class="tc-chevron" :class="{ open: expanded }" viewBox="0 0 16 16" fill="none">
          <path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        <span class="tc-icon" :class="{ spin: loading }">
          <Loading v-if="loading" :size="14" />
          <svg v-else viewBox="0 0 16 16" width="16" height="16" fill="none">
            <path d="M2 3.5h12M2 8h12M2 12.5h8" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" />
          </svg>
        </span>
        <span class="tc-name">Edit {{ files.length }} files</span>
        <span class="tc-stat add" v-if="summary.additions">+{{ summary.additions }}</span>
        <span class="tc-stat del" v-if="summary.deletions">-{{ summary.deletions }}</span>
      </button>
      <Transition enter-active-class="tc-expand-enter" leave-active-class="tc-expand-leave">
        <div v-if="expanded" class="tc-body">
          <div ref="multiScrollRef" class="tc-files tc-scroll-files">
            <div v-for="(file, i) in files" :key="`${file.status}:${file.newPath}:${i}`" class="tc-file-item">
              <button class="tc-file-head" @click="toggleFile(i)">
                <svg class="tc-chevron sm" :class="{ open: fileExpanded[i] }" viewBox="0 0 16 16" fill="none">
                  <path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                <span class="tc-file-verb">{{ verb(file.status) }}</span>
                <span class="tc-file-path">{{ file.newPath || file.oldPath }}</span>
                <span class="tc-stat add" v-if="file.additions">+{{ file.additions }}</span>
                <span class="tc-stat del" v-if="file.deletions">-{{ file.deletions }}</span>
              </button>
              <Transition enter-active-class="tc-expand-enter" leave-active-class="tc-expand-leave">
                <div v-if="fileExpanded[i]" class="tc-file-body">
                  <ScrollDiff :file="file" />
                </div>
              </Transition>
            </div>
          </div>
        </div>
      </Transition>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import Loading from '@/conversation-panel/loading/index.vue'
import ScrollDiff from './components/ScrollDiff.vue'
import { parsePatch } from './patch/parsePatch'
import type { PatchFileStatus } from './patch/patchTypes'
import { extractPartialJsonField } from './extract-partial-json'
import { Scroll } from '@/conversation-panel/core/scroll'

const props = defineProps<{ content: any; loading: boolean; expanded: boolean }>()

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
  if (props.expanded) initScroll()
})

watch(
  () => props.expanded,
  async (val) => {
    if (val) {
      await nextTick()
      initScroll()
    } else {
      multiScroll?.destroy()
      multiScroll = null
    }
  },
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

const expanded = ref(props.expanded)
watch(
  () => props.expanded,
  (val) => {
    expanded.value = val
  },
)
const fileExpanded = reactive<Record<number, boolean>>({})

function toggleFile(i: number) {
  fileExpanded[i] = !fileExpanded[i]
}

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

<style scoped>
.tool-call {
  width: 100%;
}

.tc-head {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 0;
  border: none;
  background: none;
  cursor: pointer;
  font-family: inherit;
  color: var(--mk-N500);
  transition: color 0.15s;
  max-width: 100%;
  overflow: hidden;
}
.tc-head:hover {
  color: var(--mk-N900);
}

.tc-chevron {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
  transition: transform 0.15s;
}
.tc-chevron.open {
  transform: rotate(90deg);
}
.tc-chevron.sm {
  width: 12px;
  height: 12px;
}

.tc-icon {
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.tc-icon.spin {
  color: var(--mk-N600);
}

.tc-name {
  font-size: 13px;
  font-weight: 500;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tc-stat {
  font-size: 11px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  flex-shrink: 0;
}
.tc-stat.add {
  color: #16a34a;
}
.tc-stat.del {
  color: var(--mk-danger);
}

.tc-expand-enter {
  animation: tc-open 0.2s ease-out;
  overflow: hidden;
}
.tc-expand-leave {
  animation: tc-close 0.15s ease-in forwards;
  overflow: hidden;
}
@keyframes tc-open {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 800px;
  }
}
@keyframes tc-close {
  from {
    opacity: 1;
    max-height: 800px;
  }
  to {
    opacity: 0;
    max-height: 0;
  }
}

.tc-body {
  padding: 6px 0 4px 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.tc-scroll-files {
  max-height: 400px;
  overflow-y: auto;
}

.tc-files {
  background: var(--mk-N100);
  border-radius: 6px;
  overflow: hidden;
  padding: 6px 10px;
}

.tc-file-item {
  padding: 2px 0;
}

.tc-file-head {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0;
  border: none;
  background: none;
  cursor: pointer;
  font-family: inherit;
  color: var(--mk-N500);
  transition: color 0.15s;
  max-width: 100%;
  overflow: hidden;
}
.tc-file-head:hover {
  color: var(--mk-N900);
}

.tc-file-verb {
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.tc-file-path {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 12px;
  color: var(--mk-N600);
}

.tc-file-body {
}
</style>
