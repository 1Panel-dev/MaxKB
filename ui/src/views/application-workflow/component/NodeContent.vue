<template>
  <div class="w-full">
    <div v-if="data" class="flex align-center">
      <AppIcon iconName="app-folder" style="font-size: 20px"></AppIcon>
      <span class="ml-8 ellipsis color-text-primary lighter" style="max-width: 110px" :title="data.name">
        {{ data.name }}
      </span>
    </div>

    <transition name="el-fade-in-linear">
      <div v-if="props.list?.length || (props.node?.expanded && toolList.length)"
        class="list border-r-4 layout-bg flex-wrap" @click.stop>
        <el-popover v-for="item in toolList" :key="item.id" placement="right" :width="280">
          <template #reference>
            <div class="list-item flex align-center border border-r-6 p-8-12 cursor" style="width: 39%"
              @click.stop="emit('clickNodes', item)" @mousedown.stop="emit('onmousedown', item)">
              <LogoIcon v-if="item.resource_type === 'application'" height="32px" />
              <el-avatar v-else-if="isAppIcon(item?.icon)" shape="square" :size="32" style="background: none">
                <img :src="resetUrl(item?.icon)" alt="" />
              </el-avatar>
              <el-avatar v-else class="avatar-green" shape="square" :size="32">
                <img src="@/assets/workflow/icon_tool.svg" style="width: 58%" alt="" />
              </el-avatar>
              <span class="ml-8 ellipsis">{{ item.name }}</span>
            </div>
          </template>

          <template #default>
            <div class="flex-between mb-8">
              <div class="flex align-center">
                <LogoIcon v-if="item.resource_type === 'application'" height="32px" />
                <el-avatar v-else-if="isAppIcon(item?.icon)" shape="square" :size="32" style="background: none">
                  <img :src="resetUrl(item?.icon)" alt="" />
                </el-avatar>
                <el-avatar v-else class="avatar-green" shape="square" :size="32">
                  <img src="@/assets/workflow/icon_tool.svg" style="width: 58%" alt="" />
                </el-avatar>
                <span class="font-medium ml-8">{{ item.name }}</span>
              </div>
              <div v-if="item.type" class="status-tag" style="margin-left: auto">
                <el-tag type="warning" v-if="isWorkFlow(item.type)" style="height: 22px">
                  {{ $t('views.application.workflow') }}
                </el-tag>
                <el-tag class="blue-tag" v-else style="height: 22px">
                  {{ $t('views.application.simple') }}
                </el-tag>
              </div>
            </div>
            <el-text type="info" size="small">{{ item.desc }}</el-text>
          </template>
        </el-popover>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {isAppIcon, resetUrl} from '@/utils/common'
import { isWorkFlow } from '@/utils/application'

const props = defineProps<{
  data?: any
  node?: any
  list?: any[]
}>()

const emit = defineEmits<{
  (e: 'clickNodes', item: any): void;
  (e: 'onmousedown', item: any): void;
}>();

const toolList = computed(() => props.list ?? props.data?.cardList ?? [])
</script>

<style lang="scss" scoped>
.list {
  cursor: default;
  padding: 12px;
  gap: 12px;
  margin-top: 12px;
  transform: translate(-16px, 0);

  .list-item {
    background-color: #ffffff;

    &:hover {
      border-color: var(--el-color-primary);
    }
  }
}
</style>
