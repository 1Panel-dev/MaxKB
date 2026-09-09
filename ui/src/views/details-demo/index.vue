<script setup lang="ts">
import { ref } from 'vue'
import ExecutionDetailContent from '@/workflow-canvas/details/index.vue'
import { WorkflowMode, WorkflowNodeType } from '@/workflow-canvas/types'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

defineOptions({ name: 'DetailsDemo' })

const mode = ref<WorkflowMode>(WorkflowMode.Application)

function base(type: WorkflowNodeType, index: number, name: string, overrides: Partial<ExecutionNodeDetail> = {}): ExecutionNodeDetail {
  return { type, name, status: 200, index, run_time: 0.86, ...overrides }
}

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
  // ===== AI 对话 =====
  makeAiChat({ index: 0 }),

  // ===== 判断器 =====
  base(WorkflowNodeType.Condition, 1, '判断器', {
    branch_name: '包含关键词「退款」',
  }),

  // ===== 指定回复 =====
  base(WorkflowNodeType.Reply, 2, '指定回复', {
    answer: '抱歉，该问题暂时无法回答，请换个问法。',
  }),

  // ===== 开始节点 =====
  base(WorkflowNodeType.Start, 3, '开始', {
    question: '帮我查一下报销流程',
    global_fields: [{ label: '部门', value: '财务部' }],
    document_list: [{ name: '报销制度.pdf' }],
  }),

  // ===== 问题优化 =====
  base(WorkflowNodeType.Question, 4, '问题优化', {
    system: '你负责优化用户问题，使其更清晰、更利于检索。',
    history_message: [{ role: 'user', content: '报销流程' }],
    question: 'MaxKB 的报销流程是什么？',
    answer: '报销流程包括：提交申请 → 部门审批 → 财务打款。',
  }),

  // ===== 意图识别 =====
  base(WorkflowNodeType.IntentNode, 5, '意图识别', {
    system: '判断用户意图。',
    question: '我想申请报销',
    answer: '报销申请',
  }),

  // ===== 文档内容提取 =====
  base(WorkflowNodeType.DocumentExtractNode, 6, '文档内容提取', {
    content: ['## 第一章\n这里是提取出的文档正文内容。\n\n- 要点一\n- 要点二'],
  }),

  // ===== 参数提取 =====
  base(WorkflowNodeType.ParameterExtractionNode, 7, '参数提取', {
    request: '从用户问题中提取姓名和金额。',
    result: { name: '张三', amount: '1200' },
  }),

  // ===== 变量赋值 =====
  base(WorkflowNodeType.VariableAssignNode, 8, '变量赋值', {
    result_list: [
      { name: 'amount', input_type: 'number', input_value: '1200', output_type: 'string', output_value: '1200 元' },
    ],
  }),

  // ===== 工具 =====
  base(WorkflowNodeType.ToolLibCustom, 9, '自定义工具', {
    index: 1,
    params: JSON.stringify({ city: '上海' }),
    result: JSON.stringify({ weather: '晴，26℃' }),
  }),

  // ===== MCP 节点 =====
  base(WorkflowNodeType.McpNode, 10, 'MCP 工具', {
    mcp_tool: 'github.get_repo',
    tool_params: { owner: '1Panel-dev', repo: 'MaxKB' },
    result: ['星标数: 15000'],
  }),

  // ===== 图片理解 =====
  base(WorkflowNodeType.ImageUnderstandNode, 11, '图片理解', {
    system: '识别图片内容。',
    question: '这张图里有什么？',
    reasoning_content: '识别到一辆红色轿车停在停车场。',
    answer: '图中是一辆红色轿车。',
  }),

  // ===== 图片生成 =====
  base(WorkflowNodeType.ImageGenerateNode, 12, '图片生成', {
    question: '生成一张极简风格的 Logo。',
    negative_prompt: '避免复杂花纹、避免文字。',
    answer: '![logo](data:image/svg+xml;base64,)',
  }),

  // ===== 知识库检索 =====
  base(WorkflowNodeType.SearchKnowledge, 13, '知识库检索', {
    question: 'MaxKB 支持哪些部署方式？',
    paragraph_list: [
      {
        title: '部署方式介绍',
        content: 'MaxKB 支持 Docker、Kubernetes 与裸机部署。',
        similarity: 0.92,
        document_name: '部署文档.pdf',
        knowledge_name: '产品手册',
        knowledge_type: 'common',
      },
      {
        title: '系统要求',
        content: '最低 2 核 4G 内存，推荐 4 核 8G。',
        similarity: 0.78,
        document_name: '部署文档.pdf',
        knowledge_name: '产品手册',
        knowledge_type: 'common',
      },
    ],
  }),

  // ===== 多路召回 =====
  base(WorkflowNodeType.RerankerNode, 14, '多路召回', {
    question: 'MaxKB 的检索机制',
    document_list: [
      {
        page_content: '基于关键词与向量混合检索，融合多路召回结果。',
        metadata: { title: '混合检索', similarity: 0.85, document_name: '架构说明.md', knowledge_name: '开发文档' },
      },
    ],
    result_list: [
      {
        page_content: '基于关键词与向量混合检索，融合多路召回结果。',
        metadata: { title: '混合检索', relevance_score: 0.93, document_name: '架构说明.md', knowledge_name: '开发文档' },
      },
    ],
  }),

  // ===== 表单收集 =====
  base(WorkflowNodeType.FormNode, 15, '表单收集', {
    form_field_list: [
      { field: 'name', label: '姓名', input_type: 'input', value: '' },
      { field: 'department', label: '部门', input_type: 'input', value: '' },
    ],
    form_data: { name: '张三', department: '财务部' },
    is_submit: true,
  }),

  // ===== 循环 =====
  {
    type: WorkflowNodeType.LoopNode,
    name: '循环',
    status: 200,
    index: 16,
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
