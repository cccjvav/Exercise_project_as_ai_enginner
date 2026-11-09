"""2A 闭卷小实现：自己写一遍分块区间。

文件已经建好，直接在下面函数的 raise 处改写即可。运行测试：

    python -m pytest tests/test_learning_02a.py -q

规则（与 src/evidencedesk/ingest.py 的 chunks 一致；写之前先不要打开它）：

- 步长 = size - overlap
- 起点依次是 0、步长、2 × 步长……
- 每块的 end = min(start + size, length)
- 某块 end 等于 length 时停止
- length 为 0 时返回空列表
- 参数不是 int（bool 也算不是 int），或 overlap 不满足 0 <= overlap < size，抛 ValueError

提示：两行参数校验 + 一个 for 循环；循环里三件事——算 end、append、(end == length) 就 break。
写对了 pytest 会显示 10 passed；失败时先看第一条：输入、你的输出、期望输出。
"""


def chunk_ranges(length: int, size: int, overlap: int) -> list[tuple[int, int]]:
    """返回半开区间 [start, end) 的列表。"""
    raise NotImplementedError("待实现：把这一行换成你的实现")
