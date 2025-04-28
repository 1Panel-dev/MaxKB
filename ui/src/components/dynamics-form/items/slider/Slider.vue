<template>
  <el-slider v-bind="$attrs" show-input :show-input-controls="false" class="custom-slider" />
</template>
<script setup lang="ts"></script>
<style lang="scss" scoped>
.custom-slider {
  .el-input-number.is-without-controls .el-input__wrapper {
    padding: 0 !important;
  }
}
</style>
