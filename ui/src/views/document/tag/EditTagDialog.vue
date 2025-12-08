<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEditKey ? $t('views.document.tag.edit') : $t('views.document.tag.editValue')"
    :before-close="close"
    :width="isEditKey ? '500px' : '50%'"
  >
    <el-form
      ref="FormRef"
      :model="form"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item
        :label="$t('views.document.tag.key')"
        v-if="isEditKey"
        :rules="{
          required: true,
          message: $t('views.document.tag.requiredMessage1'),
          trigger: 'blur',
        }"
        prop="key"
      >
        <el-input v-model="form.key"></el-input>
      </el-form-item>
      <el-row :gutter="8" align="bottom" v-else>
        <el-col :span="12">
          <el-form-item
            :label="$t('views.document.tag.key')"
            prop="key"
            :rules="{
              required: true,
              message: $t('views.document.tag.requiredMessage1'),
              trigger: 'blur',
            }"
          >
            <el-input v-model="form.key" :disabled="true"></el-input>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item
            :label="$t('views.document.tag.value')"
            prop="value"
            :rules="{
              required: true,
              message: $t('views.document.tag.requiredMessage2'),
              trigger: 'blur',
            }"
          >
            <el-input v-model="form.value"></el-input>
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
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
const isEditKey = ref(false)
const form = ref({
  id: '',
  key: '',
  value: '',
})

const loading = ref(false)
const dialogVisible = ref<boolean>(false)

const submit = () => {
  FormRef.value.validate((valid: boolean) => {
    if (valid) {
      loadSharedApi({ type: 'knowledge', systemType: apiType.value })
        .putTag(id, form.value.id, form.value, loading)
        .then((res: any) => {
          close()
          emit('refresh')
        })
    }
  })
}

const open = (row: any, isKey: boolean) => {
  dialogVisible.value = true
  form.value.id = row.id
  form.value.key = row.key
  form.value.value = row.value
  isEditKey.value = isKey
}

const close = () => {
  dialogVisible.value = false
}

defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
