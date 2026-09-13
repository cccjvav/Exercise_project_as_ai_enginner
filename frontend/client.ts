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
