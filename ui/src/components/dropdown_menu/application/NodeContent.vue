<template>
  <el-input
    v-model.trim="filterText"
    :placeholder="$t('common.search')"
    prefix-icon="Search"
    clearable
    style="padding: 12px 12px 0 12px"
  />
  <div class="list flex-wrap">
    <template v-if="filterList.length">
      <el-popover
        v-for="item in filterList"
        :key="item.id"
        placement="right"
        :width="280"
        :show-after="500"
      >
        <template #reference>
          <div
            class="list-item flex align-center border border-r-6 p-8-12 cursor"
            style="width: calc(50% - 6px)"
            @click.stop="emit('clickNodes', item)"
            @mousedown.stop="emit('onmousedown', item)"
          >
            <el-avatar
              v-if="isAppIcon(item?.icon)"
              shape="square"
              :size="20"
              style="background: none"
            >
              <img :src="resetUrl(item?.icon, resetUrl('./favicon.ico'))" alt="" />
            </el-avatar>
            <el-avatar v-else class="avatar-green" shape="square" :size="20">
              <img src="@/assets/workflow/icon_tool.svg" style="width: 58%" alt="" />
            </el-avatar>
            <span class="ml-8 ellipsis" :title="item.name">{{ item.name }}</span>
          </div>
        </template>

        <template #default>
          <div class="flex-between">
            <div class="flex align-center">
              <el-avatar
                v-if="isAppIcon(item?.icon)"
                shape="square"
                :size="20"
                style="background: none"
              >
                <img :src="resetUrl(item?.icon, resetUrl('./favicon.ico'))" alt="" />
              </el-avatar>
              <el-avatar v-else class="avatar-green" shape="square" :size="20">
                <img src="@/assets/workflow/icon_tool.svg" style="width: 58%" alt="" />
              </el-avatar>
              <span class="font-medium ml-8 break-all" :title="item.name">{{ item.name }}</span>
            </div>
            <div v-if="item.type" class="status-tag" style="margin-left: auto">
              <el-tag class="warning-tag" v-if="isWorkFlow(item.type)">
                {{ $t('views.application.workflow') }}
              </el-tag>
              <el-tag class="blue-tag" v-else>
                {{ $t('views.application.simple') }}
              </el-tag>
            </div>
          </div>
          <el-text type="info" size="small" class="mt-4">{{ item.desc }}</el-text>
        </template>
      </el-popover>
    </template>
    <el-empty v-else :description="$t('common.noData')" />
  </div>
</template>

<script setup lang="ts">
import { watch, ref } from 'vue'
import { isAppIcon, resetUrl } from '@/utils/common'
import { isWorkFlow } from '@/utils/application'

const props = defineProps<{
  list: any[]
}>()

const emit = defineEmits<{
  (e: 'clickNodes', item: any): void
  (e: 'onmousedown', item: any): void
}>()

const filterText = ref('')
const filterList = ref<any[]>([])

function filter(list: any[], filterText: string) {
  if (!filterText.length) {
    return list
  }
  return list.filter((v: any) => v.name.toLowerCase().includes(filterText.toLowerCase()))
}

watch([() => filterText.value, () => props.list], () => {
  filterList.value = filter(props.list, filterText.value)
})
</script>

<style lang="scss" scoped>
.list {
  cursor: default;
  padding: 12px;
  gap: 12px;
  box-sizing: border-box;

  .list-item {
    background-color: #ffffff;
    box-sizing: border-box;

    &:hover {
      border-color: var(--el-color-primary);
    }
  }

  .el-empty {
    margin: 0 auto;
  }
}
</style>
