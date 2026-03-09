<template>
  <LayoutContainer class="mindmap-container">
    <template #left>
      <h4 class="p-12-16 pb-0 mt-12">思维导图</h4>
    </template>
    <div class="mindmap-content">
      <iframe 
        src="http://10.100.52.76:3000/" 
        style="width: 100%; height: 100%; border: none;"
        title="思维导图"
      ></iframe>
    </div>
  </LayoutContainer>
</template>

<script setup lang="ts">
import LayoutContainer from '@/components/layout-container/index.vue'
</script>

<style scoped>
.mindmap-container {
  height: 100%;
  overflow: hidden;
}

.mindmap-content {
  height: 100%;
  overflow: hidden;
}
</style>
