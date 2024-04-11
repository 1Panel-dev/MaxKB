<p align="center"><img src= "https://github.com/1Panel-dev/maxkb/assets/52996290/c0694996-0eed-40d8-b369-322bf2a380bf" alt="MaxKB" width="300" /></p>
<h3 align="center">基于 LLM 大语言模型的知识库问答系统</h3>
<p align="center">
  <a href="https://www.gnu.org/licenses/old-licenses/gpl-3.0"><img src="https://img.shields.io/github/license/1Panel-dev/maxkb?color=%231890FF" alt="License: GPL v3"></a>
  <a href="https://app.codacy.com/gh/1Panel-dev/maxkb?utm_source=github.com&utm_medium=referral&utm_content=1Panel-dev/maxkb&utm_campaign=Badge_Grade_Dashboard"><img src="https://app.codacy.com/project/badge/Grade/da67574fd82b473992781d1386b937ef" alt="Codacy"></a>
  <a href="https://github.com/1Panel-dev/maxkb/releases/latest"><img src="https://img.shields.io/github/v/release/1Panel-dev/maxkb" alt="Latest release"></a>
  <a href="https://github.com/1Panel-dev/maxkb"><img src="https://img.shields.io/github/stars/1Panel-dev/maxkb?color=%231890FF&style=flat-square" alt="Stars"></a>    
  <a href="https://hub.docker.com/r/1panel/maxkb"><img src="https://img.shields.io/docker/pulls/1panel/maxkb?label=downloads" alt="Download"></a>  
</p>
<hr/>

MaxKB 是一款基于 LLM 大语言模型的知识库问答系统。MaxKB = Max Knowledge Base，旨在成为企业的最强大脑。

- **开箱即用**：支持直接上传文档、自动爬取在线文档，支持文本自动拆分、向量化，智能问答交互体验好；
- **无缝嵌入**：支持零编码快速嵌入到第三方业务系统；
- **多模型支持**：支持对接主流的大模型，包括本地私有大模型（如 Llama 2）、Azure OpenAI 和百度千帆大模型等。

## 快速开始

```
docker run -d --name=maxkb -p 8080:8080 -v ~/.maxkb:/var/lib/postgresql/data 1panel/maxkb

# 用户名: admin
# 密码: MaxKB@123..
```

你也可以通过 [1Panel 应用商店](https://apps.fit2cloud.com/1panel) 快速部署 MaxKB + Ollama + Llama 2，30 分钟内即可上线基于本地大模型的知识库问答系统，并嵌入到第三方业务系统中。

你也可以在线体验：[DataEase 小助手](https://dataease.io/docs/v2/)，它是基于 MaxKB 搭建的智能问答系统，已经嵌入到 DataEase 产品及在线文档中。

如你有更多问题，可以查看使用手册，或者通过论坛与我们交流。

-   [使用手册](https://github.com/1Panel-dev/MaxKB/wiki/1-%E5%AE%89%E8%A3%85%E9%83%A8%E7%BD%B2)
-   [论坛求助](https://bbs.fit2cloud.com/c/mk/11)
-   [演示视频](https://www.bilibili.com/video/BV1BE421M7YM/)

## UI 展示

<table style="border-collapse: collapse; border: 1px solid black;">
  <tr>
    <td style="padding: 5px;background-color:#fff;"><img src= "https://github.com/1Panel-dev/MaxKB/assets/80892890/2b893a25-ae46-48da-b6a1-61d23015565e" alt="MaxKB Demo1"   /></td>
    <td style="padding: 5px;background-color:#fff;"><img src= "https://github.com/1Panel-dev/MaxKB/assets/80892890/3e50e7ff-cdc4-4a37-b430-d84975f11d4e" alt="MaxKB Demo2"   /></td>
  </tr>
  <tr>
    <td style="padding: 5px;background-color:#fff;"><img src= "https://github.com/1Panel-dev/MaxKB/assets/80892890/dfdcc03f-ef36-4f75-bb82-797c0f9da1ad" alt="MaxKB Demo3"   /></td>
    <td style="padding: 5px;background-color:#fff;"><img src= "https://github.com/1Panel-dev/MaxKB/assets/80892890/884a9db1-3f93-4013-bc8f-a3f0dbcfeb2f" alt="MaxKB Demo4"   /></td>
  </tr>
</table>

## 技术栈

-   前端：[Vue.js](https://cn.vuejs.org/)
-   后端：[Python / Django](https://www.djangoproject.com/)
-   Langchain：[Langchain](https://www.langchain.com/)
-   向量数据库：[PostgreSQL / pgvector](https://www.postgresql.org/)
-   大模型：Azure OpenAI、百度千帆大模型、[Ollama](https://github.com/ollama/ollama)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=1Panel-dev/MaxKB&type=Date)](https://star-history.com/#1Panel-dev/MaxKB&Date)

## License

Copyright (c) 2014-2024 飞致云 FIT2CLOUD, All rights reserved.

Licensed under The GNU General Public License version 3 (GPLv3)  (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

<https://www.gnu.org/licenses/gpl-3.0.html>

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
