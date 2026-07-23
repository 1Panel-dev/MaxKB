<script setup lang="ts">
import { ref } from 'vue'
import { Setting } from '@element-plus/icons-vue'

defineOptions({ name: 'AvatarDropdown' })

type Language = 'en' | 'zh-CN' | 'zh-TW'

const currentLanguage = ref<Language>('zh-CN')
const languages: Array<{ label: string; value: Language }> = [
  { label: 'English', value: 'en' },
  { label: '简体中文', value: 'zh-CN' },
  { label: '繁體中文', value: 'zh-TW' },
]

function handleLogout() {}
</script>

<template>
  <MkDropdown ref="dropdownRef" trigger="click" placement="bottom-end">
    <el-avatar :size="32" class="cursor-pointer bg-primary-gradient!">
      <img src="@/assets/mk-icon-user-gradient.svg" alt="" class="w-[54%]!" />
    </el-avatar>

    <template #dropdown>
      <div class="w-52">
        <div class="flex items-center gap-2 p-3">
          <el-avatar :size="40" class="bg-primary-gradient!">
            <img src="@/assets/mk-icon-user-gradient.svg" alt="" class="w-[54%]!" />
          </el-avatar>
          <div>
            <div class="font-medium text-lg">{{ '飞小致' }}</div>
            <div class="text-N600">{{ 'feixaozhi' }}</div>
          </div>
        </div>
        <el-divider />
        <MkDropdownMenu>
          <MkDropdownItem :icon="Setting">修改密码</MkDropdownItem>
          <MkDropdownItem @click.stop class="p-0!">
            <MkDropdown class="w-full" trigger="hover" placement="left-start" :persistent="true">
              <div class="flex w-full items-center justify-between gap-2 p-2">
                <div class="flex items-center gap-2">
                  <MkIcon :icon="Setting" />
                  <span>语言</span>
                </div>

                <MkIcon name="icon_right_outlined" />
              </div>
              <template #dropdown>
                <MkDropdownMenu class="w-52">
                  <MkDropdownItem
                    v-for="language in languages"
                    :key="language.value"
                    selectable
                    :selected="currentLanguage === language.value"
                    @click="currentLanguage = language.value"
                  >
                    {{ language.label }}
                  </MkDropdownItem>
                </MkDropdownMenu>
              </template>
            </MkDropdown>
          </MkDropdownItem>
        </MkDropdownMenu>
        <el-divider />
        <MkDropdownMenu>
          <MkDropdownItem :icon="Setting" @click="handleLogout">退出登录</MkDropdownItem>
        </MkDropdownMenu>
      </div>
    </template>
  </MkDropdown>
</template>
