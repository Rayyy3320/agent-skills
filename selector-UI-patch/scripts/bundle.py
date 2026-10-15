#!/usr/bin/env python3
"""预览 bundle 直取 + 编译树定位 —— selector-UI-patch 的核心执行器。

原理：市场页能渲染预览 ⇒ 渲染产物必须是 CDN 上无鉴权的公开静态文件
（否则匿名访客看不到预览）。浏览器看预览本来就要下载它，直接 GET
只是省掉渲染这一步。压缩产物保留 JSX 树、className 原文、props 属性名、
displayName、handler、动效参数 —— 足以按原始结构 1:1 重建源码。

用法：
    python3 bundle.py "<详情页 URL 或 bundle.html URL>" [-o 输出目录]
                     [--name InsuranceCard] [--props a,b,c] [--text "独特文案"]

    1. 给详情页 URL → 抓 SSR HTML，自动发现预览 bundle URL（cdn…/bundle.*.html），
       顺带收集 preview.*.png（视觉对照用）
    2. GET bundle 存盘 bundle.html（全量证据）
    3. 锚点定位组件编译树：
       displayName 锚  ,"InsuranceCard")   默认由 URL slug 转 PascalCase
       props 锚        ({clientName:…})=>  --props 或自动从 demo 数据对象提取
       文案锚          --text              只打印上下文，供人工圈定
    4. 输出 compiled-tree.js（反推依据）+ inventory.json
       （className 全集 / props / 动效参数 / handler / 全 bundle 组件名）

校验模式（重建完成后）：
    python3 bundle.py --check compiled-tree.js 重建.tsx [--demo demo.tsx]
    B 级（结构 1:1）：className 全集覆盖 + props 三方对齐 + 动效 token
    python3 bundle.py --check inventory.json 重建.tsx
    C 级（等效重建）：反向覆盖——重建件的每个 class 必须出自 bundle 原词汇表

退出码：0 成功 | 1 --check 有缺失 | 2 没发现 bundle URL | 3 树锚点未命中
        （码 3 时自动落盘全 bundle 清单 inventory.json，供 C 级等效重建）
"""
import argparse
import html as _html
import json
import os
import re
import sys
import urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")


def get(url, timeout=45):
    return urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": UA}), timeout=timeout
    ).read().decode("utf-8", "replace")


def pascal(slug):
    return "".join(p.title() for p in re.split(r"[^a-zA-Z0-9]+", slug) if p)


def discover(page_html):
    """从详情页 SSR HTML 里找预览产物 URL（RSC payload 会把 & 转义，先还原）。"""
    h = page_html.replace("\\u0026", "&").replace("\\/", "/")
    bundles = []
    for u in re.findall(r'https?://[^"\'<>\\ ]+?/bundle\.[\w.]+\.html[^"\'<>\\ ]*', h):
        if u not in bundles:
            bundles.append(u)
    iframes = re.findall(r'<iframe[^>]+src="([^"]+)"', h)
    pngs = []
    for u in re.findall(r'https?://[^"\'<>\\ ]+?/preview\.[\w.]+\.png', h):
        if u not in pngs and "cdn-cgi" not in u:
            pngs.append(u)
    return bundles, iframes, pngs


def _skip_string_back(src, i):
    """src[i] 是字符串的闭合引号；跳过整个字面量，返回开头引号前一位。
    引号前连续反斜杠为偶数才是真边界（处理转义引号 \\" 与 \\\\"）。"""
    q = src[i]
    i -= 1
    while i >= 0:
        if src[i] == q:
            k, j = 0, i - 1
            while j >= 0 and src[j] == "\\":
                k += 1
                j -= 1
            if k % 2 == 0:
                return i - 1
        i -= 1
    return -1


def _skip_string_fwd(src, i):
    """src[i] 是字符串的开启引号；返回闭合引号后一位。"""
    q = src[i]
    i += 1
    n = len(src)
    while i < n:
        if src[i] == "\\":
            i += 2
            continue
        if src[i] == q:
            return i + 1
        i += 1
    return -1


def back_call_start(src, pos):
    """从 pos 向前回溯找包裹当前实参的 '('。遇引号整段跳过字符串字面量
    —— children:["(",p,")"] 里的字面括号不能计入深度。
    局部跳跃而非全局扫描：bundle 里的正则/模板字面量会污染全局状态。"""
    depth = 0
    i = min(pos, len(src) - 1)
    while i >= 0:
        c = src[i]
        if c in "\"'`":
            i = _skip_string_back(src, i)
            continue
        if c in ")]}":
            depth += 1
        elif c in "([{":
            if depth == 0:
                return i
            depth -= 1
        i -= 1
    return -1


def fwd_match(src, i):
    """i 指向 '('，返回匹配 ')' 的后一位（跳过字符串字面量）。"""
    depth = 0
    n = len(src)
    while i < n:
        c = src[i]
        if c in "\"'`":
            i = _skip_string_fwd(src, i)
            if i < 0:
                return -1
            continue
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return -1


def extract_by_name(src, name):
    """displayName 锚：s((fn),"Name") 尾部的 ,"Name")。"""
    frags = []
    for q in ('"', "'"):
        anchor = f",{q}{name}{q})"
        start = 0
        while True:
            pos = src.find(anchor, start)
            if pos < 0:
                break
            s0 = back_call_start(src, pos - 1)
            if s0 >= 0:
                s1 = fwd_match(src, s0)
                if s1 > pos:
                    frags.append(src[s0:s1])
            start = pos + 1
    frags.sort(key=len, reverse=True)
    return frags


def extract_by_props(src, props):
    """props 锚：压缩形如 s(({clientName:a,…})=>{…},"Name")，
    解构紧跟包裹调用的 '('，从该 '(' 前向配对即整棵树。"""
    frags = []
    pat = re.compile(r'\(\{' + re.escape(props[0]) + r'\s*:')
    for mo in pat.finditer(src):
        s1 = fwd_match(src, mo.start())
        if s1 < 0:
            continue
        frag = src[mo.start():s1]
        if all(re.search(re.escape(p) + r"\s*:", frag) for p in props):
            frags.append(frag)
    frags.sort(key=len, reverse=True)
    return frags


def props_from_demo(page_html):
    """从 SSR 里的 demo 薄壳提取 props 锚点：数据对象键 + onXxx 回调名。"""
    pres = re.findall(r"<pre[^>]*>(.*?)</pre>", page_html, re.S)
    if not pres:
        return []
    demo = _html.unescape(re.sub(r"<[^>]+>", "", max(pres, key=len)))
    keys = re.findall(r"^\s*(\w+)\s*:\s*[\"']", demo, re.M)
    handlers = ["on" + h for h in re.findall(r"\bon(\w+)\s*=\s*\{", demo)]
    seen, out = set(), []
    for k in keys + handlers:
        if k not in seen:
            seen.add(k)
            out.append(k)
    return out


def _looks_component(frag):
    """过滤转发引用与库内部噪音：真组件定义必有函数体和 JSX 痕迹。"""
    if len(frag) < 80:
        return False
    has_fn = "=>" in frag or frag.lstrip().startswith("function")
    return has_fn and any(k in frag for k in ("children", "jsx", "className"))


def chase_def(src, var):
    """(VAR,"Name") 是转发引用；真身是 function VAR(…) 声明或 VAR=… 赋值。
    返回完整定义片段，失败返回 None。"""
    mo = re.search(r"\bfunction\s+" + re.escape(var) + r"\s*\(", src)
    if mo:
        q = fwd_match(src, mo.end() - 1)          # 参数列表 ) 之后
        b = q
        while b < len(src) and src[b] in " \n":
            b += 1
        if b < len(src) and src[b] == "{":
            e = fwd_match(src, b)
            if e > 0:
                return src[mo.start():e]
    for mo in re.finditer(r"[,;{(]\s*" + re.escape(var) + r"\s*=", src):
        i = mo.end()
        while i < len(src) and src[i] in " \n":
            i += 1
        j = i
        while j < len(src) and src[j] not in "({":
            j += 1
        if j < len(src):
            e = fwd_match(src, j)
            if e > 0:
                return src[i:e]
    return None


def _read_ident_back(src, i):
    """从 i 向前读一个标识符，返回其起始下标 - 1。"""
    j = i
    while j >= 0 and (src[j].isalnum() or src[j] in "_$"):
        j -= 1
    return j


def named_defs(src):
    """bundle 里全部 s(fn,"Name") 包装的组件定义：{name: {alias, code}}。
    shadcn 原语走 displayName= 赋值，不匹配此模式，不会混进来。
    `ga=s((fn),"InfoItem")` 里 frag 起点前的标识符是包装函数 s，
    再往前跨过 `=` 才是组件变量名 ga（主树里引用的就是它）。
    名字发现要兼容两种箭头体：表达式体结尾是 )，语句体 {return…} 结尾是 }。
    锚点若只命中 (VAR,"Name") 转发引用，追 VAR 的真身定义（function 声明或赋值）。"""
    out = {}
    for name in sorted(set(re.findall(
            r'[)}\]\w]\s*,\s*"([A-Z]\w+)"\s*\)', src))):
        frags = [f for f in extract_by_name(src, name) if _looks_component(f)]
        if frags:
            code = frags[0]
            s0 = src.find(code)
            j = _read_ident_back(src, s0 - 1)
            k = j
            while k >= 0 and src[k].isspace():
                k -= 1
            if k >= 0 and src[k] == "=":
                j = _read_ident_back(src, k - 1)
            out[name] = {"alias": src[j + 1:k] or src[j + 1:s0], "code": code}
            continue
        raw = extract_by_name(src, name)
        m = re.match(r"\(([\w$]+)\s*,", raw[0]) if raw else None
        if not m:
            continue
        chased = chase_def(src, m.group(1))
        if chased and _looks_component(chased):
            out[name] = {"alias": m.group(1), "code": chased}
    return out


def _primitives(src):
    """shadcn 原语走 .displayName="X" 赋值（社区组件走 s(fn,"X") 包装，互不干扰）。
    这份清单 = 组件的依赖 manifest（用哪些 ui 原语，一目了然）。"""
    return sorted(set(re.findall(r'displayName\s*[=:]\s*"(\w+)"', src)))


def bundle_inventory(src):
    """锚点未命中时的全 bundle 清单 —— C 级（等效重建）的原料：
    命名组件 / shadcn 原语依赖 / className 直方图 / 演示数据线索。"""
    inv = {}
    inv["named_components"] = {n: d["alias"] for n, d in named_defs(src).items()}
    inv["shadcn_primitives"] = _primitives(src)
    inv["motion"] = sorted(set(re.findall(
        r"(?:initial|animate|exit|whileHover|whileTap|whileInView|transition)"
        r"\s*:\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", src)))[:40]
    cnt = {}
    for c in re.findall(r'className:"([^"]{1,120})"', src):
        cnt[c] = cnt.get(c, 0) + 1
    inv["classNames_top"] = sorted(cnt.items(), key=lambda kv: -kv[1])[:60]
    inv["data_urls"] = sorted(set(re.findall(r'https?://[^"\'\\ )]+', src)))[:40]
    inv["emails"] = sorted(set(re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', src)))[:30]
    return inv


def inventory(frag, full_src):
    inv = {}
    inv["classNames"] = sorted(set(re.findall(r'className:"([^"]+)"', frag)))
    dm = re.search(r"\(\{([^}]*)\}", frag)   # 解构 ({props…})=>，允许外层先有 (
    inv["props"] = re.findall(r"(\w+)\s*:", dm.group(1)) if dm else []
    inv["motion"] = re.findall(
        r"(?:initial|animate|exit|whileHover|whileTap|whileInView|transition)"
        r"\s*:\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", frag)
    inv["handlers"] = sorted(set(re.findall(
        r"navigator\.\w+(?:\.\w+)*\([^)]*\)|window\.open\([^)]*\)", frag)))
    inv["events"] = sorted(set(re.findall(
        r"on(?:Click|Change|Submit|MouseEnter|MouseLeave|Focus|Blur)\s*:", frag)))
    inv["alias_map"] = {n: d["alias"] for n, d in named_defs(full_src).items()}
    inv["shadcn_primitives"] = _primitives(full_src)
    inv["lucide_hint"] = "bundle 内图标是别名；对照预览渲染 DOM 的 lucide-xxx class 识别"
    return inv


def check(tree_path, tsx_path, demo_path):
    tsx = open(tsx_path).read()
    norm = re.sub(r"\s+", "", tsx)

    if tree_path.endswith("inventory.json"):
        # C 级（等效重建）：反向覆盖——重建件的 class 词汇必须出自 bundle。
        # 不查 recall（bundle 里还有 app 外壳的 class，反向要求会全是误报）。
        inv = json.load(open(tree_path))
        vocab = set(inv.get("classNames") or [])
        for c, _ in inv.get("classNames_top", []):
            vocab.add(c)
        vtok = set()
        for c in vocab:
            vtok.update(c.split())
        used = set()
        for u in (re.findall(r'className="([^"]+)"', tsx)
                  + re.findall(r"className=\{`([^`]+)`\}", tsx)
                  + re.findall(r'cn\("([^"]+)"\)', tsx)):
            used.update(u.split())
        unknown = sorted(t for t in used if t not in vtok)
        print(f"C 级反向覆盖：重建件用 class {len(used)} 个，bundle 词汇表外 {len(unknown)}")
        for t in unknown[:20]:
            print(f"  ✗ {t}  (自造样式？应来自 bundle 原词汇)")
        ok = not unknown
        print("总体：" + ("通过 ✓ class 全部来自 bundle 原词汇" if ok else "有词汇表外的 class ✗"))
        return 0 if ok else 1

    # B 级（结构 1:1）：recall 方向——编译树的 class 全集必须都在重建件里。
    # 兄弟组件只并入被主树以 JSX 位置引用的；radix/motion 内部不算数，
    # 否则库内部的 className 会污染全集造成假失败。
    tree = open(tree_path).read()
    subs_path = tree_path.replace("compiled-tree.js", "compiled-subs.js")
    extra = ""
    if os.path.exists(subs_path):
        text = open(subs_path).read()
        heads = list(re.finditer(r"^// \w+ \(bundle alias: ([\w$]+)\)", text, re.M))
        for idx, mo in enumerate(heads):
            start = mo.end()
            end = heads[idx + 1].start() if idx + 1 < len(heads) else len(text)
            if re.search(r"jsxs?\(\s*" + re.escape(mo.group(1)) + r"\b", tree):
                extra += text[start:end]
    ok = True

    cls = sorted(set(re.findall(r'className:"([^"]+)"', tree + extra)))
    miss = [c for c in cls if c.replace(" ", "") not in norm.replace(" ", "")]
    print(f"className 全集（含子组件）：{len(cls)} 个，缺失 {len(miss)}")
    for c in miss:
        print(f"  ✗ {c}")
    ok &= not miss

    dm = re.search(r"\(\{([^}]*)\}", tree)
    props = re.findall(r"(\w+)\s*:", dm.group(1)) if dm else []
    missp = [p for p in props if not re.search(r"\b" + re.escape(p) + r"\b", tsx)]
    print(f"props（编译树 {len(props)} 个）：缺失 {missp or '无 ✓'}")
    ok &= not missp

    if demo_path:
        demo = open(demo_path).read()
        dprops = sorted(set(re.findall(r"^\s*(\w+)\s*:\s*[\"']", demo, re.M)))
        gap = [p for p in dprops if p not in props]
        print(f"demo 传参 {len(dprops)} 个，未进组件接口：{gap or '无 ✓'}")
        ok &= not gap

    toks = []
    for ms in re.findall(
            r"(?:initial|animate|exit|whileHover|whileTap|transition)"
            r"\s*:\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", tree + extra):
        toks += re.findall(r"\w+:[\d.]+", ms)
    missm = []
    for t in sorted(set(toks)):
        cands = {t, re.sub(r":\.", ":0.", t)}  # .5 与 0.5 等价
        if not any(c in norm for c in cands):
            missm.append(t)
    print(f"动效参数 token {len(set(toks))} 个，缺失 {missm or '无 ✓'}")
    ok &= not missm

    print("总体：" + ("全部通过 ✓" if ok else "有缺失，见上 ✗"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url", nargs="?", help="详情页 URL 或 bundle.html URL")
    ap.add_argument("-o", "--out", default=".")
    ap.add_argument("--name", help="组件 displayName（默认由 slug 转 PascalCase）")
    ap.add_argument("--props", help="逗号分隔 props 名（锚点/过滤用）")
    ap.add_argument("--text", help="独特文案：只打印命中上下文，供人工圈定")
    ap.add_argument("--check", nargs=2, metavar=("COMPILED_TREE", "REBUILT_TSX"))
    ap.add_argument("--demo", help="--check 模式下可选的 demo.tsx")
    a = ap.parse_args()

    if a.check:
        sys.exit(check(a.check[0], a.check[1], a.demo))
    if not a.url:
        ap.error("需要 URL，或用 --check TREE TSX 校验")

    os.makedirs(a.out, exist_ok=True)

    if "/bundle." in a.url:
        bundle_url, page_html = a.url, ""
    else:
        page_html = get(a.url)
        bundles, iframes, pngs = discover(page_html)
        if not bundles:
            bundles = [u for u in iframes if "/bundle." in u] or iframes
        if not bundles:
            print(f"SSR 里没发现 bundle URL（iframe×{len(iframes)}）。"
                  "上浏览器列 iframe 拿 src，或直接给 bundle URL。",
                  file=sys.stderr)
            sys.exit(2)
        bundle_url = bundles[0]
        if pngs:
            print(f"  视觉对照图: {pngs[0][:110]}")
        for b in bundles[1:3]:
            print(f"  另有 bundle: {b[:110]}")

    src = get(bundle_url)
    open(os.path.join(a.out, "bundle.html"), "w").write(src)
    print(f"bundle {len(src) // 1024}KB → {a.out}/bundle.html")

    m = (re.search(r"/components/([^/?#]+)", a.url)
         or re.search(r"/([a-z0-9-]+)/[a-z]+/bundle\.", bundle_url))
    name = a.name or (pascal(m.group(1)) if m else "")

    frags = []
    if name:
        raw = extract_by_name(src, name)
        frags = [f for f in raw if _looks_component(f)]
        if frags:
            print(f'displayName 锚命中：,"{name}") ×{len(frags)}')
        elif raw:
            m = re.match(r"\(([\w$]+)\s*,", raw[0])
            chased = chase_def(src, m.group(1)) if m else None
            if chased and _looks_component(chased):
                frags = [chased]
                print(f'锚点是转发引用 (VAR,"{name}")，已追到 VAR 真身定义')
    props = ([p.strip() for p in a.props.split(",")] if a.props
             else props_from_demo(page_html) if page_html else [])
    if not frags and props:
        frags = extract_by_props(src, props)
        if frags:
            print(f"props 锚命中：{props[:6]}…")
    if a.text:
        for mo in list(re.finditer(re.escape(a.text), src))[:3]:
            print(f"  文案锚 @{mo.start()}:\n    …{src[max(0, mo.start() - 150):mo.start() + 150]}…")
    if not frags:
        inv = bundle_inventory(src)
        open(os.path.join(a.out, "inventory.json"), "w").write(
            json.dumps(inv, indent=2, ensure_ascii=False))
        print(f"树锚点未命中（name={name!r}, props={props[:4]}）——"
              f"已落盘全 bundle 清单 → {a.out}/inventory.json", file=sys.stderr)
        print(f"  命名组件 {list(inv['named_components']) or '无'} | "
              f"shadcn 原语 {inv['shadcn_primitives'] or '无'} | "
              f"className×{len(inv['classNames_top'])} "
              f"url×{len(inv['data_urls'])} email×{len(inv['emails'])}", file=sys.stderr)
        print('  重试可换 --name（找 ,"Xxx") 模式）/ --props / --text；'
              "或按清单走 C 级等效重建（SKILL.md 产出分级），"
              "完成后 --check inventory.json 重建.tsx", file=sys.stderr)
        sys.exit(3)

    tree = frags[0]
    open(os.path.join(a.out, "compiled-tree.js"), "w").write(tree)
    prims = set(_primitives(src))
    subs = named_defs(src)
    with open(os.path.join(a.out, "compiled-subs.js"), "w") as f:
        f.write("// bundle 内其他命名组件定义。三类混居，按需取用：\n"
                "//   兄弟子组件（主树引用，重建需要）｜shadcn 原语（当依赖安装，"
                "不要重建）｜radix/framer-motion 内部（忽略）\n"
                "// 判断依据：主树里是否引用其 alias + inventory.json 的 shadcn_primitives\n\n")
        for n, d in subs.items():
            if d["code"] == tree:
                continue
            tag = "  [shadcn 原语：当依赖安装，不要重建]" if n in prims else ""
            f.write(f"// {n} (bundle alias: {d['alias']}){tag}\n{d['code']}\n\n")
    inv = inventory(tree, src)
    open(os.path.join(a.out, "inventory.json"), "w").write(
        json.dumps(inv, indent=2, ensure_ascii=False))
    nsubs = sum(1 for d in subs.values() if d["code"] != tree)
    print(f"compiled-tree.js {len(tree)} 字符 | "
          f"className×{len(inv['classNames'])} props×{len(inv['props'])} "
          f"motion×{len(inv['motion'])} | 其他命名组件×{nsubs} → {a.out}/")
    print("下一步：按 compiled-tree.js 反推 JSX（SKILL.md 反推规则表），完成后：")
    print(f"  bundle.py --check {a.out}/compiled-tree.js 重建.tsx --demo demo.tsx")


if __name__ == "__main__":
    main()
