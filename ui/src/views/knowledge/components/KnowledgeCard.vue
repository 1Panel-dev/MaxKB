<script setup lang="ts">
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import type { KnowledgeItem } from '@/api/types'
import MkSourceCard from '@/components/mk-source-card/index.vue'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { numberFormat } from '@/utils/number'

defineOptions({ name: 'KnowledgeCard' })

const props = defineProps<{
  knowledge: KnowledgeItem
  shared: boolean
}>()
const loading = defineModel<boolean>('loading', { default: false })

const emit = defineEmits<{
  delete: [knowledgeId: string]
}>()

/* 删除知识库 */
function handleDeleteKnowledge() {
  return MsgConfirm(`确认删除知识库：${props.knowledge.name}？`)
    .then(() => {
      loading.value = true
      return KnowledgeApi.deleteKnowledge(props.knowledge.id)
        .then(() => {
          emit('delete', props.knowledge.id)
          MsgSuccess('删除成功')
        })
        .finally(() => {
          loading.value = false
        })
    })
    .catch(() => {})
}
</script>

<template>
  <MkSourceCard
    :create_time="knowledge.create_time"
    :nick_name="knowledge.nick_name || '-'"
    :title="knowledge.name"
  >
    <template #icon>
      <span class="flex size-8 items-center justify-center rounded-md bg-primary/10 text-primary">
        <MkIcon name="icon_book_filled" :size="20" />
      </span>
    </template>

    <template #tag>
      <el-tag v-if="shared" size="small" type="info">共享</el-tag>
    </template>

    <p class="line-clamp-2" :title="knowledge.desc ?? undefined">
      {{ knowledge.desc }}
    </p>

    <template #footer="{ Action, ActionDropdown }">
      <span>
        <span class="mr-1 font-semibold">{{ knowledge.document_count ?? 0 }}</span>
        <span class="text-N600">文档</span>
      </span>
      <el-divider direction="vertical" />
      <span>
        <strong class="mr-1 font-semibold">{{ numberFormat(knowledge.char_length) }}</strong>
        <span class="text-N600">字符</span>
      </span>

      <component :is="Action" v-if="!shared">
        <component :is="ActionDropdown">
          <MkDropdownItem>
            <template #icon><MkIcon name="icon_assigned_outlined" /></template>
            <span>资源授权</span>
          </MkDropdownItem>
          <MkDropdownItem>
            <template #icon><MkIcon name="icon_move2_outlined" /></template>
            <span>移动到</span>
          </MkDropdownItem>
          <MkDropdownItem divided @click="handleDeleteKnowledge">
            <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
            <span>删除</span>
          </MkDropdownItem>
        </component>
      </component>
    </template>
  </MkSourceCard>
</template>
