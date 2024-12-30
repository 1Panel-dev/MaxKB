<template>
  <el-card shadow="always" style="--el-card-padding: 8px 12px; --el-card-border-radius: 8px">
    <el-button link @click="zoomOut">
      <el-tooltip class="box-item" effect="dark" content="缩小" placement="top">
        <el-icon :size="16" title="缩小"><ZoomOut /></el-icon>
      </el-tooltip>
    </el-button>
    <el-button link @click="zoomIn">
      <el-tooltip class="box-item" effect="dark" content="放大" placement="top">
        <el-icon :size="16" title="放大"><ZoomIn /></el-icon>
      </el-tooltip>
    </el-button>
    <el-button link @click="fitView">
      <el-tooltip class="box-item" effect="dark" content="适应" placement="top">
        <AppIcon iconName="app-fitview" title="适应"></AppIcon>
      </el-tooltip>
    </el-button>
    <el-divider direction="vertical" />
    <el-button link @click="retract">
      <el-tooltip class="box-item" effect="dark" content="收起全部节点" placement="top">
        <AppIcon style="font-size: 16px" iconName="app-retract" title="收起全部节点"></AppIcon>
      </el-tooltip>
    </el-button>
    <el-button link @click="extend">
      <el-tooltip class="box-item" effect="dark" content="展开全部节点" placement="top">
        <AppIcon style="font-size: 16px" iconName="app-extend" title="展开全部节点"></AppIcon>
      </el-tooltip>
    </el-button>
    <el-button link @click="layout">
      <el-tooltip class="box-item" effect="dark" content="一键美化" placement="top">
        <AppIcon style="font-size: 16px" iconName="app-beautify" title="一键美化"></AppIcon>
      </el-tooltip>
    </el-button>
  </el-card>
</template>

<script setup lang="ts">
const props = defineProps({
  lf: Object || String || null
})

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
</script>
<style scoped></style>
