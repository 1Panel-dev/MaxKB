<script setup lang="ts">
import { computed, type Component } from 'vue'
import type { ThemeInfo } from '@/api/admin/auth/types'
import AppLayout from '@/layout/AppLayout.vue'

defineOptions({ name: 'ThemePlatformPreview' })

interface PreviewMenuItem {
  icon?: Component
  iconName?: string
  label: string
  rightIcon?: Boolean
}

const props = defineProps<{
  data: Pick<ThemeInfo, 'showForum' | 'showProject' | 'showUserManual'>
}>()

const accountMenuItems: PreviewMenuItem[] = [
  { iconName: 'icon-key_outlined', label: '修改密码' },
  { iconName: 'icon_passkeys_outlined', label: 'API Key' },
  { iconName: 'icon_translate_outlined', label: '语言', rightIcon: true },
]

const platformMenuItems = computed<PreviewMenuItem[]>(() => [
  ...(props.data.showProject ? [{ iconName: 'icon_github_filled', label: '项目地址' }] : []),
  ...(props.data.showUserManual ? [{ iconName: 'icon_add-dictionary_outlined', label: '用户手册' }] : []),
  ...(props.data.showForum ? [{ iconName: 'icon-maybe_outlined', label: '论坛求助' }] : []),
  { iconName: 'icon_info_outlined', label: '关于' },
])
</script>

<template>
  <div class="platform-preview relative overflow-hidden rounded-lg">
    <div class="preview-scale" inert>
      <div class="platform-page relative h-full overflow-hidden">
        <AppLayout preview />

        <div class="absolute top-12 right-6 z-10 w-54 overflow-hidden rounded-md border bg-white shadow-md">
          <div class="w-52">
            <div class="flex items-start gap-3 p-3">
              <el-avatar :size="40" class="bg-primary-gradient!">
                <img src="@/assets/mk_icon_user_gradient.svg" alt="" style="width: 54%" />
              </el-avatar>
              <div class="min-w-0">
                <h6>飞小致</h6>
                <p class="truncate text-N600" title="feixaozhi">feixaozhi</p>
                <el-tag type="primary" class="mt-1">系统管理员</el-tag>
              </div>
            </div>
            <div class="border-t py-1">
              <template v-for="menuItem in accountMenuItems" :key="menuItem.label">
                <div class="flex-between h-8 px-3 w-full">
                  <span class="flex items-center gap-2">
                    <MkIcon :name="menuItem.iconName" class="text-N600!" />
                    <span>{{ menuItem.label }}</span>
                  </span>

                  <MkIcon v-if="menuItem.rightIcon" name="icon_right_outlined" class="text-N500!" />
                </div>
              </template>
            </div>
            <div class="border-t py-1">
              <div v-for="menuItem in platformMenuItems" :key="menuItem.label" class="flex h-8 items-center gap-2 px-3">
                <MkIcon :name="menuItem.iconName" class="text-N600!" />
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
