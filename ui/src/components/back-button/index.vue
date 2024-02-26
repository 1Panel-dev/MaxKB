<template>
  <el-button class="back-button cursor mr-4" text @click="jump">
    <el-icon :size="20">
      <Back />
    </el-icon>
  </el-button>
</template>

<script setup lang="ts">
import { useRouter, type RouteLocationRaw } from 'vue-router'
defineOptions({ name: 'BackButton' })
const router = useRouter()
const props = defineProps({
  to: String
})

const emit = defineEmits(['click'])
/* 上一层路由 */
const back: any = router.options.history.state.back
function jump() {
  if (props.to === '-1') {
    back ? router.push(back) : router.go(-1)
  } else if (props.to) {
    router.push(props.to as RouteLocationRaw)
  } else {
    emit('click')
  }
}
</script>

<style lang="scss"></style>
