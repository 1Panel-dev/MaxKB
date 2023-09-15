<template>
    <div class="menu-item-container" :class="isActive ? 'active' : ''" @click="router.push({ name: menu.name })">
        <div class="icon">
            <AppIcon :iconName="menu.meta ? menu.meta.icon as string : '404'"></AppIcon>
        </div>
        <div class="title">{{ menu.meta?.title }} </div>
    </div>
</template>
<script setup lang="ts">
import { useRouter, useRoute, type RouteRecordRaw } from 'vue-router'
import { computed } from "vue";
import AppIcon from "@/components/icons/AppIcon.vue"
const router = useRouter();
const route = useRoute();
const props = defineProps<{
    menu: RouteRecordRaw
}>()

const isActive = computed(() => {
    return route.name == props.menu.name && route.path == props.menu.path
})

</script>
<style lang="scss" scoped>
.menu-item-container {
    padding: 0 20px;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    height: 100%;

}

.active {
    background-color: var(--app-base-text-hover-bg-color);
    border-bottom: 3px solid var(--app-base-text-hover-color);
    height: calc(100% - 3px);
}
</style>