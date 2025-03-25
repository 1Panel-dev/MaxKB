## 概述

Google 搜索工具是一个实时 API，可提取搜索引擎结果，提供来自 Google 的结构化数据。它支持各种搜索类型，包括 Web、图像、新闻和地图。

## 配置

1. 创建 Google Custom Search Engine
   在[Programmable Search Engine]（https://programmablesearchengine.google.com/）中 添加 Search Engine
   ![google 创建引擎](/src/assets/fx/img/google_AddSearchEngine.jpg)
2. 获取cx参数
   进入添加引擎，在【基本】菜单中获取搜索引擎的ID，即cx。
   ![google cx ](/src/assets/fx/img/google_cx.jpg) 3.获取 API Key
   打开 https://developers.google.com/custom-search/v1/overview?hl=zh-cn，获取API Key。
   ![google API Key](/src/assets/fx/img/google_APIKey.jpg)

3. 配置启动参数
   在Google搜索函数的启动参数中填写配置以上参数。
   ![启动参数](/src/assets/fx/img/google_setting.jpg)

4. 在应用中使用
   在高级编排应用中，点击添加组件->函数库->博查，设置使用参数。
   ![应用中使用](/src/assets/fx/img/google_app_used.jpg)
