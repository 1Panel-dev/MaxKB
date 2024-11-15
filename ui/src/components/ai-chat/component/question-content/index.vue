<template>
  <!-- 问题内容 -->
  <div class="item-content mb-16 lighter">
    <div class="avatar">
      <el-image
        v-if="application.user_avatar"
        :src="application.user_avatar"
        alt=""
        fit="cover"
        style="width: 32px; height: 32px; display: block"
      />
      <AppAvatar v-else>
        <img src="@/assets/user-icon.svg" style="width: 50%" alt="" />
      </AppAvatar>
    </div>
    <div class="content">
      <div class="text break-all pre-wrap">
        {{ chatRecord.problem_text }}
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { type chatType } from '@/api/type/application'
import { onMounted } from 'vue'
const props = defineProps<{
  application: any
  chatRecord: chatType
}>()

onMounted(() => {
  if (props.chatRecord.execution_details?.length > 0) {
    props.chatRecord.execution_details[0].image_list?.forEach((image: any) => {
      console.log('image', image.name, image.url)
    })
  }
})
</script>
<style lang="scss" scoped>
</style>
