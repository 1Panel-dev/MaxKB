<template>
  <div>
    <el-tooltip effect="dark" content="重新生成" placement="top">
      <el-button text @click.stop>
        <AppIcon iconName="VideoPlay"></AppIcon>
      </el-button>
    </el-tooltip>
    <el-divider direction="vertical" />
    <el-tooltip effect="dark" content="复制" placement="top">
      <el-button text @click="copyClick(item?.answer_text)">
        <AppIcon iconName="app-copy"></AppIcon>
      </el-button>
    </el-tooltip>
    <el-divider direction="vertical" />
    <el-tooltip effect="dark" content="赞同" placement="top">
      <el-button text>
        <AppIcon iconName="app-like"></AppIcon>
      </el-button>
    </el-tooltip>
    <el-tooltip effect="dark" content="取消赞同" placement="top">
      <el-button text>
        <AppIcon iconName="app-like-color"></AppIcon>
      </el-button>
    </el-tooltip>
    <el-divider direction="vertical" />
    <el-tooltip effect="dark" content="反对" placement="top">
      <el-button text>
        <AppIcon iconName="app-oppose"></AppIcon>
      </el-button>
    </el-tooltip>
    <el-tooltip effect="dark" content="取消反对" placement="top">
      <el-button text>
        <AppIcon iconName="app-oppose-color"></AppIcon>
      </el-button>
    </el-tooltip>
  </div>
</template>
<script setup lang="ts">
import { copyClick } from '@/utils/clipboard'

defineProps({
  data: {
    type: Object,
    default: () => {}
  }
})

const emit = defineEmits(['update:data'])

</script>
<style lang="scss" scoped></style>
