# UBTI 大学生大型受苦指标

UBTI 是一个面向大学生学习、生活、社交、科研、求职等场景的娱乐型校园人格测试网站。

当前版本支持：

- 24 道可点击选择题
- 每题支持 A/B/C/D 和“其他，我自己说”
- 固定计分生成主人格、副人格、受苦指数和截图友好结果卡
- 一键复制测试结果，跳转到星辰 Agent 继续深度分析
- 分享测试链接，方便邀请同学、室友、搭子一起测

## 安装依赖

```powershell
pip install -r requirements.txt
```

## 配置星辰 Agent 链接

静态部署时，填写 `static/config.js`：

```js
window.UBTI_CONFIG = {
  agentUrl: "你的星辰 Agent 公开体验地址",
};
```

如果星辰 Agent 链接还在审核，可以先留空：

```js
window.UBTI_CONFIG = {
  agentUrl: "",
};
```

如果暂时不填，网站仍然可以完成测试，只是结果页不会显示“去星辰 Agent 深度分析”的入口。

## 本地运行

```powershell
python app.py
```

打开：

```text
http://127.0.0.1:5000/ubti
```

## 部署成正式网站：优先静态托管

当前版本不在网站里调用星辰 API，推荐部署成静态网站。静态托管没有后端冷启动，更适合很多同学同时打开测试。

生成静态文件：

```powershell
python build_static.py
```

生成后上传 `dist` 目录到腾讯云 CloudBase 静态网站托管。

推荐链路：

```text
朋友打开测试网站 -> 完成 24 题 -> 一键复制 UBTI 结果 -> 跳转星辰 Agent -> 粘贴结果继续聊
```

### 腾讯云 CloudBase 云托管备用方案

如果以后又想让网站自己提供后端接口，也可以继续使用云托管。项目保留了 `Dockerfile` 和 `.dockerignore`，可以通过 CloudBase 云托管从 GitHub 仓库构建容器镜像。

创建云托管服务时：

```text
服务端口：80
构建方式：Dockerfile
Dockerfile 路径：Dockerfile
```

如果用云托管，星辰 Agent 链接可以用环境变量配置：

```text
XINGCHEN_AGENT_URL=你的星辰 Agent 公开体验地址
```

健康检查地址：

```text
/healthz
```

传播期推荐配置：

```text
容器规格：1 核 2G 起步
运行模式：持续运行，或自动扩缩容但最小实例数设为 1
最大实例数：5 起步；如果集中拉票或课堂传播，可以临时调到 10
日志采集路径：stdout
公网默认域名：开启
```

如果最小实例数设为 0，长时间没人访问后会缩容，下一位用户打开时可能遇到几十秒冷启动。正式分享、参赛展示、集中传播当天，建议至少保持 1 个实例常驻。

### Render / Railway 等海外平台

生产环境启动命令：

```bash
gunicorn app:app
```

需要在云平台配置环境变量：

```text
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
