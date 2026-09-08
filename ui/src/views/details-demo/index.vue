<script setup lang="ts">
import { ref } from 'vue'
import ExecutionDetailContent from '@/workflow-canvas/details/index.vue'
import { WorkflowMode, WorkflowNodeType } from '@/workflow-canvas/types'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

defineOptions({ name: 'DetailsDemo' })

// 一个 AI 对话节点的示例执行详情。
function makeAiChat(overrides: Partial<ExecutionNodeDetail> = {}): ExecutionNodeDetail {
  return {
    type: WorkflowNodeType.AiChat,
    name: 'AI 对话',
    status: 200,
    index: 0,
    run_time: 1.234,
    message_tokens: 128,
    answer_tokens: 96,
    system: '你是一个乐于助人的中文助手，请简洁作答。',
    history_message: [
      { role: 'user', content: '你好' },
      { role: 'ai', content: '你好，有什么可以帮你的吗？' },
    ],
    question: '用一句话介绍一下 MaxKB。',
    reasoning_content: '用户想要一句话简介，需覆盖：开源、企业级、知识库、Agent 三个要点，控制在一句。',
    answer:
      '**MaxKB** 是一款开源的企业级 AI 应用平台，支持基于知识库的 RAG 检索、Agent 工作流编排与 MCP 工具调用。\n\n- 开源、可私有化部署\n- RAG + 工作流 + 工具\n- 多模型接入',
    ...overrides,
  }
}

const detail = ref<ExecutionNodeDetail[]>([
  makeAiChat({ index: 0 }),
  {
    type: WorkflowNodeType.LoopNode,
    name: '循环',
    status: 200,
    index: 1,
    run_time: 4.567,
    loop_type: 'ARRAY',
    loop_node_data: {
      '0': {
        aiNode: makeAiChat({
          name: 'AI 对话（第 1 轮）',
          index: 0,
          question: '第 1 项：介绍知识库',
          answer: '知识库把文档切片、向量化后存入 pgvector，用于语义检索。',
          run_time: 0.98,
        }),
      },
      '1': {
        aiNode: makeAiChat({
          name: 'AI 对话（第 2 轮）',
          index: 0,
          question: '第 2 项：介绍工作流',
          answer: '工作流用 LogicFlow 编排节点，支持循环、分支与工具调用。',
          run_time: 1.12,
          status: 500,
          err_message: '模型调用超时（示例错误，用于查看失败态样式）',
        }),
      },
    },
  } as ExecutionNodeDetail,
])

const mode = ref<WorkflowMode>(WorkflowMode.Application)
</script>

<template>
  <div class="min-h-screen bg-N100 p-6">
    <div class="mx-auto max-w-[480px]">
      <div class="mb-4 flex items-center gap-3">
        <h3>执行详情样式 Demo</h3>
        <el-radio-group v-model="mode" size="small">
          <el-radio-button :value="WorkflowMode.Application">application</el-radio-button>
          <el-radio-button :value="WorkflowMode.Knowledge">knowledge</el-radio-button>
        </el-radio-group>
      </div>
      <ExecutionDetailContent :detail="detail" :workflow-mode="mode" />
    </div>
  </div>
</template>
