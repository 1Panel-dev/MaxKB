<template>
  <div class="flex">
    <AppAvatar>
      <img src="@/assets/user-icon.svg" style="width: 54%" alt="" />
    </AppAvatar>
    <div class="ml-8 w-full">
      <el-card shadow="always"> XXXXXXXXX </el-card>
      <el-card shadow="always" class="mt-12"> XXXXXXXXX </el-card>
    </div>
  </div>
</template>
<script setup lang="ts">
const props = defineProps({
  data: {
    type: Array<any>,
    default: () => []
  }
})
</script>
<style lang="scss" scoped></style>
