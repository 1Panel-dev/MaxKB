<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'

import type { ApplicationDetail } from '@/api/types'
import MkSourceCard from '@/components/mk-source-card/index.vue'
import { resetUrl } from '@/utils/common'
import { isWorkFlow } from '@/utils/application'
import { dateFormat } from '@/utils/time'

defineOptions({ name: 'ApplicationCard' })

const router = useRouter()
const route = useRoute()
const {
  params: { workspaceId },
} = route

const props = defineProps<{
  application: ApplicationDetail
}>()

function handleSettingApplication(event: MouseEvent) {
  event.stopPropagation()
  if (isWorkFlow(props.application.type)) {
    const workflowRoute = {
      name: 'workflow-application',
      params: { workspaceId, applicationId: props.application.id },
    } as const

    if (event.ctrlKey || event.metaKey) {
      window.open(router.resolve(workflowRoute).href)
      return
    }
    router.push(workflowRoute)
  }
}
</script>

<template>
  <MkSourceCard
    :create_time="application.create_time"
    :nick_name="application.nick_name || '-'"
    :title="application.name"
  >
    <template #icon>
      <el-avatar class="bg-transparent!" shape="square" :size="24">
        <img :src="resetUrl(application?.icon, true)" />
      </el-avatar>
    </template>

    <template #tag>
      <el-tag v-if="isWorkFlow(application.type)" type="warning" size="small"> 高级 </el-tag>
      <el-tag v-else type="primary" size="small"> 简易 </el-tag>
    </template>

    <p class="line-clamp-2" :title="application?.desc ?? undefined">
      {{ application?.desc }}
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
          <MkDropdownMenu>
            <MkDropdownItem @click="handleSettingApplication">
              <template #icon><MkIcon name="icon-setting" /></template>
              <span>设置</span>
            </MkDropdownItem>
          </MkDropdownMenu>
        </component>
      </component>
    </template>
  </MkSourceCard>
</template>
