<script setup lang="ts">
import { computed } from 'vue'
import type { PatchFileInfo } from './patchTypes'

const props = withDefaults(
  defineProps<{
    file: PatchFileInfo
    showMeta?: boolean
    showHunk?: boolean
  }>(),
  {
    showMeta: false,
    showHunk: false,
  },
)

const displayLines = computed(() =>
  props.file.lines.filter((line) => {
    if (!props.showMeta && line.type === 'meta') return false
    if (!props.showHunk && line.type === 'hunk') return false
    return true
  }),
)
</script>

<template>
  <div class="file-diff">
    <div class="fd-code-wrap">
      <table class="fd-table">
        <tbody>
          <tr v-for="(line, index) in displayLines" :key="index" class="fd-row" :class="`fd-row-${line.type}`">
            <template v-if="line.type === 'hunk'">
              <td class="fd-hunk" colspan="3">{{ line.content }}</td>
            </template>
            <template v-else>
              <td class="fd-ln">{{ line.displayLineNumber ?? '' }}</td>
              <td class="fd-prefix">{{ line.prefix }}</td>
              <td class="fd-code">
                <code>{{ line.content || ' ' }}</code>
              </td>
            </template>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="!displayLines.length" class="fd-empty">仅文件状态变化，无代码内容变更。</div>
  </div>
</template>

<style scoped lang="scss">
.file-diff {
  .fd-code-wrap {
    overflow: hidden;
  }

  .fd-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    font-size: 11px;
    line-height: 20px;
    table-layout: fixed;
  }

  .fd-ln {
    width: 40px;
    min-width: 40px;
    padding: 0 8px 0 10px;
    text-align: right;
    user-select: none;
    vertical-align: top;
    border-right: 1px solid var(--mk-N300);
  }

  .fd-prefix {
    width: 20px;
    min-width: 20px;
    padding: 0 3px;
    text-align: center;
    user-select: none;
    vertical-align: top;
    font-weight: 600;
  }

  .fd-code {
    white-space: pre-wrap;
    word-break: break-all;
    vertical-align: top;
  }
  .fd-code code {
    display: inline;
    color: inherit;
    font: inherit;
    white-space: pre-wrap;
    word-break: break-all;
  }

  /* 行背景 */
  .fd-row-add {
    background: var(--el-color-success-light-9);
  }
  .fd-row-add .fd-ln,
  .fd-row-add .fd-prefix {
    color: var(--el-color-success-dark-2);
  }

  .fd-row-remove {
    background: rgba(239, 68, 68, 0.1);
  }
  .fd-row-remove .fd-ln,
  .fd-row-remove .fd-prefix {
    color: var(--mk-danger);
  }

  .fd-row-context,
  .fd-row-empty {
    background: var(--color-white);
  }

  .fd-hunk {
    padding: 2px 10px;
    color: var(--mk-N600);
    background: rgba(51, 112, 255, 0.1);
    white-space: pre-wrap;
    word-break: break-all;
    font-size: 10px;
  }

  .fd-empty {
    padding: 16px;
    color: var(--mk-N600);
    text-align: center;
    font-size: 12px;
  }
}
</style>
