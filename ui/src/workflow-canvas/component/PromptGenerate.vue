<script setup lang="ts">
import { inject, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useWorkflowStore } from '@/workflow-canvas/store'
import type { PromptGenerateMessage } from '@/api/types'
import GenerateContent from '@/components/business/generate-content/index.vue'
defineOptions({ name: 'PromptGenerate' })
const props = defineProps<{
  modelId: string
}>()
const emit = defineEmits<{ replace: [prompt: string] }>()
const route = useRoute()

// 资源范围沿用画布传递的 apiType，循环内节点也使用同一上下文。
const apiType = inject<string>('apiType', 'workspace')
const store = useWorkflowStore(apiType)

// 提示词模板：约束生成结果的角色结构与内容范围。
const PROMPT_TEMPLATE = `请根据用户描述生成一个完整的AI角色人设模板:

用户需求：{userInput}

重要说明：
1. 角色设定必须服务于"{userInput}"内容设定应用的核心功能
2. 允许用户对角色设定的具体内容进行调整和优化
3. 如果用户要求修改某个技能或部分，在保持应用主题的前提下进行相应调整

请按以下格式生成：

必须严格遵循以下规则：
1. **严格禁止输出解释、前言、额外说明**，只输出最终结果。
2. **严格使用以下格式**，不能缺少标题、不能多出其他段落。
3. **如果用户要求修改角色设定的某个部分，在保持应用核心功能的前提下进行调整**。
4. **如果用户需求与角色设定生成完全无关（如闲聊、其他话题），则主要依据应用信息生成标准角色设定，但不完全忽略用户输入，可从中提取有价值的辅助信息（如领域背景、语气风格等）作为次要参考**。

# 角色:
角色概述和主要职责的一句话描述

## 目标：
角色的工作目标,如果有多目标可以分点列出,但建议更聚焦1-2个目标

## 核心技能：
### 技能 1: [技能名称，如作品推荐/信息查询/专业分析等]
1. [执行步骤1 - 描述该技能的第一个具体操作步骤，包括条件判断和处理方式]
2. [执行步骤2 - 描述该技能的第二个具体操作步骤，包括如何获取或处理信息]
3. [执行步骤3 - 描述该技能的最终输出步骤，说明如何呈现结果]

===回复示例===
- 📋 [标识符]: <具体内容格式说明>
- 🎯 [标识符]: <具体内容格式说明>
- 💡 [标识符]: <具体内容格式说明>
===示例结束===

### 技能 2: [技能名称]
1. [执行步骤1 - 描述触发条件和初始处理方式]
2. [执行步骤2 - 描述信息获取和深化处理的具体方法]
3. [执行步骤3 - 描述最终输出的具体要求和格式]

### 技能 3: [技能名称]
- [核心能力描述 - 说明该技能的主要作用和知识基础]
- [应用方法 - 描述如何运用该技能为用户提供服务，包括具体的实施方式]

## 工作流：
1. 描述角色工作流程的第一步
2. 描述角色工作流程的第二步
3. 描述角色工作流程的第三步

## 输出格式：
如果对角色的输出格式有特定要求，可以在这里强调并举例说明想要的输出格式


## 限制：
1. **严格限制回答范围**：仅回答与角色设定相关的问题。
   - 如果用户提问与角色无关，必须使用以下固定格式回复：
     “对不起，我只能回答与[角色设定]相关的问题，您的问题不在服务范围内。”
   - 不得提供任何与角色设定无关的回答。
2. 描述角色在互动过程中需要遵循的限制条件2
3. 描述角色在互动过程中需要遵循的限制条件3

输出时不得包含任何解释或附加说明，只能返回符合以上格式的内容。`

// 生成上下文：沿用节点模型和当前智能体已保存的模型参数。
const applicationId = ref('')
const activeModelId = ref('')

function initGenerate() {
  applicationId.value = route.params.applicationId as string
  activeModelId.value = props.modelId
}

function resetData() {
  applicationId.value = ''
  activeModelId.value = ''
}

function requestGeneratePrompt(messages: PromptGenerateMessage[]) {
  return store.postPromptGenerate(applicationId.value, activeModelId.value, {
    messages,
    prompt: PROMPT_TEMPLATE,
  })
}
</script>

<template>
  <GenerateContent
    title="生成提示词"
    placeholder="请输入提示词"
    empty-text="提示词显示在这里"
    :disabled="!modelId || !route.params.applicationId"
    :request="requestGeneratePrompt"
    @open="initGenerate"
    @closed="resetData"
    @replace="emit('replace', $event)"
  />
</template>
