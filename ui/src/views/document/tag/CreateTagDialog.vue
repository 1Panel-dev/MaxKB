<template>
  <el-dialog
    v-model="dialogVisible"
    :title="currentTagKey ? $t('views.document.tag.addValue') : $t('views.document.tag.create')"
    :before-close="close"
    append-to-body
  >
    <el-form
      ref="FormRef"
      :model="{ tags }"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-scrollbar>
        <el-row :gutter="8" style="margin-right: 10px" class="tag-list-max-list">
          <template v-for="(tag, index) in tags" :key="tag">
            <el-col :span="12">
              <el-form-item
                :label="index === 0 ? $t('views.document.tag.key') : ''"
                :prop="`tags.${index}.key`"
                :rules="{
                  required: true,
                  message: $t('views.document.tag.requiredMessage1'),
                  trigger: 'blur',
                }"
              >
                <el-input
                  v-model="tag.key"
                  :disabled="currentTagKey? true : false"
                  class="w-full"
                  :placeholder="$t('views.document.tag.requiredMessage1')"
                ></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="11">
              <el-form-item
                :label="index === 0 ? $t('views.document.tag.value') : ''"
                :prop="`tags.${index}.value`"
                :rules="{
                  required: true,
                  message: $t('views.document.tag.requiredMessage2'),
                  trigger: 'blur',
                }"
                class="w-full"
              >
                <el-input
                  v-model="tag.value"
                  :placeholder="$t('views.document.tag.requiredMessage2')"
                ></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="1">
              <el-button
                :disabled="tags.length === 1"
                link
                type="info"
                @click="deleteTag(index)"
                :style="{ marginTop: index === 0 ? '35px' : '5px' }"
              >
                <AppIcon iconName="app-delete"></AppIcon>
              </el-button>
            </el-col>
          </template>
        </el-row>
      </el-scrollbar>
    </el-form>

    <el-button link type="primary" @click="add">
      <AppIcon iconName="app-add-outlined" class="mr-4" />
      {{ $t('common.add') }}
    </el-button>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="close">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submit">{{ $t('common.confirm') }}</el-button>
      </div>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api.ts'
import { cloneDeep } from 'lodash'

const route = useRoute()
const {
  params: { id }, // id为knowledgeID
} = route as any
const emit = defineEmits(['refresh'])

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const FormRef = ref()
const loading = ref(false)
const dialogVisible = ref<boolean>(false)
const currentTagKey = ref(null)
const tags = ref<Array<any>>([])

const add = () => {
  if (currentTagKey.value) {
    tags.value.push({ key: currentTagKey.value })
  } else {
    tags.value.push({})
  }
}
const deleteTag = (index: number) => {
  tags.value.splice(index, 1)
}

const submit = () => {
  FormRef.value.validate((valid: boolean) => {
    if (!valid) return
    loadSharedApi({ type: 'knowledge', systemType: apiType.value })
      .postTags(id, tags.value, loading)
      .then((res: any) => {
        close()
        emit('refresh', currentTagKey.value)
      })
  })
}

const open = (row?: any) => {
  const currentRow = cloneDeep(row)
  dialogVisible.value = true
  currentTagKey.value = currentRow ? currentRow.key : null
  tags.value = currentRow ? [{ ...{ key: currentRow.key } }] : [{}]
}

const close = () => {
  dialogVisible.value = false
}

defineExpose({ open, close })
</script>
<style lang="scss" scoped>
.tag-list-max-list {
  max-height: calc(100vh - 260px);
}
</style>
