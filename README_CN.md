<p align="center"><img src= "https://github.com/1Panel-dev/maxkb/assets/52996290/c0694996-0eed-40d8-b369-322bf2a380bf" alt="MaxKB" width="300" /></p>
<h3 align="center">强大易用的企业级 AI 助手</h3>
<p align="center">
    <a href="https://trendshift.io/repositories/9113" target="_blank"><img src="https://trendshift.io/api/badge/repositories/9113" alt="1Panel-dev%2FMaxKB | Trendshift" style="width: 250px; height: auto;" /></a>
    <a href="https://market.aliyun.com/products/53690006/cmjj00067609.html?userCode=kmemb8jp" target="_blank"><img src="https://img.alicdn.com/imgextra/i2/O1CN01H5JIwY1rZ0OobDjnJ_!!6000000005644-2-tps-1000-216.png" alt="1Panel-dev%2FMaxKB | Aliyun" style="width: 250px; height: auto;" /></a>
</p>
<p align="center">
  <a href="README_EN.md"><img src="https://img.shields.io/badge/English_README-blue" alt="English README"></a>
  <a href="https://www.gnu.org/licenses/gpl-3.0.html#license-text"><img src="https://img.shields.io/github/license/1Panel-dev/maxkb" alt="License: GPL v3"></a>
  <a href="https://github.com/1Panel-dev/maxkb/releases/latest"><img src="https://img.shields.io/github/v/release/1Panel-dev/maxkb" alt="Latest release"></a>
  <a href="https://github.com/1Panel-dev/maxkb"><img src="https://img.shields.io/github/stars/1Panel-dev/maxkb?style=flat-square" alt="Stars"></a>    
  <a href="https://hub.docker.com/r/1panel/maxkb"><img src="https://img.shields.io/docker/pulls/1panel/maxkb?label=downloads" alt="Download"></a>  
</p>
<hr/>

MaxKB = Max Knowledge Brain，是一款强大易用的企业级 AI 助手，支持 RAG 检索增强生成、工作流编排、MCP 工具调用能力。MaxKB 支持对接各种主流大语言模型，广泛应用于智能客服、企业内部知识库问答、员工助手、学术研究与教育等场景。

- **RAG 检索增强生成**：高效搭建本地 AI 知识库，支持直接上传文档 / 自动爬取在线文档，支持文本自动拆分、向量化，有效减少大模型幻觉，提升问答效果；
- **灵活编排**：内置强大的工作流引擎、函数库和 MCP 工具调用能力，支持编排 AI 工作过程，满足复杂业务场景下的需求；
- **无缝嵌入**：支持零编码快速嵌入到第三方业务系统，让已有系统快速拥有智能问答能力，提高用户满意度；
- **模型中立**：支持对接各种大模型，包括本地私有大模型（DeepSeek R1 / Llama 3 / Qwen 2 等）、国内公共大模型（通义千问 / 腾讯混元 / 字节豆包 / 百度千帆 / 智谱 AI / Kimi 等）和国外公共大模型（OpenAI / Claude / Gemini 等）。

MaxKB 三分钟视频介绍：https://www.bilibili.com/video/BV18JypYeEkj/

## 快速开始

```
# Linux 机器
docker run -d --name=maxkb --restart=always -p 8080:8080 -v ~/.maxkb:/var/lib/postgresql/data -v ~/.python-packages:/opt/maxkb/app/sandbox/python-packages registry.fit2cloud.com/maxkb/maxkb

# Windows 机器
docker run -d --name=maxkb --restart=always -p 8080:8080 -v C:/maxkb:/var/lib/postgresql/data -v C:/python-packages:/opt/maxkb/app/sandbox/python-packages registry.fit2cloud.com/maxkb/maxkb

# 用户名: admin
# 密码: MaxKB@123..
```

- 你也可以通过 [1Panel 应用商店](https://apps.fit2cloud.com/1panel) 快速部署 MaxKB；
- 如果是内网环境，推荐使用 [离线安装包](https://community.fit2cloud.com/#/products/maxkb/downloads) 进行安装部署；
- MaxKB 产品版本分为社区版和专业版，详情请参见：[MaxKB 产品版本对比](https://maxkb.cn/pricing.html)；
- 如果您需要向团队介绍 MaxKB，可以使用这个 [官方 PPT 材料](https://maxkb.cn/download/introduce-maxkb_202503.pdf)。

如你有更多问题，可以查看使用手册，或者通过论坛与我们交流。

- [案例展示](USE-CASES.md)
- [使用手册](https://maxkb.cn/docs/)
- [论坛求助](https://bbs.fit2cloud.com/c/mk/11)
- 技术交流群

<image height="150px" width="150px" src="https://github.com/1Panel-dev/MaxKB/assets/52996290/a083d214-02be-4178-a1db-4f428124153a"/>

## UI 展示

<table style="border-collapse: collapse; border: 1px solid black;">
  <tr>
    <td style="padding: 5px;background-color:#fff;"><img src= "https://github.com/1Panel-dev/MaxKB/assets/52996290/d87395fa-a8d7-401c-82bf-c6e475d10ae9" alt="MaxKB Demo1"   /></td>
    <td style="padding: 5px;background-color:#fff;"><img src= "https://github.com/1Panel-dev/MaxKB/assets/52996290/47c35ee4-3a3b-4bd4-9f4f-ee20788b2b9a" alt="MaxKB Demo2"   /></td>
  </tr>
  <tr>
    <td style="padding: 5px;background-color:#fff;"><img src= "https://github.com/user-attachments/assets/9a1043cb-fa62-4f71-b9a3-0b46fa59a70e" alt="MaxKB Demo3"   /></td>
    <td style="padding: 5px;background-color:#fff;"><img src= "https://github.com/user-attachments/assets/3407ce9a-779c-4eb4-858e-9441a2ddc664" alt="MaxKB Demo4"   /></td>
  </tr>
</table>

## 技术栈

- 前端：[Vue.js](https://cn.vuejs.org/)
- 后端：[Python / Django](https://www.djangoproject.com/)
- LangChain：[LangChain](https://www.langchain.com/)
- 向量数据库：[PostgreSQL / pgvector](https://www.postgresql.org/)

## 飞致云的其他明星项目

- [1Panel](https://github.com/1panel-dev/1panel/) - 现代化、开源的 Linux 服务器运维管理面板
- [JumpServer](https://github.com/jumpserver/jumpserver/) - 广受欢迎的开源堡垒机
- [DataEase](https://github.com/dataease/dataease/) - 人人可用的开源数据可视化分析工具
- [MeterSphere](https://github.com/metersphere/metersphere/) - 新一代的开源持续测试工具
- [Halo](https://github.com/halo-dev/halo/) - 强大易用的开源建站工具

## License

Copyright (c) 2014-2025 飞致云 FIT2CLOUD, All rights reserved.

Licensed under The GNU General Public License version 3 (GPLv3)  (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

<https://www.gnu.org/licenses/gpl-3.0.html>

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
