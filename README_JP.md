[English](README_EN.md) | [中文](README.md) | [日本語](README_JP.md)

<p align="center"><img src= "https://github.com/1Panel-dev/maxkb/assets/52996290/c0694996-0eed-40d8-b369-322bf2a380bf" alt="MaxKB" width="300" /></p>
<h3 align="center">大規模言語モデルとRAGに基づくナレッジベースQ&Aシステム</h3>
<p align="center"><a href="https://trendshift.io/repositories/9113" target="_blank"><img src="https://trendshift.io/api/badge/repositories/9113" alt="1Panel-dev%2FMaxKB | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a></p>
<p align="center">
  <a href="https://www.gnu.org/licenses/gpl-3.0.html#license-text"><img src="https://img.shields.io/github/license/1Panel-dev/maxkb?color=%231890FF" alt="License: GPL v3"></a>
  <a href="https://app.codacy.com/gh/1Panel-dev/maxkb?utm_source=github.com&utm_medium=referral&utm_content=1Panel-dev/maxkb&utm_campaign=Badge_Grade_Dashboard"><img src="https://app.codacy.com/project/badge/Grade/da67574fd82b473992781d1386b937ef" alt="Codacy"></a>
  <a href="https://github.com/1Panel-dev/maxkb/releases/latest"><img src="https://img.shields.io/github/v/release/1Panel-dev/maxkb" alt="Latest release"></a>
  <a href="https://github.com/1Panel-dev/maxkb"><img src="https://img.shields.io/github/stars/1Panel-dev/maxkb?color=%231890FF&style=flat-square" alt="Stars"></a>    
  <a href="https://hub.docker.com/r/1panel/maxkb"><img src="https://img.shields.io/docker/pulls/1panel/maxkb?label=downloads" alt="Download"></a>  
</p>
<hr/>

MaxKB = Max Knowledge Baseは、大規模言語モデルとRAGに基づくオープンソースのナレッジベースQ&Aシステムであり、企業内ナレッジベース、カスタマーサービス、学術研究、教育などのシナリオで広く使用されています。

- **すぐに使える**：ドキュメントの直接アップロード/オンラインドキュメントの自動クロールをサポートし、テキストの自動分割、ベクトル化、RAG（検索強化生成）をサポートし、大規模モデルの幻覚を効果的に減らし、インテリジェントなQ&Aのインタラクティブな体験が良好です。
- **モデル中立**：さまざまな大規模モデルとの接続をサポートし、ローカルプライベート大規模モデル（Llama 3 / Qwen 2など）、国内公共大規模モデル（Tongyi Qianwen / Tencent Hunyuan / Byte Doubao / Baidu Qianfan / Zhipu AI / Kimiなど）、および海外公共大規模モデル（OpenAI / Claude / Geminiなど）を含みます。
- **柔軟なオーケストレーション**：強力なワークフローエンジンと関数ライブラリを内蔵し、AIの作業プロセスのオーケストレーションをサポートし、複雑なビジネスシナリオのニーズを満たします。
- **シームレスな埋め込み**：ゼロコーディングでサードパーティのビジネスシステムに迅速に埋め込むことをサポートし、既存のシステムが迅速にインテリジェントなQ&A機能を持ち、ユーザー満足度を向上させます。

## クイックスタート

```
docker run -d --name=maxkb --restart=always -p 8080:8080 -v ~/.maxkb:/var/lib/postgresql/data -v ~/.python-packages:/opt/maxkb/app/sandbox/python-packages cr2.fit2cloud.com/1panel/maxkb

# ユーザー名: admin
# パスワード: MaxKB@123..
```

- [1Panelアプリストア](https://apps.fit2cloud.com/1panel)を通じてMaxKB + Ollama + Llama 3 / Qwen 2を迅速にデプロイし、ローカル大規模モデルに基づくAIナレッジベースQ&Aシステムを迅速に立ち上げることができます。
- 内部ネットワーク環境の場合、[オフラインインストールパッケージ](https://community.fit2cloud.com/#/products/maxkb/downloads)を使用してインストールとデプロイを行うことをお勧めします。
- オンラインで体験することもできます：[DataEaseアシスタント](https://dataease.io/docs/v2/)、これはMaxKBに基づいて構築されたインテリジェントなAI Q&Aシステムであり、DataEase製品およびオンラインドキュメントに埋め込まれています。
- MaxKBの製品バージョンはコミュニティ版とプロフェッショナル版に分かれており、詳細は[MaxKB製品バージョン比較](https://maxkb.cn/pricing.html)をご覧ください。

さらに質問がある場合は、ユーザーマニュアルを確認するか、フォーラムを通じて私たちと交流してください。

- [ユーザーマニュアル](https://maxkb.cn/docs/)
- [デモビデオ](https://www.bilibili.com/video/BV1BE421M7YM/)
- [フォーラムヘルプ](https://bbs.fit2cloud.com/c/mk/11)
- 技術交流グループ

<image height="150px" width="150px" src="https://github.com/1Panel-dev/MaxKB/assets/52996290/a083d214-02be-4178-a1db-4f428124153a"/>

## UI表示

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

## 技術スタック

- フロントエンド：[Vue.js](https://cn.vuejs.org/)
- バックエンド：[Python / Django](https://www.djangoproject.com/)
- LangChain：[LangChain](https://www.langchain.com/)
- ベクトルデータベース：[PostgreSQL / pgvector](https://www.postgresql.org/)
- 大規模モデル：さまざまなローカルプライベートまたは公共の大規模モデル

## Feizhiyunの他のスタープロジェクト

- [1Panel](https://github.com/1panel-dev/1panel/) - モダンでオープンソースのLinuxサーバー運用管理パネル
- [JumpServer](https://github.com/jumpserver/jumpserver/) - 人気のあるオープンソースのバスティオンホスト
- [DataEase](https://github.com/dataease/dataease/) - 誰でも使えるオープンソースのデータ可視化分析ツール
- [MeterSphere](https://github.com/metersphere/metersphere/) - 新世代のオープンソースの継続的テストツール
- [Halo](https://github.com/halo-dev/halo/) - 強力で使いやすいオープンソースのウェブサイト構築ツール

## ライセンス

Copyright (c) 2014-2024 Feizhiyun FIT2CLOUD, All rights reserved.

The GNU General Public License version 3 (GPLv3)に基づいてライセンスされています（「ライセンス」）。ライセンスに準拠しない限り、このファイルを使用することはできません。ライセンスのコピーを取得するには、次のURLをご覧ください。

<https://www.gnu.org/licenses/gpl-3.0.html>

適用法により要求される場合または書面で合意された場合を除き、ライセンスに基づいて配布されるソフトウェアは、「現状のまま」提供され、明示的または黙示的な保証はありません。ライセンスの特定の言語に基づく保証および制限については、ライセンスを参照してください。
