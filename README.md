<p align="center"><img src= "https://github.com/1Panel-dev/maxkb/assets/52996290/c0694996-0eed-40d8-b369-322bf2a380bf" alt="MaxKB" width="300" /></p>
<h3 align="center">Knowledge Based Question Answering System Based on LLM (Large Language Model)</h3>
<p align="center">
  <a href="https://www.gnu.org/licenses/old-licenses/gpl-3.0"><img src="https://img.shields.io/github/license/1Panel-dev/maxkb?color=%231890FF" alt="License: GPL v3"></a>
  <a href="https://app.codacy.com/gh/1Panel-dev/maxkb?utm_source=github.com&utm_medium=referral&utm_content=1Panel-dev/maxkb&utm_campaign=Badge_Grade_Dashboard"><img src="https://app.codacy.com/project/badge/Grade/da67574fd82b473992781d1386b937ef" alt="Codacy"></a>
  <a href="https://github.com/1Panel-dev/maxkb/releases/latest"><img src="https://img.shields.io/github/v/release/1Panel-dev/maxkb" alt="Latest release"></a>
  <a href="https://github.com/1Panel-dev/maxkb"><img src="https://img.shields.io/github/stars/1Panel-dev/maxkb?color=%231890FF&style=flat-square" alt="Stars"></a>    
  <a href="https://hub.docker.com/r/1panel/maxkb"><img src="https://img.shields.io/docker/pulls/1panel/maxkb?label=downloads" alt="Download"></a>  
</p>
<hr/>

MaxKB is a knowledge based question answering system based on the LLM (Large Language Model). MaxKB = Max Knowledge Base, aiming to become the most powerful brain of the enterprise.

- **Out-of-the-box**: Supports direct uploading of documents, automatic crawling of online documents, automatic text splitting and vectorization, and a good intelligent Q&A interactive experience;
- **Seamless Embedding**: Supports rapid embedding into third-party business systems with zero coding;
- **Multi-model support**: Supports docking with mainstream large models, including local private large models (such as Llama 2), Azure OpenAI, and Baidu Qianfan large models.

## Quick start

```
docker run -d --name=maxkb -p 8080:8080 -v ~/.maxkb:/var/lib/postgresql/data 1panel/maxkb

# Username: admin
# Password: MaxKB@123..
```
You can also quickly deploy MaxKB + Ollama + Llama 2 through [1Panel App Store](https://apps.fit2cloud.com/1panel). A knowledge base question and answer system based on a local large model can be launched within 30 minutes and embedded into in third-party business systems.

You can also experience it online：[DataEase Little Helper](https://dataease.io/docs/v2/)，It is based on MaxKB. The intelligent question and answer system built has been embedded in DataEase products and online documents.

If you have more questions, you can check the user manual or communicate with us through the forum.

-   [Manual](https://github.com/1Panel-dev/MaxKB/wiki/1-%E5%AE%89%E8%A3%85%E9%83%A8%E7%BD%B2)
-   [Forum Help](https://bbs.fit2cloud.com/c/mk/11)
-   [Demo Video](https://www.bilibili.com/video/BV1BE421M7YM/)

## UI Exhibit

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

## Technology Stack

-   Front End：[Vue.js](https://cn.vuejs.org/)
-   Back End：[Python / Django](https://www.djangoproject.com/)
-   LangChain：[LangChain](https://www.langchain.com/)
-   Vector Database：[PostgreSQL / pgvector](https://www.postgresql.org/)
-   Large Language Model (LLM)：Azure OpenAI, Baidu Qianfan Large Model, [Ollama](https://github.com/ollama/ollama)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=1Panel-dev/MaxKB&type=Date)](https://star-history.com/#1Panel-dev/MaxKB&Date)

## License

Copyright (c) 2014-2024 飞致云 FIT2CLOUD, All rights reserved.

Licensed under The GNU General Public License version 3 (GPLv3)  (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

<https://www.gnu.org/licenses/gpl-3.0.html>

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
