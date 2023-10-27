<template>
  <el-icon class="back-button cursor mr-10 vertical-middle" @click="jump">
    <Back />
  </el-icon>
</template>

<script setup lang="ts">
import { useRouter, type RouteLocationRaw } from 'vue-router'
defineOptions({ name: 'BackButton' })
const router = useRouter()
const props = defineProps({
  to: String
})

const back: any = router.options.history.state.back // 上一层路由
function jump() {
  if (props.to === '-1') {
    back ? router.push(back) : router.go(-1)
  } else {
    router.push(props.to as RouteLocationRaw)
  }
}
</script>

<style lang="scss"></style>
