# 飞书每日书摘推送（GitHub Actions 版）

自动将《从零开始做运营》60天书摘推送到飞书群聊，不依赖本地电脑，关机也能正常推送。

## 文件说明

| 文件 | 说明 |
|---|---|
| `cloud_send_excerpt.py` | 推送脚本，读取书摘并发送到飞书 webhook |
| `从零开始做运营_60天书摘.md` | 60天书摘原文 |
| `书摘进度.json` | 推送进度记录 |
| `.github/workflows/daily_excerpt.yml` | GitHub Actions 定时任务配置 |

## 部署步骤

### 1. 创建 GitHub 仓库

1. 打开 https://github.com/new
2. Repository name 填：`feishu-daily-excerpt`
3. 选择 **Private**（私有）
4. 勾选 **Add a README file**
5. 点击 **Create repository**

### 2. 设置 Webhook 密钥

1. 在仓库页面点击 **Settings** → 左侧 **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. Name 填：`FEISHU_WEBHOOK_URL`
4. Secret 填你的 webhook 地址：`https://open.feishu.cn/open-apis/bot/v2/hook/96b64c23-c5d4-4c82-adad-da5ddf2dd7be`
5. 点击 **Add secret**

### 3. 上传文件

在仓库首页点击 **Add file** → **Upload files**，把以下文件拖进去：

- `cloud_send_excerpt.py`
- `从零开始做运营_60天书摘.md`
- `书摘进度.json`
- `.github/workflows/daily_excerpt.yml`

> 注意：`.github/workflows/` 是隐藏目录，需要先创建这个目录结构。可以先点击 **Add file** → **Create new file**，路径填 `.github/workflows/daily_excerpt.yml`，然后粘贴文件内容。

### 4. 验证运行

1. 上传完成后，点击仓库顶部 **Actions**
2. 左侧选择 **Daily Excerpt Push**
3. 点击右侧 **Run workflow** → **Run workflow**
4. 等待运行完成，飞书群聊会收到一条书摘

### 5. 定时说明

工作流默认每天北京时间 **22:00** 自动推送一次。如需修改时间，编辑 `.github/workflows/daily_excerpt.yml` 中的 cron 表达式。

## 故障处理

- **没有按时推送**：GitHub Actions 首次启用可能有 5-10 分钟延迟，建议运行一次手动触发验证。
- **发送失败**：检查 `FEISHU_WEBHOOK_URL` 是否设置正确，以及飞书自定义机器人是否被移出群聊。
- **进度丢失**：进度保存在 `书摘进度.json` 中，GitHub Actions 会自动提交更新。
