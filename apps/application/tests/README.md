# 工作流测试

工作流 Web 图片导入的 HTTP 回归使用 Postman CLI 1.70 或更高版本：

```bash
postman simulation run apps/application/tests/fixtures/workflow_web_images.sim.yaml --port 49643 --no-history
```

另一个终端运行：

```bash
WORKFLOW_WEB_IMAGE_TEST_URL=http://127.0.0.1:49643 \
  uv run python apps/manage.py test application.tests.test_workflow_web_images
```

测试通过真实网页抓取执行器和 boto3 客户端访问本地网页、图片和 S3 对象存储模拟，
覆盖抓取、图片下载、保存、分段、文档写入及段落附件关联。重复导入复用已保存的图片；
下载失败保留原链接，正文仍可导入。测试数据为合成内容，不调用模型。

网页模拟提供普通 HTTP GET；对象存储模拟仅覆盖 S3 PutObject、GetObject 和 DeleteObject，
不验证真实站点的访问权限、重定向或远端存储服务。未设置环境变量时跳过两项 HTTP 回归，
其余工作流图片测试照常运行。
