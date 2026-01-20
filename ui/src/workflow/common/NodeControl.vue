<template>
  <el-card shadow="always" style="--el-card-padding: 8px 12px; --el-card-border-radius: 8px">
    <el-button
      @click="changeCursor(true)"
      style="border: none; padding: 4px; height: 24px"
      :class="{ 'is-drag-active': isDrag }"
    >
      <el-icon :size="16"><Position /></el-icon>
    </el-button>
    <el-button
      @click="changeCursor(false)"
      style="border: none; padding: 4px; height: 24px; margin-left: 8px"
      :class="{ 'is-drag-active': !isDrag }"
    >
      <AppIcon iconName="app-raisehand" :size="16"></AppIcon>
    </el-button>
    <el-divider direction="vertical" />
    <el-button link @click="zoomOut" style="border: none">
      <el-tooltip
        effect="dark"
        :content="$t('workflow.control.zoomOut')"
        placement="top"
      >
        <el-icon :size="16" :title="$t('workflow.control.zoomOut')"
          ><ZoomOut
        /></el-icon>
      </el-tooltip>
    </el-button>
    <el-button link @click="zoomIn" style="border: none">
      <el-tooltip
        effect="dark"
        :content="$t('workflow.control.zoomIn')"
        placement="top"
      >
        <el-icon :size="16" :title="$t('workflow.control.zoomIn')"
          ><ZoomIn
        /></el-icon>
      </el-tooltip>
    </el-button>
    <el-button link @click="fitView" style="border: none">
      <el-tooltip
        effect="dark"
        :content="$t('workflow.control.fitView')"
        placement="top"
      >
        <AppIcon
          iconName="app-fitview"
          :title="$t('workflow.control.fitView')"
        ></AppIcon>
      </el-tooltip>
    </el-button>
    <el-divider direction="vertical" />
    <el-button link @click="retract" style="border: none">
      <el-tooltip
        effect="dark"
        :content="$t('workflow.control.retract')"
        placement="top"
      >
        <AppIcon
          style="font-size: 16px"
          iconName="app-retract"
          :title="$t('workflow.control.retract')"
        ></AppIcon>
      </el-tooltip>
    </el-button>
    <el-button link @click="extend" style="border: none">
      <el-tooltip
        effect="dark"
        :content="$t('workflow.control.extend')"
        placement="top"
      >
        <AppIcon
          style="font-size: 16px"
          iconName="app-extend"
          :title="$t('workflow.control.extend')"
        ></AppIcon>
      </el-tooltip>
    </el-button>
    <el-button link @click="layout" style="border: none">
      <el-tooltip
        effect="dark"
        :content="$t('workflow.control.beautify')"
        placement="top"
      >
        <AppIcon
          style="font-size: 16px"
          iconName="app-beautify"
          :title="$t('workflow.control.beautify')"
        ></AppIcon>
      </el-tooltip>
    </el-button>
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const props = defineProps({
  lf: Object || String || null,
})

const isDrag = ref(false)

function zoomIn() {
  props.lf?.zoom(true, [0, 0])
}
function zoomOut() {
  props.lf?.zoom(false, [0, 0])
}
function fitView() {
  props.lf?.resetZoom()
  props.lf?.resetTranslate()
  props.lf?.fitView()
}
const layout = () => {
  props.lf?.extension.dagre.layout()
  props.lf?.graphModel.nodes.forEach((node: any) => {
    if (node.type === 'loop-body-node') {
      node?.loopLayout?.()
    }
  })
}
const retract = () => {
  props.lf?.graphModel.nodes.forEach((element: any) => {
    element.properties.showNode = false
  })
}
const extend = () => {
  props.lf?.graphModel.nodes.forEach((element: any) => {
    element.properties.showNode = true
  })
}
const changeCursor = (bool: boolean) => {
  const element: HTMLElement = document.querySelector('.lf-drag-able') as HTMLElement
  isDrag.value = bool
  if (bool) {
    element.style.cursor = 'default'
    props.lf?.openSelectionSelect()
    props.lf?.extension.selectionSelect.setSelectionSense(true, false)
  } else {
    element.style.cursor = 'pointer'
    props.lf?.closeSelectionSelect()
  }
}
</script>
<style scoped lang="scss">
.is-drag-active {
  background-color: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}
</style>
