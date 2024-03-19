<p align="center"></p>
        <h3 align="center">基于大语言模型的知识库问答系统</h3>
        <p align="center">
          <a href="https://www.gnu.org/licenses/old-licenses/gpl-3.0"><img src="https://img.shields.io/github/license/1Panel-dev/maxkb?color=%231890FF" alt="License: GPL v3"></a>
          <a href="https://app.codacy.com/gh/1Panel-dev/maxkb?utm_source=github.com&utm_medium=referral&utm_content=1Panel-dev/maxkb&utm_campaign=Badge_Grade_Dashboard"><img src="https://app.codacy.com/project/badge/Grade/da67574fd82b473992781d1386b937ef" alt="Codacy"></a>
          <a href="https://github.com/1Panel-dev/maxkb/releases/latest"><img src="https://img.shields.io/github/v/release/1Panel-dev/maxkb" alt="Latest release"></a>
          <a href="https://github.com/1Panel-dev/maxkb"><img src="https://img.shields.io/github/stars/1Panel-dev/maxkb?color=%231890FF&style=flat-square" alt="Stars"></a>
        
</p>
<hr/>


MaxKB（ Max Knowlegde Base 的简称）是一款基于大语言模型的知识库问答系统，其核心目标是利用大语言模型对自然语言理解和生成的能力揣摩用户意图，对原始知识点进行汇总、整合，生成更贴切的答案。   

MaxKB 的产品特性：
- **多模型对接**  
MaxKB 支持对接市场上主流的模型供应商，包括百度千帆大模型、 Azure OpenAI 和 Ollama 私有模型平台等。

- **开箱即用**    
支持一键获取在线文本或直接上传文档，MaxKB 系统自动进行文本拆分、知识向量化；构建应用实现 LLM 问答功能，根据用户提问和知识库内容生成精确回答。

- **无缝集成**    
MaxKB 应用支持零编码集成到企业第三方系统。

## 一键启动

MaxKB 支持一键启动，仅需执行以下命令：
```
docker run --name="maxkb" -p 8000:8000 -d ghcr.io/1panel-dev/maxkb
```

## 整体架构
![arch](https://github.com/1Panel-dev/maxkb/assets/52996290/ca786342-8a0a-4921-b847-a96fff9a3e09)

## 实现原理

- 获取本地文档；
- 读取文本；
- 文本分割；
- 文本向量化；
- Query 向量化；
- 向量匹配最相似的 TOP N 个文本；
- 匹配出的文本作为上下文和问题一起添加到 prompt 中；
- 提交给 LLM 做生成回答。

![Implementation principle](https://github.com/1Panel-dev/maxkb/assets/52996290/51956c12-1396-4625-8b29-005ac60ca11d)



## 社区

如果您在使用过程中有任何疑问或建议，欢迎提交 GitHub Issue 或到我们官方论坛进行交流沟通：

-   [论坛](https://bbs.fit2cloud.com/)

## 技术栈

-   前端：[Vue3.js](https://cn.vuejs.org/)、[Element Plus](https://element-plus.org/zh-CN/)、[TypeScript](https://www.tslang.cn/)
-   后端：[django](https://www.djangoproject.com/)、[langchain](https://www.langchain.com/)
-   中间件：[postgresql](https://www.postgresql.org/)  
-   基础设施：[Docker](https://www.docker.com/)



## License

Copyright (c) 2014-2024 飞致云 FIT2CLOUD, All rights reserved.

Licensed under The GNU General Public License version 3 (GPLv3)  (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

<https://www.gnu.org/licenses/gpl-3.0.html>

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
