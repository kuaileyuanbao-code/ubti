import json
import os
from collections import Counter

from dotenv import load_dotenv
from flask import Flask, jsonify, request


load_dotenv()
app = Flask(__name__)

XINGCHEN_AGENT_URL = os.getenv("XINGCHEN_AGENT_URL", "")


PERSONAS = {
    "DDL-er": {
        "name": "最后一晚战神",
        "domain": "拖延 / DDL / 极限交付 / 自我欺骗",
        "verdict": "不是拖延，是把任务养到最后一晚再开盲盒。",
        "jab": "别人靠计划推进，你靠心率升高启动。",
        "advice": "把真实截止时间提前 24 小时，先交 60 分版本再优化。",
        "mates": "PLAN-er、TEAM-er",
        "risks": "长期项目、多人协作、需要持续反馈的任务",
    },
    "PPT-er": {
        "name": "改稿轮回人",
        "domain": "汇报 / PPT / 审美返工 / 老师灵感",
        "verdict": "你以为第 12 版是终稿，老师以为灵感刚开始。",
        "jab": "每一页都曾活过，也都被“再精简一下”送走过。",
        "advice": "先确认汇报目标和页数，再动手美化。",
        "mates": "PDF-er、MAIL-er",
        "risks": "中期汇报、答辩前夜、老师临时改方向",
    },
    "PDF-er": {
        "name": "文献屯屯鼠",
        "domain": "论文 / 文献 / 资料囤积 / 假装学术",
        "verdict": "下载时雄心万丈，打开时下次一定。",
        "jab": "你的文件夹很学术，你本人还在加载摘要。",
        "advice": "每次最多留 5 篇核心文献，每篇只写一句用途。",
        "mates": "PPT-er、LAB-er",
        "risks": "开题报告、综述作业、导师让你多看文献",
    },
    "XK-DOGE": {
        "name": "抢课赌命人",
        "domain": "选课 / 抢课 / 绩点 / 老师风评 / 信息差",
        "verdict": "抢到好课叫眼光，踩到雷课叫命。",
        "jab": "大学四年最像金融市场的，是选课系统和你的手速。",
        "advice": "查考核方式、给分分布和时间冲突。",
        "mates": "GPA-er、MUTE-er",
        "risks": "抢课系统开放前、补退选、听信玄学推荐",
    },
    "MUTE-er": {
        "name": "群聊潜水员",
        "domain": "群聊 / 通知 / 信息过载 / 消息逃避",
        "verdict": "99+ 不是消息，是一种背景装饰。",
        "jab": "只要不点开，世界就暂时没有任务。",
        "advice": "重要群置顶，每天固定 10 分钟清关键词。",
        "mates": "SIGN-er、DDL-er",
        "risks": "报名截止、临时改教室、辅导员深夜通知",
    },
    "TEAM-er": {
        "name": "小组兜底侠",
        "domain": "小组作业 / 分工 / 队友失踪 / 背锅",
        "verdict": "队友负责消失，你负责让项目看起来存在过。",
        "jab": "你说“都行”的那一刻，命运已经完成了分工。",
        "advice": "一开始写清任务、负责人和截止时间。",
        "mates": "MAIL-er、PLAN-er",
        "risks": "自由组队、期末大作业、队友说我都可以",
    },
    "CV-er": {
        "name": "简历精修怪",
        "domain": "实习 / 秋招 / 简历 / 投递焦虑",
        "verdict": "你把简历放进互联网海洋，然后等待奇迹洄游。",
        "jab": "感谢投递是你和世界最稳定的双向奔赴。",
        "advice": "每投 10 个岗位复盘一次 JD。",
        "mates": "MAIL-er、PPT-er",
        "risks": "秋招高峰、群里有人晒 offer、投递后没回音",
    },
    "NIGHT-er": {
        "name": "深夜审判官",
        "domain": "内耗 / 专业怀疑 / 深夜清醒 / 人生审判",
        "verdict": "白天正常运行，凌晨自动审判人生。",
        "jab": "你的理性白天上班，晚上交给情绪代班。",
        "advice": "凌晨不做人生重大决策，写下来白天再审。",
        "mates": "BED-er、PLAN-er",
        "risks": "考试周、找实习失败、刷到同龄人高光",
    },
    "BED-er": {
        "name": "床位绑定用户",
        "domain": "宿舍 / 外卖 / 低位移生活 / 出门困难",
        "verdict": "床是出生点，外卖架是远征终点。",
        "jab": "校内也算远方，出门需要完整心理建设。",
        "advice": "安排一个必须出门的小任务。",
        "mates": "RICE-er、8AM-er",
        "risks": "线下活动、早八、朋友说就在校内很近",
    },
    "RICE-er": {
        "name": "干饭雷达",
        "domain": "食堂 / 外卖 / 干饭路线 / 校园饮食",
        "verdict": "别人逛校园，你巡查食物供应链。",
        "jab": "哪个窗口不踩雷永远在线。",
        "advice": "保留一个稳定不踩雷食堂窗口。",
        "mates": "BED-er、CARD-er",
        "risks": "饭点排队、新窗口开业、朋友问吃什么",
    },
    "TUTOR-er": {
        "name": "导师语气分析师",
        "domain": "导师沟通 / 修改意见 / 科研表达 / 语义揣测",
        "verdict": "再看看可能是小修，可能是重开人生。",
        "jab": "你研究的不只是课题，还有导师语气里的省略号。",
        "advice": "沟通后用文字确认下一步。",
        "mates": "PDF-er、MAIL-er",
        "risks": "组会后、论文返修、导师回复嗯",
    },
    "LAB-er": {
        "name": "实验重开选手",
        "domain": "实验 / 数据 / 科研焦虑 / 结果不显著",
        "verdict": "你的数据不一定显著，你的黑眼圈很显著。",
        "jab": "实验重复三遍，结果各有立场。",
        "advice": "记录实验条件和失败原因。",
        "mates": "PDF-er、TUTOR-er",
        "risks": "实验复现、临近组会、数据和预期反着来",
    },
    "CARD-er": {
        "name": "余额蒸发受害者",
        "domain": "校园卡 / 消费 / 奶茶 / 余额焦虑",
        "verdict": "没买什么，但钱自己学会了离开。",
        "jab": "校园卡余额，是大学生最短的悬疑小说。",
        "advice": "每周看一次消费记录。",
        "mates": "RICE-er、PLAN-er",
        "risks": "奶茶第二杯半价、便利店路过、余额不足",
    },
    "SIGN-er": {
        "name": "二维码追光者",
        "domain": "讲座 / 活动 / 第二课堂 / 二维码迁徙",
        "verdict": "哪里有二维码，哪里就有你短暂而疲惫的文明。",
        "jab": "你不是参加活动，你是在给第二课堂补地图。",
        "advice": "优先选和综测、竞赛、简历相关的活动。",
        "mates": "MUTE-er、GPA-er",
        "risks": "临时活动通知、讲座扎堆、签到码出现 30 秒",
    },
    "RETAKE-er": {
        "name": "低空飘过大师",
        "domain": "期末 / 挂科 / 补考 / 绩点保卫",
        "verdict": "平时知识不认识你，补考前突然相认。",
        "jab": "不是不会，是知识和考试长期异地恋。",
        "advice": "每周留一次捡知识尸体的时间。",
        "mates": "EXAM-er、PLAN-er",
        "risks": "期末周、查成绩、老师说这题上课讲过",
    },
    "8AM-er": {
        "name": "早八断联用户",
        "domain": "早八 / 起床 / 课堂续航 / 睡眠债",
        "verdict": "闹钟响了，灵魂没接电话。",
        "jab": "你的身体到了教室，意识还在被窝里加载。",
        "advice": "早八前一晚别和短视频谈恋爱。",
        "mates": "BED-er、PLAN-er",
        "risks": "冬天早八、第一节点名、宿舍离教学楼远",
    },
    "MAIL-er": {
        "name": "老师您好编辑器",
        "domain": "邮件 / 老师沟通 / 礼貌内耗 / 措辞焦虑",
        "verdict": "老师您好四个字，炼了二十分钟。",
        "jab": "发送键不是按钮，是一次小型渡劫。",
        "advice": "准备 3 个常用邮件模板。",
        "mates": "TUTOR-er、CV-er",
        "risks": "联系导师、投递简历、催老师签字",
    },
    "LOVE404": {
        "name": "恋爱信号乱码机",
        "domain": "恋爱 / 暧昧 / 表情包解读 / 社交误判",
        "verdict": "别人是心动信号，你是请求超时。",
        "jab": "每一个表情包，都可能被你解析成期末大题。",
        "advice": "真诚表达比反复截图分析有效。",
        "mates": "NIGHT-er、RICE-er",
        "risks": "突然秒回、朋友圈点赞、聊天停在哈哈哈",
    },
    "JOB-er": {
        "name": "offer 漂流瓶",
        "domain": "求职 / 面试 / offer / 自我怀疑",
        "verdict": "你不是没上岸，只是还在互联网海面漂着。",
        "jab": "每次刷新邮箱，都是一次微型人生判决。",
        "advice": "拆成岗位表、简历版本、投递记录、面试复盘。",
        "mates": "CV-er、MAIL-er",
        "risks": "身边人拿 offer、面试后等通知、岗位关闭",
    },
    "GPA-er": {
        "name": "小数点守护者",
        "domain": "成绩 / 绩点 / 综测 / 排名焦虑",
        "verdict": "别人看分数，你看小数点后第二位。",
        "jab": "你的快乐有时候只差 0.01。",
        "advice": "保绩点没错，但别让每门课变成情绪股市。",
        "mates": "XK-DOGE、EXAM-er",
        "risks": "查分系统开放、综测排名、不给平时分细则",
    },
    "CLUB-er": {
        "name": "社团免费劳动力",
        "domain": "社团 / 学生组织 / 活动排期 / 免费劳动力",
        "verdict": "你以为加入的是社团，后来发现是项目制外包。",
        "jab": "青春确实精彩，主要精彩在排班表里。",
        "advice": "同时最多承担两个核心身份。",
        "mates": "SIGN-er、TEAM-er",
        "risks": "活动前一天、部长临时加需求、多个群同时 @你",
    },
    "ROOM-er": {
        "name": "宿舍忍耐大师",
        "domain": "宿舍关系 / 作息冲突 / 卫生分歧 / 人际忍耐",
        "verdict": "大学第一课不是高数，是如何在四人间保持体面。",
        "jab": "你每天都在学习一种叫我忍一下的高级沟通技术。",
        "advice": "小事提前说，规则写清楚。",
        "mates": "BED-er、MAIL-er",
        "risks": "熄灯后外放、卫生轮值、空调温度之争",
    },
    "EXAM-er": {
        "name": "考前玄学大师",
        "domain": "复习 / 考试 / 押题 / 临时抱佛脚",
        "verdict": "你复习的不只是知识，还有好运和祖传玄学。",
        "jab": "资料打印得越厚，心里越像已经学过。",
        "advice": "先做近三年题型，再背重点。",
        "mates": "RETAKE-er、GPA-er",
        "risks": "考前一晚、同学说这章不考、老师突然反押题",
    },
    "PLAN-er": {
        "name": "计划收藏家",
        "domain": "学习计划 / 自律失败 / App 打卡 / 间歇性上进",
        "verdict": "计划写得像论文，执行起来像失踪人口。",
        "jab": "你不是没有自律，只是它经常请假。",
        "advice": "每天只设 3 个任务。",
        "mates": "DDL-er、8AM-er",
        "risks": "新学期第一周、买新本子、下载第 6 个自律 App",
    },
}


QUESTIONS = [
    ("老师只说“随便做做”，你先？", [
        ("A", "先搭个大纲", ["PPT-er"]),
        ("B", "等等再说", ["DDL-er"]),
        ("C", "找往年参考", ["PDF-er"]),
        ("D", "问同学啥意思", ["TEAM-er", "MUTE-er"]),
    ]),
    ("班群突然 99+，你会？", [
        ("A", "先扫一眼", ["MUTE-er"]),
        ("B", "只搜关键词", ["PLAN-er", "MUTE-er"]),
        ("C", "先放着不看", ["DDL-er", "MUTE-er"]),
        ("D", "问朋友重点", ["MUTE-er", "SIGN-er"]),
    ]),
    ("选课马上开抢，你？", [
        ("A", "提前蹲点", ["XK-DOGE"]),
        ("B", "先查规则", ["XK-DOGE", "GPA-er"]),
        ("C", "差不多就行", ["BED-er"]),
        ("D", "总慢半拍", ["8AM-er", "RETAKE-er"]),
    ]),
    ("小组作业刚开始，你会？", [
        ("A", "哪里缺人补哪里", ["TEAM-er"]),
        ("B", "先定分工时间", ["PLAN-er", "TEAM-er"]),
        ("C", "负责展示效果", ["PPT-er"]),
        ("D", "先整理资料", ["PDF-er"]),
    ]),
    ("明天就要交，你会？", [
        ("A", "突然高效", ["DDL-er"]),
        ("B", "先慌再冲", ["NIGHT-er", "DDL-er"]),
        ("C", "找模板救命", ["PPT-er", "PDF-er"]),
        ("D", "先看别人进度", ["TEAM-er"]),
    ]),
    ("你的文件夹里最多？", [
        ("A", "一堆最终版", ["PPT-er"]),
        ("B", "收藏的资料", ["PDF-er"]),
        ("C", "不同版本的自己", ["CV-er", "JOB-er"]),
        ("D", "重新开始的计划", ["PLAN-er"]),
    ]),
    ("早八前 10 分钟，你？", [
        ("A", "人到魂没到", ["8AM-er"]),
        ("B", "醒来已错过", ["BED-er", "8AM-er"]),
        ("C", "靠目标硬撑", ["GPA-er"]),
        ("D", "先吃点东西", ["8AM-er", "RICE-er"]),
    ]),
    ("同学拿到 offer，你会？", [
        ("A", "打开机会清单", ["JOB-er"]),
        ("B", "怀疑一下人生", ["NIGHT-er", "JOB-er"]),
        ("C", "改改自己的包装", ["CV-er"]),
        ("D", "先收藏再说", ["DDL-er", "CV-er"]),
    ]),
    ("食堂开新窗口，你会？", [
        ("A", "直接试试", ["RICE-er"]),
        ("B", "先观察评价", ["RICE-er", "PLAN-er"]),
        ("C", "等别人踩雷", ["BED-er"]),
        ("D", "先看预算", ["CARD-er"]),
    ]),
    ("老师只回“嗯”，你会？", [
        ("A", "反复揣摩", ["TUTOR-er"]),
        ("B", "补充解释", ["MAIL-er", "TUTOR-er"]),
        ("C", "当作通过", ["DDL-er"]),
        ("D", "找人解读", ["TUTOR-er", "NIGHT-er"]),
    ]),
    ("实验结果不对，你先？", [
        ("A", "再试一遍", ["LAB-er"]),
        ("B", "查有没有先例", ["PDF-er", "LAB-er"]),
        ("C", "先记录下来", ["LAB-er", "PLAN-er"]),
        ("D", "先离开一下", ["RICE-er", "LAB-er"]),
    ]),
    ("校园卡刷不出来，你想？", [
        ("A", "钱去哪了", ["CARD-er"]),
        ("B", "小快乐太多了", ["CARD-er", "RICE-er"]),
        ("C", "先找人救急", ["LOVE404", "RICE-er"]),
        ("D", "打开账单审计", ["CARD-er", "PLAN-er"]),
    ]),
    ("讲座可去可不去，你看？", [
        ("A", "有没有加分", ["SIGN-er"]),
        ("B", "能不能写进经历", ["SIGN-er", "CV-er"]),
        ("C", "可能已经错过", ["MUTE-er"]),
        ("D", "要出门就再说", ["BED-er"]),
    ]),
    ("成绩快出了，你会？", [
        ("A", "盯死每一分", ["GPA-er"]),
        ("B", "只求过线", ["RETAKE-er"]),
        ("C", "先不敢看", ["MUTE-er", "NIGHT-er"]),
        ("D", "立刻算影响", ["GPA-er", "PLAN-er"]),
    ]),
    ("考前来不及了，你靠？", [
        ("A", "资料越多越稳", ["EXAM-er"]),
        ("B", "找规律和运气", ["EXAM-er", "RETAKE-er"]),
        ("C", "最后硬冲", ["DDL-er", "EXAM-er"]),
        ("D", "先写计划", ["PLAN-er"]),
    ]),
    ("给老师发消息前，你会？", [
        ("A", "改开头语气", ["MAIL-er"]),
        ("B", "找人看措辞", ["MAIL-er", "TUTOR-er"]),
        ("C", "拖到最后发", ["DDL-er", "MAIL-er"]),
        ("D", "写得像公文", ["MAIL-er"]),
    ]),
    ("室友外放很吵，你会？", [
        ("A", "先忍着", ["ROOM-er"]),
        ("B", "委婉提醒", ["MAIL-er", "ROOM-er"]),
        ("C", "自己隔离", ["MUTE-er", "ROOM-er"]),
        ("D", "把规则说清", ["PLAN-er", "ROOM-er"]),
    ]),
    ("社团临时派活，你会？", [
        ("A", "先接住再崩", ["CLUB-er"]),
        ("B", "问清要求", ["PLAN-er"]),
        ("C", "能不回就不回", ["MUTE-er"]),
        ("D", "边吐槽边做", ["TEAM-er", "CLUB-er"]),
    ]),
    ("TA 发来表情包，你会？", [
        ("A", "分析第二层意思", ["LOVE404"]),
        ("B", "拉朋友会诊", ["LOVE404", "NIGHT-er"]),
        ("C", "回安全答案", ["MUTE-er", "LOVE404"]),
        ("D", "立刻换话题", ["LOVE404"]),
    ]),
    ("新学期第一天，你会？", [
        ("A", "写完整计划", ["PLAN-er"]),
        ("B", "下载新工具", ["PLAN-er"]),
        ("C", "买点仪式感", ["PLAN-er", "GPA-er"]),
        ("D", "热血三分钟", ["BED-er", "DDL-er"]),
    ]),
    ("朋友问“吃什么”，你会？", [
        ("A", "直接给方案", ["RICE-er"]),
        ("B", "说随便但挑", ["RICE-er", "TEAM-er"]),
        ("C", "先看预算", ["CARD-er"]),
        ("D", "选最省事的", ["BED-er"]),
    ]),
    ("老师说“不够扎实”，你？", [
        ("A", "怀疑要全改", ["TUTOR-er"]),
        ("B", "补依据引用", ["PDF-er"]),
        ("C", "重做表达", ["PPT-er"]),
        ("D", "先确认意思", ["MAIL-er", "TUTOR-er"]),
    ]),
    ("项目会开始前，你想？", [
        ("A", "希望大家真做了", ["TEAM-er"]),
        ("B", "别又让我兜底", ["TEAM-er", "DDL-er"]),
        ("C", "先开记录模板", ["PLAN-er"]),
        ("D", "能不能不开", ["BED-er", "MUTE-er"]),
    ]),
    ("哪句话最让你一紧？", [
        ("A", "明天就要", ["DDL-er"]),
        ("B", "简单展示一下", ["PPT-er"]),
        ("C", "你再想想", ["TUTOR-er", "NIGHT-er"]),
        ("D", "大家自由安排", ["TEAM-er", "ROOM-er"]),
    ]),
]


def score_answers(answers: list[str]) -> dict:
    scores = Counter()
    late_scores = Counter()
    for index, answer in enumerate(answers):
        options = QUESTIONS[index][1]
        targets = next((item[2] for item in options if item[0] == answer), [])
        points = 2 if len(targets) == 1 else 1
        for persona in targets:
            scores[persona] += points
            if index >= 18:
                late_scores[persona] += 1

    ranked = sorted(
        PERSONAS,
        key=lambda key: (scores[key], late_scores[key], -list(PERSONAS).index(key)),
        reverse=True,
    )
    primary = ranked[0]
    secondary = next(key for key in ranked[1:] if key != primary)
    total = sum(scores.values()) or 1
    suffering = min(99, 58 + round((scores[primary] / total) * 120))
    return {
        "primary": primary,
        "secondary": secondary,
        "scores": dict(scores),
        "suffering": suffering,
        "answers": answers,
    }


@app.get("/")
def index():
    return ubti_page()


@app.get("/healthz")
def healthz():
    return jsonify({"ok": True})


@app.get("/ubti")
def ubti_page():
    avatar_path = "static/ubti-avatar.png"
    avatar_url = f"{request.url_root.rstrip('/')}/{avatar_path}"
    data = {
        "questions": [
            {
                "text": text,
                "options": [
                    {"key": key, "label": label, "targets": targets}
                    for key, label, targets in options
                ],
            }
            for text, options in QUESTIONS
        ],
        "personas": PERSONAS,
        "agentUrl": XINGCHEN_AGENT_URL,
    }
    payload = json.dumps(data, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>UBTI 大学生大型受苦指标</title>
  <meta name="description" content="UBTI 是一个面向大学生学习、生活、社交、科研、求职场景的娱乐型校园受苦人格测试。">
  <meta property="og:title" content="UBTI 大学生大型受苦指标">
  <meta property="og:description" content="不是测你是什么人，是测你在大学被什么反复暴打。">
  <meta property="og:image" content="{avatar_url}">
  <meta property="og:type" content="website">
  <link rel="icon" type="image/png" href="{avatar_path}">
  <link rel="apple-touch-icon" href="{avatar_path}">
  <style>
    :root {{
      --paper: #f7f8fb;
      --ink: #14171f;
      --muted: #697386;
      --line: #d7dce8;
      --blue: #2459ff;
      --green: #177a5b;
      --red: #c63d2f;
      --yellow: #f2b84b;
      --mint: #e9f7ef;
      --panel: #ffffff;
      --lilac: #ece7ff;
      --cyan: #dff8ff;
      --shadow: 0 18px 45px rgba(20, 23, 31, .12);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      background:
        linear-gradient(90deg, rgba(40,88,255,.055) 1px, transparent 1px),
        linear-gradient(0deg, rgba(40,88,255,.055) 1px, transparent 1px),
        var(--paper);
      background-size: 28px 28px;
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    button {{ font: inherit; }}
    .shell {{
      min-height: 100vh;
      display: grid;
      grid-template-columns: 280px minmax(0, 1fr);
    }}
    .rail {{
      border-right: 2px solid var(--ink);
      padding: 28px 22px;
      background: var(--panel);
      display: flex;
      flex-direction: column;
      gap: 24px;
    }}
    .brand {{
      display: grid;
      gap: 8px;
    }}
    .brand-kicker {{
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
      color: var(--muted);
      font-size: 12px;
      font-weight: 750;
      line-height: 1.2;
    }}
    .brand-mark {{
      display: inline-grid;
      place-items: center;
      height: 30px;
      padding: 0 10px;
      border: 2px solid var(--ink);
      background: #fff;
      color: var(--ink);
      font-size: 16px;
      font-weight: 950;
      border-radius: 8px;
      box-shadow: inset 0 -5px 0 var(--mint);
      flex: 0 0 auto;
    }}
    .brand-full {{
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    h1 {{
      font-size: 26px;
      line-height: 1.05;
      margin: 0;
      letter-spacing: 0;
    }}
    .sub {{
      color: var(--muted);
      line-height: 1.55;
      margin: 0;
      font-size: 14px;
    }}
    .meter {{
      display: grid;
      gap: 10px;
    }}
    .meter-row {{
      display: flex;
      justify-content: space-between;
      font-size: 13px;
      color: var(--muted);
    }}
    .bar {{
      height: 10px;
      border: 1px solid var(--ink);
      background: #fff;
      overflow: hidden;
    }}
    .bar span {{
      display: block;
      width: 0;
      height: 100%;
      background: var(--green);
      transition: width .2s ease;
    }}
    .mini-grid {{
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      gap: 6px;
    }}
    .dot {{
      aspect-ratio: 1;
      border: 1px solid var(--line);
      background: #fff;
    }}
    .dot.done {{ background: var(--blue); border-color: var(--ink); }}
    .content {{
      padding: 28px;
      display: grid;
      align-items: center;
    }}
    .quiz {{
      width: min(100%, 980px);
      margin: 0 auto;
      display: grid;
      gap: 18px;
    }}
    .topline {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
      color: var(--muted);
      font-size: 14px;
    }}
    .question-panel {{
      background: var(--panel);
      border: 2px solid var(--ink);
      box-shadow: var(--shadow);
      padding: 28px;
      display: grid;
      gap: 24px;
      border-radius: 8px;
    }}
    .question-title {{
      font-size: clamp(24px, 3vw, 34px);
      line-height: 1.16;
      margin: 0;
      letter-spacing: 0;
      overflow-wrap: anywhere;
    }}
    .options {{
      display: grid;
      gap: 12px;
    }}
    .other-box {{
      display: none;
      gap: 8px;
      margin-top: 4px;
    }}
    .other-box.active {{
      display: grid;
    }}
    .other-box textarea {{
      width: 100%;
      min-height: 92px;
      resize: vertical;
      border: 1.5px solid var(--ink);
      border-radius: 8px;
      padding: 12px;
      color: var(--ink);
      background: #fff;
      font: inherit;
      line-height: 1.5;
    }}
    .other-note {{
      margin: 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.5;
    }}
    .option {{
      width: 100%;
      min-height: 66px;
      border: 1.5px solid var(--ink);
      background: #fff;
      color: var(--ink);
      display: grid;
      grid-template-columns: 44px 1fr;
      align-items: center;
      text-align: left;
      padding: 10px 16px 10px 10px;
      cursor: pointer;
      transition: transform .12s ease, background .12s ease, box-shadow .12s ease;
      border-radius: 8px;
    }}
    .option:hover {{
      transform: translateY(-1px);
      box-shadow: 4px 4px 0 rgba(25, 32, 45, .18);
    }}
    .option.selected {{
      background: var(--cyan);
      box-shadow: 5px 5px 0 var(--blue);
    }}
    .key {{
      width: 34px;
      height: 34px;
      border: 1.5px solid var(--ink);
      display: grid;
      place-items: center;
      font-weight: 800;
      background: var(--yellow);
      border-radius: 7px;
    }}
    .option span:last-child {{
      line-height: 1.45;
      overflow-wrap: anywhere;
    }}
    .nav {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .btn {{
      min-height: 44px;
      border: 1.5px solid var(--ink);
      background: #fff;
      color: var(--ink);
      padding: 0 16px;
      cursor: pointer;
      font-weight: 700;
      border-radius: 8px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      text-decoration: none;
    }}
    .btn.primary {{
      background: var(--ink);
      color: #fff;
    }}
    .btn:disabled {{
      opacity: .45;
      cursor: not-allowed;
    }}
    .result {{
      display: none;
      width: min(100%, 980px);
      margin: 0 auto;
      background: #fff;
      border: 2px solid var(--ink);
      box-shadow: var(--shadow);
      border-radius: 8px;
      overflow: hidden;
    }}
    .result-head {{
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 16px;
      padding: 26px;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(135deg, var(--cyan), var(--lilac));
      align-items: start;
    }}
    .result-visual {{
      display: grid;
      justify-items: center;
      gap: 12px;
    }}
    .persona-art {{
      width: 142px;
      aspect-ratio: 1;
      object-fit: contain;
      border-radius: 8px;
      background: rgba(255,255,255,.48);
    }}
    .result-code {{
      font-size: clamp(42px, 8vw, 86px);
      font-weight: 950;
      line-height: .95;
      margin: 0;
      letter-spacing: 0;
    }}
    .result-name {{
      margin: 8px 0 0;
      font-size: clamp(22px, 4vw, 36px);
    }}
    .score {{
      border: 2px solid var(--ink);
      min-width: 124px;
      height: 124px;
      display: grid;
      place-items: center;
      background: #fff;
      font-weight: 900;
      font-size: 28px;
      text-align: center;
      border-radius: 8px;
      box-shadow: inset 0 -12px 0 var(--mint);
    }}
    .result-body {{
      padding: 24px;
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px 18px;
    }}
    .block {{
      padding: 0;
      background: transparent;
    }}
    .block.wide {{ grid-column: 1 / -1; }}
    .block.highlight {{
      margin: 8px 0 2px;
      padding: 16px 0;
      border-top: 1px solid var(--line);
      border-bottom: 1px solid var(--line);
    }}
    .block.boost {{
      margin-top: 10px;
      padding: 18px;
      border: 1.5px solid var(--green);
      background: var(--mint);
      border-radius: 8px;
    }}
    .label {{
      color: var(--muted);
      font-size: 13px;
      margin-bottom: 8px;
    }}
    .text {{
      margin: 0;
      line-height: 1.65;
    }}
    .big-line {{
      font-size: clamp(20px, 3vw, 28px);
      font-weight: 850;
      line-height: 1.35;
    }}
    .fineprint {{
      grid-column: 1 / -1;
      margin: 2px 0 0;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.5;
    }}
    .actions {{
      padding: 0 24px 24px;
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .boost-actions {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 12px;
    }}
    .sub-actions {{
      grid-column: 1 / -1;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      padding-top: 8px;
      border-top: 1px solid var(--line);
    }}
    .sub-actions .btn {{
      min-height: 40px;
      padding: 8px 12px;
      font-size: 14px;
    }}
    .toast {{
      position: fixed;
      left: 50%;
      bottom: 22px;
      transform: translateX(-50%);
      background: var(--ink);
      color: #fff;
      padding: 10px 14px;
      display: none;
      font-size: 14px;
    }}
    @media (max-width: 780px) {{
      .shell {{ grid-template-columns: 1fr; }}
      .rail {{ border-right: 0; border-bottom: 1px solid var(--line); padding: 16px 18px; gap: 14px; }}
      .brand {{ gap: 7px; }}
      .brand-kicker {{ gap: 8px; }}
      .brand-mark {{ height: 28px; padding: 0 9px; font-size: 15px; }}
      h1 {{ font-size: 24px; }}
      .meter {{ gap: 8px; }}
      .mini-grid {{ display: none; }}
      .content {{ padding: 18px; align-items: start; }}
      .question-panel {{ padding: 18px; }}
      .question-title {{ font-size: 26px; }}
      .result-head {{ grid-template-columns: 1fr; }}
      .result-visual {{ justify-items: start; }}
      .persona-art {{ width: 128px; }}
      .score {{ width: 112px; height: 112px; }}
      .result-body {{ grid-template-columns: 1fr; padding: 18px; }}
      .actions {{ padding: 0 18px 18px; }}
      .actions .btn {{ flex: 1 1 120px; }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <aside class="rail">
      <div class="brand">
        <div class="brand-kicker"><span class="brand-mark">UBTI</span><span class="brand-full">Powered by Xingchen Agent</span></div>
        <h1>大学生大型受苦指标</h1>
        <p class="sub">先测出你的校园受苦人格，想深入分析再交给星辰 Agent。</p>
      </div>
      <div class="meter">
        <div class="meter-row"><span id="progressText">第 1 / 24 题</span><span id="pickedText">0 已选</span></div>
        <div class="bar"><span id="barFill"></span></div>
        <div class="mini-grid" id="miniGrid"></div>
      </div>
    </aside>
    <main class="content">
      <section class="quiz" id="quiz">
        <div class="topline">
          <span id="domainHint">Xingchen Agent Campus Test</span>
          <span id="answerHint"></span>
        </div>
        <div class="question-panel">
          <h2 class="question-title" id="questionTitle"></h2>
          <div class="options" id="options"></div>
          <div class="other-box" id="otherBox">
            <textarea id="otherInput" placeholder="写下你的真实反应。"></textarea>
          </div>
          <div class="nav">
            <button class="btn" id="prevBtn" type="button">上一题</button>
            <button class="btn primary" id="nextBtn" type="button">下一题</button>
          </div>
        </div>
      </section>
      <section class="result" id="result">
        <div class="result-head">
          <div>
            <p class="label">你的 UBTI 主人格</p>
            <h2 class="result-code" id="resultCode"></h2>
            <p class="result-name" id="resultName"></p>
          </div>
          <div class="result-visual">
            <img class="persona-art" id="personaArt" src="static/personas/DDL-er.webp" alt="UBTI 人格蛋">
            <div class="score"><span id="sufferScore"></span></div>
          </div>
        </div>
        <div class="result-body">
          <div class="block"><div class="label">副人格</div><p class="text" id="secondary"></p></div>
          <div class="block"><div class="label">今日自救</div><p class="text" id="advice"></p></div>
          <div class="block wide highlight"><div class="label">你最像的一句话</div><p class="text big-line" id="verdict"></p></div>
          <div class="block wide"><div class="label">分享文案</div><p class="text" id="shareText"></p></div>
          <div class="block wide boost" id="agentBoost">
            <div class="label">想让 AI 分析你的情况？</div>
            <p class="text">复制你的 UBTI 结果，去星辰 Agent 继续聊。它会根据你的结果生成更贴脸的分析、自救计划和分享文案。</p>
            <div class="boost-actions">
              <button class="btn primary" id="agentCopyBtn" type="button">复制结果，打开星辰 Agent</button>
            </div>
          </div>
          <div class="sub-actions">
            <button class="btn" id="shareSiteBtn" type="button">分享测试</button>
            <button class="btn" id="copySiteBtn" type="button">复制链接</button>
          </div>
          <p class="fineprint">UBTI 是娱乐型校园人格测试，不是心理诊断或专业测评。</p>
        </div>
        <div class="actions">
          <button class="btn primary" id="copyBtn" type="button">复制结果</button>
          <button class="btn" id="restartBtn" type="button">重新测试</button>
        </div>
      </section>
    </main>
  </div>
  <div class="toast" id="toast">已复制</div>
  <script src="static/config.js"></script>
  <script id="ubti-data" type="application/json">{payload}</script>
  <script>
    const data = JSON.parse(document.getElementById('ubti-data').textContent);
    const questions = data.questions;
    const personas = data.personas;
    const agentUrl = (window.UBTI_CONFIG && window.UBTI_CONFIG.agentUrl) || data.agentUrl || '';
    let current = 0;
    let answers = Array(questions.length).fill(null);
    let otherAnswers = Array(questions.length).fill('');
    let lastResultText = '';
    let lastAgentPrompt = '';
    let lastScored = null;

    const $ = (id) => document.getElementById(id);
    const miniGrid = $('miniGrid');
    if (!agentUrl) {{
      $('agentBoost').style.display = 'none';
    }}

    function siteUrl() {{
      const url = new URL(window.location.href);
      url.search = '';
      url.hash = '';
      return url.toString().replace(/index\\.html$/, '');
    }}

    function showToast(message = '已复制') {{
      $('toast').textContent = message;
      $('toast').style.display = 'block';
      setTimeout(() => $('toast').style.display = 'none', 1400);
    }}

    questions.forEach((_, index) => {{
      const dot = document.createElement('div');
      dot.className = 'dot';
      dot.addEventListener('click', () => {{
        current = index;
        renderQuestion();
      }});
      miniGrid.appendChild(dot);
    }});

    function scoreAnswers() {{
      const scores = Object.fromEntries(Object.keys(personas).map((key) => [key, 0]));
      const late = Object.fromEntries(Object.keys(personas).map((key) => [key, 0]));
      answers.forEach((answer, index) => {{
        if (!answer) return;
        const option = questions[index].options.find((item) => item.key === answer);
        if (!option) return;
        const points = option.targets.length === 1 ? 2 : 1;
        option.targets.forEach((target) => {{
          scores[target] += points;
          if (index >= 18) late[target] += 1;
        }});
      }});
      const ranked = Object.keys(personas).sort((a, b) => {{
        if (scores[b] !== scores[a]) return scores[b] - scores[a];
        if (late[b] !== late[a]) return late[b] - late[a];
        return Object.keys(personas).indexOf(a) - Object.keys(personas).indexOf(b);
      }});
      const total = Object.values(scores).reduce((sum, value) => sum + value, 0) || 1;
      const suffering = Math.min(99, 58 + Math.round((scores[ranked[0]] / total) * 120));
      return {{ primary: ranked[0], secondary: ranked[1], scores, suffering }};
    }}

    function renderQuestion() {{
      const picked = answers.filter(Boolean).length;
      $('progressText').textContent = `第 ${{current + 1}} / ${{questions.length}} 题`;
      $('pickedText').textContent = `${{picked}} 已选`;
      $('barFill').style.width = `${{(picked / questions.length) * 100}}%`;
      [...miniGrid.children].forEach((dot, index) => dot.classList.toggle('done', Boolean(answers[index])));
      const question = questions[current];
      $('questionTitle').textContent = question.text;
      $('answerHint').textContent = answers[current] ? `已选 ${{answers[current]}}` : '未选择';
      $('prevBtn').disabled = current === 0;
      $('nextBtn').textContent = current === questions.length - 1 ? '查看结果' : '下一题';
      $('nextBtn').disabled = !answers[current] || (answers[current] === 'OTHER' && !otherAnswers[current].trim());
      const options = $('options');
      options.innerHTML = '';
      question.options.forEach((option) => {{
        const button = document.createElement('button');
        button.type = 'button';
        button.className = `option ${{answers[current] === option.key ? 'selected' : ''}}`;
        button.innerHTML = `<span class="key">${{option.key}}</span><span>${{option.label}}</span>`;
        button.addEventListener('click', () => {{
          answers[current] = option.key;
          if (current < questions.length - 1) {{
            current += 1;
            renderQuestion();
          }} else {{
            renderQuestion();
          }}
        }});
        options.appendChild(button);
      }});
      const otherButton = document.createElement('button');
      otherButton.type = 'button';
      otherButton.className = `option ${{answers[current] === 'OTHER' ? 'selected' : ''}}`;
      otherButton.innerHTML = `<span class="key">?</span><span>其他，我不在这四个里</span>`;
      otherButton.addEventListener('click', () => {{
        answers[current] = 'OTHER';
        renderQuestion();
        setTimeout(() => $('otherInput').focus(), 0);
      }});
      options.appendChild(otherButton);
      $('otherBox').classList.toggle('active', answers[current] === 'OTHER');
      $('otherInput').value = otherAnswers[current] || '';
    }}

    function showResult() {{
      const missing = answers.findIndex((answer) => !answer);
      if (missing !== -1) {{
        current = missing;
        renderQuestion();
        return;
      }}
      const scored = scoreAnswers();
      lastScored = scored;
      const primary = personas[scored.primary];
      const secondary = personas[scored.secondary];
      $('resultCode').textContent = scored.primary;
      $('resultName').textContent = primary.name;
      $('personaArt').src = `static/personas/${{scored.primary}}.webp`;
      $('personaArt').alt = `${{scored.primary}}｜${{primary.name}} 人格蛋`;
      $('sufferScore').innerHTML = `${{scored.suffering}}<br><span style="font-size:13px">受苦指数</span>`;
      $('secondary').textContent = `${{scored.secondary}}｜${{secondary.name}}`;
      $('verdict').textContent = primary.verdict;
      $('advice').textContent = primary.advice;
      const share = `我测出了 ${{scored.primary}}｜${{primary.name}}。笑死，不是性格，是大学给我的工伤鉴定。`;
      $('shareText').textContent = share;
      lastAgentPrompt = [
        '我的 UBTI 测试结果：',
        `主人格：${{scored.primary}}｜${{primary.name}}`,
        `副人格：${{scored.secondary}}｜${{secondary.name}}`,
        `受苦指数：${{scored.suffering}}/100`,
        `受苦领域：${{primary.domain}}`,
        `人格判词：${{primary.verdict}}`,
        `自救建议：${{primary.advice}}`,
        '',
        '请基于这个结果继续分析我的情况，给我更贴脸的 AI 补刀、3 条今日自救任务和一条朋友圈文案。'
      ].join('\\n');
      lastResultText = [
        `我的 UBTI 主人格：${{scored.primary}}｜${{primary.name}}`,
        `副人格：${{scored.secondary}}｜${{secondary.name}}`,
        `受苦指数：${{scored.suffering}}/100`,
        `最像的一句话：${{primary.verdict}}`,
        `自救建议：${{primary.advice}}`,
        `分享文案：${{share}}`,
        `测试入口：${{siteUrl()}}`,
        agentUrl ? `星辰 Agent 深度分析入口：${{agentUrl}}` : ''
      ].filter(Boolean).join('\\n');
      $('quiz').style.display = 'none';
      $('result').style.display = 'block';
    }}

    $('prevBtn').addEventListener('click', () => {{
      if (current > 0) {{
        current -= 1;
        renderQuestion();
      }}
    }});
    $('nextBtn').addEventListener('click', () => {{
      if (current === questions.length - 1) showResult();
      else {{
        current += 1;
        renderQuestion();
      }}
    }});
    $('otherInput').addEventListener('input', (event) => {{
      otherAnswers[current] = event.target.value;
      $('nextBtn').disabled = !event.target.value.trim();
    }});
    $('restartBtn').addEventListener('click', () => {{
      answers = Array(questions.length).fill(null);
      otherAnswers = Array(questions.length).fill('');
      current = 0;
      lastScored = null;
      lastAgentPrompt = '';
      $('result').style.display = 'none';
      $('quiz').style.display = 'grid';
      renderQuestion();
    }});
    $('agentCopyBtn').addEventListener('click', async () => {{
      if (!agentUrl || !lastAgentPrompt) return;
      try {{
        await navigator.clipboard.writeText(lastAgentPrompt);
        showToast('已复制，去星辰继续追问');
      }} catch (error) {{
        showToast('已打开 Agent，请手动粘贴结果');
      }}
      window.open(agentUrl, '_blank', 'noopener');
    }});
    $('copyBtn').addEventListener('click', async () => {{
      await navigator.clipboard.writeText(lastResultText);
      showToast('结果已复制');
    }});
    $('copySiteBtn').addEventListener('click', async () => {{
      await navigator.clipboard.writeText(siteUrl());
      showToast('网站链接已复制');
    }});
    $('shareSiteBtn').addEventListener('click', async () => {{
      const text = '来测测你的 UBTI 大学生大型受苦指标，看看你在大学被什么反复暴打。';
      if (navigator.share) {{
        try {{
          await navigator.share({{ title: 'UBTI 大学生大型受苦指标', text, url: siteUrl() }});
          return;
        }} catch (error) {{}}
      }}
      await navigator.clipboard.writeText(`${{text}}\\n${{siteUrl()}}`);
      showToast('分享文案已复制');
    }});
    renderQuestion();
  </script>
</body>
</html>"""


@app.post("/api/ubti/result")
def api_ubti_result():
    body = request.get_json(force=True) or {}
    answers = body.get("answers", [])
    if len(answers) != len(QUESTIONS):
        return jsonify({"error": "Need 24 answers"}), 400
    if any(answer not in {"A", "B", "C", "D", "OTHER"} for answer in answers):
        return jsonify({"error": "Answers must be A/B/C/D/OTHER"}), 400
    result = score_answers(answers)
    return jsonify(result)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
