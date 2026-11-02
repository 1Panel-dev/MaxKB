<script setup lang="ts">
import type { ChatApplicationProfile } from '@/api/types'

defineOptions({ name: 'PortalApplicationCards' })

defineProps<{ applications: ChatApplicationProfile[] }>()

const emit = defineEmits<{ select: [applicationId: string] }>()
</script>

<template>
  <!-- 门户智能体卡片：全部智能体页与选择智能体抽屉共用，点击卡片进入该智能体的新建对话 -->
  <div class="portal-application-cards mk-resource-card-grid">
    <template v-for="application in applications" :key="application.id">
      <MkResourceCard :title="application.name" class="min-h-29!" @click="emit('select', application.id)">
        <template #icon>
          <ApplicationIcon :icon="application.icon" :size="20" class="shrink-0" />
        </template>
        <div class="line-clamp-2" :title="application.desc || ''">{{ application.desc || '暂无描述' }}</div>
      </MkResourceCard>
    </template>
  </div>
</template>

<style scoped lang="scss"></style>
