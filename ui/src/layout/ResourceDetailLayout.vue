<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { getMatchedChildRouteList } from '@/router/admin/utils'
import type { LayoutMenuItem } from './types'

defineOptions({ name: 'ResourceDetailLayout' })

const props = withDefaults(defineProps<{ loading?: boolean }>(), { loading: false })

const emit = defineEmits<{ back: [] }>()

defineSlots<{ 'resource-header': () => unknown }>()

const route = useRoute()
const router = useRouter()
const detailMenuItems = computed(() => getMatchedChildRouteList(route))
const activeDetailMenuName = computed(() => route.meta.detailActiveMenu ?? String(route.name ?? ''))

function isDetailMenuActive(detailMenuItem: LayoutMenuItem) {
  return detailMenuItem.name === activeDetailMenuName.value
}

function navigateBack() {
  emit('back')
}

function navigateToDetailMenu(detailMenuItem: LayoutMenuItem) {
  void router.push({ name: detailMenuItem.name, params: route.params, query: route.query })
}
</script>

<template>
  <MkViewLayout :loading="props.loading" title="">
    <template #aside="{ Header }">
      <component :is="Header">
        <div class="flex min-w-0 items-center gap-1">
          <el-button class="-ml-1" text @click="navigateBack">
            <MkIcon name="icon_arrow-left_outlined" :size="20" />
          </el-button>
          <slot name="resource-header" />
        </div>
      </component>

      <el-scrollbar class="min-h-0 flex-1">
        <div class="space-y-1 px-4">
          <template v-for="detailMenuItem in detailMenuItems" :key="detailMenuItem.name">
            <MkListItem :active="isDetailMenuActive(detailMenuItem)" @click="navigateToDetailMenu(detailMenuItem)">
              <template #default="{ active }">
                <MkIcon
                  v-if="detailMenuItem.icon"
                  class="mr-3"
                  :name="active ? (detailMenuItem.activeIcon ?? detailMenuItem.icon) : detailMenuItem.icon"
                />
                <span class="min-w-0 flex-1 truncate" :title="detailMenuItem.label">{{ detailMenuItem.label }}</span>
              </template>
            </MkListItem>
          </template>
        </div>
      </el-scrollbar>
    </template>

    <template #default="{ Header }">
      <component :is="Header">
        <h4>{{ route.meta.title }}</h4>
      </component>
      <RouterView />
    </template>
  </MkViewLayout>
</template>
