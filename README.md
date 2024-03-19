<p align="center"><img src= "https://github.com/1Panel-dev/maxkb/assets/52996290/c0694996-0eed-40d8-b369-322bf2a380bf" alt="MaxKB" width="300" /></p>
<h3 align="center">基于 LLM 大语言模型的知识库问答系统</h3>
<p align="center">
  <a href="https://www.gnu.org/licenses/old-licenses/gpl-3.0"><img src="https://img.shields.io/github/license/1Panel-dev/maxkb?color=%231890FF" alt="License: GPL v3"></a>
  <a href="https://app.codacy.com/gh/1Panel-dev/maxkb?utm_source=github.com&utm_medium=referral&utm_content=1Panel-dev/maxkb&utm_campaign=Badge_Grade_Dashboard"><img src="https://app.codacy.com/project/badge/Grade/da67574fd82b473992781d1386b937ef" alt="Codacy"></a>
  <a href="https://github.com/1Panel-dev/maxkb/releases/latest"><img src="https://img.shields.io/github/v/release/1Panel-dev/maxkb" alt="Latest release"></a>
  <a href="https://github.com/1Panel-dev/maxkb"><img src="https://img.shields.io/github/stars/1Panel-dev/maxkb?color=%231890FF&style=flat-square" alt="Stars"></a>    
</p>
<hr/>

MaxKB 是一款基于 LLM 大语言模型的知识库问答系统。   

- **多模型**：支持对接主流的大模型，包括本地私有大模型（如 Llama 2）、Azure OpenAI 和百度千帆大模型等；
- **开箱即用**：支持直接上传文档、自动爬取在线文档，支持文本自动拆分、向量化，智能问答交互体验好；
- **无缝嵌入**：支持零编码快速嵌入到第三方业务系统。

## 快速开始

```
docker run -d --name=maxkb -p 8000:8000 ghcr.io/1panel-dev/maxkb
```

也可以通过 [1Panel 应用商店](https://apps.fit2cloud.com/1panel) 快速部署 MaxKB + Ollama（Llama 2），30 分钟内即可上线基于本地大模型的知识库问答系统。


## UI 展示

TBD

## 微信交流群

TBD

## 技术栈

-   前端：[Vue.js](https://cn.vuejs.org/)
-   后端：[Django](https://www.djangoproject.com/)
-   Langchain：[Langchain](https://www.langchain.com/)
-   向量数据库：[PostgreSQL](https://www.postgresql.org/)
-   大模型：Azure OpenAI、百度千帆大模型、[Ollama](https://github.com/ollama/ollama)

## License

Copyright (c) 2014-2024 飞致云 FIT2CLOUD, All rights reserved.

Licensed under The GNU General Public License version 3 (GPLv3)  (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

<https://www.gnu.org/licenses/gpl-3.0.html>

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
