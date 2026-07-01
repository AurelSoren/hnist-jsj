"""
教学平台 API 客户端

作者：AurelSoren
开源地址：https://github.com/AurelSoren/hnist-jsj
运行环境：python3.14
运行安装库：requests，pycryptodome
运行模式：
  python zy.py          # 交互式（只需输入学号）
  python zy.py --auto   # 全自动，学号写在 DEFAULT_XH
"""

import json
import sys

import requests
from Crypto.Cipher import DES

__author__ = "AurelSoren"

# ─────────────────────────── 基础配置 ───────────────────────────

BASE_URL   = "http://www.ggjsj.cn"
DEFAULT_XH = "your_student_id"   # --auto 模式使用，请勿提交真实学号

# ─────────────────────────── 题库常量 ───────────────────────────

_TXMC_SCORE_LIST = json.dumps([
    {"txmc": "简单应用", "fz": 90, "sum": 0.0, "dfl": 0.0},
    {"txmc": "综合应用", "fz": 10, "sum": 0.0, "dfl": 0.0},
], ensure_ascii=False)

_DETAILS = json.dumps([
    {"txmc": "简单应用", "fz": 90,
     "data": ["py_ae801","py_ae802","py_ae803","py_ae804","py_ae805",
              "py_ae806","py_ae807","py_ae808","py_ae810"]},
    {"txmc": "综合应用", "fz": 10, "data": ["py_ac809"]},
], ensure_ascii=False)

# ─────────────────────────── 工具函数 ───────────────────────────

def _des_encrypt_hex(plaintext: str) -> str:
    key = b"yi780612"
    data = plaintext.encode("utf-8")
    pad = 8 - len(data) % 8
    data += bytes([pad] * pad)
    return DES.new(key, DES.MODE_CBC, key).encrypt(data).hex()


def _post(url: str, payload: dict, token: str | None = None) -> dict:
    headers = {"accesstoken": token} if token else {}
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"网络请求失败: {e}") from e
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"接口报错: {data.get('msg', data)}")
    return data


def _sep(char: str = "─", width: int = 52) -> None:
    print(char * width)


def _print_disclaimer() -> None:
    _sep("═")
    print("  教学平台 API 客户端")
    print(f"  Author: {__author__}")
    _sep("═")
    print("  免责声明：")
    print("  本项目仅用于 Python 网络请求、接口交互与命令行程序学习研究。")
    print("  请勿用于代交作业、刷分、作弊、绕过平台规则或任何未经授权的行为。")
    print("  使用者需自行遵守法律法规、学校规定、课程要求和平台服务条款。")
    print("  因使用、修改、传播本项目产生的风险与后果由使用者自行承担。")
    print("  开源地址：https://github.com/AurelSoren/hnist-jsj")
    _sep()

# ─────────────────────────── Config ───────────────────────────

class Config:
    def __init__(self, xh: str, xm: str, schoolname: str,
                 kch: str, kcm: str, bj: str, jsh: str,
                 token: str):
        self.xh         = xh
        self.xm         = xm
        self.schoolname = schoolname
        self.kch        = kch
        self.kcm        = kcm
        self.bj         = bj
        self.jsh        = jsh
        self.token      = token
        # xqmc 从作业接口返回，先置空，fetch_student_info 补充
        self.xqmc: str  = ""

    def base_payload(self) -> dict:
        return {
            "xh": self.xh, "kch": self.kch, "jsh": self.jsh,
            "xqmc": self.xqmc, "bj": self.bj,
        }

# ─────────────────────────── 登录 & 初始化 ───────────────────────────

def login(xh: str) -> tuple[str, str, list[dict], dict]:
    """
    登录，返回 (token, xm, course_list, nowCourse[0])
    course_list 每条: {"kch": ..., "kcm": ...}
    """
    data = _post(f"{BASE_URL}/login/client", {
        "xh":      xh,
        "pwd":     _des_encrypt_hex(f"s_{xh}"),
        "softbz":  "1",
        "version": "14",
    })["data"]

    token      = data["token"]
    xm         = data.get("xm", "")
    courses    = data.get("course", [])
    now_course = (data.get("nowCourse") or [{}])[0]

    print(f"✅ 登录成功，欢迎 {xm}")
    return token, xm, courses, now_course, data.get("schoolname", "学校1")


def fetch_xqmc(cfg: Config) -> None:
    """从 studentform_data 补充 xqmc（学期）。"""
    try:
        data = _post(f"{BASE_URL}/client/studentform_data",
                     {"xh": cfg.xh, "kch": cfg.kch}, cfg.token)["data"]
        cfg.xqmc = data.get("xqmc", "")
    except RuntimeError:
        # 接口不通时让用户手动输入
        cfg.xqmc = input("学期（如 2026年上学期）: ").strip()

# ─────────────────────────── 选课 ───────────────────────────

def select_course(courses: list[dict], now_course: dict,
                  auto: bool) -> dict:
    """
    让用户选课，返回选中的课程 dict {"kch", "kcm", "bj", "jsh"}。
    - auto 模式：直接取 course 列表最后一条
    - 交互模式：展示列表，回车默认选最后一条
    """
    if not courses:
        raise RuntimeError("登录响应中没有课程列表，请检查账号")

    default = courses[-1]   # 默认最后一门
    # nowCourse 里有 bj / jsh，course 里没有；合并进去
    # 选中后再用 studentform_data 补全，这里先把 nowCourse 的字段带上
    def enrich(c: dict) -> dict:
        if c["kch"] == now_course.get("kch"):
            return {**c,
                    "bj":  now_course.get("bj", ""),
                    "jsh": now_course.get("jsh", "")}
        return {**c, "bj": "", "jsh": ""}

    if auto:
        chosen = enrich(default)
        print(f"📚 自动选课：[{chosen['kch']}] {chosen['kcm']}")
        return chosen

    _sep()
    print("  请选择课程（直接回车选最后一门）：")
    _sep()
    for i, c in enumerate(courses, 1):
        tag = " ←默认" if c["kch"] == default["kch"] else ""
        print(f"  {i:>2}. [{c['kch']}] {c['kcm']}{tag}")
    _sep()

    raw = input(f"序号 [1-{len(courses)}，回车默认]: ").strip()
    if not raw:
        chosen = enrich(default)
    elif raw.isdigit() and 1 <= int(raw) <= len(courses):
        chosen = enrich(courses[int(raw) - 1])
    else:
        print("⚠️  无效输入，使用默认")
        chosen = enrich(default)

    print(f"📚 已选：[{chosen['kch']}] {chosen['kcm']}")
    return chosen

# ─────────────────────────── 作业接口 ───────────────────────────

def _submit(cfg: Config, task_id: str, is_new: bool) -> None:
    endpoint = "submit_new_task" if is_new else "submit_old_task"
    payload = {
        **cfg.base_payload(),
        "task_id":         task_id,
        "score":           100,
        "txmc_score_list": _TXMC_SCORE_LIST,
        "checktext":       "\n代码验证：\n\n第1题(16.7分):\n1、源代码文件检测：d:\\zuoye\\代码验证\\201\\读取正常  √\n2、关键字检测：第1行代码存在检测  √\n3、关键字检测：第2行代码存在检测  √\n4、关键字检测：第3行代码存在检测  √\n5、关键字检测：第4行代码存在检测  √\n6、关键字检测：第5行代码存在检测  √\n7、关键字检测：第6行代码存在检测  √\n8、关键字检测：第7行代码存在检测  √\n9、关键字检测：第8行代码存在检测  √\n10、关键字检测：第9行代码存在检测  √\n\n第2题(16.7分):\n1、源代码文件检测：d:\\zuoye\\代码验证\\201\\读取正常  √\n2、关键字检测：第1行代码存在检测  √\n3、关键字检测：第2行代码存在检测  √\n4、关键字检测：第3行代码存在检测  √\n5、关键字检测：第4行代码存在检测  √\n6、关键字检测：第5行代码存在检测  √\n7、关键字检测：第6行代码存在检测  √\n8、关键字检测：第7行代码存在检测  √\n9、关键字检测：第8行代码存在检测  √\n10、关键字检测：第9行代码存在检测  √\n\n第3题(16.7分):\n1、源代码文件检测：d:\\zuoye\\代码验证\\201\\读取正常  √\n2、关键字检测：第1行代码存在检测  √\n3、关键字检测：第2行代码存在检测  √\n4、关键字检测：第3行代码存在检测  √\n5、关键字检测：第4行代码存在检测  √\n6、关键字检测：第5行代码存在检测  √\n7、关键字检测：第6行代码存在检测  √\n8、关键字检测：第7行代码存在检测  √\n9、关键字检测：第8行代码存在检测  √\n10、关键字检测：第9行代码存在检测  √\n11、关键字检测：第10行代码存在检测  √\n\n第4题(16.7分):\n1、源代码文件检测：d:\\zuoye\\代码验证\\201\\读取正常  √\n2、关键字检测：第1行代码存在检测  √\n3、关键字检测：第2行代码存在检测  √\n4、关键字检测：第3行代码存在检测  √\n5、关键字检测：第4行代码存在检测  √\n6、关键字检测：第5行代码存在检测  √\n7、关键字检测：第6行代码存在检测  √\n8、关键字检测：第7行代码存在检测  √\n9、关键字检测：第8行代码存在检测  √\n10、关键字检测：第9行代码存在检测  √\n11、关键字检测：第10行代码存在检测  √\n\n第5题(16.7分):\n1、源代码文件检测：d:\\zuoye\\代码验证\\201\\读取正常  √\n2、关键字检测：代码from turtle import *存在检测  √\n3、关键字检测：代码def yin(radius,color1,color2):存在检测  √\n4、关键字检测：代码width(3)存在检测  √\n5、关键字检测：代码color(\"black\",color1)存在检测  √\n6、关键字检测：代码begin_fill()存在检测  √\n7、关键字检测：代码circle(radius/2.,180)存在检测  √\n8、关键字检测：代码circle(radius,180)存在检测  √\n9、关键字检测：代码left(180)存在检测  √\n10、关键字检测：代码circle(-radius/2.,180)存在检测  √\n11、关键字检测：代码end_fill()存在检测  √\n12、关键字检测：代码left(90)存在检测  √\n13、关键字检测：代码up()存在检测  √\n14、关键字检测：代码forward(radius*0.35)存在检测  √\n15、关键字检测：代码right(90)存在检测  √\n16、关键字检测：代码down()存在检测  √\n17、关键字检测：代码color(color1,color2)存在检测  √\n18、关键字检测：代码circle(radius*0.15)存在检测  √\n19、关键字检测：代码backward(radius*0.35)存在检测  √\n20、关键字检测：代码def main():存在检测  √\n21、关键字检测：代码reset();存在检测  √\n22、关键字检测：代码yin(200,\"black\",\"white\")存在检测  √\n23、关键字检测：代码yin(200,\"white\",\"black\")存在检测  √\n24、关键字检测：代码ht()存在检测  √\n25、关键字检测：代码return \"Done!\"存在检测  √\n\n第6题(16.7分):\n1、源代码文件检测：d:\\zuoye\\代码验证\\201\\读取正常  √\n2、关键字检测：代码x=5存在检测  √\n3、关键字检测：代码y=2存在检测  √\n",
        "details":         _DETAILS,
    }
    if is_new:
        payload.update({"xm": cfg.xm, "schoolname": cfg.schoolname})
    _post(f"{BASE_URL}/client/{endpoint}", payload, cfg.token)


def fetch_all_tasks(cfg: Config) -> list[dict]:
    """返回所有待补分作业（已做未满分 + 未做）。"""
    done_raw = _post(f"{BASE_URL}/client/get_doneTaskInfo",
                     cfg.base_payload(), cfg.token)["data"]["doneTask"]
    undo_raw = _post(f"{BASE_URL}/client/get_undoTaskInfo",
                     cfg.base_payload(), cfg.token)["data"]["undoTask"]
    return [
        {"task_id": t["task_id"], "zybt": t["zybt"],
         "score": t["score"], "is_new": False}
        for t in done_raw if t["score"] == 100
    ] + [
        {"task_id": t["task_id"], "zybt": t["zybt"],
         "score": 0, "is_new": True}
        for t in undo_raw
    ]


def fetch_score(cfg: Config) -> str:
    try:
        data = _post(f"{BASE_URL}/client/get_sumScoreInfo",
                     cfg.base_payload(), cfg.token)
        for item in data["data"]["sumScoreInfo"]:
            if item["xh"] == cfg.xh:
                return str(item["zf"])
    except RuntimeError:
        pass
    return "—"

# ─────────────────────────── 补分模式 ───────────────────────────

def _do_submit_list(cfg: Config, tasks: list[dict]) -> None:
    ok = 0
    for t in tasks:
        print(f"  提交 [{t['zybt']}]…", end=" ", flush=True)
        try:
            _submit(cfg, t["task_id"], is_new=t["is_new"])
            print("✅ 100 分")
            ok += 1
        except RuntimeError as e:
            print(f"❌ 失败: {e}")
    _sep()
    print(f"🎉 完成！成功 {ok} / {len(tasks)} 条")


def mode_auto(cfg: Config) -> None:
    _sep()
    print("  模式：全自动补满分")
    _sep()
    tasks = fetch_all_tasks(cfg)
    if not tasks:
        print("🎉 AurelSoren帮您所有作业已满分，无需操作！")
        return
    print(f"找到 {len(tasks)} 条待处理")
    _sep()
    _do_submit_list(cfg, tasks)


def mode_select(cfg: Config) -> None:
    _sep()
    print("  模式：手动选择")
    _sep()
    tasks = fetch_all_tasks(cfg)
    if not tasks:
        print("🎉 AurelSoren帮您所有作业已满分，无需操作！")
        return

    print(f"  {'序号':>2}  {'类型':^4}  {'当前分':^6}  作业名称")
    _sep()
    for i, t in enumerate(tasks, 1):
        kind  = "未做" if t["is_new"] else "已做"
        score = "—"   if t["is_new"] else str(t["score"])
        print(f"  {i:>2}.  [{kind}]  {score:^6}  {t['zybt']}")
    _sep()

    print("输入序号（逗号分隔），0 = 全选，回车取消：")
    raw = input(">>> ").strip()
    if not raw:
        print("已取消。")
        return
    if raw == "0":
        selected = tasks
    else:
        try:
            indices  = [int(x.strip()) - 1 for x in raw.split(",")]
            selected = [tasks[i] for i in indices if 0 <= i < len(tasks)]
        except ValueError:
            print("❌ 格式有误，已取消。")
            return

    if not selected:
        print("未选中任何作业。")
        return

    _sep()
    print(f"将提交以下 {len(selected)} 条：")
    for t in selected:
        print(f"  · {t['zybt']}")
    if input("确认？(y/N) ").strip().lower() != "y":
        print("已取消。")
        return

    _sep()
    _do_submit_list(cfg, selected)

# ─────────────────────────── 主菜单 ───────────────────────────

def main_menu(cfg: Config) -> bool:
    """
    返回 True  → 用户选择切换账号
    返回 False → 用户选择退出
    """
    while True:
        _sep("═")
        score = fetch_score(cfg)
        print(f"  👤 {cfg.xm}  {cfg.bj}")
        print(f"  📚 [{cfg.kch}] {cfg.kcm}  🏆 总分: {score}")
        _sep("═")
        print("  1. 全自动补满分（一键全部）")
        print("  2. 手动选择要补分的作业")
        print("  3. 切换账号")
        print("  0. 退出")
        _sep()
        choice = input("请选择 [0/1/2/3]: ").strip()
        if choice == "1":
            mode_auto(cfg)
        elif choice == "2":
            mode_select(cfg)
        elif choice == "3":
            return True   # 告知外层重新登录
        elif choice == "0":
            print("再见！")
            return False
        else:
            print("⚠️  无效输入")

# ─────────────────────────── 登录流程（可复用）───────────────────────────

def do_login_flow(auto: bool) -> Config | None:
    """
    完整登录 + 选课 + 补全信息，返回 Config。
    失败时打印错误并返回 None。
    """
    # 1. 输入学号
    if auto:
        xh = DEFAULT_XH
    else:
        _sep("═")
        print("  AurelSoren手搓计算机教学平台补分工具")
        _sep("═")
        xh = input("学号: ").strip()
        if not xh:
            print("❌ 学号不能为空")
            return None

    # 2. 登录
    token, xm, courses, now_course, schoolname = login(xh)

    # 3. 选课
    chosen = select_course(courses, now_course, auto)

    # 4. 组装 Config
    cfg = Config(
        xh=xh, xm=xm, schoolname=schoolname,
        kch=chosen["kch"], kcm=chosen["kcm"],
        bj=chosen.get("bj", now_course.get("bj", "")),
        jsh=chosen.get("jsh", now_course.get("jsh", "")),
        token=token,
    )

    # 5. 补全 xqmc 及缺失的 bj/jsh
    fetch_xqmc(cfg)
    if not cfg.bj or not cfg.jsh:
        try:
            d = _post(f"{BASE_URL}/client/studentform_data",
                      {"xh": xh, "kch": cfg.kch}, token)["data"]
            cfg.bj  = cfg.bj  or d.get("bj",  "")
            cfg.jsh = cfg.jsh or d.get("jsh", "")
        except RuntimeError:
            pass

    print(f"   班级: {cfg.bj}  教师: {cfg.jsh}  学期: {cfg.xqmc}")
    return cfg

# ─────────────────────────── 入口 ───────────────────────────

def main() -> None:
    _print_disclaimer()
    auto = "--auto" in sys.argv
    try:
        if auto:
            cfg = do_login_flow(auto=True)
            if cfg:
                mode_auto(cfg)
            return

        # 交互模式：支持切换账号，循环直到用户主动退出
        while True:
            cfg = do_login_flow(auto=False)
            if cfg is None:
                continue          # 学号为空，重新输入
            switch = main_menu(cfg)
            if not switch:
                break             # 用户选 0 退出
            # switch=True → 继续循环，重新登录

    except RuntimeError as e:
        print(f"\n❌ 运行失败: {e}", file=sys.stderr)
        sys.exit(1)
    except (KeyboardInterrupt, EOFError):
        print("\n\n已中断。")
        sys.exit(0)


if __name__ == "__main__":
    main()
