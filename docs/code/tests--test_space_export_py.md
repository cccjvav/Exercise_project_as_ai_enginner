# Space导出白名单的静态回归：逐行精讲

[精讲总目录](index.md) · [对应源码](../../tests/test_space_export.py)

本页是提前备好的阅读材料，不表示学习者已学过或已通过。行号对应当前完整源码；空行和注释也列出，但重点是执行语句的数据变化与边界。

## 先知道它解决什么问题

检查打包内容及关键部署字段，避免把本地私密文件误放进云端导出。

### 输入、输出与调用关系

调用space_files获得路径到字节的字典，不上传、不构建镜像。

### 运行与风险边界

`python -m pytest tests/test_space_export.py -q`，离线，无需Hugging Face Key。

这些是静态约束测试，不是云端运行/E2E，也不是万能密钥扫描器。

## 完整源码

<!-- source: tests/test_space_export.py -->
```python
from tools.export_space import space_files


def test_bundle_has_no_private_inputs():
    files = space_files()
    assert "Dockerfile" in files and "app_port: 8000" in files["README.md"].decode()
    assert "--uid 1000" in files["Dockerfile"].decode()
    assert "localhost" not in files["frontend/client.ts"].decode().split('fetch(')[-1]
    for name in files:
        assert not name.startswith((".env", ".git/", "artifacts/", "data/raw/", "data/processed/"))
        assert "node_modules" not in name and "AGNES_API_KEY=" not in files[name].decode(errors="ignore")
    assert "src/evidencedesk/api.py" in files and "data/sample/webhook-delivery.md" in files
```

## 逐行：语法、数据变化、理由与边界

同一条调用跨多行时，每行解释自己的参数或字段；同一物理行包含多个语句时，解释按执行次序展开。不用把闭合括号误读为另一次调用。

<a id="L1"></a>
### 第 1 行

```python
from tools.export_space import space_files
```

**语法与数据变化：** 从仓库工具导入space_files函数。

**为什么与边界：** 导入不会运行导出CLI，但模块顶层常量会建立；真正读取白名单文件发生在调用时。

<a id="L2"></a>
### 第 2 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L3"></a>
### 第 3 行

空行分隔相邻逻辑，不创建变量、不读写文件，也不改变控制流。阅读时仍保留行号，方便与源文件定位一致。

<a id="L4"></a>
### 第 4 行

```python
def test_bundle_has_no_private_inputs():
```

**语法与数据变化：** 定义导出安全边界测试。

**为什么与边界：** 名字强调不包含私密输入，实际覆盖范围由下面断言决定。

<a id="L5"></a>
### 第 5 行

```python
    files = space_files()
```

**语法与数据变化：** 读取白名单文件成字节字典。

**为什么与边界：** 不创建ZIP、不上传账号，也不读取仓库每一个文件。

<a id="L6"></a>
### 第 6 行

```python
    assert "Dockerfile" in files and "app_port: 8000" in files["README.md"].decode()
```

**语法与数据变化：** 要求Dockerfile存在且Space README配置端口8000。

**为什么与边界：** decode将文本字节还原字符串；只检查关键片段，不验证全部YAML或容器网络。

<a id="L7"></a>
### 第 7 行

```python
    assert "--uid 1000" in files["Dockerfile"].decode()
```

**语法与数据变化：** 要求镜像创建用户时指定UID1000。

**为什么与边界：** 静态包含字段不等于云平台已使用该用户启动成功。

<a id="L8"></a>
### 第 8 行

```python
    assert "localhost" not in files["frontend/client.ts"].decode().split('fetch(')[-1]
```

**语法与数据变化：** 检查client.ts最后一段fetch(之后不出现localhost。

**为什么与边界：** 是有限字符串启发式，可漏掉其他形式的错误URL，不是全面浏览器网络测试。

<a id="L9"></a>
### 第 9 行

```python
    for name in files:
```

**语法与数据变化：** 逐个审查导出字典里的路径。

**为什么与边界：** 只针对实际白名单输出，不是扫描所有本地文件。

<a id="L10"></a>
### 第 10 行

```python
        assert not name.startswith((".env", ".git/", "artifacts/", "data/raw/", "data/processed/"))
```

**语法与数据变化：** 禁止.env、.git、产物、原始/处理数据目录前缀。

**为什么与边界：** startsWith规则只覆盖列举的位置，新私密路径仍需人工评审。

<a id="L11"></a>
### 第 11 行

```python
        assert "node_modules" not in name and "AGNES_API_KEY=" not in files[name].decode(errors="ignore")
```

**语法与数据变化：** 禁止node_modules路径和文本中的AGNES_API_KEY=赋值样式。

**为什么与边界：** decode(errors=ignore)跳过不可解码字节，只是粗检查，不能识别所有类型或格式的秘密。

<a id="L12"></a>
### 第 12 行

```python
    assert "src/evidencedesk/api.py" in files and "data/sample/webhook-delivery.md" in files
```

**语法与数据变化：** 确认API和公开Webhook样例确实被带入。

**为什么与边界：** 安全导出不能只靠删空一切通过禁止检查，还必须带上运行所需核心文件。

## 跟一遍数据与验证边界

如果导出含.env或node_modules，这些断言应失败；Dockerfile有UID1000和README端口8000只证明配置存在，不证明远端构建成功。

## 只练一个关键点（不是新的学习验收记录）

1. 运行测试，逐个圈出禁止路径、部署字段和必需文件断言。
2. 检查localhost测试只覆盖最后一个fetch片段，列出它未覆盖的浏览器行为。
3. **复盘：** 静态白名单测试为何不是万能秘密扫描或云端E2E？

无需默写整份实现。涉及临时变异只在备份/副本里进行，完成后恢复；未来课程的联网、写库、上传和部署动作仍待相应阶段确认。

## 阅读完成不等于运行验收

本页逐行解释代码，不把源码中的 assert、测试 fixture 或演示输出冒充本轮实际运行结果。涉及网络、模型、数据库和部署的验证，仍按对应课程单独确认；报错时保留异常类型、输入与预期，不输出密钥。
