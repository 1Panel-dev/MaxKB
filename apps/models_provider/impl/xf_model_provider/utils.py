# coding=utf-8
"""讯飞星火 MaaS OpenAI 兼容接口地址归一化工具。

MaaS 的 OpenAI 兼容接口必须带版本前缀（/v1 或 /v2），否则请求会 404
（No Route matched）；且官方控制台复制出来的完整接口地址末尾会带具体
endpoint（如 .../v2.1/embeddings）。OpenAI 客户端会在 api_base 后再拼一次
endpoint，若不清掉这些后缀，实际会请求 .../v2.1/embeddings/embeddings，
同样 404。这里统一做两件事：
1. 去掉末尾的 endpoint 后缀；
2. 把 MaaS 并不存在的版本段（如控制台复制的 /v2.1）修正为官方默认的 /v2。
"""

import re
from urllib.parse import urlparse

DEFAULT_XUNFEI_API_BASE = "https://maas-api.cn-huabei-1.xf-yun.com/v2"

ENDPOINT_SUFFIXES = ("/embeddings", "/chat/completions", "/completions", "/models")

_VERSION_RE = re.compile(r"^v\d+(\.\d+)?$")


def normalize_xunfei_api_base(api_base: str | None) -> str:
    """对讯飞 MaaS 的 api_base 做归一化，使其指向真正的版本根地址。

    - 裸主机地址补官方默认的 /v2；
    - 已带 /v1 或 /v2 版本段的保持原样；
    - 末尾带 endpoint 后缀的去掉该后缀；
    - 版本段不是 /v1、/v2（例如控制台复制的 /v2.1，实际不存在）时重置为 /v2。
    """
    if not api_base or not api_base.strip():
        return DEFAULT_XUNFEI_API_BASE
    url = api_base.strip().rstrip("/")
    for suffix in ENDPOINT_SUFFIXES:
        if url.endswith(suffix):
            url = url[: -len(suffix)].rstrip("/")
            break
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    if path in ("", "/"):
        return url + "/v2"
    last = path.rsplit("/", 1)[-1]
    if _VERSION_RE.match(last) and last not in ("v1", "v2"):
        prefix = path[: path.rfind("/") + 1] if "/" in path else "/"
        return parsed._replace(path=prefix + "v2").geturl()
    return url
