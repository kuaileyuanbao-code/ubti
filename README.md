# UBTI 大学生大型受苦指标

UBTI 是一个面向大学生学习、生活、社交、科研、求职等场景的娱乐型校园人格测试网站。

当前版本支持：

- 24 道可点击选择题
- 每题支持 A/B/C/D 和“其他，我自己说”
- 固定计分生成主人格、副人格、受苦指数和截图友好结果卡
- 调用星辰 Agent 生成 AI 补刀、今日自救任务和分享文案

## 安装依赖

```powershell
pip install -r requirements.txt
```

## 配置星辰 Agent API

复制 `.env.example` 为 `.env`：

```powershell
Copy-Item .env.example .env
```

填写 UBTI 专用星辰 Agent API 信息：

```text
XINGCHEN_API_KEY=你的 API Key
XINGCHEN_API_SECRET=你的 API Secret
XINGCHEN_FLOW_ID=你的 UBTI Agent FlowID
```

不要把 `.env` 发给别人，也不要提交到公开仓库。

## 本地运行

```powershell
python app.py
```

打开：

```text
http://127.0.0.1:5000/ubti
```

## 部署成正式网站

本项目需要后端保护星辰 API Key，不能直接部署成纯静态网页。推荐部署到 Render、Railway、PythonAnywhere 或自己的云服务器。

### 腾讯云 CloudBase 云托管

项目已包含 `Dockerfile` 和 `.dockerignore`，可以通过 CloudBase 云托管从 GitHub 仓库构建容器镜像。

创建云托管服务时：

```text
服务端口：80
构建方式：Dockerfile
Dockerfile 路径：Dockerfile
```

需要配置环境变量：

```text
XINGCHEN_API_KEY=你的 API Key
XINGCHEN_API_SECRET=你的 API Secret
XINGCHEN_FLOW_ID=你的 UBTI Agent FlowID
XINGCHEN_API_URL=https://xingchen-api.xf-yun.com/workflow/v1/chat/completions
XINGCHEN_AGENT_URL=你的星辰 Agent 公开体验地址
```

健康检查地址：

```text
/healthz
```

### Render / Railway 等海外平台

生产环境启动命令：

```bash
gunicorn app:app
```

需要在云平台配置环境变量：

```text
XINGCHEN_API_KEY=你的 API Key
XINGCHEN_API_SECRET=你的 API Secret
XINGCHEN_FLOW_ID=你的 UBTI Agent FlowID
XINGCHEN_API_URL=https://xingchen-api.xf-yun.com/workflow/v1/chat/completions
XINGCHEN_AGENT_URL=你的星辰 Agent 公开体验地址
```

健康检查地址：

```text
/healthz
```

## 临时公网演示

可以用 Cloudflare Tunnel、ngrok 或 cpolar 暴露本地端口：

```powershell
cloudflared tunnel --url http://127.0.0.1:5000
```

拿到公网地址后，访问公网地址即可体验 UBTI 网站。
