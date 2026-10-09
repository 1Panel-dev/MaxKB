<script setup lang="ts">
import type { ChatApplicationProfile } from '@/api/types'

defineOptions({ name: 'PortalApplicationCards' })

defineProps<{ applications: ChatApplicationProfile[] }>()

const emit = defineEmits<{ select: [applicationId: string] }>()
</script>

<template>
  <!-- 门户智能体卡片：全部智能体页与选择智能体抽屉共用，点击卡片或“去对话”进入该智能体的新建对话 -->
  <div class="portal-application-cards">
    <el-card
      v-for="application in applications"
      :key="application.id"
      shadow="hover"
      class="group cursor-pointer"
      @click="emit('select', application.id)"
    >
      <div class="mb-2 flex-align-center gap-2">
        <ApplicationIcon :icon="application.icon" :size="20" class="shrink-0" />
        <h4 class="min-w-0 flex-1 truncate" :title="application.name">{{ application.name }}</h4>
        <!-- 去对话 -->
        <el-button type="primary" size="small" class="invisible shrink-0 group-hover:visible" @click.stop="emit('select', application.id)">
          去对话
        </el-button>
      </div>
      <div class="line-clamp-2 h-11 text-sm text-N600" :title="application.desc || ''">{{ application.desc || '暂无描述' }}</div>
    </el-card>
  </div>
</template>

<style scoped lang="scss">
.portal-application-cards {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
}
</style>
