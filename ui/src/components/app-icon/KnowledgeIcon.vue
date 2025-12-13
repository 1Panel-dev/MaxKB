<template>
  <el-avatar v-if="type == 1" class="avatar-purple" shape="square" :size="size">
    <img src="@/assets/knowledge/icon_web.svg" style="width: 58%" alt="" />
  </el-avatar>
  <el-avatar
    v-else-if="type == 2"
    class="avatar-purple"
    shape="square"
    :size="size"
    style="background: none"
  >
    <img src="@/assets/knowledge/logo_lark.svg" style="width: 100%" alt="" />
  </el-avatar>
  <el-avatar
    v-else-if="type == 4"
    class="avatar-orange"
    shape="square"
    :size="size"
  >
    <img src="@/assets/knowledge/logo_workflow.svg" style="width: 60%" alt="" />
  </el-avatar>
  <el-avatar v-else class="avatar-blue" shape="square" :size="size">
    <img src="@/assets/knowledge/icon_document.svg" style="width: 58%" alt="" />
  </el-avatar>
</template>
<script setup lang="ts">
defineOptions({ name: 'KnowledgeIcon' })
const props = defineProps({
  type: {
    type: [String, Number],
    default: '',
  },
  size: {
    type: [String, Number],
    default: 32,
  },
})
</script>
