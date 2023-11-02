<template>
  <el-tabs v-model="activeName" class="demo-tabs" @tab-click="handleClick">
    <el-tab-pane label="User" name="first">
      <div>
        
      </div>

    </el-tab-pane>
    <el-tab-pane label="Config" name="second">Config</el-tab-pane>
    <el-tab-pane label="Role" name="third">Role</el-tab-pane>
    <el-tab-pane label="Task" name="fourth">Task</el-tab-pane>
  </el-tabs>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import type { TabsPaneContext } from 'element-plus'
const activeName = ref('first')
onMounted(() => {})

const handleClick = (tab: TabsPaneContext, event: Event) => {
  console.log(tab, event)
}
</script>
<style scoped lang="scss">
.set-rules {
  &__radio {
    display: block;
  }
}
</style>
