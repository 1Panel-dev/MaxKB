<template>
  <el-dropdown placement="bottom-start" class="workspace-dropdown">
    <el-button text style="font-size: 14px" class="workspace-dropdown__button">
      <AppIcon iconName="app-workspace" style="font-size: 18px"></AppIcon>
      <span class="ellipsis" style="max-width: 155px">
        {{ currentWorkspace?.name }}
      </span>
      <el-icon class="el-icon--right">
        <CaretBottom />
      </el-icon>
    </el-button>
    <template #dropdown>
      <el-dropdown-menu v-loading="loading">
        <el-dropdown-item
          v-for="item in data"
          :key="item.id"
          :class="item.id === currentWorkspace?.id ? 'active' : ''"
          @click="changeWorkspace(item)"
        >
          <AppIcon class="mr-8" iconName="app-workspace" style="font-size: 16px"></AppIcon>
          <span class="ellipsis" style="max-width: 230px">
            {{ item.name }}
          </span>
          <el-icon
            v-show="item.id === currentWorkspace?.id"
            class="ml-8"
            style="font-size: 16px; margin-right: 0"
          >
            <Check />
          </el-icon>
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { WorkspaceItem } from '@/api/type/workspace'
import useStore from '@/stores'
const props = defineProps({
  data: {
    type: Array<any>,
    default: () => [],
  },
  currentWorkspace: {
    type: Object,
    default: () => {},
  },
})

const { folder } = useStore()
const loading = ref(false)
const emit = defineEmits(['changeWorkspace'])
function changeWorkspace(item: WorkspaceItem) {
  folder.setCurrentFolder({})
  emit('changeWorkspace', item)
}
</script>
<style lang="scss" scoped>
.workspace-dropdown {
  &__button {
    font-size: 14px;
    padding: 0 12px !important;
    max-height: 32px;
  }
}
</style>
