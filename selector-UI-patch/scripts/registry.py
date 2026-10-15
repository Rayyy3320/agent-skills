#!/usr/bin/env python3
"""从开源组件库直取组件源码 —— 免登录、免费、结构化。

市场站（21st.dev）的 /r/ 端点匿名 403（付费墙），但**同一组件的上游开源站是开放的**。
别在市场里抠，去上游拿：代码更全、更新，还不花钱。

用法：
    python3 registry.py <站点域名> <组件名> [--style new-york] [-o 输出目录]

    python3 registry.py magicui.design animated-beam
    python3 registry.py ui.shadcn.com button --style new-york

策略（依次尝试）：
    1. 站点 /r/<name>.json  —— shadcn registry 协议，JSON 里 files[].content 就是完整源码
    2. 站点 GitHub 仓库      —— trees API 定位同名 .tsx，再走 raw.githubusercontent 直取

退出码：0 成功 | 2 都没找到 | 3 GitHub API 速率超限（未认证 60 次/小时）
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")

# 实测（2026-09-04）：registry JSON 并非所有站都有，标 tpl=None 的只能走 GitHub
SITES = {
    "magicui.design":    {"gh": "magicuidesign/magicui",
                          "tpl": "https://magicui.design/r/{name}.json"},
    "ui.shadcn.com":     {"gh": "shadcn-ui/ui",
                          "tpl": "https://ui.shadcn.com/r/styles/{style}/{name}.json"},
    "ui.aceternity.com": {"gh": None, "tpl": None},   # /r/ 404
    "originui.com":      {"gh": None, "tpl": None},   # /r/ 非 JSON
    "reui.io":           {"gh": None, "tpl": None},   # /r/ 401
}


def get(url, timeout=25):
    return urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": UA}), timeout=timeout
    ).read().decode("utf-8", "replace")


def try_registry(tpl, name, style, outdir):
    """shadcn registry JSON —— 最干净的数据源。"""
    url = tpl.format(name=name, style=style)
    try:
        d = json.loads(get(url))
    except urllib.error.HTTPError as e:
        return 0, f"registry {e.code}"
    except Exception as e:
        return 0, f"registry 不可用（{str(e)[:30]}）"
    files = d.get("files", []) if isinstance(d, dict) else []
    if not files:
        return 0, "registry JSON 无 files 字段"
    for f in files:
        path = f.get("path") or f.get("target") or "component.tsx"
        dest = os.path.join(outdir, os.path.basename(path))
        open(dest, "w").write(f.get("content", ""))
        print(f"  ✓ {os.path.basename(path):38s} {len(f.get('content','').splitlines()):4d} 行")
    return len(files), url


def try_github(repo, name, outdir):
    """GitHub 兜底：trees API 定位文件 + raw 直取。"""
    if not repo:
        return 0, "该站点无已知 GitHub 仓库"
    try:
        tree = json.loads(get(f"https://api.github.com/repos/{repo}/git/trees/main?recursive=1"))
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print("  GitHub API 速率超限（未认证 60 次/小时），稍后再试或配 GITHUB_TOKEN",
                  file=sys.stderr)
            return 0, "rate limit"
        return 0, f"trees API {e.code}"
    if tree.get("truncated"):
        pass
    cands = [t["path"] for t in tree.get("tree", []) if t["type"] == "blob"
             and re.search(rf"/{re.escape(name)}\.(tsx|jsx)$", "/" + t["path"])]
    # 组件本体优先于 demo：路径里含 demo/example 的排后面
    cands.sort(key=lambda p: ("demo" in p.lower() or "example" in p.lower(), len(p)))
    if not cands:
        return 0, f"仓库里没有 {name}.tsx/.jsx"
    branch = "main"
    for p in cands[:1]:
        raw = get(f"https://raw.githubusercontent.com/{repo}/{branch}/{p}")
        dest = os.path.join(outdir, os.path.basename(p))
        open(dest, "w").write(raw)
        print(f"  ✓ {os.path.basename(p):38s} {len(raw.splitlines()):4d} 行  ({p})")
    return len(cands[:1]), f"github:{repo}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("site", help="站点域名或 registry URL，如 magicui.design")
    ap.add_argument("name", help="组件名，如 animated-beam")
    ap.add_argument("--style", default="new-york", help="shadcn 样式（default/new-york）")
    ap.add_argument("-o", "--out", default=".")
    ap.add_argument("--repo", help="手动指定 GitHub 仓库 owner/repo，覆盖内置表")
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    site = SITES.get(a.site, {"gh": a.repo, "tpl": None})
    if a.repo:
        site["gh"] = a.repo

    print(f"目标：{a.name} @ {a.site}\n")
    if site.get("tpl"):
        n, src = try_registry(site["tpl"], a.name, a.style, a.out)
        if n:
            print(f"\n成功：走 registry JSON（{src}），{n} 个文件 → {a.out}/")
            return
        print(f"  ✗ {src}，转 GitHub\n")
    else:
        print("  (该站点无可用 registry 端点，直接走 GitHub)\n")

    n, src = try_github(site.get("gh"), a.name, a.out)
    if n:
        print(f"\n成功：走 GitHub（{src}），{n} 个文件 → {a.out}/")
        return
    print(f"未找到。{src}", file=sys.stderr)
    print("  可加 --repo owner/repo 手动指定仓库；或让 agent 用 WebSearch 找组件的开源出处。",
          file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
