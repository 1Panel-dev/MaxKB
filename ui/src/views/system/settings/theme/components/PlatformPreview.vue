<script setup lang="ts">
import { computed, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ThemeInfo } from '@/api/admin/auth/types'
import type { Component } from 'vue'
import AppLayout from '@/layout/AppLayout.vue'

defineOptions({ name: 'ThemePlatformPreview' })

interface PreviewMenuItem {
  icon?: Component
  iconName?: string
  label: string
  rightIcon?: Boolean
}

const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{
  data: Pick<ThemeInfo, 'showForum' | 'showProject' | 'showUserManual'>
}>()

const accountMenuItems: PreviewMenuItem[] = reactive([
  { iconName: 'icon-key_outlined', label: computed(() => t('auth.changePassword.title')) },
  { iconName: 'icon_passkeys_outlined', label: 'API Key' },
  { iconName: 'icon_internet_outlined', label: computed(() => t('common.labels.language')), rightIcon: true },
])

const platformMenuItems = computed<PreviewMenuItem[]>(() => [
  ...(props.data.showProject ? [{ iconName: 'icon_github_filled', label: t('layout.project') }] : []),
  ...(props.data.showUserManual ? [{ iconName: 'icon_add-dictionary_outlined', label: t('layout.userManual') }] : []),
  ...(props.data.showForum ? [{ iconName: 'icon-maybe_outlined', label: t('layout.forum') }] : []),
  { iconName: 'icon_info_outlined', label: t('layout.about.title') },
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
                <el-tag size="small" type="primary" class="mt-1">系统管理员</el-tag>
              </div>
            </div>
            <div class="border-t py-1">
              <template v-for="menuItem in accountMenuItems" :key="menuItem.label">
                <div class="flex-between h-8 px-3 w-full">
                  <span class="flex-align-center gap-2">
                    <MkIcon :name="menuItem.iconName" class="text-N600!" />
                    <span>{{ menuItem.label }}</span>
                  </span>

                  <MkIcon v-if="menuItem.rightIcon" name="icon_right_outlined" class="text-N500!" />
                </div>
              </template>
            </div>
            <div class="border-t py-1">
              <div v-for="menuItem in platformMenuItems" :key="menuItem.label" class="flex-align-center h-8 gap-2 px-3">
                <MkIcon :name="menuItem.iconName" class="text-N600!" />
                <span>{{ menuItem.label }}</span>
              </div>
            </div>
            <div class="border-t py-1">
              <div class="flex-align-center h-8 gap-2 px-3">
                <MkIcon name="icon_logout_outlined" class="text-N600!" />
                <span>{{ t('auth.logout.label') }}</span>
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
