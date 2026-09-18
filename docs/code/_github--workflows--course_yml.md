# 无模型密钥的持续检查工作流：逐行精讲

[精讲总目录](index.md) · [对应源码](../../.github/workflows/course.yml)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

在push/PR自动复核测试、源码副本和前端构建，但不把CI当付费模型实验。

### 输入、输出与调用关系

GitHub Actions拉代码、装依赖、构建、跑测试和原八题评测。

### 运行与风险边界

由GitHub事件触发；本地等价命令见各run行。本轮本地结果与远端check状态分开报告。

offline指不调用在线模型，不是全程断网：取actions/依赖仍需网络。不能给不可信PR生产Secrets。

## 完整源码

<!-- source: .github/workflows/course.yml -->
```yaml
#: 8A：只跑无密钥测试；pull_request 不获得生产密钥或模型费用权限。
name: Course checks
on: [push, pull_request]
#: 最小权限只读仓库；测试不需要向 GitHub 或生产服务写入。
permissions:
  contents: read
jobs:
  offline:
    runs-on: ubuntu-latest
    steps:
      #: 按当前提交检出并固定 Python/Node 主版本；生产可进一步固定 action 提交摘要。
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      #: 先安装已测试依赖快照，再注册本地包；前端使用 npm lock 复现编译。
      - run: pip install -r requirements-tested.lock.txt && pip install --no-deps -e .
      - run: npm --prefix frontend ci --ignore-scripts && npm --prefix frontend run build
      #: 不调用在线模型；本地源码同步检查防止教材示例与实际实现漂移。
      - run: python -m pytest -q
      - run: python tools/check_course.py
      - run: python -m evidencedesk.evaluate --k 1
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```yaml
#: 8A：只跑无密钥测试；pull_request 不获得生产密钥或模型费用权限。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：8A：只跑无密钥测试；pull_request 不获得生产密钥或模型费用权限。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L2"></a>
### 第 2 行

```yaml
name: Course checks
```

**语法与数据变化：** 定义Actions界面中工作流名称。

**为什么与边界：** 不是Python模块名或服务器进程名。

<a id="L3"></a>
### 第 3 行

```yaml
on: [push, pull_request]
```

**语法与数据变化：** push和pull_request均触发。

**为什么与边界：** 同一变更可能产生不同事件运行，不表示重复业务写入。

<a id="L4"></a>
### 第 4 行

```yaml
#: 最小权限只读仓库；测试不需要向 GitHub 或生产服务写入。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：最小权限只读仓库；测试不需要向 GitHub 或生产服务写入。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L5"></a>
### 第 5 行

```yaml
permissions:
```

**语法与数据变化：** 开始声明工作流token权限。

**为什么与边界：** 遵守最小权限，避免默认获得不必要写能力。

<a id="L6"></a>
### 第 6 行

```yaml
  contents: read
```

**语法与数据变化：** 只允许读取仓库contents。

**为什么与边界：** 测试无需提交代码或管理生产资源。

<a id="L7"></a>
### 第 7 行

```yaml
jobs:
```

**语法与数据变化：** jobs映射包含待执行任务。

**为什么与边界：** 不是shell循环。

<a id="L8"></a>
### 第 8 行

```yaml
  offline:
```

**语法与数据变化：** 任务标识offline。

**为什么与边界：** 名字不保证网络隔离，实际run中会安装依赖。

<a id="L9"></a>
### 第 9 行

```yaml
    runs-on: ubuntu-latest
```

**语法与数据变化：** 使用ubuntu-latest runner。

**为什么与边界：** 系统版本可随平台变化，需记录环境，不应称完全固定镜像。

<a id="L10"></a>
### 第 10 行

```yaml
    steps:
```

**语法与数据变化：** 按顺序定义步骤。

**为什么与边界：** 前面失败时后续通常不会照常执行。

<a id="L11"></a>
### 第 11 行

```yaml
      #: 按当前提交检出并固定 Python/Node 主版本；生产可进一步固定 action 提交摘要。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：按当前提交检出并固定 Python/Node 主版本；生产可进一步固定 action 提交摘要。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L12"></a>
### 第 12 行

```yaml
      - uses: actions/checkout@v4
```

**语法与数据变化：** checkout取当前事件对应代码。

**为什么与边界：** @v4是可读主版本标签，生产可进一步固定提交摘要。

<a id="L13"></a>
### 第 13 行

```yaml
      - uses: actions/setup-python@v5
```

**语法与数据变化：** setup-python配置解释器。

**为什么与边界：** 不自动安装项目依赖。

<a id="L14"></a>
### 第 14 行

```yaml
        with:
```

**语法与数据变化：** with提供该action的输入参数。

**为什么与边界：** 缩进决定归属当前步骤。

<a id="L15"></a>
### 第 15 行

```yaml
          python-version: '3.11'
```

**语法与数据变化：** 使用Python3.11。

**为什么与边界：** 固定小系列而非补丁版本，不等于依赖锁。

<a id="L16"></a>
### 第 16 行

```yaml
      - uses: actions/setup-node@v4
```

**语法与数据变化：** setup-node配置Node。

**为什么与边界：** 与Python步骤服务不同构建工具链。

<a id="L17"></a>
### 第 17 行

```yaml
        with:
```

**语法与数据变化：** 开始Node action参数。

**为什么与边界：** 不是给后面npm脚本传业务变量。

<a id="L18"></a>
### 第 18 行

```yaml
          node-version: '22'
```

**语法与数据变化：** Node主版本22。

**为什么与边界：** 仍可能拿到更新补丁，构建复现还依赖锁文件。

<a id="L19"></a>
### 第 19 行

```yaml
      #: 先安装已测试依赖快照，再注册本地包；前端使用 npm lock 复现编译。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：先安装已测试依赖快照，再注册本地包；前端使用 npm lock 复现编译。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L20"></a>
### 第 20 行

```yaml
      - run: pip install -r requirements-tested.lock.txt && pip install --no-deps -e .
```

**语法与数据变化：** 安装Python快照后--no-deps注册本包。

**为什么与边界：** &&防前一步失败仍继续；网络安装不调用模型，但可遇版本/平台兼容问题。

<a id="L21"></a>
### 第 21 行

```yaml
      - run: npm --prefix frontend ci --ignore-scripts && npm --prefix frontend run build
```

**语法与数据变化：** npm ci按锁安装并禁生命周期脚本，然后tsc构建。

**为什么与边界：** 本地有JS不等于此步骤一定能从干净checkout复现。

<a id="L22"></a>
### 第 22 行

```yaml
      #: 不调用在线模型；本地源码同步检查防止教材示例与实际实现漂移。
```

这是源码注释，不是执行语句。它提醒本段的设计意图：不调用在线模型；本地源码同步检查防止教材示例与实际实现漂移。 实际是否满足要看随后的实现和测试，不能仅凭注释当成验证结论。

<a id="L23"></a>
### 第 23 行

```yaml
      - run: python -m pytest -q
```

**语法与数据变化：** 运行pytest收集测试。

**为什么与边界：** 可选依赖缺失的skip须看明细，不能仅看无失败就声称全功能通过。

<a id="L24"></a>
### 第 24 行

```yaml
      - run: python tools/check_course.py
```

**语法与数据变化：** 运行课程静态检查。

**为什么与边界：** 查源码副本/链接/语法，不评价解释深度或学习掌握。

<a id="L25"></a>
### 第 25 行

```yaml
      - run: python -m evidencedesk.evaluate --k 1
```

**语法与数据变化：** 执行原八题k1词检索评测。

**为什么与边界：** 不是九题回归、在线生成评测或自动性能提升判定。

## 跟一遍数据与验证边界

如果源码副本漂移check_course应失败；远端成功仍不证明Docker构建、浏览器代理、模型账户和托管DB可用。

## 只练一个关键点（不是新的学习验收记录）

1. 把各run行与本地命令对应，区分安装网络和模型调用。
2. 本地通过后再查看远端具体commit的Actions状态，不能从push成功推断CI成功。
3. **复盘：** offline任务名是否意味着所有步骤完全不联网？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
