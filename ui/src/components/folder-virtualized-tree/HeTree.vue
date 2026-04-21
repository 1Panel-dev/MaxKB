<template>
  <Draggable
    ref="treeRef"
    virtualization
    :defaultOpen="false"
    v-bind="$attrs"
    class="maxkb-virtualized-tree"
    @click:node="handleNodeClick"
  >
    <template #default="{ node, stat }">
      <div
        class="flex align-center maxkb-tree-node"
        :class="currentNodeKey === node.id ? 'is-current' : ''"
      >
        <el-icon
          class="tree-arrow-icon"
          :class="stat.open ? 'rotate-90' : ''"
          :style="{ visibility: stat.children.length ? 'visible' : 'hidden' }"
        >
          <CaretRight />
        </el-icon>
        <div class="tree-label lighter">
          <slot name="default" v-bind="{ node, stat }">
            <span :title="node.name">{{ node.name }}</span>
          </slot>
        </div>
      </div>
    </template>
  </Draggable>
</template>

<script lang="ts" setup>
import { ref, watch, nextTick } from 'vue'
import { Draggable } from '@he-tree/vue'
import '@he-tree/vue/style/default.css'
const props = defineProps({
  currentNodeKey: {
    type: String,
    default: 'default',
  },
})

type DraggableInstance = InstanceType<typeof Draggable>
const treeRef = ref<DraggableInstance | null>(null)
const emit = defineEmits(['handleNodeClick'])

const handleNodeClick = (node: any) => {
  node.open = !node.open
  emit('handleNodeClick', node.data)
}
</script>

<style lang="scss">
.maxkb-virtualized-tree {
  overflow: overlay !important;
  scrollbar-gutter: stable;

  ::-webkit-scrollbar-thumb {
    background-color: rgba(0, 0, 0, 0.2);
    border-radius: 5px;
    transition: all 0.2s ease-in-out;

    &:hover {
      cursor: pointer;
      background-color: rgba(0, 0, 0, 0.3);
    }
  }
  .tree-arrow-icon {
    color: var(--app-text-color-secondary);
    padding: 6px;
    font-size: 16px;
  }
  .tree-label {
    width: 100%;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  .tree-node {
    position: relative;
    border-radius: var(--el-border-radius-base);
    padding: 7px 0;
    cursor: pointer;
    width: 100%;
    box-sizing: border-box;
    &:hover {
      background: rgba(var(--el-text-color-primary-rgb), 0.1);
    }
    &:has(.maxkb-tree-node.is-current) {
      background: var(--el-color-primary-light-9);
      color: var(--el-color-primary);
      font-weight: 500;
    }
  }
}
</style>
