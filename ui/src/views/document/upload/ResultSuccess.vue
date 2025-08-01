<template>
  <el-scrollbar>
    <el-result icon="color-success" :title="`🎉 ${$t('views.knowledge.ResultSuccess.title')} 🎉`">
      <template #sub-title>
        <div class="mt-8">
          <span class="bold">{{ data?.document_list.length || 0 }}</span>
          <el-text type="info" class="ml-4">{{ $t('common.fileUpload.document') }}</el-text>
          <el-divider direction="vertical" />
          <span class="bold">{{ paragraph_count || 0 }}</span>
          <el-text type="info" class="ml-4">{{
            $t('views.knowledge.ResultSuccess.paragraph')
          }}</el-text>
          <el-divider direction="vertical" />
          <span class="bold">{{ numberFormat(char_length) || 0 }}</span>
          <el-text type="info" class="ml-4">{{ $t('common.character') }} </el-text>
        </div>
      </template>
      <template #extra>
        <el-button
          v-if="apiType === 'workspace'"
          @click="
            router.push({
              path: `/knowledge`,
            })
          "
          >{{ $t('views.knowledge.ResultSuccess.buttons.toknowledge') }}</el-button
        >
        <el-button
          v-else
          @click="
            router.push({
              path: `/system/${folderId}/knowledge`,
            })
          "
          >{{ $t('views.knowledge.ResultSuccess.buttons.toknowledge') }}</el-button
        >
        <el-button
          type="primary"
          @click="
            router.push({
              path: `/knowledge/${data?.id}/${folderId}/document`,
            })
          "
          >{{ $t('views.knowledge.ResultSuccess.buttons.toDocument') }}</el-button
        >
      </template>
    </el-result>
    <div class="result-success">
      <p class="bolder">{{ $t('views.knowledge.ResultSuccess.documentList') }}</p>
      <el-card
        shadow="never"
        class="file-List-card mt-8"
        v-for="(item, index) in data?.document_list"
        :key="index"
      >
        <div class="flex-between">
          <div class="flex">
            <img :src="getImgUrl(item && item?.name)" alt="" width="40" />
            <div class="ml-8">
              <p>{{ item && item?.name }}</p>
              <el-text type="info" size="small">{{ filesize(item && item?.char_length) }}</el-text>
            </div>
          </div>
          <div>
            <el-text type="info" class="mr-16"
              >{{ item && item?.paragraph_count }}
              {{ $t('views.knowledge.ResultSuccess.paragraph_count') }}</el-text
            >
            <el-text v-if="item.status === '1'">
              <el-icon class="color-success"><SuccessFilled /></el-icon>
            </el-text>
            <el-text v-else-if="item.status === '2'">
              <el-icon class="color-danger"><CircleCloseFilled /></el-icon>
            </el-text>
            <el-text v-else-if="item.status === '0'">
              <el-icon class="is-loading primary"><Loading /></el-icon>
              {{ $t('views.knowledge.ResultSuccess.loading') }}...
            </el-text>
          </div>
        </div>
      </el-card>
    </div>
  </el-scrollbar>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getImgUrl, filesize, numberFormat } from '@/utils/common'

const props = defineProps({
  data: {
    type: Object,
    default: () => {},
  },
})
const router = useRouter()
const route = useRoute()
const {
  params: { id, folderId }, // id为knowledgeID
} = route as any

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const paragraph_count = computed(() =>
  props.data?.document_list.reduce((sum: number, obj: any) => (sum += obj.paragraph_count), 0),
)

const char_length = computed(
  () =>
    props.data?.document_list.reduce((sum: number, obj: any) => (sum += obj.char_length), 0) || 0,
)
</script>
<style scoped lang="scss">
.result-success {
  width: 70%;
  margin: 0 auto;
  margin-bottom: 30px;
}
</style>
