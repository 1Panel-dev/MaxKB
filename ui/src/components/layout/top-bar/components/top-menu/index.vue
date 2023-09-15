<template >
    <div class="top-menu-container">
        <MenuItem :menu="menu" v-for="(menu, index) in topMenuList" :key="index">
        </MenuItem>
    </div>
</template>
<script setup lang="ts">
import { computed } from "vue";
import { getChildRouteListByPathAndName } from "@/router/index"
import MenuItem from "@/components/layout/top-bar/components/top-menu/MenuItem.vue"
const topMenuList = computed(() => {
    return getChildRouteListByPathAndName("/", "home")
})

</script>
<style lang="scss" scope>
.top-menu-container {
    display: flex;
    align-items: center;
    height: 100%;
}
</style>