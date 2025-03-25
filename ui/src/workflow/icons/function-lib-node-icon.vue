<template>
  <AppAvatar
    v-if="isAppIcon(item?.icon)"
    shape="square"
    :size="32"
    style="background: none"
    class="mr-8"
  >
    <img :src="item?.icon" alt="" />
  </AppAvatar>
  <AppAvatar v-else shape="square" style="background: #34c724">
    <img src="@/assets/icon_function_outlined.svg" style="width: 75%" alt="" />
  </AppAvatar>
</template>
<script setup lang="ts">
import { isAppIcon } from '@/utils/application'
const props = defineProps<{
  item?: {
    name: string
    icon: string
  }
}>()
</script>

<script setup lang="ts"></script>
