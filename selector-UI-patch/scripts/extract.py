#!/usr/bin/env python3
"""从组件市场详情页抓出 demo 用法示例（selector-UI-patch 通道 1 执行器）。

用法：
    python3 extract.py "<详情页 URL>" [-o demo.tsx] [--proxy http://127.0.0.1:10808] [--pick N]

退出码：
    0  拿到真实源码（少数页面 SSR 直接下发实现）
    1  抓到内容但自检未全过（已存盘，供人工确认）
    2  页面无代码块 / --pick 越界
    3  只拿到 demo 薄壳 —— 预期路径，不是失败：转 scripts/bundle.py（通道 2）

注意：sys.exit("消息") 在 Python 里退出码恒为 1，要区分码必须 print(stderr) + sys.exit(N)
"""
import argparse
import html
import re
import sys
import urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")
strip = lambda s: re.sub(r"<[^>]+>", "", s)          # shiki 把每个 token 包进 <span>


def slug_of(url):
    """从详情页 URL 取组件 slug，用于识别「导入自己」的薄壳 demo。"""
    m = re.search(r"/components/([^/?#]+)", url)
    return m.group(1) if m else ""


def classify(code, slug):
    """判别抓到的是真实源码，还是只有用法示例。

    21st.dev 上大量组件页的 <pre> 只有 5~30 行的 demo 薄壳：
        import X from "@/components/ui/x"; export default function Demo(){ return <X/> }
    组件实现（const/function X）压根不在页面里 —— 这是信息不在场，任何解析技巧都取不到。
    """
    n = len(code.splitlines())
    imports_self = bool(slug) and bool(
        re.search(r'from\s+["\']@/components/ui/' + re.escape(slug) + r'["\']', code))
    # 组件实现不会 import 自己：import 自己的块按定义就是用法示例，与行数无关
    if imports_self:
        return 3, f"{n} 行的用法示例（import 本组件后渲染），实现源码不在页面里"
    if n < 12 and re.search(r"return\s*\(?\s*<\w+\s*/?>", code):
        return 3, f"仅 {n} 行的用法示例，实现源码未下发"
    ok = [code.lstrip().startswith(("'use client'", '"use client"', "import")),
          "export default" in code,
          80 <= n <= 400]
    return (0 if sum(ok) == 3 else 1), f"{n} 行 | 自检 {sum(ok)}/3 {ok}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url", help="组件详情页 URL")
    ap.add_argument("-o", "--out", default="demo.tsx",
                    help="demo 是用法示例不是组件实现，默认名就叫 demo.tsx")
    ap.add_argument("--proxy", help="如 http://127.0.0.1:10808")
    ap.add_argument("--pick", type=int, default=1, help="取第 N 长的代码块（默认 1）")
    a = ap.parse_args()

    if a.proxy:
        urllib.request.install_opener(urllib.request.build_opener(
            urllib.request.ProxyHandler({"http": a.proxy, "https": a.proxy})))

    h = urllib.request.urlopen(
        urllib.request.Request(a.url, headers={"User-Agent": UA}), timeout=45
    ).read().decode("utf-8", "replace")

    pres = re.findall(r"<pre[^>]*>(.*?)</pre>", h, re.S)
    if not pres:
        print(f"无 <pre>（页面 {len(h)}B, shiki={h.count('shiki')}）"
              f"→ 客户端渲染，源码不在 HTML 里，需走退路", file=sys.stderr)
        sys.exit(2)

    blocks = sorted(pres, key=lambda b: len(strip(b)), reverse=True)
    if not 1 <= a.pick <= len(blocks):
        print(f"只有 {len(blocks)} 个代码块，--pick {a.pick} 越界", file=sys.stderr)
        sys.exit(2)

    code = html.unescape(strip(blocks[a.pick - 1]))   # 实体 &lt; &quot; &#x27; 必须反转义
    rc, msg = classify(code, slug_of(a.url))
    print(f"{len(h)}B | <pre>×{len(pres)} | {msg} → {a.out}")
    open(a.out, "w").write(code)

    if rc == 3:
        print("\n[退出码 3] 页面只有 demo 用法示例 —— 预期路径，不是失败。", file=sys.stderr)
        print("  实现源码不在页面 HTML 里（信息不在场），重试 / 改 UA 无效；"
              "组件数据在预览渲染链路里。", file=sys.stderr)
        print("  下一步：python3 scripts/bundle.py <详情页URL> —— 自动发现预览 bundle、"
              "下载、锚定编译树并出反推清单；", file=sys.stderr)
        print("  本脚本存下的 demo.tsx 里的 props 名和文案就是 bundle.py 的定位锚点。",
              file=sys.stderr)
        sys.exit(3)

    if rc == 1:
        print("\n自检未全过（可能抓到了 install 命令块或过短片段）。各块预览，改 --pick N 重选：")
        for i, b in enumerate(blocks[:3], 1):
            first = html.unescape(strip(b)).strip().splitlines()
            print(f"  --pick {i}  {len(first):4d} 行  {first[0][:66] if first else '(空)'}")
        sys.exit(1)


if __name__ == "__main__":
    main()
