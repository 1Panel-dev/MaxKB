# coding=utf-8

import hashlib

from jinja2.sandbox import SandboxedEnvironment

from common.cache.mem_cache import MemCache

# 缓存 reset_prompt 后的模板编译产物（只依赖配置，同一工作流运行期间恒定）
template_cache = MemCache(
    "workflow_template_cache",
    {
        "TIMEOUT": 3600,  # 缓存有效期为 1 小时
        "OPTIONS": {
            "MAX_ENTRIES": 1000,  # 最多缓存 1000 个条目
            "CULL_FREQUENCY": 10,  # 达到上限时，删除约 1/10 的缓存
        },
    },
)


def render_prompt(input_template, context):
    """
    渲染提示词，编译一次后缓存编译产物，之后每轮仅渲染
    @param input_template: reset_prompt 处理后的模板字符串
    @param context:        渲染模板所需的上下文数据
    @return: 渲染后的提示词字符串
    """
    key = f"workflow_template::{hashlib.sha256(input_template.encode('utf-8')).hexdigest()}"
    template = template_cache.get(key)
    if template is None:
        template = SandboxedEnvironment().from_string(input_template)
        template_cache.set(key, template)
    return template.render(context=context)
