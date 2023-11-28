<template>
  <card-box
    style="
      --app-card-box-description-height: 100%;
      --card-min-height: 153px;
      --card-min-width: 20px;
      width: 100%;
    "
    :title="model.name"
  >
    <template #icon>
      <AppAvatar
        class="mr-12"
        shape="square"
        style="--el-avatar-bg-color: rgba(255, 255, 255, 0)"
        :size="32"
      >
        <span style="height: 24px; width: 24px" :innerHTML="icon"></span
      ></AppAvatar>
    </template>
    <template #description>
      <el-descriptions :column="1" label-align="center">
        <el-descriptions-item label="模型类型" label-class-name="ellipsis-1">
          <span class="ellipsis-1"> {{ model.model_type }}</span></el-descriptions-item
        >
        <el-descriptions-item label="模型名称" label-class-name="ellipsis-1">
          <span class="ellipsis-1">{{ model.model_name }}</span></el-descriptions-item
        >
      </el-descriptions>
    </template>
  </card-box>
</template>
<script setup lang="ts">
import type { Provider, Model } from '@/api/type/model'
import { computed } from 'vue'
const props = defineProps<{
  model: Model
  provider_list: Array<Provider>
}>()

const icon = computed(() => {
  return props.provider_list.find((p) => p.provider === props.model.provider)?.icon
})
</script>
<style lang="scss" scoped>
:deep(.el-descriptions__cell) {
  display: flex;
  flex-wrap: nowrap;
}
</style>
