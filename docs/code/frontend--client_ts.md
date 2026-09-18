# 浏览器查询、身份头与请求竞态：逐行精讲

[精讲总目录](index.md) · [对应源码](../../frontend/client.ts)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

把表单输入转成同源HTTP请求，区分取消、错误和正常空候选，防旧请求覆盖新结果。

### 输入、输出与调用关系

DOM输入→POST /api/search→安全文本展示；不调用模型、不保存真实Key。

### 运行与风险边界

`npm --prefix frontend ci --ignore-scripts && npm --prefix frontend run build`；由启用虚构演示的API提供HTML和编译后的client.js。

TypeScript类型在编译后擦除，不验证远端JSON。真实浏览器401是否消失仍需端到端观察，进程内测试不能代替。

## 完整源码

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

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```typescript
//: 类型用于编译期检查；网络返回 JSON 的运行时校验在生产版还需补充。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：类型用于编译期检查；网络返回 JSON 的运行时校验在生产版还需补充。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L2"></a>
### 第 2 行

```typescript
type Hit = { document_id: string; title: string; score: number; text: string; source: string };
```

**语法与数据变化：** 声明Hit对象五字段的编译期类型，分号分隔属性。

**为什么与边界：** 网络JSON不经运行时schema检查，声明Hit[]不能保证服务器真的返回此形状。

<a id="L3"></a>
### 第 3 行

```typescript
const form = document.querySelector<HTMLFormElement>("#search-form")!;
```

**语法与数据变化：** 按#search-form查找表单，泛型告诉TS元素类型，末尾!断言非空。

**为什么与边界：** !不是运行时检查；HTML缺该ID仍会报错。

<a id="L4"></a>
### 第 4 行

```typescript
const output = document.querySelector<HTMLElement>("#output")!;
```

**语法与数据变化：** 查找输出节点并断言存在。

**为什么与边界：** 依赖index.html的契约，类型不自动创建元素。

<a id="L5"></a>
### 第 5 行

```typescript
let active: AbortController | undefined;
```

**语法与数据变化：** let声明当前请求控制器，初始undefined；联合类型允许无请求。

**为什么与边界：** 它同时用于取消和识别结果是否已过时。

<a id="L6"></a>
### 第 6 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L7"></a>
### 第 7 行

```typescript
//: 取消当前请求；可选链在尚无请求时不会报错。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：取消当前请求；可选链在尚无请求时不会报错。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L8"></a>
### 第 8 行

```typescript
document.querySelector("#cancel")!.addEventListener("click", () => active?.abort());
```

**语法与数据变化：** 找到取消按钮并注册点击箭头函数，active?.abort只在存在时调用。

**为什么与边界：** 没有请求时安全无操作；abort客户端不保证服务器所有任务已停止。

<a id="L9"></a>
### 第 9 行

```typescript
form.addEventListener("submit", async (event) => {
```

**语法与数据变化：** 注册异步提交回调，接收事件对象。

**为什么与边界：** addEventListener不等待返回Promise，异常需在内部try/catch管理。

<a id="L10"></a>
### 第 10 行

```typescript
  event.preventDefault();
```

**语法与数据变化：** 阻止表单默认导航/刷新。

**为什么与边界：** 否则页面可能离开，JavaScript结果展示中断。

<a id="L11"></a>
### 第 11 行

```typescript
  active?.abort();
```

**语法与数据变化：** 取消前一请求。

**为什么与边界：** 仍需后面的身份检查防竞态，不能假设abort瞬间撤销所有旧回调。

<a id="L12"></a>
### 第 12 行

```typescript
  const controller = new AbortController();
```

**语法与数据变化：** 为本次请求创建新AbortController。

**为什么与边界：** 已中止的旧controller不能复用成新请求。

<a id="L13"></a>
### 第 13 行

```typescript
  active = controller;
```

**语法与数据变化：** 将当前控制器记录为active。

**为什么与边界：** 后续通过对象身份而不是问题字符串判断“最新请求”。

<a id="L14"></a>
### 第 14 行

```typescript
  const question = document.querySelector<HTMLInputElement>("#question")!.value;
```

**语法与数据变化：** 读取输入框value得到问题字符串。

**为什么与边界：** 未trim，服务端仍负责验证；浏览器长度限制不是可信安全边界。

<a id="L15"></a>
### 第 15 行

```typescript
  const token = document.querySelector<HTMLSelectElement>("#token")!.value;
```

**语法与数据变化：** 读取下拉框的演示token。

**为什么与边界：** 只是公开虚构身份，绝不能把真实模型Key写到此处。

<a id="L16"></a>
### 第 16 行

```typescript
  output.textContent = "正在检索…";
```

**语法与数据变化：** 用textContent显示进行中提示。

**为什么与边界：** 按纯文本展示，不执行用户输入HTML。

<a id="L17"></a>
### 第 17 行

```typescript
  //: 使用演示专用头，避免预览代理对 Authorization 的处理；这里绝不能放真实模型密钥。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：使用演示专用头，避免预览代理对 Authorization 的处理；这里绝不能放真实模型密钥。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L18"></a>
### 第 18 行

```typescript
  try {
```

**语法与数据变化：** 开始捕获fetch、JSON解析及显式throw错误。

**为什么与边界：** DOM查找发生在此块之前，因此缺元素错误不在本catch范围。

<a id="L19"></a>
### 第 19 行

```typescript
    const response = await fetch("/api/search", {
```

**语法与数据变化：** await同源相对URL请求。

**为什么与边界：** 浏览器访问的是预览/部署域名，不是沙箱localhost；不需硬编码第二个服务地址。

<a id="L20"></a>
### 第 20 行

```typescript
      method: "POST",
```

**语法与数据变化：** 指定POST匹配后端路由。

**为什么与边界：** 默认GET不能带此接口的JSON请求契约。

<a id="L21"></a>
### 第 21 行

```typescript
      headers: { "Content-Type": "application/json", "X-Demo-Token": token },
```

**语法与数据变化：** 声明JSON内容类型并发送专用演示头。

**为什么与边界：** 不依赖代理可能占用的Authorization，仍保留后端身份检查。

<a id="L22"></a>
### 第 22 行

```typescript
      body: JSON.stringify({ question, k: 3 }),
```

**语法与数据变化：** JSON.stringify序列化简写question与固定k=3。

**为什么与边界：** 浏览器对象不是自动JSON；k来自代码而非随意字符串输入。

<a id="L23"></a>
### 第 23 行

```typescript
      signal: controller.signal,
```

**语法与数据变化：** 关联本次controller.signal以支持取消。

**为什么与边界：** 不传signal则按钮abort不会影响这个fetch。

<a id="L24"></a>
### 第 24 行

```typescript
    });
```

**语法与数据变化：** 闭合配置与fetch并等待响应。

**为什么与边界：** fetch遇HTTP401通常仍resolve，所以下面必须检查ok。

<a id="L25"></a>
### 第 25 行

```typescript
    if (!response.ok) {
```

**语法与数据变化：** 非2xx进入错误分支。

**为什么与边界：** 不能直接把错误JSON当Hit[]展示。

<a id="L26"></a>
### 第 26 行

```typescript
      const hint = response.status === 401 ? "演示身份校验失败，请刷新页面后重新选择用户；无需 Agnes API Key。"
```

**语法与数据变化：** 401给出身份失败提示，明确不需Agnes Key。

**为什么与边界：** 正常选中演示用户的请求不应401；不能要求真实模型密钥来修这个演示身份问题。

<a id="L27"></a>
### 第 27 行

```typescript
        : response.status === 503 ? "服务端尚未启用虚构数据演示模式。"
```

**语法与数据变化：** 503提示服务未启用演示模式。

**为什么与边界：** 不同于无证据，属于服务配置状态。

<a id="L28"></a>
### 第 28 行

```typescript
        : response.status === 422 ? "查询参数无效，请检查问题和结果数量。"
```

**语法与数据变化：** 422提示输入参数失败。

**为什么与边界：** 可由Pydantic范围/类型检查触发，不是模型未回答。

<a id="L29"></a>
### 第 29 行

```typescript
        : "服务暂时不可用，请稍后重试。";
```

**语法与数据变化：** 其他状态使用有限通用提示，结束嵌套三元表达式。

**为什么与边界：** 不把服务端原始敏感错误体直接抛给页面。

<a id="L30"></a>
### 第 30 行

```typescript
      throw new Error(`HTTP ${response.status}：${hint}`);
```

**语法与数据变化：** 构造含HTTP状态和提示的Error并throw。

**为什么与边界：** 交给下面catch统一展示，而非继续解析为成功数据。

<a id="L31"></a>
### 第 31 行

```typescript
    }
```

**语法与数据变化：** 结束非ok分支。

**为什么与边界：** 只有正常HTTP才继续下一行。

<a id="L32"></a>
### 第 32 行

```typescript
    const hits: Hit[] = await response.json();
```

**语法与数据变化：** await解析响应JSON，编译期标成Hit[]。

**为什么与边界：** 没有运行时验证，畸形结构可能在map中报错；生产应补schema检查。

<a id="L33"></a>
### 第 33 行

```typescript
    //: 旧请求不能覆盖新结果；textContent 将内容当文本而非 HTML，减少 XSS 风险。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：旧请求不能覆盖新结果；textContent 将内容当文本而非 HTML，减少 XSS 风险。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L34"></a>
### 第 34 行

```typescript
    if (active !== controller) return;
```

**语法与数据变化：** 如果active已指向别的controller，立即返回。

**为什么与边界：** 旧请求即使完成也不能覆盖新结果；finally仍会执行。

<a id="L35"></a>
### 第 35 行

```typescript
    output.textContent = hits.length ? hits.map(hit => `${hit.title}\n来源：${hit.source}\n匹配分数：${hit.score}\n${hit.text}`).join("\n\n——\n\n") : "未找到词语匹配证据；这不证明资料中没有答案。";
```

**语法与数据变化：** 非空则map各候选为标题、来源、分数、原文，用分隔符join；空则显示词匹配不足提示。

**为什么与边界：** textContent减小XSS风险；词分数不是概率，候选也不是模型答案，空不证明资料无答案。

<a id="L36"></a>
### 第 36 行

```typescript
  } catch (error) {
```

**语法与数据变化：** catch接收任意捕获异常。

**为什么与边界：** 包括显式HTTP错误、网络失败、取消与JSON解析失败。

<a id="L37"></a>
### 第 37 行

```typescript
    if (active !== controller) return;
```

**语法与数据变化：** 旧请求的错误也不应覆盖新页面状态。

**为什么与边界：** 不能只在成功路径检查active。

<a id="L38"></a>
### 第 38 行

```typescript
    output.textContent = controller.signal.aborted ? "已取消" : String(error);
```

**语法与数据变化：** signal已aborted显示已取消，否则把错误转字符串。

**为什么与边界：** 不把取消混同服务失败；仍避免错误对象携带秘密。

<a id="L39"></a>
### 第 39 行

```typescript
  } finally {
```

**语法与数据变化：** finally无论成功、失败或try内return都执行。

**为什么与边界：** 用于清理当前状态，不是成功标志。

<a id="L40"></a>
### 第 40 行

```typescript
    if (active === controller) active = undefined;
```

**语法与数据变化：** 仅当active仍为本次控制器才清空。

**为什么与边界：** 旧请求清理不能把新请求的取消能力抹掉。

<a id="L41"></a>
### 第 41 行

```typescript
  }
```

**语法与数据变化：** 结束finally块。

**为什么与边界：** 没有额外请求或DOM更新。

<a id="L42"></a>
### 第 42 行

```typescript
});
```

**语法与数据变化：** 闭合回调和事件注册。

**为什么与边界：** 初始化时注册一次，实际检索要等用户提交。

## 跟一遍数据与验证边界

快速提交A再提交B：A被abort；即使A稍后返回，active身份检查也阻止覆盖B。取消不会保证服务端已停止所有工作。

## 只练一个关键点（不是新的学习验收记录）

1. 先npm构建，通过时对照active/controller三处比较。
2. 本课浏览器可用后快速提交两次并取消最新请求，记录页面是否被旧响应覆盖；未观察前不标E2E通过。
3. **复盘：** abort和结果身份检查为什么都保留？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
