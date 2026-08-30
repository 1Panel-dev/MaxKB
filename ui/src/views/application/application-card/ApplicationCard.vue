<script setup lang="ts">
import type { ApplicationDetail } from '@/api/types'
import MkSourceCard from '@/components/mk-source-card/index.vue'
import { resetUrl } from '@/utils/icon'
import { isWorkFlow } from '@/utils/application'
import { dateFormat } from '@/utils/time'

defineOptions({ name: 'ApplicationCard' })

defineProps<{ application: ApplicationDetail; selectable?: boolean; selected?: boolean }>()

const emit = defineEmits<{ selected: [selected: boolean] }>()

defineSlots<{ 'action-dropdown'?: () => unknown }>()
</script>

<template>
  <MkSourceCard
    :create_time="application.create_time"
    :nick_name="application.nick_name || '-'"
    :selectable="selectable"
    :selected="selected"
    :title="application.name"
    @selected="emit('selected', $event)"
  >
    <template #icon>
      <el-avatar class="bg-transparent!" shape="square" :size="24">
        <img :src="resetUrl(application.icon, true)" />
      </el-avatar>
    </template>

    <template #tag>
      <el-tag v-if="isWorkFlow(application.type)" type="warning" size="small">高级</el-tag>
      <el-tag v-else type="default" size="small">简易</el-tag>
    </template>

    <p class="line-clamp-2" :title="application.desc ?? undefined">
      {{ application.desc }}
    </p>

    <template #footer="{ Action, ActionDropdown }">
      <MkStatusLabel :active="application.is_publish" active-text="已发布" inactive-text="未发布" />
      <template v-if="application.is_publish">
        <el-divider direction="vertical" />
        <span class="flex items-center gap-2">
          <MkIcon name="icon_time_outlined" class="text-N500!" />
          <span class="text-N600">{{ dateFormat(application.update_time) }}</span>
        </span>
      </template>

      <component :is="Action">
        <el-divider direction="vertical" />
        <component :is="ActionDropdown">
          <slot name="action-dropdown" />
        </component>
      </component>
    </template>
  </MkSourceCard>
</template>
