<template>
  <el-card shadow="always" style="--el-card-padding: 8px 12px; --el-card-border-radius: 8px">
    <el-button link @click="zoomOut">
      <el-tooltip
        effect="dark"
        :content="$t('views.applicationWorkflow.control.zoomOut')"
        placement="top"
      >
        <el-icon :size="16" :title="$t('views.applicationWorkflow.control.zoomOut')"
          ><ZoomOut
        /></el-icon>
      </el-tooltip>
    </el-button>
    <el-button link @click="zoomIn">
      <el-tooltip
        effect="dark"
        :content="$t('views.applicationWorkflow.control.zoomIn')"
        placement="top"
      >
        <el-icon :size="16" :title="$t('views.applicationWorkflow.control.zoomIn')"
          ><ZoomIn
        /></el-icon>
      </el-tooltip>
    </el-button>
    <el-button link @click="fitView">
      <el-tooltip
        effect="dark"
        :content="$t('views.applicationWorkflow.control.fitView')"
        placement="top"
      >
        <AppIcon
          iconName="app-fitview"
          :title="$t('views.applicationWorkflow.control.fitView')"
        ></AppIcon>
      </el-tooltip>
    </el-button>
    <el-divider direction="vertical" />
    <el-button link @click="retract">
      <el-tooltip
        effect="dark"
        :content="$t('views.applicationWorkflow.control.retract')"
        placement="top"
      >
        <AppIcon
          style="font-size: 16px"
          iconName="app-retract"
          :title="$t('views.applicationWorkflow.control.retract')"
        ></AppIcon>
      </el-tooltip>
    </el-button>
    <el-button link @click="extend">
      <el-tooltip
        effect="dark"
        :content="$t('views.applicationWorkflow.control.extend')"
        placement="top"
      >
        <AppIcon
          style="font-size: 16px"
          iconName="app-extend"
          :title="$t('views.applicationWorkflow.control.extend')"
        ></AppIcon>
      </el-tooltip>
    </el-button>
    <el-button link @click="layout">
      <el-tooltip
        effect="dark"
        :content="$t('views.applicationWorkflow.control.beautify')"
        placement="top"
      >
        <AppIcon
          style="font-size: 16px"
          iconName="app-beautify"
          :title="$t('views.applicationWorkflow.control.beautify')"
        ></AppIcon>
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
