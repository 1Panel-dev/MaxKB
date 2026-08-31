<script setup lang="ts">
import { computed, type Component } from 'vue'
import { ArrowRight, InfoFilled, Key, Lock, Operation, QuestionFilled } from '@element-plus/icons-vue'
import type { ThemeInfo } from '@/api/admin/auth/types'
import AppLayout from '@/layout/AppLayout.vue'

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
  <div class="platform-preview relative overflow-hidden rounded-lg">
    <div class="preview-scale" inert>
      <div class="platform-page relative h-full overflow-hidden">
        <AppLayout preview />

        <div class="absolute top-12 right-6 z-10 w-54 overflow-hidden rounded-md border bg-white shadow-md">
          <div class="w-52">
            <div class="flex items-center gap-3 p-3">
              <el-avatar :size="40" class="bg-primary-gradient!">
                <img src="@/assets/mk_icon_user_gradient.svg" alt="" style="width: 54%" />
              </el-avatar>
              <div class="min-w-0">
                <h6>飞小致</h6>
                <p class="truncate text-N600" title="feixaozhi">feixaozhi</p>
                <el-tag type="primary">系统管理员</el-tag>
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
      </div>
    </div>
    <div class="preview-mask absolute inset-0" aria-hidden="true"></div>
  </div>
</template>

<style scoped lang="scss">
.platform-preview {
  height: 225px;
}

.preview-mask {
  z-index: 20;
}

.preview-scale {
  height: 904px;
  transform: scale(0.5);
  transform-origin: left top;
  width: 200%;
}
</style>
