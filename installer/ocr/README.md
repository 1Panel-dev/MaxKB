# 扫描 PDF 文本向量化（最小版本）

现有知识库上传流程不变：无文字层或仅有少量文字的图片页先调用本机 PaddleOCR，再走原有分段、入库和向量化流程。有正常文字层的页面沿用原解析器。正文识别在本地进行，不提交到云端。

OCR 扫描页只输出识别文字，不再将原扫描图片重复附加到正文或保存为分段附件；
页面之间保留空行便于分段。有正常文字层的页面仍保留原有插图。
此行为对新解析生效，已入库的旧分段需要编辑去掉扫描图片后重新向量化，或重新解析导入。

本版只做文字识别，不包含批量异步任务、审核界面或表格结构恢复。长扫描件的分段预览会等待 OCR，先用短文件验证；扫描中的金额、比例和日期应在现有分段预览中核对。

## 首次安装（项目根目录，PowerShell）

    uv --cache-dir tmp/ocr-uv-cache venv --python .venv/Scripts/python.exe installer/ocr/.venv
    uv --cache-dir tmp/ocr-uv-cache pip install --python installer/ocr/.venv/Scripts/python.exe -r installer/ocr/requirements.lock
    installer/ocr/.venv/Scripts/python.exe installer/ocr/server.py --warmup

模型只在首次 warmup 时下载；运行时校验本地模型文件的 SHA-256，使用本地模型路径。虚拟环境、模型、运行日志及认证 token 保存在本项目忽略目录内，与 MaxKB 主 Python 环境隔离。

2026-10-07 已清理早期结构化方案的 runtime/models、重复下载缓存 runtime/cache，
以及 tmp/ocr-uv-cache 安装缓存。当前必需的 .venv 和 runtime/text-models 保留，OCR 目录约 1.06 GiB。
运行时可能重新生成少量缓存元数据；无需再次执行 warmup。重新安装或 warmup 时会重新下载所需文件。
清理记录保存在 runtime/cleanup-report.json。

## 启动

    powershell -ExecutionPolicy Bypass -File installer/ocr/start.ps1

服务仅监听 127.0.0.1:11637，自动创建本机认证 token 文件。MaxKB 默认读取同一个文件，无需复制 token。也可用 -Foreground 在当前终端运行。

在项目 .env 中增加，并重启 MaxKB web 和 Celery 服务：

    MAXKB_OCR_ENABLED=true
    MAXKB_OCR_URL=http://127.0.0.1:11637

YAML 配置模式使用 OCR_ENABLED: true 和 OCR_URL: http://127.0.0.1:11637。
显式配置认证时，MaxKB 使用 MAXKB_OCR_TOKEN（YAML 为 OCR_TOKEN），OCR 服务也使用同名环境变量；token 不应提交到 Git。

随后直接在原有知识库中上传扫描 PDF，检查分段预览出现正文，点击导入，等待原有向量化状态变为成功。此改动不需要数据库迁移。

## 失败与关闭

OCR 不可用、超时或未识别到文字时，上传返回具体错误，不会将 OCR 失败伪装为成功的空正文。单页上限 300 秒，超时终止识别子进程，后续请求可重新启动识别进程。

CPU 识别串行执行；重叠请求最多排队 300 秒，超出时返回明确的“服务忙”错误。
服务在内存中保留最近 32 页的识别结果，相同页内容、页码和 DPI 的重复预览复用结果，
不受文件名影响；不同内容重新识别。缓存随 OCR 服务重启清除，不保存原 PDF。
MaxKB 的单次请求等待上限包含排队、模型恢复及识别时间；本机 OCR 请求绕过系统 HTTP 代理。

日志：installer/ocr/runtime/service-error.log。设置 MAXKB_OCR_ENABLED=false 并重启 MaxKB 可恢复原 PDF 解析行为。纯空白扫描页可能识别不到文字，需先移除；多栏与复杂表格的阅读顺序不在本次最小版本的验收范围内。

    .venv/Scripts/python.exe apps/manage.py test knowledge.test_pdf_ocr
    installer/ocr/.venv/Scripts/python.exe installer/ocr/test_server.py
