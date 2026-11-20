<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

defineOptions({ name: 'DescriptionDialog' })

const { t } = useI18n({ useScope: 'global' })

const visible = ref(false)
const description = ref('')

function open(content: string) {
  description.value = content
  visible.value = true
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" :title="t('workflow.publishHistory.descriptionLabel')" @closed="description = ''">
    {{ description || t('workflow.publishHistory.emptyDescription') }}
  </MkDialog>
</template>

<style scoped></style>
