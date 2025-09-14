<template>
  <CardBox :title="props.tool.name" :description="props.tool.desc" class="cursor">
    <template #icon>
      <el-avatar
        v-if="isAppIcon(props.tool?.icon)"
        shape="square"
        :size="32"
        style="background: none"
      >
        <img :src="resetUrl(props.tool?.icon)" alt="" />
      </el-avatar>
      <el-avatar
        v-else-if="props.tool?.name"
        :name="props.tool?.name"
        pinyinColor
        shape="square"
        :size="32"
      />
    </template>
    <template #title>
      <div>
        {{ props.tool?.name }}
        <el-tag v-if="props.tool?.version" class="ml-4" type="info" effect="plain">
          {{ props.tool?.version }}
        </el-tag>
      </div>
    </template>
    <template #subTitle>
      <el-text class="color-secondary" size="small">
        {{ getSubTitle(props.tool) }}
      </el-text>
    </template>
    <template #footer>
      <span class="card-footer-left color-secondary">
        {{ `${$t('common.author')}: MaxKB` }}
      </span>
      <div class="card-footer-operation" @click.stop>
        <el-button @click="emit('handleDetail')">
          {{ $t('common.detail') }}
        </el-button>
        <el-button type="primary" :loading="props.addLoading" @click="emit('handleAdd')">
          {{ $t('common.add') }}
        </el-button>
      </div>
    </template>
  </CardBox>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { isAppIcon, resetUrl } from '@/utils/common'

const props = defineProps<{
  tool: any
  getSubTitle: (v: any) => string
  addLoading: boolean
}>()

const emit = defineEmits<{
  (e: 'handleAdd'): void
  (e: 'handleDetail'): void
}>()
</script>

<style lang="scss" scoped>
.el-card {
  :deep(.card-footer) {
    & > div:first-of-type {
      flex: 1;
    }

    .card-footer-operation {
      display: none;
    }
  }

  &:hover {
    .card-footer-left {
      display: none;
    }

    .card-footer-operation {
      display: flex !important;

      .el-button {
        flex: 1;
      }
    }
  }
}
</style>
