<template>
  <el-avatar
    v-if="isAppIcon(item?.icon)"
    shape="square"
    :size="32"
    style="background: none"
    class="mr-8"
  >
    <img :src="item?.icon" alt="" />
  </el-avatar>
  <el-avatar
    v-else-if="item?.name"
    :name="item?.name"
    pinyinColor
    shape="square"
    :size="32"
    class="mr-8"
  />
</template>
<script setup lang="ts">
import { isAppIcon } from '@/utils/common'
const props = defineProps<{
  item: {
    name: string
    icon: string
  }
}>()
</script>
