# 5B · TypeScript 前端、取消与安全展示

[全部课程](../course/index.md) · [上一课](05a-api-security.md) · [下一课](05c-postgres-cache.md)

- **前置理解：** 5A；Node.js 22、已启用虚构演示服务
- **验证状态：** TypeScript 编译已测；尚未做真实浏览器端到端自动化。
- **节奏：** 建议拆成“读例子/讲解”和“关键实操/复盘”两次，每次 20–45 分钟；遇到不懂的一行就停下问。
- **学习规则：** 教材已提前备齐不代表你已通过；无需先独立写实现。跨阶段前仍需你确认。

> **401 排查实例：** 页面选择用户后不应全部 401；本轮新增专用演示请求头和缓存版本。`401` 是身份校验失败，`200 + []` 才是正常的无匹配/无可见证据；两者都不需要填写 Agnes Key。

## 1. 问题：现在为什么需要它？

用户需要看到原文、来源和失败状态，而不是原始 JSON。多次点击时旧响应可能覆盖新结果，模型返回的 HTML 也可能成为脚本注入入口。

## 2. 原理：在这个问题里理解技术

TypeScript 类型帮助编译检查，不自动验证 HTTP JSON。fetch 使用同源相对路径；远程预览中的 localhost 是用户电脑，不是后端。示例前后端由同一服务提供，避免开放全部 CORS。

AbortController 取消请求，但取消网络不一定停止服务端计算。controller 身份比较避免旧响应覆盖新结果；textContent 把内容当纯文本，不将检索内容放进 innerHTML。

## 3. 完整示例与逐行讲解

所有命令默认在仓库根目录、已激活 Python 虚拟环境下运行；环境准备见[课程使用说明](../course/setup.md)。不要把多个小课的新增依赖一次性安装。

### `frontend/client.ts`

完整源文件：[打开源码](../../frontend/client.ts)。行号包含注释和空行；`#:` / `//:` / `--:` 为就近讲解。逐条语句先读代码旁解释，再沿下表追踪输入与输出；相邻语句共同实现一个动作时合并说明，不用记忆行号。

<!-- source: frontend/client.ts -->
```typescript
//: 类型用于编译期检查；网络返回 JSON 的运行时校验在生产版还需补充。
type Hit = { document_id: string; title: string; score: number; text: string; source: string };
const form = document.querySelector<HTMLFormElement>("#search-form")!;
const output = document.querySelector<HTMLElement>("#output")!;
let active: AbortController | undefined;

//: 取消当前请求；可选链在尚无请求时不会报错。
document.querySelector("#cancel")!.addEventListener("click", () => active?.abort());
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  active?.abort();
  const controller = new AbortController();
  active = controller;
  const question = document.querySelector<HTMLInputElement>("#question")!.value;
  const token = document.querySelector<HTMLSelectElement>("#token")!.value;
  output.textContent = "正在检索…";
  //: 使用演示专用头，避免预览代理对 Authorization 的处理；这里绝不能放真实模型密钥。
  try {
    const response = await fetch("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Demo-Token": token },
      body: JSON.stringify({ question, k: 3 }),
      signal: controller.signal,
    });
    if (!response.ok) {
      const hint = response.status === 401 ? "演示身份校验失败，请刷新页面后重新选择用户；无需 Agnes API Key。"
        : response.status === 503 ? "服务端尚未启用虚构数据演示模式。"
        : response.status === 422 ? "查询参数无效，请检查问题和结果数量。"
        : "服务暂时不可用，请稍后重试。";
      throw new Error(`HTTP ${response.status}：${hint}`);
    }
    const hits: Hit[] = await response.json();
    //: 旧请求不能覆盖新结果；textContent 将内容当文本而非 HTML，减少 XSS 风险。
    if (active !== controller) return;
    output.textContent = hits.length ? hits.map(hit => `${hit.title}\n来源：${hit.source}\n匹配分数：${hit.score}\n${hit.text}`).join("\n\n——\n\n") : "未找到词语匹配证据；这不证明资料中没有答案。";
  } catch (error) {
    if (active !== controller) return;
    output.textContent = controller.signal.aborted ? "已取消" : String(error);
  } finally {
    if (active === controller) active = undefined;
  }
});
```

#### 逐行 / 相邻语句讲解

| 源码行 | 为什么这样写、数据如何变化 |
|---|---|
| 1–6 | 类型用于编译期检查；网络返回 JSON 的运行时校验在生产版还需补充。 |
| 7–16 | 取消当前请求；可选链在尚无请求时不会报错。 |
| 17–32 | 使用演示专用头，避免预览代理对 Authorization 的处理；这里绝不能放真实模型密钥。 |
| 33–42 | 旧请求不能覆盖新结果；textContent 将内容当文本而非 HTML，减少 XSS 风险。 |

## 4. 跟着运行与关键实操

### 运行命令

```bash
npm --prefix frontend ci --ignore-scripts
npm --prefix frontend run build
# 保持 5A 的 uvicorn 运行，打开其预览首页
```

### 只做这些关键改动

1. 用 Alice 搜“Webhook”，核对来源和正文；切 Bob 搜同题，预期没有可见匹配。
2. 在浏览器网络面板限速，连续提交两个不同问题，确认旧请求不会覆盖新结果。
3. 点击取消，观察“已取消”；接口很快时可用限速帮助观察。
4. 阅读源码中的 textContent，解释如果某文档包含 `<script>`，为什么不会按 HTML 执行。不要为测试改成 innerHTML。

操作前先预测结果；临时改动完成后恢复参考示例，或把学习版本另存并标注。不要修改金标准迎合模型。

## 5. 验证与排错

npm run build 应零错误；手工验收记录请求失败、取消、空结果、权限切换与长原文展示。终端测试通过不能替代浏览器手动验收。

遇到错误按顺序查：① 是否在仓库根目录、使用当前虚拟环境；② 依赖是否属于本课且版本兼容；③ 输入/配置是否满足约定；④ 失败发生在文件、检索、协议、模型还是外部服务。发给导师运行命令、完整错误栈和预期/实际，删除密钥与个人数据。未经执行的步骤标“待验”，不编造输出。

## 6. 反思与本课产出

**反思：** 为什么当前公开演示 token 不可用于真实登录？取消操作需要怎样向后端和模型服务继续传播？

**产出：** 可编译 TS 页面与手工浏览器验收清单，不宣称生产级登录已实现。

本课提交运行结果、一个预测和一段解释即可；阶段结束再汇总[验收记录](../reviews/template.md)。导师需区分参考代码通过测试与学习者已理解，不提前打勾。

### 与 SSE 的关系

当前页面刻意使用 JSON 接口，先学清异步与取消。5A 的 POST SSE 接口可用 fetch 的 ReadableStream 读取；EventSource 原生主要使用 GET 且不支持任意 Authorization 头，不能直接替换。实现 POST SSE 消费时应使用 TextDecoder 保留跨块 UTF-8 状态，缓冲到双换行再解析，分别处理 done/error；流式 UI 属于产品集成验收项，当前页面没有声称已实现 token 流。

## 卡住时按需查阅

- https://www.typescriptlang.org/docs/handbook/intro.html
- https://developer.mozilla.org/en-US/docs/Web/API/AbortController

外部教程可能使用不同版本；优先对照本仓库依赖记录和官方迁移文档，不要求通读整站。
