<script setup lang="ts">
import { computed, type Component } from 'vue'
import { ArrowRight, ChatDotRound, InfoFilled, Key, Lock, Operation, QuestionFilled } from '@element-plus/icons-vue'
import type { ThemeInfo } from '@/api/admin/auth/types'
import avatarIcon from '@/assets/mk_icon_user_gradient.svg'
import LogoFull from '@/components/mk-logo/LogoFull.vue'

defineOptions({ name: 'ThemePlatformPreview' })

interface PreviewMenuItem {
  icon?: Component
  iconName?: string
  label: string
  trailingIcon?: Component
}

const props = defineProps<{
  data: Pick<ThemeInfo, 'showForum' | 'showProject' | 'showUserManual'>
}>()

const accountMenuItems: PreviewMenuItem[] = [
  { icon: Lock, label: '修改密码' },
  { icon: Key, label: 'API Key' },
  { icon: Operation, label: '语言', trailingIcon: ArrowRight },
]

const platformMenuItems = computed<PreviewMenuItem[]>(() => [
  ...(props.data.showProject ? [{ iconName: 'icon_launch_outlined', label: '项目地址' }] : []),
  ...(props.data.showUserManual ? [{ iconName: 'icon_book_outlined', label: '用户手册' }] : []),
  ...(props.data.showForum ? [{ icon: QuestionFilled, label: '论坛求助' }] : []),
  { icon: InfoFilled, label: '关于' },
])
</script>

<template>
  <div class="platform-preview relative overflow-hidden rounded-xl bg-N100">
    <header class="flex h-14 items-center px-6">
      <LogoFull class="h-8 shrink-0" />

      <div class="ml-auto flex items-center text-N600">
        <span class="flex items-center gap-1">
          <MkIcon :icon="ChatDotRound" />
          门户
        </span>
        <el-divider class="mx-4! h-4!" direction="vertical" />
        <span class="flex items-center gap-1">
          <MkIcon :icon="Operation" />
          系统管理
        </span>
        <span class="ml-5 flex size-9 items-center justify-center rounded-full bg-primary-gradient">
          <img :src="avatarIcon" alt="" style="width: 54%" />
        </span>
      </div>
    </header>

    <div class="absolute right-0 bottom-0 left-sidebar top-14 rounded-tl-xl bg-white"></div>

    <div class="absolute top-12 right-6 z-10 w-54 overflow-hidden rounded-md border bg-white shadow-md">
      <div class="flex gap-3 p-3">
        <span class="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary-gradient">
          <img :src="avatarIcon" alt="" style="width: 54%" />
        </span>
        <div class="min-w-0">
          <h6>飞小致</h6>
          <p class="truncate text-N600" title="feixaozhi">feixaozhi</p>
          <span class="rounded-sm bg-primary/10 px-1 text-sm text-primary">系统管理员</span>
        </div>
      </div>

      <div class="border-t py-1">
        <div v-for="menuItem in accountMenuItems" :key="menuItem.label" class="flex h-8 items-center gap-2 px-3">
          <MkIcon :icon="menuItem.icon" class="text-N600!" />
          <span>{{ menuItem.label }}</span>
          <MkIcon v-if="menuItem.trailingIcon" :icon="menuItem.trailingIcon" class="ml-auto text-N500!" />
        </div>
      </div>

      <div class="border-t py-1">
        <div v-for="menuItem in platformMenuItems" :key="menuItem.label" class="flex h-8 items-center gap-2 px-3">
          <MkIcon :icon="menuItem.icon" :name="menuItem.iconName" class="text-N600!" />
          <span>{{ menuItem.label }}</span>
        </div>
      </div>

      <div class="border-t py-1">
        <div class="flex h-8 items-center gap-2 px-3">
          <MkIcon name="icon_logout_outlined" class="text-N600!" />
          <span>退出登录</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.platform-preview {
  height: 452px;
}
</style>
