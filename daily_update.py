#!/usr/bin/env python3
"""书斋每日更新: 知乎真实素材 → 加工 → 追加 daily.json
用法: python3 daily_update.py [--dry-run]
每个板块每天生成 N 篇(默认哲学3/广告4/故事3,可调),内容真实来源+评析,不重复。
"""
import json, os, subprocess, re, time, sys, datetime

BASE = '/Users/rocky-mei/Books/梅导书斋'
DATA = os.path.join(BASE, 'data')
CLI = "/Users/rocky-mei/Library/Application Support/zhihu-cli/current/zhihu-cli"
DEEPSEEK_KEY = None
for line in open('/Users/rocky-mei/.hermes/.env', encoding='utf-8'):
    if line.startswith('DEEPSEEK_API_KEY='):
        DEEPSEEK_KEY = line.strip().split('=', 1)[1]

# 每个板块的搜索主题池(轮换用,避免每天重复)
TOPICS = {
    "哲学": [
        "改变认知的哲学观点 具体事例", "人生顿悟的瞬间 经历",
        "哲学如何改变一个人", "值得反复思考的哲理",
        "认知升级 思维方式 实例", "存在主义 现代生活",
    ],
    "广告文案": [
        "经典广告文案 拆解 创意", "泰式广告 案例分析",
        "广告语 案例 爆款", "文案技巧 实战 案例",
        "品牌广告 情感营销 案例", "创意广告 神转折 分析",
    ],
    "故事": [
        "真实故事 感人 人生", "微小说 短篇 精彩",
        "民间故事 寓意 深刻", "人间真实 小故事",
        "寓言故事 现实 讽刺", "真实经历 改变人生",
    ],
}

def zhihu_search(query, count=5):
    """调知乎CLI搜索,返回内容条目"""
    try:
        r = subprocess.run([CLI, 'search', 'zhihu', '--query', query, '--count', str(count)],
                           capture_output=True, text=True, timeout=60)
        d = json.loads(r.stdout)
        items = d.get('Data', {}).get('Items', [])
        out = []
        for it in items:
            title = it.get('Title', '').replace(' - 知乎', '').strip()
            text = it.get('ContentText', '').strip()
            url = it.get('Url', '').split('?')[0]
            votes = it.get('VoteUpCount', 0)
            if text and len(text) > 100:
                out.append({"title": title, "text": text[:1500], "url": url, "votes": votes})
        return out
    except Exception as e:
        print(f"  搜索失败 {query}: {e}")
        return []

def gen_content(section, item):
    """DeepSeek加工: 从真实素材提炼 正文+评析"""
    if not DEEPSEEK_KEY:
        return None
    prompt = f"""你是一个内容编辑,把下面的{section}素材加工成一篇书斋短文。要求:
1. 正文:保留素材的**具体内容和真实细节**(事例、数据、原话都可以用),120-200字,不要空谈道理
2. 评析:从创作者/内容人视角点评"这篇好在哪/能怎么用",60-100字,具体
3. 输出格式严格:
【正文】
...
【评析】
..."""
    import urllib.request
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是资深内容编辑,输出克制、具体、有信息量,杜绝空话套话。"},
            {"role": "user", "content": f"素材标题: {item['title']}\n素材内容: {item['text'][:1200]}\n来源: {item['url']}\n\n{prompt}"}
        ],
        "max_tokens": 500, "temperature": 0.7,
    }
    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"  加工失败: {str(e)[:80]}")
        return None

def parse_output(text):
    body = re.search(r'【正文】\s*(.*?)(?=【评析】|$)', text, re.S)
    ping = re.search(r'【评析】\s*(.*)', text, re.S)
    return (body.group(1).strip() if body else ''), (ping.group(1).strip() if ping else '')

def main():
    dry = '--dry-run' in sys.argv
    today = datetime.date.today().isoformat()
    plan = {"哲学": 3, "广告文案": 4, "故事": 3}  # 每天10篇
    used_urls = set()  # 全库去重

    # 载入已用URL(去重) - 规范化:去 query、去尾部斜杠
    for sec in plan:
        f = os.path.join(DATA, sec, 'daily.json')
        if os.path.exists(f):
            for it in json.load(open(f, encoding='utf-8')):
                u = (it.get('url') or it.get('来源') or '').split('?')[0].rstrip('/')
                if u:
                    used_urls.add(u)

    for sec, need in plan.items():
        f = os.path.join(DATA, sec, 'daily.json')
        existing = json.load(open(f, encoding='utf-8')) if os.path.exists(f) else []
        # 已有 URL 集合(规范化)
        existing_urls = set()
        for it in existing:
            u = (it.get('来源') or '').split('?')[0].rstrip('/')
            if u:
                existing_urls.add(u)
        print(f"\n=== {sec}: 需要 {need} 篇,已有 {len(existing)} 篇 ===")
        added = 0
        topic_idx = 0
        while added < need and topic_idx < len(TOPICS[sec]) * 3:
            topic = TOPICS[sec][topic_idx % len(TOPICS[sec])]
            topic_idx += 1
            items = zhihu_search(topic, count=8)
            for it in items:
                url = it['url'].split('?')[0].rstrip('/')
                if url in used_urls or url in existing_urls:
                    continue
                if added >= need:
                    break
                print(f"  [{added+1}/{need}] {it['title'][:40]} ({it['votes']}赞)")
                if dry:
                    added += 1; used_urls.add(url); continue
                out = gen_content(sec, it)
                if not out:
                    continue
                body, ping = parse_output(out)
                if not body or not ping:
                    print("    加工结果格式异常,跳过")
                    continue
                existing.insert(0, {
                    "日期": today, "标题": it['title'],
                    "正文": body, "评析": ping, "来源": url, "赞": it['votes']
                })
                used_urls.add(url)
                added += 1
                time.sleep(1.5)
        if not dry and added:
            json.dump(existing, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print(f"  ✅ {sec}: 新增 {added} 篇 → 共 {len(existing)} 篇")
        else:
            print(f"  ({sec} 新增 {added} 篇)")

    # 重建书斋
    if not dry:
        print("\n=== 重新构建书斋 ===")
        r = subprocess.run([sys.executable, os.path.join(BASE, 'build_library_v2.py')],
                           capture_output=True, text=True, timeout=120)
        print(r.stdout[-500:] if r.stdout else r.stderr[-500:])

if __name__ == '__main__':
    main()
