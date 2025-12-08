<template>
  <el-dropdown
    trigger="click"
    placement="bottom-start"
    class="workspace-dropdown"
    popper-class="workspace-dropdown-popper"
  >
    <el-button text style="font-size: 14px" class="workspace-dropdown__button">
      <AppIcon iconName="app-workspace" style="font-size: 18px"></AppIcon>
      <span class="ellipsis" style="max-width: 155px" :title="currentWorkspace?.name">
        {{ i18n_name(currentWorkspace?.name) }}
      </span>
      <el-icon class="el-icon--right">
        <CaretBottom />
      </el-icon>
    </el-button>
    <template #dropdown>
      <div class="w-full p-8" style="box-sizing: border-box">
        <el-input
          v-model="filterText"
          :placeholder="$t('common.search')"
          prefix-icon="Search"
          clearable
        />
      </div>
      <el-scrollbar max-height="300">
        <el-dropdown-menu v-loading="loading">
          <el-dropdown-item
            v-for="item in filterData"
            :key="item.id"
            :class="`${item.id === currentWorkspace?.id ? 'active' : ''} flex-between`"
            @click="changeWorkspace(item)"
          >
            <div class="flex align-center" style="overflow: hidden">
              <AppIcon class="mr-8" iconName="app-workspace" style="font-size: 16px"></AppIcon>
              <span class="ellipsis" style="flex: 1" :title="item.name">
                {{ item.name }}
              </span>
              <TagGroup v-if="item.role_name" class="ml-8" size="small" :tags="item.role_name" />
            </div>
            <el-icon
              v-show="item.id === currentWorkspace?.id"
              class="ml-8"
              style="font-size: 16px; margin-right: 0"
            >
              <Check />
            </el-icon>
          </el-dropdown-item>
        </el-dropdown-menu>
      </el-scrollbar>
      <div class="no-data color-info" v-if="!filterData.length">{{ $t('common.noData') }}</div>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { watch, ref } from 'vue'
import { i18n_name } from '@/utils/common'
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

const filterText = ref('')
const filterData = ref<any[]>([])

watch(
  [() => props.data, () => filterText.value],
  () => {
    if (!filterText.value.length) {
      filterData.value = props.data
    }
    filterData.value = props.data.filter((v: any) =>
      v.name.toLowerCase().includes(filterText.value.toLowerCase()),
    )
  },
  { immediate: true },
)
</script>
<style lang="scss" scoped>
.workspace-dropdown {
  &__button {
    font-size: 14px;
    padding: 0 12px !important;
    max-height: 32px;
    color: var(--el-text-color-primary) !important;
  }
}

.no-data {
  text-align: center;
  padding-bottom: 16px;
  font-size: 14px;
}
</style>
<style lang="scss">
.workspace-dropdown-popper {
  width: 340px;
}
</style>
