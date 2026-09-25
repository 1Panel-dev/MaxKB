<script lang="ts">
/** 资源详情布局直接传给当前子页面的标题栏属性。 */
export interface ResourceDetailPageProps {
  headerTarget: HTMLElement | null
  title: string
}
</script>

<script setup lang="ts">
import { computed, shallowRef } from 'vue'
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

/* 提供整个标题栏的挂载位置和当前路由标题。 */
const headerTarget = shallowRef<HTMLElement | null>(null)
const title = computed(() => route.meta.title ?? '')
const detailPageRef = shallowRef<{ customHeader?: boolean } | null>(null)

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
        <div v-show="detailPageRef?.customHeader" ref="headerTarget" class="w-full min-w-0" />
        <h4 v-if="!detailPageRef?.customHeader">{{ title }}</h4>
      </component>
      <RouterView v-slot="{ Component }">
        <component :is="Component" ref="detailPageRef" :header-target="headerTarget" :title="title" />
      </RouterView>
    </template>
  </MkViewLayout>
</template>
