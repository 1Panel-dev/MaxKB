<p align="center"><img src= "https://github.com/1Panel-dev/maxkb/assets/52996290/c0694996-0eed-40d8-b369-322bf2a380bf" alt="MaxKB" width="300" /></p>
<h3 align="center">Top-Rated Retrieval-Augmented Generation (RAG) Chatbot.</h3>
<p align="center"><a href="https://trendshift.io/repositories/9113" target="_blank"><img src="https://trendshift.io/api/badge/repositories/9113" alt="1Panel-dev%2FMaxKB | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a></p>
<p align="center">
  <a href="https://www.gnu.org/licenses/gpl-3.0.html#license-text"><img src="https://img.shields.io/github/license/1Panel-dev/maxkb?color=%231890FF" alt="License: GPL v3"></a>
  <a href="https://github.com/1Panel-dev/maxkb/releases/latest"><img src="https://img.shields.io/github/v/release/1Panel-dev/maxkb" alt="Latest release"></a>
  <a href="https://github.com/1Panel-dev/maxkb"><img src="https://img.shields.io/github/stars/1Panel-dev/maxkb?color=%231890FF&style=flat-square" alt="Stars"></a>    
  <a href="https://hub.docker.com/r/1panel/maxkb"><img src="https://img.shields.io/docker/pulls/1panel/maxkb?label=downloads" alt="Download"></a>  
</p>
<hr/>

MaxKB = Max Knowledge Base, it is a chatbot based on Large Language Models (LLM) and Retrieval-Augmented Generation (RAG). MaxKB is widely applied in scenarios such as intelligent customer service, corporate internal knowledge bases, academic research, and education.

- **Ready-to-Use**: Supports direct uploading of documents / automatic crawling of online documents, with features for automatic text splitting, vectorization, and RAG (Retrieval-Augmented Generation). This effectively reduces hallucinations in large models, providing a superior smart Q&A interaction experience.
- **Model-Agnostic**: Supports various large models, including private models (such as Llama 3, Qwen 2, etc.) and public models (like OpenAI, Claude, Gemini, etc.).
- **Flexible Orchestration**: Equipped with a powerful workflow engine and function library, enabling the orchestration of AI processes to meet the needs of complex business scenarios. 
- **Seamless Integration**: Facilitates zero-coding rapid integration into third-party business systems, quickly equipping existing systems with intelligent Q&A capabilities to enhance user satisfaction.

## Quick start

```
docker run -d --name=maxkb --restart=always -p 8080:8080 -v ~/.maxkb:/var/lib/postgresql/data -v ~/.python-packages:/opt/maxkb/app/sandbox/python-packages cr2.fit2cloud.com/1panel/maxkb

# username: admin
# pass: MaxKB@123..
```

## Screenshots

<table style="border-collapse: collapse; border: 1px solid black;">
  <tr>
    <td style="padding: 5px;background-color:#fff;"><img src= "https://github.com/1Panel-dev/MaxKB/assets/52996290/d87395fa-a8d7-401c-82bf-c6e475d10ae9" alt="MaxKB Demo1"   /></td>
    <td style="padding: 5px;background-color:#fff;"><img src= "https://github.com/1Panel-dev/MaxKB/assets/52996290/47c35ee4-3a3b-4bd4-9f4f-ee20788b2b9a" alt="MaxKB Demo2"   /></td>
  </tr>
  <tr>
    <td style="padding: 5px;background-color:#fff;"><img src= "https://github.com/1Panel-dev/MaxKB/assets/52996290/1c0c5e32-6194-47f9-bc32-487996349d9c" alt="MaxKB Demo3"   /></td>
    <td style="padding: 5px;background-color:#fff;"><img src= "https://github.com/1Panel-dev/MaxKB/assets/52996290/f32f5fe9-a769-488c-ae0e-783bc2b89b3e" alt="MaxKB Demo4"   /></td>
  </tr>
</table>

## Technical stack

- Frontend：[Vue.js](https://vuejs.org/)
- Backend：[Python / Django](https://www.djangoproject.com/)
- LangChain：[LangChain](https://www.langchain.com/)
- Vector DB：[PostgreSQL / pgvector](https://www.postgresql.org/)

## License

Licensed under The GNU General Public License version 3 (GPLv3)  (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

<https://www.gnu.org/licenses/gpl-3.0.html>

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
