# 浏览器入口与DOM契约：逐行精讲

[精讲总目录](index.md) · [对应源码](../../frontend/index.html)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

用最小表单提供虚构身份和查询入口，清楚标明展示的是候选证据。

### 输入、输出与调用关系

浏览器解析HTML/CSS，按模块加载/client.js；元素ID供client.ts定位。

### 运行与风险边界

先编译TypeScript，再通过API的静态路由打开页面；不是双击TS源码执行。

不含真实Key，公开身份不能作生产认证。表单约束只是用户体验，服务端必须重复校验。

## 完整源码

<!-- source: frontend/index.html -->
```html
<!doctype html>
<html lang="zh-CN">
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>EvidenceDesk · 课程演示</title>
<style>body{max-width:760px;margin:60px auto;padding:20px;background:#f4f5f1;color:#183d3b;font:17px/1.7 system-ui}input,select,button{font:inherit;padding:8px;margin:6px 0}input{width:90%}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:white;padding:20px;border-radius:10px}small{color:#58655e}</style>
<h1>EvidenceDesk</h1><p>候选证据检索 · 不是模型回答</p>
<small>仅用于虚构资料。选择下方演示用户即可，无需 Agnes 或 Hugging Face API Key。公开演示身份不能用作生产认证。</small>
<form id="search-form"><label>演示用户 <select id="token"><option value="demo-alice">Alice / alpha</option><option value="demo-bob">Bob / beta</option></select></label><br><label>问题 <input id="question" value="Webhook 重试多少次？" required maxlength="1000"></label><br><button>检索</button><button type="button" id="cancel">取消</button></form>
<pre id="output" role="status" aria-live="polite">输入问题，查看原文依据。</pre>
<script type="module" src="/client.js?v=demo-header-v2"></script>
</html>
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```html
<!doctype html>
```

**语法与数据变化：** HTML5文档类型声明，使浏览器按标准模式渲染。

**为什么与边界：** 不是可见标题，也不是引入外部DTD下载。

<a id="L2"></a>
### 第 2 行

```html
<html lang="zh-CN">
```

**语法与数据变化：** 打开根html，lang=zh-CN声明简体中文。

**为什么与边界：** 帮助辅助技术和语言识别，不自动翻译正文。

<a id="L3"></a>
### 第 3 行

```html
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
```

**语法与数据变化：** 同一行两条meta：UTF-8保证中文解码，viewport按设备宽度、初始缩放1。

**为什么与边界：** 浏览器可推断省略的head/body标签；元信息不等于界面正文。

<a id="L4"></a>
### 第 4 行

```html
<title>EvidenceDesk · 课程演示</title>
```

**语法与数据变化：** title定义标签页名称。

**为什么与边界：** 不同于下方可见h1，可帮助用户辨认课程演示。

<a id="L5"></a>
### 第 5 行

```html
<style>body{max-width:760px;margin:60px auto;padding:20px;background:#f4f5f1;color:#183d3b;font:17px/1.7 system-ui}input,select,button{font:inherit;padding:8px;margin:6px 0}input{width:90%}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:white;padding:20px;border-radius:10px}small{color:#58655e}</style>
```

**语法与数据变化：** 内联CSS：body限宽760、上下边距60且水平居中、内边距20、背景/文字色与17px/1.7系统字体；控件继承字体并加间距，input宽90%；pre保留换行且长词可断、白底圆角；small换次级颜色。

**为什么与边界：** CSS只影响展示，不能实施权限；移动端靠viewport及宽度约束仍需实际浏览器验收。

<a id="L6"></a>
### 第 6 行

```html
<h1>EvidenceDesk</h1><p>候选证据检索 · 不是模型回答</p>
```

**语法与数据变化：** h1品牌名和段落明确“候选证据检索，不是模型回答”。

**为什么与边界：** 防止把原文搜索结果包装成已核验生成答案。

<a id="L7"></a>
### 第 7 行

```html
<small>仅用于虚构资料。选择下方演示用户即可，无需 Agnes 或 Hugging Face API Key。公开演示身份不能用作生产认证。</small>
```

**语法与数据变化：** small说明仅虚构资料、选身份即可、不需外部API Key。

**为什么与边界：** 公开demo token只用于教学，不能上线保护真实客户数据。

<a id="L8"></a>
### 第 8 行

```html
<form id="search-form"><label>演示用户 <select id="token"><option value="demo-alice">Alice / alpha</option><option value="demo-bob">Bob / beta</option></select></label><br><label>问题 <input id="question" value="Webhook 重试多少次？" required maxlength="1000"></label><br><button>检索</button><button type="button" id="cancel">取消</button></form>
```

**语法与数据变化：** form提供与脚本匹配的ID；select两option的value发给后端；input默认问题且required/maxlength1000；首button默认submit，取消button明确type=button。

**为什么与边界：** label改善可访问性，br换行；取消若默认submit会误发请求；客户端限制可绕过，后端仍需校验。

<a id="L9"></a>
### 第 9 行

```html
<pre id="output" role="status" aria-live="polite">输入问题，查看原文依据。</pre>
```

**语法与数据变化：** pre输出区保留文本换行，role=status与aria-live=polite向辅助技术温和提示更新。

**为什么与边界：** 内容通过textContent写入，不把证据当HTML执行。

<a id="L10"></a>
### 第 10 行

```html
<script type="module" src="/client.js?v=demo-header-v2"></script>
```

**语法与数据变化：** 以module加载编译后的/client.js，查询串demo-header-v2用于区分旧缓存版本。

**为什么与边界：** 浏览器不直接执行client.ts；同源根路径适配代理，版本串也不保证所有旧缓存问题已消失。

<a id="L11"></a>
### 第 11 行

```html
</html>
```

**语法与数据变化：** 闭合html根元素。

**为什么与边界：** 省略的body/head由HTML解析规则处理，不是程序缺少导入语句。

## 跟一遍数据与验证边界

把#question或#output改名却不改client.ts会破坏DOM查找；浏览器不会从TypeScript泛型自动生成缺少的元素。

## 只练一个关键点（不是新的学习验收记录）

1. 逐个核对search-form、question、token、cancel、output与client.ts选择器。
2. 查看取消按钮type和script目标后缀；只编译，不把真实Key写进option。
3. **复盘：** 客户端required/maxlength为什么不能代替服务端验证？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
