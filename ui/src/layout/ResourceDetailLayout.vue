<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { getMatchedChildRouteList } from '@/router/admin/utils'
import type { LayoutMenuItem } from './types'
import ResourceDetailMenu from './sidebar/ResourceDetailMenu.vue'

defineOptions({ name: 'ResourceDetailLayout' })

const props = withDefaults(defineProps<{ loading?: boolean }>(), { loading: false })

const emit = defineEmits<{ back: [] }>()

defineSlots<{ 'resource-header': () => unknown }>()

const route = useRoute()
const router = useRouter()
const detailMenuItems = computed(() => getMatchedChildRouteList(route))
const activeDetailMenuName = computed(() => route.meta.detailActiveMenu ?? String(route.name ?? ''))

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
        <div class="flex-align-center min-w-0 gap-2">
          <!-- 返回资源列表 -->
          <el-button class="-ml-1" text @click="navigateBack">
            <MkIcon name="icon_arrow-left_outlined" :size="20" />
          </el-button>
          <slot name="resource-header" />
        </div>
      </component>

      <el-scrollbar class="min-h-0 flex-1">
        <ResourceDetailMenu :menu-items="detailMenuItems" :active-name="activeDetailMenuName" @select="navigateToDetailMenu" />
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
