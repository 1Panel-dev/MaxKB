<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useMessageInputStore } from '../index'

defineOptions({ name: 'MessageInputUrlUpload' })
const emit = defineEmits<{ localUpload: [] }>()
const { canUpload, uploadEnabled, urlUploading, urlUploadTypes, addUrls, disabled, streamLoading } = useMessageInputStore()
const visible = ref(false)
const addresses = ref('')
const selectedType = ref<(typeof urlUploadTypes.value)[number]['value']>('document_list')
const urls = computed(() =>
  addresses.value
    .split(/\r?\n/)
    .map((address) => address.trim())
    .filter(Boolean),
)
watch(
  urlUploadTypes,
  (types) => {
    if (!types.some((type) => type.value === selectedType.value) && types[0]) selectedType.value = types[0].value
  },
  { immediate: true },
)
watch([disabled, streamLoading], () => {
  if (disabled.value || streamLoading.value) visible.value = false
})
async function confirm() {
  if (urls.value.length && (await addUrls(urls.value, selectedType.value))) visible.value = false
}
function localUpload() {
  emit('localUpload')
  visible.value = false
}
</script>

<template>
  <el-popover
    v-model:visible="visible"
    trigger="click"
    placement="top-start"
    :width="320"
    :disabled="!canUpload && !visible"
    @after-leave="addresses = ''"
  >
    <template #reference>
      <!-- 打开附件上传 -->
      <el-button text :disabled="!canUpload">
        <MkIcon name="icon_attachment_outlined" :size="18" class="text-N900!" />
      </el-button>
    </template>
    <div class="p-4">
      <div class="flex-between mb-2">
        <span>URL 地址</span>
        <!-- 选择 URL 文件类型 -->
        <el-select v-model="selectedType" :disabled="urlUploading" :teleported="false" size="small" class="w-15!">
          <el-option v-for="type in urlUploadTypes" :key="type.value" :label="type.label" :value="type.value" />
        </el-select>
      </div>
      <el-input v-model="addresses" :disabled="urlUploading" type="textarea" :rows="5" placeholder="请输入URL地址，每行一个地址" />
      <div class="mt-4 text-right">
        <!-- 取消 URL 上传 -->
        <el-button plain @click="visible = false">取消</el-button>
        <!-- 确定 URL 上传 -->
        <el-button
          type="primary"
          :loading="urlUploading"
          :disabled="urlUploading || !canUpload || !urls.length || !urlUploadTypes.length"
          @click="confirm"
        >
          确定
        </el-button>
      </div>

      <el-divider v-if="uploadEnabled" class="my-4!" />
      <!-- 选择本地文件 -->
      <el-button v-if="uploadEnabled" type="primary" plain class="w-full" :disabled="urlUploading || !canUpload" @click="localUpload">
        本地上传
      </el-button>
    </div>
  </el-popover>
</template>
