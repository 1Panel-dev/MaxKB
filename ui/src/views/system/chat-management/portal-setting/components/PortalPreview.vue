<script setup lang="ts">
import LogoIcon from '@/components/mk-logo/LogoIcon.vue'

defineProps<{ name: string; logo: string | null }>()
</script>

<template>
  <section class="flex min-h-140 min-w-0 flex-1 overflow-hidden rounded-xl border">
    <div class="flex-column w-chat-sidebar shrink-0 border-r bg-N100 p-4">
      <div class="flex-align-center mb-5 gap-2">
        <img v-if="logo" :src="logo" alt="门户 Logo" :height="24" class="shrink-0 object-contain" />
        <LogoIcon v-else :height="24" class="shrink-0" />
        <h4 class="min-w-0 flex-1 truncate" :title="name">{{ name }}</h4>
        <MkIcon name="icon_sidebar_outlined" class="shrink-0" />
      </div>
      <div class="flex-align-center gap-2 mk-white-card-sm text-primary">
        <MkIcon name="icon_card_filled" :size="18" />
        <span class="font-medium">全部智能体</span>
      </div>
      <div class="flex-align-center gap-2 px-2 py-3">
        <MkIcon name="icon_new-chat_outlined" :size="18" />
        <span>新建对话</span>
      </div>
      <div class="flex-align-center mt-auto gap-2 px-2">
        <el-avatar :size="32" class="shrink-0 bg-primary-gradient!">
          <img src="@/assets/mk_icon_user_gradient.svg" alt="" style="width: 54%" />
        </el-avatar>
        <span>用户名</span>
      </div>
    </div>
    <div class="min-w-0 flex-1 p-6">
      <div class="flex-between">
        <h4 class="shrink-0">全部智能体</h4>
        <MkSearchInput readonly class="w-60! max-w-full" />
      </div>
    </div>
  </section>
</template>
