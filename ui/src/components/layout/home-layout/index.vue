<script setup lang="ts">
import TopBar from "@/components/layout/top-bar/index.vue"
</script>

<template>
    <div class="common-layout">
        <el-container>
            <el-header>
                <TopBar></TopBar>
            </el-header>
            <el-main>
                <RouterView></RouterView>
            </el-main>
        </el-container>
    </div>
</template>
<style lang="scss" scoped>
.el-header {
    --el-header-padding: 0;
    --el-header-height: 56px;
    padding: var(--el-header-padding);
    box-sizing: border-box;
    flex-shrink: 0;
    height: var(--el-header-height);
}

.el-main {
    --el-main-padding: 0;
    width: 100vw;
    height: calc(100vh - var(--el-header-height, 60px));
}
</style>
