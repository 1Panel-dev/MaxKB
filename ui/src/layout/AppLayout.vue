<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { LayoutMode } from './types'
import LayoutHeader from './LayoutHeader.vue'
import LayoutSidebar from './LayoutSidebar.vue'
import { useStore } from '@/stores'

const { t } = useI18n({ useScope: 'global' })
const route = useRoute()

withDefaults(defineProps<{ preview?: boolean }>(), { preview: false })
const { auth } = useStore()
const mode = computed<LayoutMode>(() => route.meta.scope ?? 'workspace')
</script>

<template>
  <div class="mk-layout flex-column overflow-hidden" :class="preview ? 'h-full' : 'h-screen'">
    <el-alert
      v-if="auth.isExpire"
      :title="t('layout.licenseMissingOrExpired')"
      type="warning"
      class="shrink-0 rounded-none! border-b"
      show-icon
      :closable="false"
    />
    <LayoutHeader class="shrink-0" :mode="preview ? 'workspace' : mode" :preview="preview" />
    <div class="flex min-h-0 flex-1">
      <aside v-if="preview" class="w-sidebar"></aside>
      <LayoutSidebar v-else :mode="mode" />
      <main class="mk-layout__main w-full overflow-hidden rounded-tl-xl bg-white transition-[margin] duration-200">
        <RouterView v-if="!preview" />
      </main>
    </div>
  </div>
</template>

<style scoped lang="scss">
.mk-layout {
  background: rgb(var(--mk-primary-rgb) / 5%);

  &__main {
    box-shadow: 0px 0px 4px 0px rgb(var(--mk-N900-rgb) / 2%);
  }
}
</style>
