# coding=utf-8
"""
@project: MaxKB
@file： workflow_generator.py
@desc: 自然语言生成工作流

设计要点（区别于"让大模型直接吐完整 LogicFlow JSON"的脆弱做法）：
1. 大模型只负责它擅长的部分——把用户需求拆成一份**简单的编排计划**（节点类型 + 语义参数 + 连接关系）。
2. 复杂且死板的真实节点 JSON（config.fields / node_data / 锚点 / 布局 / 变量接线）全部由**确定性代码**按照
   MaxKB 真实节点结构拼装，模型碰不到这套 schema，因此弱模型也不会"猜错格式"。
3. 资源（模型 / 知识库 / 工具）按**该用户在该工作空间真实有权限**的范围解析为真实 id。
4. 拼装完成后用**真实运行期 serializer 逐节点校验**，硬保证"生成完即可用、无需用户再填表单"。
"""
import json
import re
import uuid
from typing import Dict, List, Optional, Tuple

from django.db.models import QuerySet
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field, ValidationError

from common.exception.app_exception import AppApiException
from common.utils.logger import maxkb_logger
from models_provider.models import Model
from models_provider.tools import get_model

# ============================================================
# 计划（Plan）数据结构 —— 大模型输出的中间表示，刻意保持简单、语义化
# ============================================================

# 支持的业务节点类型（开始 / 基本信息节点由代码自动注入，不在计划里）
SUPPORTED_NODE_TYPES = [
    'ai-chat', 'search-knowledge', 'reply', 'tool', 'condition', 'question', 'intent',
    'doc-extract', 'loop', 'variable-assign', 'form', 'application', 'mcp',
]

# 资源需求描述 - 大模型只需要描述需要什么类型的资源
class ResourceNeed(BaseModel):
    """资源需求描述"""
    need_knowledge: bool = Field(default=False, description="是否需要知识库（文档问答、知识检索）")
    knowledge_keywords: List[str] = Field(default_factory=list, description="知识库关键词（用于匹配）")
    need_tool: bool = Field(default=False, description="是否需要工具（API调用、数据处理）")
    tool_keywords: List[str] = Field(default_factory=list, description="工具关键词（用于匹配）")
    need_application: bool = Field(default=False, description="是否需要应用（子智能体、流程复用）")
    application_keywords: List[str] = Field(default_factory=list, description="应用关键词（用于匹配）")

# 条件节点可用的比较运算符（与 apps/application/flow/compare 保持一致）
COMPARE_OPERATORS = [
    'is_null', 'is_not_null', 'contain', 'not_contain', 'eq', 'not_eq',
    'ge', 'gt', 'le', 'lt', 'len_eq', 'len_ge', 'len_gt', 'len_le', 'len_lt',
    'is_true', 'is_not_true', 'start_with', 'end_with', 'regex', 'wildcard',
]


class PlanCondition(BaseModel):
    ref: str = Field(description="被判断的上游变量，格式 '节点标题.字段'，如 '知识库检索.directly_return'")
    compare: str = Field(default='is_not_null', description="比较运算符")
    value: str = Field(default='', description="比较值，is_null/is_not_null 等可留空")


class PlanBranch(BaseModel):
    name: str = Field(description="分支显示名，如 '命中知识库' / '未命中'")
    logic: str = Field(default='and', description="多个条件之间的关系：and 或 or")
    conditions: List[PlanCondition] = Field(default_factory=list, description="条件列表；ELSE 兜底分支留空")
    target: Optional[str] = Field(default=None, description="该分支连向的节点 key")


class PlanIntent(BaseModel):
    intent: str = Field(description="该意图的描述（用于分类判断），如 '查询订单状态'")
    target: Optional[str] = Field(default=None, description="命中该意图后连向的节点 key")
    is_other: bool = Field(default=False, description="是否为兜底「其他」分支（无法归类时走这里）")


class PlanNode(BaseModel):
    key: str = Field(description="计划内唯一标识，如 n1、n2")
    type: str = Field(description=f"节点类型，取值之一：{SUPPORTED_NODE_TYPES}")
    title: str = Field(description="节点显示名（中文，整个工作流内唯一）")
    # 节点执行条件：AND=所有前置节点执行完才执行，OR=任一前置节点执行完就执行
    # 当节点有多个前置节点（如分支汇合）时，应该设为 OR
    condition: Optional[str] = Field(default=None, description="节点执行条件：AND（所有前置节点执行完才执行）或 OR（任一前置节点执行完就执行）。分支汇合节点应设为 OR")
    # ai-chat / question（问题优化）
    model: Optional[str] = Field(default=None, description="ai-chat/question/intent：使用的模型名称（从可用模型列表里选）")
    system: Optional[str] = Field(default='', description="ai-chat/question：系统提示词/角色设定")
    prompt: Optional[str] = Field(default=None, description="ai-chat/question：用户提示词，可用 {{节点标题.字段}} 引用上游")
    # AI 节点工具配置
    tools: Optional[List[str]] = Field(default=None, description="ai-chat：工具名称列表（从可用工具里选），让 AI 可以调用这些工具")
    applications: Optional[List[str]] = Field(default=None, description="ai-chat：应用名称列表（从可用应用里选），让 AI 可以调用这些应用")
    mcp_tools: Optional[List[str]] = Field(default=None, description="ai-chat：MCP 工具名称列表")
    # search-knowledge
    knowledge: Optional[List[str]] = Field(default=None, description="search-knowledge：知识库名称列表（从可用知识库里选）")
    # reply
    content: Optional[str] = Field(default=None, description="reply：直接回复文本，可含 {{节点标题.字段}}")
    reference: Optional[str] = Field(default=None, description="reply：直接引用某节点输出，格式 '节点标题.字段'")
    # tool
    tool: Optional[str] = Field(default=None, description="tool：工具名称（从可用工具里选）")
    tool_params: Optional[Dict[str, str]] = Field(default=None, description="tool：入参映射 {参数名: 值或{{引用}}}")
    # condition
    branches: Optional[List[PlanBranch]] = Field(default=None, description="condition：分支列表，每个分支含条件与去向")
    # intent（意图识别，按意图分支路由）
    input: Optional[str] = Field(default=None, description="intent：待分类的输入引用，格式 '节点标题.字段'，默认 '开始.question'")
    intents: Optional[List[PlanIntent]] = Field(default=None, description="intent：意图分支列表，每个含意图描述与去向")
    # loop（循环）
    loop_type: Optional[str] = Field(default=None, description="loop：循环类型 ARRAY/NUMBER/LOOP")
    loop_source: Optional[str] = Field(default=None, description="loop：ARRAY 类型的数据源引用，格式 '节点标题.字段'")
    loop_count: Optional[int] = Field(default=None, description="loop：NUMBER 类型的循环次数")
    loop_body: Optional[List[str]] = Field(default=None, description="loop：循环体内执行的节点 key 列表")
    # variable-assign（变量赋值）
    variables: Optional[Dict[str, str]] = Field(default=None, description="variable-assign：变量赋值映射 {变量名: 值或引用}")
    # form（表单）
    form_fields: Optional[List[Dict]] = Field(default=None, description="form：表单字段列表 [{name, type, required, label}]")
    # application（应用调用）
    application: Optional[str] = Field(default=None, description="application：应用名称（从可用应用里选）")
    # mcp（MCP 工具调用）
    mcp_server: Optional[str] = Field(default=None, description="mcp：MCP 服务器名称")
    mcp_tool_name: Optional[str] = Field(default=None, description="mcp：MCP 工具名称")


class PlanEdge(BaseModel):
    source: str = Field(description="源节点 key（条件节点的出边写在 branches 里，不要写在这里）")
    target: str = Field(description="目标节点 key")


class WorkflowPlan(BaseModel):
    app_name: str = Field(default='智能体', description="智能体名称")
    app_desc: str = Field(default='', description="智能体描述")
    prologue: str = Field(default='您好，有什么可以帮您？', description="开场白")
    nodes: List[PlanNode] = Field(default_factory=list)
    edges: List[PlanEdge] = Field(default_factory=list)


# ============================================================
# 资源解析 —— 复用 MaxKB 既有的"按用户权限列资源"逻辑
# ============================================================

class WorkspaceResources:
    """该用户在该工作空间真实可用的资源（模型 / 知识库 / 工具 / 应用 / 工具商店）"""

    def __init__(self, models: List[Dict], knowledge: List[Dict], tools: List[Dict],
                 applications: List[Dict] = None, store_tools: List[Dict] = None):
        self.models = models
        self.knowledge = knowledge
        self.tools = tools
        self.applications = applications or []
        self.store_tools = store_tools or []
        # 名称 -> 资源，便于把计划里的"名称引用"解析成真实 id（名称做了去空格/小写归一）
        self._model_by_name = {self._norm(m['name']): m for m in models}
        self._knowledge_by_name = {self._norm(k['name']): k for k in knowledge}
        self._tool_by_name = {self._norm(t['name']): t for t in tools}
        self._application_by_name = {self._norm(a['name']): a for a in self.applications}
        self._store_tool_by_name = {self._norm(t['name']): t for t in self.store_tools}

    @staticmethod
    def _norm(name: str) -> str:
        return str(name or '').strip().lower()

    def resolve_model(self, name: Optional[str]) -> Optional[Dict]:
        if name and self._norm(name) in self._model_by_name:
            return self._model_by_name[self._norm(name)]
        # 名称没匹配上时，退化为第一个可用模型，保证 ai-chat 可运行
        return self.models[0] if self.models else None

    def resolve_knowledge(self, names: Optional[List[str]]) -> List[Dict]:
        result = []
        seen = set()
        for name in (names or []):
            n = self._norm(name)
            if not n:
                continue
            hit = self._knowledge_by_name.get(n)
            if not hit:
                # 模糊兜底：名称互相包含（模型常把"报销制度知识库"写成"报销知识库"之类）
                for kb in self.knowledge:
                    kn = self._norm(kb['name'])
                    if kn and (n in kn or kn in n):
                        hit = kb
                        break
            if hit and hit['id'] not in seen:
                seen.add(hit['id'])
                result.append(hit)
        return result

    def resolve_tool(self, name: Optional[str]) -> Optional[Dict]:
        return self._tool_by_name.get(self._norm(name)) if name else None

    def resolve_application(self, name: Optional[str]) -> Optional[Dict]:
        return self._application_by_name.get(self._norm(name)) if name else None

    def resolve_mcp(self, name: Optional[str]) -> Optional[Dict]:
        return self._mcp_by_name.get(self._norm(name)) if name else None

    def resolve_store_tool(self, name: Optional[str]) -> Optional[Dict]:
        """解析工具商店中的工具"""
        return self._store_tool_by_name.get(self._norm(name)) if name else None

    def resolve_tools(self, names: Optional[List[str]]) -> List[Dict]:
        """解析多个工具名称"""
        result = []
        for name in (names or []):
            hit = self._tool_by_name.get(self._norm(name))
            if hit:
                result.append(hit)
        return result

    def resolve_applications(self, names: Optional[List[str]]) -> List[Dict]:
        """解析多个应用名称"""
        result = []
        for name in (names or []):
            hit = self._application_by_name.get(self._norm(name))
            if hit:
                result.append(hit)
        return result


def load_workspace_resources(workspace_id: str, user_id: str) -> WorkspaceResources:
    """加载该用户有权限使用的 LLM 模型、知识库、自定义工具"""
    from models_provider.serializers.model_serializer import ModelSerializer
    from knowledge.serializers.knowledge import KnowledgeSerializer
    from knowledge.models import KnowledgeScope
    from tools.serializers.tool import ToolTreeSerializer
    from tools.models.tool import ToolScope

    # --- 模型（仅 LLM）---
    models: List[Dict] = []
    try:
        model_result = ModelSerializer.Query(
            data={'user_id': str(user_id), 'workspace_id': workspace_id, 'model_type': 'LLM'}
        ).model_list(workspace_id, with_valid=True)
        for m in [*model_result.get('model', []), *model_result.get('shared_model', [])]:
            models.append({'id': str(m['id']), 'name': m['name'], 'provider': m.get('provider', '')})
    except Exception as e:
        maxkb_logger.error(f'生成工作流-加载模型列表失败: {e}')

    # --- 知识库 ---
    knowledge: List[Dict] = []
    try:
        knowledge_result = KnowledgeSerializer.Query(
            data={'workspace_id': workspace_id, 'user_id': str(user_id), 'scope': KnowledgeScope.WORKSPACE}
        ).list()
        for k in (knowledge_result or []):
            knowledge.append({'id': str(k['id']), 'name': k['name'], 'desc': k.get('desc', '')})
    except Exception as e:
        maxkb_logger.error(f'生成工作流-加载知识库列表失败: {e}')

    # --- 工具 ---
    tools: List[Dict] = []
    try:
        tool_result = ToolTreeSerializer.Query(
            # folder_id 必填；传工作空间根目录 id（== workspace_id）表示取整个工作空间、不按文件夹过滤
            data={'workspace_id': workspace_id, 'folder_id': workspace_id,
                  'user_id': str(user_id), 'scope': ToolScope.WORKSPACE}
        ).get_tools()
        for t in (tool_result.get('tools', []) or []):
            tools.append({
                'id': str(t['id']),
                'name': t['name'],
                'desc': t.get('desc', ''),
                'input_field_list': t.get('input_field_list', []) or [],
            })
        # 也加载共享工具
        shared_tool_result = ToolTreeSerializer.Query(
            data={'workspace_id': workspace_id, 'folder_id': workspace_id,
                  'user_id': str(user_id), 'scope': ToolScope.SHARED}
        ).get_tools()
        for t in (shared_tool_result.get('tools', []) or []):
            tools.append({
                'id': str(t['id']),
                'name': t['name'],
                'desc': t.get('desc', ''),
                'input_field_list': t.get('input_field_list', []) or [],
            })
    except Exception as e:
        maxkb_logger.error(f'生成工作流-加载工具列表失败: {e}')

    # --- 应用 ---
    applications: List[Dict] = []
    try:
        from application.models import Application
        app_queryset = QuerySet(Application).filter(
            workspace_id=workspace_id,
            is_publish=True  # 只加载已发布的应用（Application 没有 status 字段）
        )
        for a in app_queryset[:50]:
            if a.work_flow:  # 只加载有工作流的应用
                applications.append({
                    'id': str(a.id),
                    'name': a.name,
                    'desc': a.desc if hasattr(a, 'desc') else '',
                })
    except Exception as e:
        maxkb_logger.error(f'生成工作流-加载应用列表失败: {e}')

    # --- 工具商店 ---
    store_tools: List[Dict] = []
    try:
        from tools.serializers.tool import ToolSerializer
        store_result = ToolSerializer.StoreTool(
            data={'user_id': str(user_id)}
        ).get_appstore_tools()
        for t in (store_result.get('apps', []) or []):
            name = t.get('name', '')
            if not name:  # 跳过没有名称的工具
                continue
            store_tools.append({
                'id': t.get('downloadUrl', ''),  # 使用 downloadUrl 作为标识
                'name': name,
                'desc': t.get('desc', '') or '',
                'is_store': True,  # 标记为工具商店工具
                'download_url': t.get('downloadUrl', ''),
                'version': t.get('version', ''),
            })
    except Exception as e:
        maxkb_logger.error(f'生成工作流-加载工具商店列表失败: {e}')

    return WorkspaceResources(models, knowledge, tools, applications, store_tools)


# ============================================================
# 资源匹配 —— 根据需求描述匹配最合适的资源
# ============================================================

def match_resources(description: str, resources: WorkspaceResources) -> Dict[str, List[Dict]]:
    """
    根据需求描述匹配最合适的资源
    
    返回：{
        'knowledge': [匹配的知识库],
        'tools': [匹配的工具],
        'applications': [匹配的应用]
    }
    """
    import re
    
    # 提取关键词
    desc_lower = description.lower()
    
    matched = {
        'knowledge': [],
        'tools': [],
        'applications': [],
    }
    
    # 匹配知识库
    for kb in resources.knowledge:
        name = kb['name'].lower()
        desc = kb.get('desc', '').lower()
        # 如果知识库名称或描述出现在需求中，或者需求中包含相关关键词
        if (name in desc_lower or 
            any(kw in desc_lower for kw in ['知识', '文档', '问答', '检索', '查询']) and 
            any(kw in name or kw in desc for kw in ['产品', '手册', '文档', '指南', '帮助'])):
            matched['knowledge'].append(kb)
    
    # 匹配工具
    for tool in resources.tools:
        name = tool['name'].lower()
        desc = tool.get('desc', '').lower()
        # 如果工具名称出现在需求中
        if name in desc_lower:
            matched['tools'].append(tool)
        # 或者需求中包含工具相关的动词
        elif any(kw in desc_lower for kw in ['调用', '查询', '获取', '发送', '创建', '更新', '删除']):
            # 检查工具名称是否包含相关动词
            if any(kw in name for kw in ['查询', '获取', '发送', '创建', '更新', '删除', 'api', '接口']):
                matched['tools'].append(tool)
    
    # 匹配应用
    for app in resources.applications:
        name = app['name'].lower()
        if name in desc_lower:
            matched['applications'].append(app)
    
    return matched


def build_plan_messages_with_matching(description: str, resources: WorkspaceResources) -> List:
    """构建带资源匹配的计划消息"""
    # 先进行资源匹配
    matched = match_resources(description, resources)
    
    # 构建资源描述
    def fmt_matched(items, resource_type):
        if not items:
            return f'（无匹配的{resource_type}）'
        lines = []
        for it in items[:10]:  # 最多显示10个
            line = f"- {it['name']}"
            if it.get('desc'):
                line += f"：{it['desc'][:50]}"
            lines.append(line)
        return '\n'.join(lines)
    
    def fmt_all(items, extra=''):
        if not items:
            return '（无）'
        lines = []
        for it in items[:50]:
            line = f"- {it['name']}"
            if extra == 'tool' and it.get('input_field_list'):
                params = '、'.join([f.get('name', '') for f in it['input_field_list'] if f.get('name')])
                if params:
                    line += f"（入参：{params}）"
            lines.append(line)
        return '\n'.join(lines)
    
    default_model = resources.models[0]['name'] if resources.models else ''
    system_prompt = PLAN_SYSTEM_PROMPT % {
        'compares': '、'.join(COMPARE_OPERATORS),
        'default_model': default_model,
    }
    
    user_prompt = f"""用户需求：
{description}

## 系统推荐使用的资源（根据需求自动匹配）
### 推荐知识库
{fmt_matched(matched['knowledge'], '知识库')}

### 推荐工具
{fmt_matched(matched['tools'], '工具')}

### 推荐应用
{fmt_matched(matched['applications'], '应用')}

## 所有可用资源（如果推荐不合适，可以从这里选择）
### 可用模型
{fmt_all(resources.models)}

### 可用知识库
{fmt_all(resources.knowledge)}

### 可用工具
{fmt_all(resources.tools, extra='tool')}

### 可用应用
{fmt_all(resources.applications)}

### 工具商店
{fmt_all(resources.store_tools)}

请输出编排计划 JSON。优先使用系统推荐的资源，如果推荐不合适再从所有可用资源中选择。"""
    
    return [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]

PLAN_SYSTEM_PROMPT = """你是 MaxKB 的工作流编排专家。请把用户的自然语言需求拆解成一份**编排计划**，以 JSON 返回。
你不需要、也不要输出 MaxKB 的底层节点 JSON——底层格式由程序根据你的计划自动生成。

## 可用节点类型（type 取值）
- "intent"：意图识别（按用户意图把流程分流到不同分支）。参数：model（模型名）、input（待分类输入，默认 "开始.question"）、intents=[{intent(意图描述), target(命中后连向的节点key), is_other(是否兜底)}]。务必包含一个 is_other:true 的兜底分支。输出变量：category（分类）、reason（理由）。
- "question"：问题优化（结合历史对话把用户问题改写得更完整，用于提升检索准确率）。参数：model、system、prompt。输出变量：answer（优化后的问题，引用 {{节点标题.answer}}）。
- "ai-chat"：大模型对话。参数：model（模型名）、system（角色设定，可空）、prompt（用户提示词，可引用上游变量）。**可选工具配置**：tools（工具名称数组，让 AI 可调用这些工具）、applications（应用名称数组，让 AI 可调用这些应用）。输出变量：answer。
- "search-knowledge"：知识库检索。参数：knowledge（知识库名称数组）。输出变量：data（检索结果文本）、directly_return（可直接回答的内容）、paragraph_list、is_hit_handling_method_list。
- "reply"：指定回复。两种用法二选一：content（直接文本，可含变量）；或 reference（直接引用某节点输出，如 "知识库检索.directly_return"）。
- "doc-extract"：文档内容提取。**当用户需要"上传文档/合同/文件并对其内容进行分析、审核、总结、提取"时，必须用它**（系统会自动开启文件上传）。无需参数。输出变量：content（文档正文）、document_list。后续用 {{节点标题.content}} 引用提取到的内容。
- "tool"：调用已有工具。参数：tool（工具名）、tool_params（入参映射 {参数名: 值}）。输出变量：result。
- "condition"：条件判断（按变量值分支）。参数：branches=[{name, logic(and/or), conditions:[{ref, compare, value}], target}]。
- "loop"：循环节点（对列表数据循环处理或指定次数循环）。参数：loop_type（ARRAY/NUMBER）、loop_source（ARRAY类型的数据源引用）、loop_count（NUMBER类型的循环次数）、loop_body（循环体内执行的节点key列表）。输出变量：current_index（当前索引）、current_item（当前项）。
- "variable-assign"：变量赋值。参数：variables（{变量名: 值或引用}）。用于在流程中存储中间结果。
- "application"：调用其他应用。参数：application（应用名称）。输出变量：result。
- "mcp"：调用 MCP 工具。参数：mcp_server（MCP服务器名称）、mcp_tool_name（工具名称）。输出变量：result。

## 系统会自动补充的节点（不要写进 nodes）
- "开始" 节点：输出 question（用户问题）。引用方式 {{开始.question}}。
- "基本信息" 节点：承载 app_name / app_desc / prologue。

## 编排要求（追求完整、充分拆解——宁可细，不要省）
0. **节点数量目标 10~20 个（力争 15 个左右）**（不含自动补的开始/基本信息节点）。要把用户需求**充分展开成有层次的完整流程**，每个环节该有的步骤都补齐，**不要为了简洁而合并或省略步骤**。只有需求确实极简单时才可少于 10 个。注意：结构正确性由程序的修复层兜底，你只需把流程拆得完整、丰富，不必担心步骤多会出错。
1. 优先用 **intent 意图识别路由**把流程扇开：只要用户提问可能有多种类型（咨询/查询/办理/闲聊等），就用 intent 分 2~4 类，**每一类都走一条独立且完整的处理链路**，不要几类共用一个笼统回答。
2. 涉及知识库问答的分支，走**完整链路**：question（问题优化）→ search-knowledge（检索）→ condition（命中判断）→ 命中走 ai-chat 增强回答 / 未命中走 reply 兜底。不要把这几步压成一两个节点。
3. 每条分支都要有明确的**结束节点**（ai-chat 或 reply），不要出现断头分支；务必为"无结果/兜底"场景准备回复。
4. 让流程**充分体现真实业务逻辑**：改写、检索、判断、增强回答、兜底、必要的追问确认等环节都补齐，宁可拆细一点。
5. 当需要 AI 同时具备工具调用能力时，在 ai-chat 节点的 tools 参数里指定工具名称。
6. 需要批量处理列表数据时用 loop 节点；需要存储/汇总中间结果时用 variable-assign 节点。

## 资源使用铁律（违反会导致生成不可用，务必遵守）
1. knowledge（知识库）、tool（工具）、application（应用）的名称**只能从下方"可用资源"列表里逐字复制**，禁止编造、禁止臆测名称。
2. 若某项能力在可用列表里没有对应资源，**不要硬凑工具**：
   - 需要"读取/分析用户上传的文档、合同、文件内容" → 用 **doc-extract** 节点（不是 tool）。
   - 其它无法用现有资源完成的处理 → 用 **ai-chat** 节点，让大模型直接处理。
3. 当"可用工具"列表为空时，**绝对不要**使用 type 为 "tool" 的节点。
4. tool 只在确有名称匹配、且该工具用途与步骤目标一致时才用；不确定就别用。
5. 合同审核/文档分析类需求的正确做法：doc-extract（提取正文）→ ai-chat（按规则审核/优化），而不是去找"提取合同""审核合同"之类的工具。
6. ai-chat 节点的 tools 参数里的工具，必须是"可用工具"列表中存在的工具名称。

## 变量引用规则（非常重要）
- 在 prompt / system / content 文本里用 `{{节点标题.字段}}` 引用上游输出，例如 {{开始.question}}、{{知识库检索.data}}、{{AI对话.answer}}。
- 全局变量用 {{global.time}}、{{global.history_context}}。
- condition 的 ref、reply 的 reference 用不带花括号的 "节点标题.字段"。
- 节点标题（title）整个工作流内必须唯一，引用时大小写/文字要完全一致。
- loop 节点的 loop_source 用不带花括号的 "节点标题.字段"。

## 比较运算符（condition.compare 取值）
%(compares)s
（判断"非空"用 is_not_null，"为空"用 is_null。）

## 节点执行条件（condition 字段，非常重要）
每个节点有一个 condition 字段，控制该节点何时执行：
- **AND**（默认）：所有前置节点都执行完才执行当前节点。适用于顺序流程。
- **OR**：任一前置节点执行完就执行当前节点。适用于分支汇合场景。

**自动判断规则**：
- 如果节点只有1个前置节点，自动设为 AND
- 如果节点有多个前置节点（如分支汇合），自动设为 OR
- 你也可以在计划中显式指定 condition 值来覆盖自动判断

**典型场景**：
```
        ┌─ 分支A ─┐
开始 ──┤         ├──→ 汇合节点(OR) ──→ 结束
        └─ 分支B ─┘
```
汇合节点必须设为 OR，否则它会等待所有分支都执行完，但条件分支只会走一条路，导致汇合节点永远不执行。

## 连接关系
- 普通顺序连接写在 edges：[{"source": 源key, "target": 目标key}]。
- condition / intent 节点的去向写在它自己的 branches[].target / intents[].target 里，**不要**再写进 edges。
- loop 节点的循环体节点写在 loop_body 里，**不要**写进 edges。
- 需要并行时，让同一个源在 edges 里连向多个目标即可。
- 分支汇合时，汇合节点的 condition 会自动设为 OR（如果有多个前置节点）。

## 输出格式（只输出 JSON，不要任何解释、不要 markdown 代码块）
{
  "app_name": "...", "app_desc": "...", "prologue": "...",
  "nodes": [ {"key":"n1","type":"...","title":"...", ...该类型的参数...} ],
  "edges": [ {"source":"n1","target":"n2"} ]
}

## 示例1（智能客服：意图分流 + 知识问答增强 + 兜底，体现多级步骤）
{
  "app_name":"智能客服助手","app_desc":"按意图分流并基于知识库回答","prologue":"您好，我是智能客服，请问有什么可以帮您？",
  "nodes":[
    {"key":"n1","type":"intent","title":"意图识别","model":"%(default_model)s","input":"开始.question","intents":[
      {"intent":"产品咨询或使用问题","target":"n2","is_other":false},
      {"intent":"闲聊或问候","target":"n6","is_other":false},
      {"intent":"其他","target":"n7","is_other":true}
    ]},
    {"key":"n2","type":"question","title":"问题优化","model":"%(default_model)s","prompt":"结合历史对话，把用户问题补全为完整独立的问题：\\n{{开始.question}}"},
    {"key":"n3","type":"search-knowledge","title":"知识库检索","knowledge":["产品手册"]},
    {"key":"n4","type":"condition","title":"判断是否命中","branches":[
      {"name":"命中","logic":"and","conditions":[{"ref":"知识库检索.paragraph_list","compare":"is_not_null","value":""}],"target":"n5"},
      {"name":"未命中","logic":"and","conditions":[],"target":"n7"}
    ]},
    {"key":"n5","type":"ai-chat","title":"知识增强回答","model":"%(default_model)s","system":"你是专业的产品客服","prompt":"已知信息：\\n{{知识库检索.data}}\\n请根据以上信息回答用户问题：\\n{{问题优化.answer}}"},
    {"key":"n6","type":"ai-chat","title":"闲聊回复","model":"%(default_model)s","system":"你是友好的客服助手","prompt":"请友好地回应用户：\\n{{开始.question}}"},
    {"key":"n7","type":"reply","title":"兜底回复","content":"抱歉，没有找到相关内容，您可以换个问法或联系人工客服。"}
  ],
  "edges":[
    {"source":"n2","target":"n3"},
    {"source":"n3","target":"n4"}
  ]
}

## 示例2（AI + 工具调用 + 循环处理）
{
  "app_name":"订单查询助手","app_desc":"帮用户查询订单状态并批量处理","prologue":"您好，请问有什么可以帮您？",
  "nodes":[
    {"key":"n1","type":"ai-chat","title":"订单查询","model":"%(default_model)s","system":"你是订单查询助手","prompt":"请帮用户查询订单：{{开始.question}}","tools":["订单查询工具"]},
    {"key":"n2","type":"loop","title":"批量处理","loop_type":"ARRAY","loop_source":"订单查询.answer","loop_body":["n3"]},
    {"key":"n3","type":"ai-chat","title":"单条处理","model":"%(default_model)s","system":"你是订单处理助手","prompt":"请处理这条订单信息：{{批量处理.current_item}}"},
    {"key":"n4","type":"reply","title":"汇总回复","reference":"订单查询.answer"}
  ],
  "edges":[
    {"source":"n1","target":"n2"},
    {"source":"n2","target":"n4"}
  ]
}
"""


def build_user_prompt(description: str, resources: WorkspaceResources) -> str:
    def fmt(items, extra=''):
        if not items:
            return '（无）'
        lines = []
        for it in items[:50]:
            line = f"- {it['name']}"
            if extra == 'tool' and it.get('input_field_list'):
                params = '、'.join([f.get('name', '') for f in it['input_field_list'] if f.get('name')])
                if params:
                    line += f"（入参：{params}）"
            lines.append(line)
        return '\n'.join(lines)

    return f"""用户需求：
{description}

## 可用模型（ai-chat 的 model 只能从这里选）
{fmt(resources.models)}

## 可用知识库（search-knowledge 的 knowledge 只能从这里选）
{fmt(resources.knowledge)}

## 可用工具（tool 的 tool 只能从这里选，ai-chat 的 tools 也只能从这里选）
{fmt(resources.tools, extra='tool')}

## 可用应用（ai-chat 的 applications 只能从这里选）
{fmt(resources.applications)}

## 工具商店（可直接使用，系统会自动安装）
{fmt(resources.store_tools)}

请输出编排计划 JSON。"""


# ============================================================
# 调用大模型，得到并校验计划
# ============================================================

def _extract_json(text: str) -> str:
    """从模型输出里抽出 JSON 主体，兼容 ```json 代码块与裸 JSON"""
    if text is None:
        raise AppApiException(500, '模型未返回内容')
    fence = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if fence:
        return fence.group(1)
    start = text.find('{')
    end = text.rfind('}')
    if start >= 0 and end > start:
        return text[start:end + 1]
    raise AppApiException(500, '模型输出中未找到 JSON')


def build_plan_messages(description: str, resources: WorkspaceResources) -> List:
    default_model = resources.models[0]['name'] if resources.models else ''
    system_prompt = PLAN_SYSTEM_PROMPT % {
        'compares': '、'.join(COMPARE_OPERATORS),
        'default_model': default_model,
    }
    return [SystemMessage(content=system_prompt), HumanMessage(content=build_user_prompt(description, resources))]


def _loads_lenient(json_str: str) -> Dict:
    """容错解析：仅做绝对安全的修复（去掉 } / ] 前的尾逗号）。
    不动引号/全角标点等，避免破坏中文字符串内容。"""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return json.loads(re.sub(r',(\s*[}\]])', r'\1', json_str))


def parse_plan(raw_text: str) -> WorkflowPlan:
    plan = WorkflowPlan(**_loads_lenient(_extract_json(raw_text)))
    if not plan.nodes:
        raise ValueError('计划里没有任何业务节点')
    return plan


# ============================================================
# 计划 -> 真实工作流 JSON
# ============================================================

X_START = 120
X_GAP = 620
Y_START = 100
Y_GAP = 480


def _new_id() -> str:
    return str(uuid.uuid4())


def _short_id() -> str:
    return str(uuid.uuid4())[:8]


class WorkflowBuilder:
    """把编排计划确定性地拼装成 MaxKB 真实工作流 {nodes, edges}"""

    def __init__(self, plan: WorkflowPlan, resources: WorkspaceResources):
        self.plan = plan
        self.resources = resources
        self.key_to_id: Dict[str, str] = {}      # 计划 key -> 真实节点 id
        self.title_to_id: Dict[str, str] = {}     # 节点标题(stepName) -> 真实节点 id
        self.id_to_title: Dict[str, str] = {}
        # 带分支的节点(condition/intent) key -> [(分支id, 目标节点key)]，建分支边时用
        self.branch_edges: Dict[str, List[Tuple[str, Optional[str]]]] = {}
        # 是否需要在基本信息节点开启文件上传（含 doc-extract 时为 True）
        self.needs_file_upload: bool = False
        self.nodes: List[Dict] = []
        self.edges: List[Dict] = []

    # ---- 标题唯一化 ----
    def _unique_title(self, title: str, used: set) -> str:
        base = (title or '节点').strip()
        name = base
        i = 1
        while name in used:
            i += 1
            name = f'{base}{i}'
        used.add(name)
        return name

    # ---- 引用解析 ----
    def _resolve_ref(self, ref: Optional[str]) -> Optional[List[str]]:
        """把 '节点标题.字段' 解析为结构化引用 [node_id, field]"""
        if not ref or '.' not in ref:
            return None
        title, field = ref.split('.', 1)
        title, field = title.strip(), field.strip()
        if title in ('global', 'chat'):
            return [title, field]
        node_id = self.title_to_id.get(title)
        if node_id:
            return [node_id, field]
        return None

    def _prune_unresolved_tools(self):
        """删除工具无法解析的 tool 节点，并把指向它的连线/分支旁路到其后继"""
        invalid = {pn.key for pn in self.plan.nodes
                   if pn.type == 'tool' and self.resources.resolve_tool(pn.tool) is None}
        if not invalid:
            return
        maxkb_logger.warning(f'生成工作流-剔除无法解析的工具节点: {invalid}')
        succ: Dict[str, List[str]] = {}
        for e in self.plan.edges:
            succ.setdefault(e.source, []).append(e.target)

        def redirect(target: Optional[str]) -> Optional[str]:
            seen = set()
            while target in invalid:
                if target in seen:
                    return None
                seen.add(target)
                nexts = succ.get(target, [])
                target = nexts[0] if nexts else None
            return target

        new_edges = []
        for e in self.plan.edges:
            if e.source in invalid:
                continue
            nt = redirect(e.target)
            if nt:
                new_edges.append(PlanEdge(source=e.source, target=nt))
        self.plan.edges = new_edges
        for pn in self.plan.nodes:
            for b in (pn.branches or []):
                if b.target in invalid:
                    b.target = redirect(b.target)
            for it in (pn.intents or []):
                if it.target in invalid:
                    it.target = redirect(it.target)
        self.plan.nodes = [pn for pn in self.plan.nodes if pn.key not in invalid]

    def build(self) -> Dict:
        # 0) 剔除引用了不存在/无权限工具的节点（模型有时会编造工具），并把它们的连线旁路，
        #    避免产出"该工具不可用"的坏节点，也避免整次生成失败。
        self._prune_unresolved_tools()
        self.needs_file_upload = any(pn.type == 'doc-extract' for pn in self.plan.nodes)

        # 1) 为每个计划节点分配真实 id 与唯一标题（"开始"/"基本信息"为保留标题）。
        #    stepName 必须唯一（渲染与变量引用都依赖它）。若模型给了重名标题则自动去重；
        #    引用按模型原文保留——运行期 {{标题.字段}} 会解析到该标题的首个节点，确定性且合理。
        used_titles = {'开始', '基本信息'}
        for pn in self.plan.nodes:
            node_id = _new_id()
            self.key_to_id[pn.key] = node_id
            new_title = self._unique_title(pn.title, used_titles)
            pn.title = new_title
            self.title_to_id.setdefault(new_title, node_id)
            self.id_to_title[node_id] = new_title

        # 3) 计算布局层级
        levels = self._compute_levels()

        # 4) 计算每个节点的入边数量，用于自动判断 condition 值
        #    AND: 只有1个前置节点（默认）
        #    OR: 有多个前置节点（如分支汇合）
        in_degree = self._compute_in_degree()

        # 5) 注入开始 / 基本信息节点
        self._append_base_and_start()

        # 6) 逐个构建业务节点
        for pn in self.plan.nodes:
            x, y = self._position(pn.key, levels)
            # 自动判断 condition 值
            # 如果用户明确指定了 condition，使用用户的值
            # 否则根据入边数量自动判断：多个前置节点用 OR，否则用 AND
            if pn.condition is None:
                pn.condition = 'OR' if in_degree.get(pn.key, 0) > 1 else 'AND'
            builder = {
                'ai-chat': self._build_ai_chat,
                'search-knowledge': self._build_search_knowledge,
                'reply': self._build_reply,
                'tool': self._build_tool,
                'condition': self._build_condition,
                'question': self._build_question,
                'intent': self._build_intent,
                'doc-extract': self._build_doc_extract,
                'loop': self._build_loop,
                'variable-assign': self._build_variable_assign,
                'application': self._build_application,
                'mcp': self._build_mcp,
            }.get(pn.type)
            if builder is None:
                raise AppApiException(500, f'不支持的节点类型：{pn.type}')
            self.nodes.append(builder(pn, x, y))

        # 6) 构建连线
        self._build_edges()

        # 7) 收尾修复：补全条件节点里"空"的判断条件，避免出现需要用户手填的空值
        self._repair_conditions()

        # 8) 连通性修复：给悬空的非结束节点（如 search-knowledge）补合法收尾节点
        self._repair_terminal_nodes()

        # 9) 引用可达性修复：把引用了非上游节点的悬空引用兜底掉（否则前端选择器解析不出 -> 漏值）
        self._repair_references()

        return {'nodes': self.nodes, 'edges': self.edges}

    # ---- 布局 ----
    def _compute_levels(self) -> Dict[str, int]:
        """从开始节点出发做 BFS，给每个计划节点分配层级（列）"""
        adj: Dict[str, List[str]] = {pn.key: [] for pn in self.plan.nodes}
        indeg: Dict[str, int] = {pn.key: 0 for pn in self.plan.nodes}
        for e in self.plan.edges:
            if e.source in adj and e.target in indeg:
                adj[e.source].append(e.target)
                indeg[e.target] += 1
        for pn in self.plan.nodes:
            # 条件 / 意图节点的去向写在各自的分支里
            branch_targets = []
            if pn.type == 'condition' and pn.branches:
                branch_targets = [b.target for b in pn.branches]
            elif pn.type == 'intent' and pn.intents:
                branch_targets = [it.target for it in pn.intents]
            for target in branch_targets:
                if target and target in indeg:
                    adj[pn.key].append(target)
                    indeg[target] += 1
        # 入度为 0 的作为第 1 列
        levels: Dict[str, int] = {}
        queue = [k for k, d in indeg.items() if d == 0]
        for k in queue:
            levels[k] = 1
        head = 0
        while head < len(queue):
            cur = queue[head]
            head += 1
            for nxt in adj[cur]:
                lv = levels[cur] + 1
                if nxt not in levels or lv > levels[nxt]:
                    levels[nxt] = lv
                    queue.append(nxt)
        for pn in self.plan.nodes:
            levels.setdefault(pn.key, 1)
        return levels

    def _compute_in_degree(self) -> Dict[str, int]:
        """计算每个节点的入边数量（包括普通边和分支边）"""
        in_degree: Dict[str, int] = {pn.key: 0 for pn in self.plan.nodes}
        
        # 普通边
        for e in self.plan.edges:
            if e.target in in_degree:
                in_degree[e.target] += 1
        
        # 分支边（条件/意图节点的分支目标）
        for pn in self.plan.nodes:
            branch_targets = []
            if pn.type == 'condition' and pn.branches:
                branch_targets = [b.target for b in pn.branches]
            elif pn.type == 'intent' and pn.intents:
                branch_targets = [it.target for it in pn.intents]
            for target in branch_targets:
                if target and target in in_degree:
                    in_degree[target] += 1
        
        return in_degree

    def _position(self, key: str, levels: Dict[str, int]) -> Tuple[int, int]:
        level = levels.get(key, 1)
        # 同列里第几个
        same = [k for k, lv in levels.items() if lv == level]
        same.sort()
        idx = same.index(key)
        x = X_START + level * X_GAP
        y = Y_START + idx * Y_GAP
        return x, y

    # ---- 开始 / 基本信息 ----
    def _append_base_and_start(self):
        base_node_data = {
            'name': self.plan.app_name or '智能体',
            'desc': self.plan.app_desc or '',
            'prologue': self.plan.prologue or '您好，有什么可以帮您？',
            'tts_type': 'BROWSER',
        }
        # 含文档提取节点时，自动开启文件上传（否则用户没法上传文档/合同，doc-extract 取不到内容）
        if self.needs_file_upload:
            base_node_data['file_upload_enable'] = True
            base_node_data['file_upload_setting'] = {
                'maxFiles': 3, 'fileLimit': 50,
                'document': True, 'image': False, 'audio': False, 'video': False, 'other': False,
            }
        self.nodes.append({
            'id': 'base-node', 'type': 'base-node', 'x': X_START, 'y': Y_START,
            'properties': {
                'height': 728.375, 'stepName': '基本信息', 'showNode': True,
                'input_field_list': [], 'api_input_field_list': [], 'user_input_field_list': [],
                'user_input_config': {'title': '用户输入'},
                'config': {},
                'node_data': base_node_data,
            },
        })
        start_fields = [{'label': '用户问题', 'value': 'question'}]
        if self.needs_file_upload:
            start_fields.append({'label': '文档', 'value': 'document'})
        self.nodes.append({
            'id': 'start-node', 'type': 'start-node', 'x': X_START, 'y': Y_START + 700,
            'properties': {
                'height': 364, 'stepName': '开始', 'showNode': True,
                'config': {
                    'fields': start_fields,
                    'globalFields': [
                        {'label': '当前时间', 'value': 'time'},
                        {'label': '历史聊天记录', 'value': 'history_context'},
                        {'label': '对话 ID', 'value': 'chat_id'},
                    ],
                },
                'fields': start_fields,
                'globalFields': [{'label': '当前时间', 'value': 'time'}],
            },
        })

    # ---- 各类型业务节点 ----
    def _build_ai_chat(self, pn: PlanNode, x: int, y: int) -> Dict:
        model = self.resources.resolve_model(pn.model)
        
        # 解析工具配置
        tools = self.resources.resolve_tools(pn.tools)
        tool_ids = [t['id'] for t in tools]
        
        # 解析应用配置
        applications = self.resources.resolve_applications(pn.applications)
        application_ids = [a['id'] for a in applications]
        
        node_data = {
            'prompt': pn.prompt or '{{开始.question}}',
            'system': pn.system or '',
            'model_id': model['id'] if model else '',
            'model_id_type': 'custom',
            'dialogue_type': 'WORKFLOW',
            'dialogue_number': 1,
            'is_result': True,
            'model_setting': {
                'reasoning_content_enable': False,
                'reasoning_content_start': '<think>',
                'reasoning_content_end': '</think>',
            },
            'model_params_setting': {},
        }
        
        # 添加工具配置
        if tool_ids:
            node_data['tool_ids'] = tool_ids
        if application_ids:
            node_data['application_ids'] = application_ids
        
        return {
            'id': self.key_to_id[pn.key], 'type': 'ai-chat-node', 'x': x, 'y': y,
            'properties': {
                'height': 993.383, 'showNode': True, 'stepName': pn.title, 'condition': pn.condition,
                'config': {'fields': [
                    {'label': 'AI 回答内容', 'value': 'answer'},
                    {'label': '思考过程', 'value': 'reasoning_content'},
                    {'label': '历史聊天记录', 'value': 'history_message'},
                ]},
                'node_data': node_data,
            },
        }

    def _build_search_knowledge(self, pn: PlanNode, x: int, y: int) -> Dict:
        kbs = self.resources.resolve_knowledge(pn.knowledge)
        # 自动修复：知识库没匹配上但工作空间有知识库时，兜底选第一个，避免检索节点留空导致不可用
        if not kbs and self.resources.knowledge:
            kbs = [self.resources.knowledge[0]]
            maxkb_logger.warning(
                f"生成工作流-知识库节点[{pn.title}]未匹配到 {pn.knowledge}，已兜底使用「{kbs[0]['name']}」")
        id_list = [k['id'] for k in kbs]
        return {
            'id': self.key_to_id[pn.key], 'type': 'search-knowledge-node', 'x': x, 'y': y,
            'properties': {
                'height': 794, 'showNode': True, 'stepName': pn.title, 'condition': pn.condition,
                'config': {'fields': [
                    {'label': '检索结果的分段列表', 'value': 'paragraph_list'},
                    {'label': '满足直接回答的分段列表', 'value': 'is_hit_handling_method_list'},
                    {'label': '检索结果', 'value': 'data'},
                    {'label': '满足直接回答的分段内容', 'value': 'directly_return'},
                ]},
                'node_data': {
                    'knowledge_id_list': id_list,
                    'all_knowledge_id_list': id_list,
                    'knowledge_list': [{'id': k['id'], 'name': k['name']} for k in kbs],
                    'knowledge_setting': {
                        'top_n': 3, 'similarity': 0.6,
                        'search_mode': 'embedding', 'max_paragraph_char_number': 5000,
                    },
                    'question_reference_address': ['start-node', 'question'],
                    'show_knowledge': False,
                    'search_scope_type': 'custom',
                    'search_scope_source': 'knowledge',
                    'search_scope_reference': [],
                },
            },
        }

    def _build_reply(self, pn: PlanNode, x: int, y: int) -> Dict:
        ref = self._resolve_ref(pn.reference)
        if ref and len(ref) >= 2:
            node_data = {'reply_type': 'referencing', 'fields': ref, 'content': '', 'is_result': True}
        else:
            node_data = {'reply_type': 'content', 'content': pn.content or '', 'fields': [], 'is_result': True}
        return {
            'id': self.key_to_id[pn.key], 'type': 'reply-node', 'x': x, 'y': y,
            'properties': {
                'height': 386, 'showNode': True, 'stepName': pn.title, 'condition': pn.condition,
                'config': {'fields': [{'label': '内容', 'value': 'answer'}]},
                'node_data': node_data,
            },
        }

    def _build_tool(self, pn: PlanNode, x: int, y: int) -> Dict:
        tool = self.resources.resolve_tool(pn.tool)
        
        # 如果工具不存在，尝试从工具商店查找并安装
        if tool is None:
            store_tool = self.resources.resolve_store_tool(pn.tool)
            if store_tool:
                # 自动安装工具商店中的工具
                tool = self._install_store_tool(store_tool)
            if tool is None:
                raise AppApiException(500, f"工具不存在或无权限：{pn.tool}")
        
        # 按工具真实入参定义生成 input_field_list，缺省引用用户问题，保证可运行
        params = pn.tool_params or {}
        input_field_list = []
        for field in tool.get('input_field_list', []):
            name = field.get('name')
            if not name:
                continue
            input_field_list.append({'name': name, 'value': params.get(name, '{{开始.question}}')})
        return {
            'id': self.key_to_id[pn.key], 'type': 'tool-lib-node', 'x': x, 'y': y,
            'properties': {
                'height': 260, 'showNode': True, 'stepName': pn.title, 'condition': pn.condition,
                'config': {'fields': [{'label': '结果', 'value': 'result'}]},
                'node_data': {
                    'tool_lib_id': tool['id'],
                    'input_field_list': input_field_list,
                    'is_result': True,
                },
            },
        }

    def _install_store_tool(self, store_tool: Dict) -> Optional[Dict]:
        """从工具商店安装工具"""
        try:
            from tools.serializers.tool import ToolSerializer
            result = ToolSerializer.AddStoreTool(
                data={
                    'user_id': self.plan.user_id if hasattr(self.plan, 'user_id') else None,
                    'workspace_id': self.plan.workspace_id if hasattr(self.plan, 'workspace_id') else None,
                    'tool_id': store_tool.get('id', ''),
                }
            ).add({
                'name': store_tool['name'],
                'download_url': store_tool.get('download_url', ''),
                'versions': store_tool.get('versions', []),
                'icon': store_tool.get('icon', ''),
            })
            if result:
                return {
                    'id': str(result.id),
                    'name': result.name,
                    'desc': result.desc,
                    'input_field_list': result.input_field_list or [],
                }
        except Exception as e:
            maxkb_logger.error(f'生成工作流-安装工具商店工具失败: {e}')
        return None

    def _build_doc_extract(self, pn: PlanNode, x: int, y: int) -> Dict:
        """文档内容提取：从用户上传的文档中提取正文，供后续 AI 分析（如合同审核）"""
        return {
            'id': self.key_to_id[pn.key], 'type': 'document-extract-node', 'x': x, 'y': y,
            'properties': {
                'height': 252, 'showNode': True, 'stepName': pn.title, 'condition': pn.condition,
                'config': {'fields': [
                    {'label': '文档内容', 'value': 'content'},
                    {'label': '文档列表', 'value': 'document_list'},
                ]},
                'node_data': {'document_list': ['start-node', 'document']},
            },
        }

    def _build_condition(self, pn: PlanNode, x: int, y: int) -> Dict:
        branch_list = []
        branch_condition_list = []
        branches = pn.branches or []
        
        # 自动为条件节点添加默认条件（如果大模型没有生成）
        # 找到上游节点，作为默认的判断依据
        upstream_node = self._find_upstream_node(pn.key)
        default_ref = f'{upstream_node}.answer' if upstream_node else '开始.question'
        
        for i, b in enumerate(branches):
            branch_id = self._short_branch_id()
            # 分支类型：第一个 IF，最后一个无条件的为 ELSE，其余 ELSE IF n
            if i == 0:
                btype = 'IF'
            elif not b.conditions:
                btype = 'ELSE'
            else:
                btype = f'ELSE IF {i}'
            conditions = []
            
            # 如果大模型生成了条件，使用它
            if b.conditions:
                for c in b.conditions:
                    field = self._resolve_ref(c.ref)
                    if not field:
                        continue
                    compare = c.compare if c.compare in COMPARE_OPERATORS else 'is_not_null'
                    conditions.append({'field': field, 'compare': compare, 'value': c.value or '1'})
            # 否则，为 IF/ELSE IF 分支自动添加默认条件
            elif btype != 'ELSE':
                # 自动添加默认条件：判断上游节点的输出是否非空
                ref_field = self._resolve_ref(default_ref)
                if ref_field:
                    conditions.append({'field': ref_field, 'compare': 'is_not_null', 'value': '1'})
                else:
                    # 如果无法解析上游节点，使用开始节点的问题字段
                    conditions.append({'field': ['start-node', 'question'], 'compare': 'is_not_null', 'value': '1'})
            
            branch_list.append({
                'id': branch_id,
                'type': btype,
                'condition': b.logic if b.logic in ('and', 'or') else 'and',
                'conditions': conditions,
            })
            branch_condition_list.append({'index': i, 'height': 121.383, 'id': branch_id})
            # 记录分支 id 与去向，建分支边时用
            self.branch_edges.setdefault(pn.key, []).append((branch_id, b.target))
        return {
            'id': self.key_to_id[pn.key], 'type': 'condition-node', 'x': x, 'y': y,
            'properties': {
                'width': 600, 'height': 544.148, 'showNode': True, 'stepName': pn.title, 'condition': pn.condition,
                'config': {'fields': [{'label': '分支名称', 'value': 'branch_name'}]},
                'node_data': {'branch': branch_list},
                'branch_condition_list': branch_condition_list,
            },
        }

    def _build_question(self, pn: PlanNode, x: int, y: int) -> Dict:
        """问题优化节点：结合上下文改写用户问题，提升后续检索准确率"""
        model = self.resources.resolve_model(pn.model)
        return {
            'id': self.key_to_id[pn.key], 'type': 'question-node', 'x': x, 'y': y,
            'properties': {
                'height': 345, 'showNode': True, 'stepName': pn.title, 'condition': pn.condition,
                'config': {'fields': [{'label': '问题优化结果', 'value': 'answer'}]},
                'node_data': {
                    'prompt': pn.prompt or '请结合历史对话，将用户问题补全为完整、独立的问题：\n{{开始.question}}',
                    'system': pn.system or '你是一个问题改写助手，只输出改写后的问题本身。',
                    'model_id': model['id'] if model else '',
                    'model_id_type': 'custom',
                    'dialogue_number': 1,
                    'is_result': False,
                    'model_params_setting': {},
                },
            },
        }

    def _build_intent(self, pn: PlanNode, x: int, y: int) -> Dict:
        """意图识别节点：按意图把流程分到不同分支（多级步骤路由）"""
        model = self.resources.resolve_model(pn.model)
        content_list = self._resolve_ref(pn.input) or ['start-node', 'question']
        intents = pn.intents or []
        # 确保存在兜底「其他」分支
        if not any(it.is_other for it in intents):
            intents = intents + [PlanIntent(intent='其他', target=None, is_other=True)]
        branch_list = []
        branch_condition_list = []
        for i, it in enumerate(intents):
            branch_id = self._short_branch_id()
            branch_list.append({
                'id': branch_id,
                'content': it.intent or ('其他' if it.is_other else f'意图{i + 1}'),
                'isOther': bool(it.is_other),
            })
            branch_condition_list.append({'index': i, 'height': 12, 'id': branch_id})
            self.branch_edges.setdefault(pn.key, []).append((branch_id, it.target))
        return {
            'id': self.key_to_id[pn.key], 'type': 'intent-node', 'x': x, 'y': y,
            'properties': {
                'width': 430, 'height': 260, 'showNode': True, 'stepName': pn.title, 'condition': pn.condition,
                'config': {'fields': [
                    {'label': '分类', 'value': 'category'},
                    {'label': '理由', 'value': 'reason'},
                ]},
                'node_data': {
                    'model_id': model['id'] if model else '',
                    'model_id_type': 'custom',
                    'model_id_reference': [],
                    'content_list': content_list,
                    'dialogue_number': 1,
                    'model_params_setting': {},
                    'branch': branch_list,
                },
                'branch_condition_list': branch_condition_list,
            },
        }

    def _find_upstream_node(self, node_key: str) -> Optional[str]:
        """找到指定节点的上游节点标题"""
        # 查找指向该节点的边
        for e in self.plan.edges:
            if e.target == node_key:
                # 找到上游节点，返回其标题
                for pn in self.plan.nodes:
                    if pn.key == e.source:
                        return pn.title
        # 如果没有找到，尝试从分支中查找
        for pn in self.plan.nodes:
            if pn.type in ('condition', 'intent'):
                for b in (pn.branches or []):
                    if b.target == node_key:
                        return pn.title
                for it in (pn.intents or []):
                    if it.target == node_key:
                        return pn.title
        return None

    def _build_loop(self, pn: PlanNode, x: int, y: int) -> Dict:
        """循环节点：对列表数据循环处理或指定次数循环"""
        loop_type = pn.loop_type or 'ARRAY'
        array_ref = self._resolve_ref(pn.loop_source) if pn.loop_source else []
        
        # 循环体内的节点（简化处理：记录循环体节点的 key 列表）
        loop_body_keys = pn.loop_body or []
        
        return {
            'id': self.key_to_id[pn.key], 'type': 'loop-node', 'x': x, 'y': y,
            'properties': {
                'height': 252, 'showNode': True, 'stepName': pn.title, 'condition': pn.condition,
                'config': {'fields': [
                    {'label': '当前索引', 'value': 'index'},
                    {'label': '当前项', 'value': 'item'},
                ]},
                'node_data': {
                    'loop_type': loop_type,
                    'array': array_ref if loop_type == 'ARRAY' else [],
                    'number': pn.loop_count if loop_type == 'NUMBER' else 1,
                    'loop_body': {},  # 循环体由前端编辑器管理
                },
            },
        }

    def _build_variable_assign(self, pn: PlanNode, x: int, y: int) -> Dict:
        """变量赋值节点：在流程中存储和传递中间结果"""
        variable_list = []
        for name, value in (pn.variables or {}).items():
            ref = self._resolve_ref(value)
            if ref:
                variable_list.append({'name': name, 'value': ref, 'type': 'reference'})
            else:
                variable_list.append({'name': name, 'value': value, 'type': 'custom'})
        
        return {
            'id': self.key_to_id[pn.key], 'type': 'variable-assign-node', 'x': x, 'y': y,
            'properties': {
                'height': 252, 'showNode': True, 'stepName': pn.title, 'condition': pn.condition,
                'config': {},
                'node_data': {
                    'variable_list': variable_list,
                },
            },
        }

    def _build_application(self, pn: PlanNode, x: int, y: int) -> Dict:
        """应用节点：调用其他应用"""
        app = self.resources.resolve_application(pn.application)
        if app is None:
            raise AppApiException(500, f"应用不存在或无权限：{pn.application}")
        
        return {
            'id': self.key_to_id[pn.key], 'type': 'application-node', 'x': x, 'y': y,
            'properties': {
                'height': 260, 'showNode': True, 'stepName': pn.title, 'condition': pn.condition,
                'config': {'fields': [{'label': '结果', 'value': 'result'}]},
                'node_data': {
                    'application_id': app['id'],
                    'is_result': True,
                },
            },
        }

    def _build_mcp(self, pn: PlanNode, x: int, y: int) -> Dict:
        """MCP 工具节点：调用 MCP 服务器提供的工具"""
        return {
            'id': self.key_to_id[pn.key], 'type': 'mcp-node', 'x': x, 'y': y,
            'properties': {
                'height': 252, 'showNode': True, 'stepName': pn.title, 'condition': pn.condition,
                'config': {'fields': [{'label': '结果', 'value': 'result'}]},
                'node_data': {
                    'mcp_server_id': pn.mcp_server or '',
                    'tool_name': pn.mcp_tool_name or '',
                    'is_result': True,
                },
            },
        }

    @staticmethod
    def _short_branch_id() -> str:
        return str(uuid.uuid4().int % 9000 + 1000)

    # ---- 连线 ----
    def _add_edge(self, source_id: str, target_id: str, source_anchor: str, target_anchor: str):
        self.edges.append({
            'id': f'edge-{_short_id()}',
            'type': 'app-edge',
            'sourceNodeId': source_id,
            'targetNodeId': target_id,
            'sourceAnchorId': source_anchor,
            'targetAnchorId': target_anchor,
            'properties': {},
        })

    def _build_edges(self):
        # 普通边
        for e in self.plan.edges:
            src = self.key_to_id.get(e.source)
            tgt = self.key_to_id.get(e.target)
            if src and tgt:
                self._add_edge(src, tgt, f'{src}_right', f'{tgt}_left')
        # 分支边（条件 / 意图，锚点格式一致：{nodeId}_{branchId}_right）
        for node_key, branches in self.branch_edges.items():
            node_id = self.key_to_id[node_key]
            for branch_id, target_key in branches:
                tgt = self.key_to_id.get(target_key) if target_key else None
                if branch_id and tgt:
                    self._add_edge(node_id, tgt, f'{node_id}_{branch_id}_right', f'{tgt}_left')

        self._connect_start_node()

    # 各节点类型的"主输出字段"，用于自动兜底条件判断
    PRIMARY_OUTPUT = {
        'search-knowledge-node': 'paragraph_list',
        'ai-chat-node': 'answer',
        'question-node': 'answer',
        'tool-lib-node': 'result',
        'document-extract-node': 'content',
        'intent-node': 'category',
        'reply-node': 'answer',
    }

    def _repair_conditions(self):
        """
        收尾校验/修复：条件节点的非 ELSE 分支必须有有效判断条件（模型常把 ref 写错导致解析失败、
        留下"请选择变量"的空条件）。这里向上回溯找最近能提供输出的上游节点兜底一个 is_not_null，
        实在找不到就退到 开始.question 不为空——**确保任何分支都不会留空值，无需用户手填**。
        """
        from collections import deque
        preds: Dict[str, List[str]] = {}
        for e in self.edges:
            preds.setdefault(e['targetNodeId'], []).append(e['sourceNodeId'])
        node_by_id = {n['id']: n for n in self.nodes}

        def find_upstream_field(cond_id: str) -> List[str]:
            # 向上 BFS：优先知识库检索（命中判断最常见来源），否则取最近的有意义输出
            visited = set()
            queue = deque(preds.get(cond_id, []))
            best = None
            while queue:
                nid = queue.popleft()
                if nid in visited or nid == 'start-node':
                    continue
                visited.add(nid)
                n = node_by_id.get(nid)
                if n:
                    if n['type'] == 'search-knowledge-node':
                        return [nid, 'paragraph_list']
                    field = self.PRIMARY_OUTPUT.get(n['type'])
                    if field and best is None:
                        best = [nid, field]
                queue.extend(preds.get(nid, []))
            return best or ['start-node', 'question']

        for node in self.nodes:
            if node['type'] != 'condition-node':
                continue
            fallback_field = find_upstream_field(node['id'])
            for branch in node['properties']['node_data'].get('branch', []):
                if branch.get('type') == 'ELSE':
                    continue
                valid = [c for c in branch.get('conditions', []) if c.get('field')]
                if valid:
                    branch['conditions'] = valid
                else:
                    branch['conditions'] = [
                        {'field': fallback_field, 'compare': 'is_not_null', 'value': '1'}
                    ]
                    maxkb_logger.warning(
                        f"生成工作流-条件节点[{node['properties'].get('stepName')}]存在空判断，"
                        f"已自动兜底为 {fallback_field[0]}.{fallback_field[1]} 不为空")

    def _repair_terminal_nodes(self):
        """
        连通性铁律（见 flow/common.py end_nodes）：只有部分类型可作"结束节点"，其余类型（如
        search-knowledge / question / doc-extract 等）**没有出边就非法**——检索完/处理完必须有下游消费。
        这里给每个这样的悬空节点自动补一个合法收尾节点：search-knowledge 补一个基于检索结果作答的
        ai-chat；其余补一个引用其主输出的 reply。保证每条分支都以合法结束节点收口，
        不再报"XX 节点不能当做结束节点"。
        """
        from application.flow.common import end_nodes

        out_deg: Dict[str, int] = {}
        for e in self.edges:
            out_deg[e['sourceNodeId']] = out_deg.get(e['sourceNodeId'], 0) + 1

        # condition/intent 出边走分支锚点、另有连通性逻辑，这里不处理
        skip_types = {'condition-node', 'intent-node'}
        used_titles = {n['properties'].get('stepName') for n in self.nodes if n.get('properties')}

        fixed = 0
        for node in list(self.nodes):
            nid, ntype = node['id'], node['type']
            if (nid in ('start-node', 'base-node') or ntype in end_nodes
                    or ntype in skip_types or out_deg.get(nid, 0) > 0):
                continue
            # 悬空的非结束节点 -> 补收尾节点
            orig_title = node['properties'].get('stepName') or ntype
            new_id = _new_id()
            new_key = f'_auto_{new_id[:8]}'
            self.key_to_id[new_key] = new_id
            x = node.get('x', X_START) + X_GAP
            y = node.get('y', Y_START)

            if ntype == 'search-knowledge-node':
                title = self._unique_title(f'{orig_title}回答', used_titles)
                pn = PlanNode(
                    key=new_key, type='ai-chat', title=title,
                    system='你是专业的问答助手，只依据已知信息回答。',
                    prompt=f'已知信息：\n{{{{{orig_title}.data}}}}\n请根据以上信息回答用户问题：\n{{{{开始.question}}}}',
                )
                pn.condition = 'AND'
                self.title_to_id.setdefault(title, new_id)
                self.id_to_title[new_id] = title
                self.nodes.append(self._build_ai_chat(pn, x, y))
            else:
                fields = node.get('properties', {}).get('config', {}).get('fields') or []
                field = self.PRIMARY_OUTPUT.get(ntype) or (fields[0]['value'] if fields else None)
                title = self._unique_title(f'{orig_title}结果', used_titles)
                pn = PlanNode(key=new_key, type='reply', title=title)
                pn.condition = 'AND'
                if field:
                    pn.reference = f'{orig_title}.{field}'
                else:
                    pn.content = '{{开始.question}}'
                self.title_to_id.setdefault(title, new_id)
                self.id_to_title[new_id] = title
                self.nodes.append(self._build_reply(pn, x, y))

            self._add_edge(nid, new_id, f'{nid}_right', f'{new_id}_left')
            out_deg[nid] = 1
            fixed += 1

        if fixed:
            maxkb_logger.warning(f'生成工作流-补结束节点：为 {fixed} 个悬空的非结束节点自动补了收尾节点')

    def _repair_references(self):
        """
        结构不变量：节点里引用的每个变量，其来源节点必须是该节点沿 edges 可达的**上游**。
        前端选择器 get_up_node_field_dict 是靠入边递归取上游的——引用一个非上游节点，选择器里
        根本没有它、值解析不出来，就成了肉眼可见的"漏值节点"。这里把所有悬空引用兜底掉：
          - 文本 {{标题.字段}}：换成最近上游节点的主输出，实在没有就退到 {{开始.question}}；
          - 结构化 [node_id, 字段]（reply/condition/intent/loop/variable-assign）：同理换成
            最近上游主输出，否则退到 [start-node, question]。
        由此硬保证"填进去的值一定能被选择器解析"，不会再生成漏值节点。
        """
        from collections import deque

        preds: Dict[str, List[str]] = {}
        for e in self.edges:
            preds.setdefault(e['targetNodeId'], []).append(e['sourceNodeId'])

        # 始终可用的来源：开始 / 基本信息 /（若存在）知识库节点。全局变量 global、chat 另行放行。
        always_ok = {'start-node', 'base-node'}
        if any(n['id'] == 'knowledge-base-node' for n in self.nodes):
            always_ok.add('knowledge-base-node')

        node_by_id = {n['id']: n for n in self.nodes}

        # 每个节点"可被引用的输出字段"集合（= 前端选择器里该节点能选到的字段），
        # 用于校验引用不仅节点可达、字段也必须真实存在（否则选择器解析不出 -> "引用变量必填"）。
        node_fields: Dict[str, set] = {}
        for n in self.nodes:
            cfg = n.get('properties', {}).get('config', {}) or {}
            fset: set = set()
            for f in (cfg.get('fields') or []):
                if f.get('value'):
                    fset.add(f['value'])
            for f in (cfg.get('globalFields') or []):
                if f.get('value'):
                    fset.add(f['value'])
            node_fields[n['id']] = fset

        _upstream_cache: Dict[str, set] = {}

        def upstream_ids(node_id: str) -> set:
            if node_id not in _upstream_cache:
                seen: set = set()
                queue = deque(preds.get(node_id, []))
                while queue:
                    nid = queue.popleft()
                    if nid in seen:
                        continue
                    seen.add(nid)
                    queue.extend(preds.get(nid, []))
                _upstream_cache[node_id] = seen
            return _upstream_cache[node_id]

        def nearest_output(node_id: str) -> Optional[List[str]]:
            """向上 BFS 找最近的、有主输出字段的上游节点 -> [id, field]"""
            seen: set = set()
            queue = deque(preds.get(node_id, []))
            while queue:
                nid = queue.popleft()
                if nid in seen or nid == 'start-node':
                    continue
                seen.add(nid)
                n = node_by_id.get(nid)
                if n:
                    field = self.PRIMARY_OUTPUT.get(n['type'])
                    if field:
                        return [nid, field]
                queue.extend(preds.get(nid, []))
            return None

        def ref_ok(node_id: str, src_id: Optional[str]) -> bool:
            return bool(src_id) and (src_id in always_ok or src_id in upstream_ids(node_id))

        # global/chat 是全局变量，字段不在节点里枚举，放行不校验字段。
        # 某些节点(如 variable-assign)输出字段是动态的、config.fields 为空——这类"字段未知"的节点
        # 不强校验字段（只要节点可达即可），避免把合法引用误伤替换。
        def field_ok(src_id: str, field: str) -> bool:
            if src_id in ('global', 'chat'):
                return True
            known = node_fields.get(src_id)
            if not known:
                return True
            return bool(field) and field in known

        def valid_ref(node_id: str, src_id: Optional[str], field: str) -> bool:
            return bool(src_id) and (src_id in ('global', 'chat')
                                     or (ref_ok(node_id, src_id) and field_ok(src_id, field)))

        stats = {'n': 0}

        def fix_text(node_id: str, text: Optional[str]) -> Optional[str]:
            if not text or '{{' not in text:
                return text

            def _sub(m):
                parts = m.group(1).split('.', 1)
                title = parts[0].strip()
                field = parts[1].strip() if len(parts) > 1 else ''
                # 标题 -> 节点 id（开始/基本信息为保留标题；global/chat 走 valid_ref 放行）
                src_id = ('start-node' if title == '开始'
                          else 'base-node' if title == '基本信息'
                          else title if title in ('global', 'chat')
                          else self.title_to_id.get(title))
                if valid_ref(node_id, src_id, field):
                    return m.group(0)
                stats['n'] += 1
                out = nearest_output(node_id)
                if out:
                    return '{{%s.%s}}' % (self.id_to_title.get(out[0], '开始'), out[1])
                return '{{开始.question}}'

            return re.sub(r'\{\{([^}]+)\}\}', _sub, text)

        def fix_struct(node_id: str, ref: Optional[list]) -> Optional[list]:
            if not ref or len(ref) < 2:
                return ref
            if valid_ref(node_id, ref[0], ref[1]):
                return ref
            stats['n'] += 1
            return nearest_output(node_id) or ['start-node', 'question']

        for node in self.nodes:
            nid = node['id']
            nd = node.get('properties', {}).get('node_data', {})
            ntype = node['type']
            if ntype in ('ai-chat-node', 'question-node'):
                nd['prompt'] = fix_text(nid, nd.get('prompt'))
                nd['system'] = fix_text(nid, nd.get('system'))
            elif ntype == 'reply-node':
                if nd.get('reply_type') == 'referencing':
                    fixed = fix_struct(nid, nd.get('fields'))
                    # 引用型回复的 fields 若被兜底成 start.question 也算有效；仍为空则退回内容型
                    if fixed and len(fixed) >= 2:
                        nd['fields'] = fixed
                    else:
                        nd['reply_type'] = 'content'
                        nd['fields'] = []
                        nd['content'] = nd.get('content') or '{{开始.question}}'
                else:
                    nd['content'] = fix_text(nid, nd.get('content'))
                    if not str(nd.get('content') or '').strip():
                        # 内容型回复不能留空，兜底引用最近上游输出
                        out = nearest_output(nid)
                        nd['content'] = ('{{%s.%s}}' % (self.id_to_title.get(out[0], '开始'), out[1])
                                         if out else '{{开始.question}}')
            elif ntype == 'condition-node':
                for branch in nd.get('branch', []):
                    for c in branch.get('conditions', []):
                        c['field'] = fix_struct(nid, c.get('field'))
            elif ntype == 'intent-node':
                nd['content_list'] = fix_struct(nid, nd.get('content_list'))
            elif ntype == 'loop-node':
                if nd.get('loop_type') == 'ARRAY' and nd.get('array'):
                    nd['array'] = fix_struct(nid, nd.get('array'))
            elif ntype == 'variable-assign-node':
                for v in nd.get('variable_list', []):
                    if v.get('type') == 'reference':
                        v['value'] = fix_struct(nid, v.get('value'))

        if stats['n']:
            maxkb_logger.warning(f'生成工作流-引用可达性修复：兜底了 {stats["n"]} 处悬空引用')

    def _connect_start_node(self):
        # 开始节点必须连到流程入口：模型计划不含开始节点，其 edges 从第一个业务节点开始，
        # 这里把所有"没有任何入边、也不是分支目标"的根节点连到 start-node。
        targets = {e.target for e in self.plan.edges}
        for branches in self.branch_edges.values():
            for _branch_id, target_key in branches:
                if target_key:
                    targets.add(target_key)
        for pn in self.plan.nodes:
            if pn.key not in targets:
                entry_id = self.key_to_id.get(pn.key)
                if entry_id:
                    self._add_edge('start-node', entry_id, 'start-node_right', f'{entry_id}_left')


# ============================================================
# 真实运行期 serializer 校验 —— 硬保证"生成完即可用"
# ============================================================

def validate_nodes(nodes: List[Dict]) -> List[str]:
    """用每个节点真实的参数 serializer 校验 node_data，返回错误列表"""
    from application.flow.step_node.ai_chat_step_node.i_chat_node import ChatNodeSerializer
    from application.flow.step_node.search_knowledge_node.i_search_knowledge_node import SearchDatasetStepNodeSerializer
    from application.flow.step_node.direct_reply_node.i_reply_node import ReplyNodeParamsSerializer
    from application.flow.step_node.condition_node.i_condition_node import ConditionNodeParamsSerializer
    from application.flow.step_node.tool_lib_node.i_tool_lib_node import FunctionLibNodeParamsSerializer
    from application.flow.step_node.question_node.i_question_node import QuestionNodeSerializer
    from application.flow.step_node.intent_node.i_intent_node import IntentNodeSerializer
    from application.flow.step_node.document_extract_node.i_document_extract_node import \
        DocumentExtractNodeSerializer
    from application.flow.step_node.loop_node.i_loop_node import ILoopNodeSerializer
    from application.flow.step_node.variable_assign_node.i_variable_assign_node import VariableAssignNodeParamsSerializer

    serializer_map = {
        'ai-chat-node': ChatNodeSerializer,
        'search-knowledge-node': SearchDatasetStepNodeSerializer,
        'reply-node': ReplyNodeParamsSerializer,
        'condition-node': ConditionNodeParamsSerializer,
        'tool-lib-node': FunctionLibNodeParamsSerializer,
        'question-node': QuestionNodeSerializer,
        'intent-node': IntentNodeSerializer,
        'document-extract-node': DocumentExtractNodeSerializer,
        'loop-node': ILoopNodeSerializer,
        'variable-assign-node': VariableAssignNodeParamsSerializer,
    }
    
    errors = []
    for node in nodes:
        serializer_cls = serializer_map.get(node['type'])
        if serializer_cls is None:
            continue
        node_data = node.get('properties', {}).get('node_data', {})
        try:
            serializer_cls(data=node_data).is_valid(raise_exception=True)
        except Exception as e:
            step_name = node.get('properties', {}).get('stepName', node['type'])
            error_msg = f'节点「{step_name}」配置不合法：{e}'
            errors.append(error_msg)
            maxkb_logger.error(f'生成工作流-节点校验失败 [{step_name}]: {e}; node_data={node_data}')
    
    return errors


def _clean_err(e: Exception) -> str:
    """把 DRF ValidationError / AppApiException 的报错提取成干净的一句话"""
    detail = getattr(e, 'detail', None)
    if detail is not None:
        if isinstance(detail, (list, tuple)) and detail:
            return str(detail[0])
        return str(detail)
    return getattr(e, 'message', None) or str(e)


def validate_and_repair(workflow: Dict, workspace_id: str = None, user_id: str = None) -> Tuple[bool, List[str]]:
    """
    结构校验，返回 (是否通过, 错误列表)。两层互补：
      1. validate_nodes —— 用各节点真实参数 serializer 校验 node_data（Workflow.is_valid 实例化节点时不校验参数）。
      2. Workflow.new_instance(...).is_valid() —— 复用 MaxKB 发布应用时的权威校验：连通性（条件每个分支必须连线、
         非末端节点必须有出边）、模型存在且可用、开始/基本信息节点唯一。
    确定性修复（补空模型/知识库、条件兜底、剔除无效工具）已在 WorkflowBuilder 内完成。
    """
    from application.flow.common import Workflow

    errors = validate_nodes(workflow.get('nodes', []))
    if errors:
        return False, errors
    try:
        Workflow.new_instance(workflow).is_valid()
    except Exception as e:
        return False, [_clean_err(e)]
    return True, []


def run_debug_workflow(workflow: Dict, workspace_id: str, user_id: str) -> Tuple[bool, str]:
    """
    用 service 层 debug 真正跑一遍工作流，确认能跑通：
      1. 建临时应用（落库）
      2. OpenChatSerializers.open() 建会话缓存（必须先 open，否则 chat 拿不到 ChatInfo）
      3. DebugChatSerializers.chat() 发一条测试消息，同步执行整条流程
      4. 清理临时应用
    返回 (是否跑通, 错误信息)。注意：会真实调用大模型/嵌入，较慢且依赖环境配置。
    """
    # MaxKB 用 uuid_utils.compat 提供 uuid7（标准库 uuid 没有），这里保持一致
    import uuid_utils.compat as uuid_lib
    from application.models import Application, ApplicationTypeChoices, ChatUserType
    from chat.serializers.chat import OpenChatSerializers, DebugChatSerializers
    from common.handle.impl.response.system_to_response import SystemToResponse

    temp_app_id = None
    try:
        temp_app_id = str(uuid_lib.uuid7())
        Application(
            id=temp_app_id, name=f'_tmp_gen_test_{temp_app_id[:8]}', desc='生成校验临时应用',
            workspace_id=workspace_id, user_id=user_id,
            type=ApplicationTypeChoices.WORK_FLOW, work_flow=workflow,
            prologue='', dialogue_number=1,
        ).save()
        chat_id = OpenChatSerializers(data={
            'workspace_id': workspace_id, 'application_id': temp_app_id,
            'chat_user_id': str(uuid_lib.uuid7()), 'chat_user_type': ChatUserType.ANONYMOUS_USER,
            'debug': True,
        }).open()
        DebugChatSerializers(data={'chat_id': str(chat_id)}).chat(
            {'message': '你好', 're_chat': False, 'stream': False},
            base_to_response=SystemToResponse())
        return True, ''
    except Exception as e:
        msg = str(e)
        if 'Exception:' in msg:
            msg = msg.split('Exception:')[-1].strip()
        maxkb_logger.warning(f'生成工作流-debug 试跑失败: {e}')
        return False, msg
    finally:
        if temp_app_id:
            try:
                QuerySet(Application).filter(id=temp_app_id).delete()
            except Exception:
                pass


# ============================================================
# 对外入口
# ============================================================

def _ev(type_: str, **kwargs) -> Dict:
    """构造一个过程事件（is_end 默认 False）"""
    return {'type': type_, 'is_end': kwargs.pop('is_end', False), **kwargs}


def _regenerate_plan(chat_model, messages: List, feedback: str):
    """重试场景：把反馈追加给大模型，重新生成并解析计划；失败返回 None（不再流式回传 token）"""
    messages.append(HumanMessage(content=feedback))
    try:
        resp = chat_model.invoke(messages)
        accumulated = resp.content if hasattr(resp, 'content') else str(resp)
        return parse_plan(accumulated)
    except Exception as e:
        maxkb_logger.warning(f'生成工作流-重新生成计划失败: {e}')
        return None


def generate_workflow_stream(model_id: str, workspace_id: str, description: str, user_id: str):
    """
    流式生成工作流：依次产出过程事件，便于前端实时展示"Agent 正在干活"。
    事件类型：
    - stage : {message}          阶段提示
    - plan  : {content}          大模型正在书写的计划片段（token 流）
    - done  : {workflow}         最终 {nodes, edges}，is_end=True
    - error : {error}            失败信息，is_end=True
    """
    try:
        yield _ev('stage', message='正在理解需求…')
        model = QuerySet(Model).filter(id=model_id).first()
        if model is None:
            yield _ev('error', error='所选模型不存在', is_end=True)
            return
        # get_model 内部已硬编码 streaming=True；用 .stream() 实时获取 token
        chat_model = get_model(model)

        yield _ev('stage', message='正在分析可用资源…')
        resources = load_workspace_resources(workspace_id, user_id)
        yield _ev('stage', message=(f'可用资源：模型 {len(resources.models)} 个、'
                                     f'知识库 {len(resources.knowledge)} 个、工具 {len(resources.tools)} 个'))

        # ---- 资源匹配 ----
        yield _ev('stage', message='正在匹配最合适的资源…')
        matched = match_resources(description, resources)
        
        # 构建资源匹配结果
        matched_info = {}
        if matched['knowledge']:
            matched_info['knowledge'] = [{'id': k.get('id', ''), 'name': k['name']} for k in matched['knowledge']]
        if matched['tools']:
            matched_info['tools'] = [{'id': t.get('id', ''), 'name': t['name']} for t in matched['tools']]
        if matched['applications']:
            matched_info['applications'] = [{'id': a.get('id', ''), 'name': a['name']} for a in matched['applications']]
        
        if matched_info:
            yield _ev('stage', message='已匹配到推荐资源', matched=matched_info)
        else:
            yield _ev('stage', message='将根据需求从可用资源中自动选择')

        # ---- 规划（流式书写计划）+ 一次修复重试 ----
        messages = build_plan_messages_with_matching(description, resources)
        plan = None
        last_error = None
        for attempt in range(2):
            yield _ev('stage', message=('正在规划编排（大模型思考中）…' if attempt == 0 else '输出有误，正在修正…'))
            accumulated = ''
            try:
                for chunk in chat_model.stream(messages):
                    piece = chunk.content if hasattr(chunk, 'content') else str(chunk)
                    if piece:
                        accumulated += piece
                        yield _ev('plan', content=piece)
            except Exception as e:  # 流式异常则退回一次性调用
                maxkb_logger.warning(f'生成工作流-流式调用失败，退回 invoke: {e}')
                resp = chat_model.invoke(messages)
                accumulated = resp.content if hasattr(resp, 'content') else str(resp)
            try:
                plan = parse_plan(accumulated)
                break
            except (json.JSONDecodeError, ValidationError, ValueError, AppApiException) as e:
                last_error = e
                maxkb_logger.warning(f'生成工作流-计划解析失败(第{attempt + 1}次): {e}')
                messages.append(HumanMessage(
                    content=f"你上一次的输出无法解析或不合法，错误：{e}。请严格按要求只输出合法 JSON，修复后重新输出。"))
        if plan is None:
            yield _ev('error', error=f'未能生成有效的编排计划：{last_error}', is_end=True)
            return

        yield _ev('stage', message=f'规划完成，共 {len(plan.nodes)} 个步骤')
        
        # ---- 构建 + 结构校验循环（确定性修复已在 builder 内，通常 1 轮即过，最多 3 轮）----
        workflow = None
        for build_attempt in range(3):
            yield _ev('stage', message='正在生成节点与连线…')
            try:
                workflow = WorkflowBuilder(plan, resources).build()
            except Exception as e:
                maxkb_logger.warning(f'生成工作流-构建失败(第{build_attempt + 1}次): {e}')
                if build_attempt == 2:
                    yield _ev('error', error=f'生成工作流失败：{e}', is_end=True)
                    return
                yield _ev('stage', message='构建出错，正在修正计划…')
                plan = _regenerate_plan(chat_model, messages,
                                        f"构建工作流时出错：{e}。请修正计划后只输出合法 JSON。") or plan
                continue

            yield _ev('stage', message='正在校验配置…')
            ok, errors = validate_and_repair(workflow)
            if ok:
                yield _ev('stage', message='结构校验通过 ✅')
                break
            maxkb_logger.warning(f'生成工作流-校验失败(第{build_attempt + 1}次): {errors}')
            if build_attempt == 2:
                break  # 用尽重试：serializer 仍不过极少见，带工作流交付让用户微调
            yield _ev('stage', message=f'校验发现 {len(errors)} 个问题，正在修正…')
            feedback = "工作流校验发现以下问题：\n" + "\n".join(f"- {e}" for e in errors[:5]) + \
                       "\n请修正计划后只输出合法 JSON。"
            plan = _regenerate_plan(chat_model, messages, feedback) or plan

        if workflow is None:
            yield _ev('error', error='生成工作流失败', is_end=True)
            return

        # ---- 最后：用 service 层 debug 真跑一遍，确认能跑通 ----
        yield _ev('stage', message='正在调试运行验证（真实跑一遍）…')
        run_ok, run_err = run_debug_workflow(workflow, workspace_id, user_id)
        if run_ok:
            yield _ev('stage', message='调试运行通过 ✅')
        else:
            # 真跑失败：按运行错误让大模型修一次；仍失败则带警告交付——
            # 运行报错多为环境/模型额度问题，不该让整次生成作废。
            yield _ev('stage', message=f'调试运行报错：{run_err[:80]}，尝试修正一次…')
            new_plan = _regenerate_plan(chat_model, messages,
                                        f"工作流实际运行时报错：{run_err}。请据此修正计划后只输出合法 JSON。")
            fixed = None
            if new_plan is not None:
                try:
                    candidate = WorkflowBuilder(new_plan, resources).build()
                    if validate_and_repair(candidate)[0]:
                        fixed = candidate
                except Exception as e:
                    maxkb_logger.warning(f'生成工作流-修正后构建失败: {e}')
            if fixed is not None:
                workflow = fixed
                run_ok2, run_err2 = run_debug_workflow(workflow, workspace_id, user_id)
                yield _ev('stage', message='修正后调试运行通过 ✅' if run_ok2
                          else f'仍未跑通（{run_err2[:60]}），已生成可编辑工作流，请检查后使用')
            else:
                yield _ev('stage', message='已生成可编辑工作流，请检查后使用')

        yield _ev('stage', message='生成完成 ✅')
        yield _ev('done', workflow=workflow, is_end=True)
    except AppApiException as e:
        yield _ev('error', error=e.message, is_end=True)
    except Exception as e:
        maxkb_logger.error(f'生成工作流失败: {e}', exc_info=True)
        yield _ev('error', error=f'生成工作流失败: {e}', is_end=True)


def generate_workflow(model_id: str, workspace_id: str, description: str, user_id: str) -> Dict:
    """非流式入口（供脚本/测试使用）：消费流式生成器，返回最终工作流"""
    workflow = None
    for event in generate_workflow_stream(model_id, workspace_id, description, user_id):
        if event['type'] == 'error':
            raise AppApiException(500, event['error'])
        if event['type'] == 'done':
            workflow = event['workflow']
    if workflow is None:
        raise AppApiException(500, '生成失败')
    return workflow
