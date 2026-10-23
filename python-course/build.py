"""Builds python-course.html.

Every code example on the page is executed here, and the output shown on the
page is the real output (or the real error) from this Python. If an example
that should work fails, or an example that should fail raises a different
error than the text says, the build stops.

Run:  python3 build.py
"""
import base64
import html
import re
import json
import os
import pathlib
import platform
import subprocess
import sys
import tempfile
import datetime

from quizbank import BREAKIT, BUGS, CHEAT, JOKES, MODULES, PUZZLES, QUIZ, REVISION, TAKEAWAYS

HERE = pathlib.Path(__file__).parent
OUT = HERE / "python-course.html"
PYVER = platform.python_version()
TODAY = datetime.date.today().strftime("%d %b %Y")
esc = html.escape

SITE = r'''
import builtins, json, os, sys
_q = json.loads(os.environ.get("FAKE_INPUT", "[]"))
def _inp(prompt=""):
    v = _q.pop(0)
    sys.stdout.write(str(prompt) + v + "\n")
    return v
builtins.input = _inp
'''


def run(code, typed=None, files=None):
    d = tempfile.mkdtemp()
    for name, body in (files or {}).items():
        pathlib.Path(d, name).write_text(body)
    pathlib.Path(d, "lesson.py").write_text(code.strip() + "\n")
    env = dict(os.environ, PYTHON_COLORS="0", NO_COLOR="1", PYTHONHASHSEED="0")
    if typed is not None:
        site = tempfile.mkdtemp()
        pathlib.Path(site, "sitecustomize.py").write_text(SITE)
        env["PYTHONPATH"] = site
        env["FAKE_INPUT"] = json.dumps(typed)
    p = subprocess.run([sys.executable, "lesson.py"], cwd=d, capture_output=True,
                       text=True, env=env, timeout=30)
    real = os.path.realpath(d)
    err, out = p.stderr, p.stdout
    for prefix in (real + "/", d + "/"):
        err = err.replace(prefix, "")
        out = out.replace(prefix, "")
    return p.returncode, out, err


def code_html(code):
    return f'<pre class="code"><code class="language-python">{esc(code.strip())}</code></pre>'


def out_html(out, err, label):
    parts = []
    if out:
        parts.append(f'<span class="o">{esc(out.rstrip(chr(10)))}</span>')
    if err:
        lines = err.rstrip("\n").split("\n")
        body = esc("\n".join(lines[:-1]))
        last = esc(lines[-1])
        parts.append(f'<span class="tb">{body}\n</span><span class="errline">{last}</span>'
                     if len(lines) > 1 else f'<span class="errline">{last}</span>')
    text = "\n".join(parts) if parts else '<span class="o muted">(nothing is printed)</span>'
    return f'<div class="outlabel">{label}</div><pre class="out">{text}</pre>'


def run_attrs(typed=None, files=None):
    a = ""
    if typed:
        a += f' data-typed="{esc(json.dumps(typed))}"'
    if files:
        a += f' data-files="{esc(json.dumps(files))}"'
    return a


def runbox(inner, typed=None, files=None):
    """An example the reader can edit and run in the browser."""
    return f'<div class="runbox"{run_attrs(typed, files)}>{inner}</div>'


def etype_of(err):
    last = err.strip().split("\n")[-1] if err.strip() else ""
    return last.split(":")[0].strip() if last else ""


AUTO_Q = {}


def works(code, typed=None, files=None):
    rc, out, err = run(code, typed, files)
    if rc != 0 or err:
        sys.exit(f"EXPECTED TO WORK but failed:\n{code}\n---\n{err}")
    return runbox(code_html(code) + out_html(out, "", "Output"), typed, files)


def breaks(code, expect, typed=None, files=None):
    rc, out, err = run(code, typed, files)
    last = err.strip().split("\n")[-1] if err.strip() else ""
    if rc == 0 or not last.startswith(expect):
        sys.exit(f"EXPECTED {expect} but got rc={rc}:\n{code}\n---\n{err}")
    return runbox(code_html(code) + out_html(out, err, "Error"), typed, files)


def silent(code, typed=None, files=None):
    """Runs without an error, but does something you did not mean."""
    rc, out, err = run(code, typed, files)
    if rc != 0:
        sys.exit(f"TRAP EXPECTED TO RUN:\n{code}\n---\n{err}")
    return runbox(code_html(code) + out_html(out, "", "Output"), typed, files)


# ---------------------------------------------------------------- blocks

RULE_INDEX = {}


def rule(num, title, body, ok=None, bad=None, expect=None, why=None,
         ok_typed=None, files=None):
    rid = "r" + num.replace(".", "-")
    RULE_INDEX.setdefault(num.split(".")[0], []).append((rid, num, title))
    if not ok_typed and not files:
        pool = AUTO_Q.setdefault(num.split(".")[0], [])
        for c in ([] if ok is None else ok if isinstance(ok, list) else [ok]):
            if c.count("\n") <= 5:
                pool.append({"type": "output", "code": c, "from": f"Rule {num}"})
        for c, e in ([] if bad is None else bad if isinstance(bad, list) else [bad] if isinstance(bad, tuple) else [(bad, expect)]):
            if c.count("\n") <= 5:
                pool.append({"type": "error", "code": c, "from": f"Rule {num}"})
    h = [f'<section class="rule" id="{rid}"><h3><span class="rnum">Rule {num}</span>{title}</h3>',
         f'<div class="prose">{body}</div>']
    if ok:
        for c in (ok if isinstance(ok, list) else [ok]):
            h.append(f'<div class="case good"><div class="case-h"><span class="mark">&#10003;</span> Works</div>'
                     f'{works(c, ok_typed, files)}</div>')
    if bad:
        for c, e in (bad if isinstance(bad, list) else [bad] if isinstance(bad, tuple) else [(bad, expect)]):
            h.append(f'<div class="case bad"><div class="case-h"><span class="mark">&#10007;</span> Breaks</div>'
                     f'{breaks(c, e, files=files)}</div>')
    if why:
        h.append(f'<p class="why"><b>Why:</b> {why}</p>')
    h.append("</section>")
    return "\n".join(h)


def trap(title, code, why, typed=None, files=None):
    return (f'<div class="case trap"><div class="case-h"><span class="mark">!</span> Trap: {title}</div>'
            f'{silent(code, typed, files)}<p class="why"><b>Why:</b> {why}</p></div>')


def concept(title, body, cid=None):
    a = f' id="{cid}"' if cid else ""
    return f'<section class="concept"{a}><h3>{title}</h3><div class="prose">{body}</div></section>'


def table(headers, rows, cls=""):
    th = "".join(f"<th>{h}</th>" for h in headers)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tablewrap"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def example(code, typed=None, label=None, files=None):
    pre = f'<p class="exlabel">{label}</p>' if label else ""
    return f'<div class="case plain">{pre}{works(code, typed, files)}</div>'


EX_COUNT = [0]


def exercises(items, tid):
    h = ['<section class="exercises"><h3>Exercises</h3>',
         '<p class="hint">Write your answer in the box first. Then open the answer. '
         'Guessing before you look is what makes it stick.</p><ol class="exlist">']
    for i, it in enumerate(items, 1):
        EX_COUNT[0] += 1
        n = EX_COUNT[0]
        kind = it["kind"]
        q = f'<p>{it["q"]}</p>' if it.get("q") else ""
        code = code_html(it["code"]) if it.get("code") else ""
        if kind == "Predict":
            rc, out, err = run(it["code"], it.get("typed"))
            exp = it.get("expect")
            if exp:
                last = err.strip().split("\n")[-1] if err.strip() else ""
                if not last.startswith(exp):
                    sys.exit(f"EXERCISE expected {exp}: {it['code']}\n{err}")
            elif rc != 0:
                sys.exit(f"EXERCISE should run: {it['code']}\n{err}")
            ans = out_html(out, err, "Real output" if rc == 0 else "Real result")
        elif kind == "Write":
            rc, out, err = run(it["sol"], it.get("typed"))
            if rc != 0:
                sys.exit(f"SOLUTION failed: {it['sol']}\n{err}")
            ans = '<div class="outlabel">One answer</div>' + code_html(it["sol"]) + out_html(out, "", "Output")
        else:
            ans = ""
        explain = f'<p class="why">{it["a"]}</p>' if it.get("a") else ""
        data = ""
        if kind == "Predict":
            data = f' data-out="{esc(out)}" data-etype="{esc(etype_of(err) if rc != 0 else "")}"'
        elif kind == "Write":
            data = run_attrs(it.get("typed")) + ' data-write="1"'
        h.append(f'<li class="ex"{data}><div class="ex-h"><span class="ex-n">{tid}.{i}</span>'
                 f'<span class="ex-kind">{kind}</span></div>{q}{code}'
                 f'<label class="sr" for="ans-{n}">Your answer</label>'
                 f'<textarea id="ans-{n}" class="mine" rows="2" placeholder="Your answer"></textarea>'
                 f'<details><summary>Show answer</summary>{ans}{explain}</details></li>')
    h.append("</ol></section>")
    return "\n".join(h)


# ---------------------------------------------------------------- quizzes and break-it
# Every code question is run here. The answer the page checks against is what
# Python really did, never a hand-typed guess.

def verify_q(q, where):
    q = dict(q)
    if q["type"] == "mcq":
        return q
    rc, out, err = run(q["code"])
    if q["type"] == "output":
        if rc != 0:
            sys.exit(f"QUIZ {where}: output question must run:\n{q['code']}\n{err}")
        q["answer"] = out
    else:
        q["answer"] = etype_of(err) if rc != 0 else "Works"
    q["out"] = out
    q["err"] = err
    return q


def quiz_pool(topic_num):
    qs = [verify_q(q, f"chapter {topic_num}") for q in QUIZ.get(topic_num, [])]
    return qs


def auto_pool(topic_num):
    keep = []
    for q in AUTO_Q.get(topic_num, []):
        v = verify_q(q, q["from"])
        rn = q["from"].split(" ")[1]
        if rn in RULE_LABEL:
            v["from"] = f"Chapter {topic_num}, {RULE_LABEL[rn][0]}, rule {RULE_LABEL[rn][1]}"
        if v["type"] == "output" and (not v["out"].strip() or v["out"].count("\n") > 6):
            continue
        keep.append(v)
    return keep


def quiz_section(qid, title, questions, n, note):
    return (f'<section class="quiz" id="quiz-{qid}" data-quiz="{qid}" data-n="{n}">'
            f'<h3>{title}</h3><p class="hint">{note} <span class="quiz-best"></span></p>'
            f'<div class="quiz-body"><button type="button" class="btn primary quiz-start">Start quiz</button></div>'
            f'<script type="application/json" class="quiz-data">{json.dumps(questions).replace("</", "<\\/")}</script></section>')


def breakit_section(topic_num):
    items = BREAKIT.get(topic_num, [])
    if not items:
        return ""
    h = ['<section class="breakit"><h3>Break it</h3>',
         '<p class="hint">Each box starts with code that works. Change it so Python raises the error named, then press Run and check. '
         'Making errors on purpose is the fastest way to learn what causes them.</p><ol class="exlist">']
    for i, it in enumerate(items, 1):
        rc, out, err = run(it["code"])
        if rc != 0:
            sys.exit(f"BREAKIT start must run: {it['code']}\n{err}")
        rc2, out2, err2 = run(it["sol"])
        if etype_of(err2) != it["target"]:
            sys.exit(f"BREAKIT solution must raise {it['target']}: {it['sol']}\n{err2}")
        h.append(f'<li class="ex brk" data-target="{it["target"]}"><div class="ex-h"><span class="ex-n">{topic_num}.{i}</span>'
                 f'<span class="ex-kind">Make it raise {it["target"]}</span></div>'
                 f'<label class="sr" for="brk-{topic_num}-{i}">Your code</label>'
                 f'<textarea id="brk-{topic_num}-{i}" class="editor brk-code" rows="{it["code"].count(chr(10)) + 2}" spellcheck="false">{esc(it["code"])}</textarea>'
                 f'<div class="runbar"><button type="button" class="btn primary brk-run">Run and check</button>'
                 f'<button type="button" class="btn brk-reset" data-start="{esc(it["code"])}">Reset</button></div>'
                 f'<div class="brk-result" aria-live="polite"></div>'
                 f'<details><summary>Hint and one answer</summary><p class="why">{it["hint"]}</p>'
                 f'{code_html(it["sol"])}{out_html(out2, err2, "Real result")}</details></li>')
    h.append("</ol></section>")
    return "\n".join(h)


# ---------------------------------------------------------------- sketches
# Excalidraw-like: shapes go through a displacement filter and hachure fill,
# labels are set in a hand font.

def sbox(x, y, w, h, lines, fill="hb", size=19, mono=False):
    cls = "mono" if mono else "hand"
    t = []
    n = len(lines)
    for i, ln in enumerate(lines):
        ty = y + h / 2 + (i - (n - 1) / 2) * (size * 1.25) + size * 0.35
        t.append(f'<text x="{x + w / 2}" y="{ty:.1f}" class="{cls}" font-size="{size}" text-anchor="middle">{esc(ln)}</text>')
    return (f'<g filter="url(#rough)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="url(#{fill})" class="stroke"/>'
            f'<rect x="{x + 1.5}" y="{y - 1}" width="{w - 2}" height="{h + 1}" rx="9" fill="none" class="stroke thin"/></g>'
            + "".join(t))


def sarrow(x1, y1, x2, y2, label=None, lx=None, ly=None, size=16, curve=0):
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - curve
    s = (f'<path d="M{x1},{y1} Q{mx},{my} {x2},{y2}" class="stroke arrow" fill="none" '
         f'marker-end="url(#ah)" filter="url(#rough)"/>')
    if label:
        lx = mx if lx is None else lx
        ly = (my - 8) if ly is None else ly
        s += f'<text x="{lx}" y="{ly}" class="hand note" font-size="{size}" text-anchor="middle">{esc(label)}</text>'
    return s


def stext(x, y, txt, size=17, cls="hand note", anchor="start"):
    return f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" text-anchor="{anchor}">{esc(txt)}</text>'


def figure(w, h, inner, caption, minw=560):
    return (f'<figure class="sketch"><div class="sketch-scroll"><svg viewBox="0 0 {w} {h}" '
            f'style="min-width:{minw}px" role="img" aria-label="{esc(caption)}">{inner}</svg></div>'
            f'<figcaption>{caption}</figcaption></figure>')


DEFS = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<filter id="rough" filterUnits="userSpaceOnUse" x="-50" y="-50" width="1100" height="800"><feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="7"/><feDisplacementMap in="SourceGraphic" scale="2.6"/></filter>
<pattern id="hb" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(-40)"><line x1="0" y1="0" x2="0" y2="9" stroke="#306998" stroke-width="1.3" opacity=".30"/></pattern>
<pattern id="hy" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(-40)"><line x1="0" y1="0" x2="0" y2="9" stroke="#D9A400" stroke-width="1.6" opacity=".45"/></pattern>
<pattern id="hg" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(-40)"><line x1="0" y1="0" x2="0" y2="9" stroke="#2B7A4B" stroke-width="1.3" opacity=".32"/></pattern>
<pattern id="hr" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(-40)"><line x1="0" y1="0" x2="0" y2="9" stroke="#B42318" stroke-width="1.3" opacity=".30"/></pattern>
<pattern id="hn" width="9" height="9" patternUnits="userSpaceOnUse"><rect width="9" height="9" fill="#FFFFFF"/></pattern>
<marker id="ah" viewBox="0 0 12 12" refX="10" refY="6" markerWidth="11" markerHeight="11" orient="auto-start-reverse"><path d="M1,1 L10,6 L1,11" fill="none" stroke="#18222E" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></marker>
</defs></svg>'''


def d_program():
    s = sbox(20, 70, 130, 70, ["You"], "hy")
    s += sarrow(152, 105, 222, 105, "write")
    s += sbox(225, 60, 170, 90, ["Code", "hello.py"], "hn", 18)
    s += sarrow(397, 105, 467, 105, "read by")
    s += sbox(470, 70, 150, 70, ["Python"], "hb")
    s += sarrow(622, 105, 692, 105, "tells")
    s += sbox(695, 70, 170, 70, ["Computer"], "hn")
    s += sarrow(780, 142, 780, 192, "does it", 830, 172)
    s += sbox(690, 195, 180, 60, ["Output: Hi"], "hg", 18)
    s += stext(225, 190, 'print("Hi")', 18, "mono")
    s += stext(250, 230, "a file of exact steps", 16)
    return figure(900, 275, s, "A program is a file of exact steps. Python reads it and tells the computer what to do.")


def d_recipe():
    s = '<g filter="url(#rough)">'
    s += '<rect x="40" y="30" width="250" height="230" rx="6" fill="url(#hy)" class="stroke"/>'
    s += '<rect x="610" y="40" width="250" height="160" rx="8" fill="#FFFFFF" class="stroke"/>'
    s += '<path d="M580,215 L890,215 L860,245 L610,245 Z" fill="url(#hb)" class="stroke"/></g>'
    s += stext(165, 65, "Masala chai", 22, "hand", "middle")
    steps = ["1. Boil 1 cup water", "2. Add 1 tsp tea", "3. Add milk + sugar", "4. Boil 2 minutes", "5. Strain into a cup"]
    for i, st in enumerate(steps):
        s += stext(60, 105 + i * 30, st, 17, "hand")
    code = ['water = 1', 'tea = 1', 'chai = water + tea', 'print("Chai ready")']
    for i, c in enumerate(code):
        s += stext(630, 80 + i * 30, c, 15, "mono")
    s += sarrow(300, 140, 595, 120, "same idea: exact steps, in order", 448, 105, 17, 25)
    s += stext(165, 290, "recipe = program", 17, "hand note", "middle")
    s += stext(735, 285, "code = program for a computer", 17, "hand note", "middle")
    return figure(900, 305, s, "A recipe and a program are both exact steps, done in order, top to bottom.")


def d_translate():
    s = sbox(10, 50, 200, 80, ['print("Hi")', "you can read this"], "hn", 15, True)
    s += sarrow(212, 90, 302, 90, "translates", 257, 78, 15)
    s += sbox(305, 45, 170, 90, ["Python", "the translator"], "hb", 18)
    s += sarrow(477, 90, 567, 90, "gives", 522, 78, 15)
    s += sbox(570, 50, 220, 80, ["01001000 01101001", "machine code"], "hn", 15, True)
    s += sarrow(792, 90, 832, 90)
    s += sbox(835, 60, 55, 60, ["Hi"], "hg")
    return figure(900, 170, s, "Computers only understand machine code. Python translates your readable code for it.")


def d_compile():
    s = ""
    rows = [
        (40, "C", [("hello.c", "your code", "hn"), ("clang", "the compiler", "hb"), ("hello", "an app file", "hy"), ("./hello", "prints Hi", "hg")],
         ["1. build once", "makes a file", "2. run the app"], "Translate ONCE, before running. Later runs use the app; no compiler needed."),
        (180, "Python", [("hello.py", "your code", "hn"), ("python3", "translate + run", "hb"), None, ("Hi", "printed", "hg")],
         ["hand it over", "", "every run"], "Translate EVERY time you run it. No app file appears."),
        (320, "Java", [("Hello.java", "your code", "hn"), ("javac", "the compiler", "hb"), ("Hello.class", "bytecode", "hy"), ("java", "the JVM runs it", "hg")],
         ["compile", "makes a file", "run on the JVM"], "Both: compile to bytecode once, then the Java Virtual Machine runs it."),
    ]
    xs = [100, 300, 500, 700]
    for y, name, boxes, labels, note in rows:
        s += stext(20, y + 45, name, 22, "hand")
        for k, bx in enumerate(boxes):
            if bx:
                s += sbox(xs[k], y, 165, 70, [bx[0], bx[1]], bx[2], 16, False)
        # arrows between the boxes that exist
        live = [k for k, bx in enumerate(boxes) if bx]
        for i in range(len(live) - 1):
            k1, k2 = live[i], live[i + 1]
            x1, x2 = xs[k1] + 167, xs[k2] - 3
            lab = labels[k2 - 1] if k2 - k1 > 1 else ""
            s += sarrow(x1, y + 35, x2, y + 35, lab, (x1 + x2) / 2, y + 26, 15)
        s += stext(xs[0], y + 100, note, 15, "hand note")
    return figure(880, 450, s, "Three ways a language turns your code into something the computer runs. Python has no app file: it goes straight from your code to the result.", 600)


SDK_ENV = dict(os.environ, SDKROOT="/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk",
               PATH="/Library/Developer/CommandLineTools/usr/bin:" + os.environ.get("PATH", ""))


def shell_demo(files, commands, title):
    """Runs real terminal commands in a fresh folder and shows the transcript."""
    d = tempfile.mkdtemp()
    for name, body in files.items():
        pathlib.Path(d, name).write_text(body)
    lines = []
    for c in commands:
        p = subprocess.run(c, shell=True, cwd=d, capture_output=True, text=True, env=SDK_ENV, timeout=60)
        if p.returncode != 0:
            sys.exit(f"SHELL DEMO failed: {c}\n{p.stderr}")
        lines.append(f'<span class="tb">$</span> {esc(c)}')
        if p.stdout.strip():
            lines.append(esc(p.stdout.rstrip("\n")))
    return (f'<div class="case plain"><p class="exlabel">{title}</p>'
            f'<pre class="out shellrun">' + "\n".join(lines) + '</pre></div>')


def d_timeline():
    s = '<path d="M40,130 L870,130" class="stroke" fill="none" filter="url(#rough)"/>'
    pts = [(80, "Dec 1989", ["Guido starts it", "over Christmas"]),
           (215, "Feb 1991", ["first shared", "on USENET"]),
           (350, "1995", ["work moves", "to CNRI, USA"]),
           (485, "2001", ["Python Software", "Foundation formed"]),
           (620, "Dec 2008", ["Python 3.0", "released"]),
           (760, "Jan 2020", ["Python 2", "retired"])]
    for x, yr, lines in pts:
        s += f'<g filter="url(#rough)"><circle cx="{x}" cy="130" r="9" fill="url(#hy)" class="stroke"/></g>'
        s += stext(x, 100, yr, 19, "hand", "middle")
        for i, ln in enumerate(lines):
            s += stext(x, 168 + i * 22, ln, 16, "hand note", "middle")
    return figure(900, 230, s, "Python's history, from python.org (docs.python.org FAQ and license page, python.org release pages).", 640)


def d_twopass():
    s = sbox(20, 95, 130, 70, ["lesson.py"], "hn", 18, True)
    s += sarrow(152, 130, 222, 130)
    s += sbox(225, 80, 200, 100, ["Pass 1", "check the grammar", "of the WHOLE file"], "hb", 17)
    s += sarrow(325, 182, 325, 240, "grammar broken", 400, 220, 15)
    s += sbox(215, 245, 220, 80, ["SyntaxError", "nothing runs at all"], "hr", 17)
    s += sarrow(427, 130, 497, 130, "ok")
    s += sbox(500, 80, 200, 100, ["Pass 2", "run line 1, line 2,", "line 3 ... in order"], "hb", 17)
    s += sarrow(600, 182, 600, 240, "a line fails", 668, 220, 15)
    s += sbox(490, 245, 220, 80, ["NameError, TypeError...", "lines above already ran"], "hr", 16)
    s += sarrow(702, 130, 772, 130, "all ok")
    s += sbox(775, 95, 105, 70, ["done"], "hg")
    return figure(900, 345, s, "How Python runs a file: first it checks the grammar of the whole file, then it runs it line by line.")


def d_traceback():
    lines = ['Traceback (most recent call last):',
             '  File "lesson.py", line 2, in <module>',
             '    print(scor)',
             '          ^^^^',
             "NameError: name 'scor' is not defined"]
    s = '<g filter="url(#rough)"><rect x="20" y="20" width="520" height="170" rx="8" fill="#FFFFFF" class="stroke"/></g>'
    for i, ln in enumerate(lines):
        cls = "mono err" if i == 4 else "mono"
        s += f'<text x="40" y="{55 + i * 30}" class="{cls}" font-size="15" xml:space="preserve">{esc(ln)}</text>'
    s += sarrow(560, 172, 610, 175, "", )
    s += stext(615, 168, "3. READ THIS FIRST:", 17, "hand")
    s += stext(615, 190, "error type + reason", 17, "hand note")
    s += sarrow(560, 83, 610, 70)
    s += stext(615, 66, "1. which file + which line", 17, "hand")
    s += sarrow(560, 128, 610, 118)
    s += stext(615, 115, "2. the line itself, ^ marks", 17, "hand")
    s += stext(615, 137, "the exact spot", 17, "hand note")
    return figure(900, 215, s, "Reading an error: start at the last line, then look at the line number and the ^ marks.", 700)


def d_label():
    s = sbox(40, 90, 110, 60, ["30"], "hn", 22, True)
    s += f'<g filter="url(#rough)"><path d="M60,40 L150,40 L170,58 L150,76 L60,76 Z" fill="url(#hy)" class="stroke"/></g>'
    s += stext(110, 64, "age", 18, "mono", "middle")
    s += sarrow(100, 78, 96, 88)
    s += stext(95, 185, "age = 30", 17, "mono", "middle")
    s += sarrow(220, 110, 330, 110, "then", 275, 95)
    s += sbox(380, 90, 110, 60, ["30"], "hn", 22, True)
    s += sbox(560, 90, 110, 60, ["31"], "hn", 22, True)
    s += f'<g filter="url(#rough)"><path d="M570,40 L660,40 L680,58 L660,76 L570,76 Z" fill="url(#hy)" class="stroke"/></g>'
    s += stext(620, 64, "age", 18, "mono", "middle")
    s += sarrow(612, 78, 610, 88)
    s += stext(525, 185, "age = age + 1", 17, "mono", "middle")
    s += stext(435, 215, "1. right side first: 30 + 1 = 31", 16, "hand note", "middle")
    s += stext(615, 215, "2. move the tag to 31", 16, "hand note", "middle")
    s += stext(740, 120, "A variable is a name tag", 17, "hand")
    s += stext(740, 142, "stuck on a value.", 17, "hand")
    return figure(900, 235, s, "= works out the right side first, then puts the name tag on the result.")


def d_index(word="Python"):
    s = ""
    w = 70
    x0 = 160
    for i, ch in enumerate(word):
        x = x0 + i * w
        s += sbox(x, 70, w, 64, [ch], "hy" if 1 <= i <= 3 else "hn", 26, True)
        s += stext(x + w / 2, 55, str(i), 18, "mono", "middle")
        s += stext(x + w / 2, 162, str(i - len(word)), 18, "mono note", "middle")
    s += stext(150, 55, "index", 17, "hand note", "end")
    s += stext(150, 162, "negative", 17, "hand note", "end")
    s += stext(x0 + 3 * w + w / 2 - 35, 210, 'word[1:4]  gives  "yth"', 18, "mono", "middle")
    s += stext(x0 + 3 * w, 236, "start at 1, stop BEFORE 4", 16, "hand note", "middle")
    return figure(760, 255, s, "Every character has a position. Counting starts at 0. Negative numbers count from the end.")


def d_alias():
    s = sbox(260, 50, 220, 60, ["[1, 2, 3, 99]"], "hn", 20, True)
    for x, name in ((40, "a"), (40, "b")):
        pass
    s += f'<g filter="url(#rough)"><path d="M40,30 L100,30 L116,46 L100,62 L40,62 Z" fill="url(#hy)" class="stroke"/>'
    s += f'<path d="M40,100 L100,100 L116,116 L100,132 L40,132 Z" fill="url(#hy)" class="stroke"/>'
    s += f'<path d="M40,180 L100,180 L116,196 L100,212 L40,212 Z" fill="url(#hy)" class="stroke"/></g>'
    s += stext(75, 52, "a", 18, "mono", "middle")
    s += stext(75, 122, "b", 18, "mono", "middle")
    s += stext(75, 202, "c", 18, "mono", "middle")
    s += sarrow(118, 46, 256, 72)
    s += sarrow(118, 116, 256, 92)
    s += sbox(260, 170, 220, 60, ["[1, 2, 3]"], "hn", 20, True)
    s += sarrow(118, 196, 256, 200)
    s += stext(510, 70, "b = a  : two tags, ONE list.", 17, "hand")
    s += stext(510, 94, "b.append(99) changes what a sees too", 17, "hand note")
    s += stext(510, 196, "c = a.copy()  : a NEW list", 17, "hand")
    s += stext(510, 220, "changing c leaves a alone", 17, "hand note")
    return figure(900, 250, s, "= never copies a list. It adds another name tag to the same list.")


def d_dict():
    s = '<g filter="url(#rough)"><rect x="30" y="20" width="560" height="200" rx="10" fill="none" class="stroke"/></g>'
    s += stext(48, 46, "student = {", 17, "mono")
    rows = [('"name"', '"Ravi"'), ('"age"', "21"), ('"city"', '"Mysuru"')]
    for i, (k, v) in enumerate(rows):
        y = 70 + i * 48
        s += sbox(70, y, 140, 38, [k], "hy", 17, True)
        s += sarrow(212, y + 19, 330, y + 19)
        s += sbox(335, y, 160, 38, [v], "hn", 17, True)
    s += stext(48, 238, "}", 17, "mono")
    s += stext(620, 90, "keys: unique labels", 17, "hand")
    s += stext(620, 140, "values: anything", 17, "hand")
    s += stext(620, 190, 'student["age"]  gives 21', 16, "mono")
    return figure(900, 255, s, "A dictionary stores pairs. You look a value up by its key, not by a position.")


def d_venn():
    s = '<g filter="url(#rough)"><circle cx="300" cy="125" r="95" fill="url(#hb)" class="stroke"/>'
    s += '<circle cx="430" cy="125" r="95" fill="url(#hy)" class="stroke"/></g>'
    s += stext(250, 40, "a = {1, 2, 3, 4}", 17, "mono", "middle")
    s += stext(480, 40, "b = {3, 4, 5, 6}", 17, "mono", "middle")
    s += stext(255, 132, "1  2", 22, "mono", "middle")
    s += stext(365, 132, "3  4", 22, "mono", "middle")
    s += stext(475, 132, "5  6", 22, "mono", "middle")
    s += stext(640, 80, "a | b  all:  {1, 2, 3, 4, 5, 6}", 16, "mono")
    s += stext(640, 115, "a & b  both: {3, 4}", 16, "mono")
    s += stext(640, 150, "a - b  only a: {1, 2}", 16, "mono")
    return figure(900, 240, s, "Sets keep each value once, and can be combined like circles in a diagram.")


SNAKE_WM = '''<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg"><g fill="none" stroke="#306998" stroke-width="10" stroke-linecap="round" filter="url(#rough)">
<path d="M60,330 C60,250 170,260 170,190 C170,120 70,130 70,80 C70,40 120,30 150,45"/>
<path d="M190,340 C190,270 300,280 300,210 C300,140 200,150 200,100 C200,60 250,50 280,65" stroke="#D9A400"/></g>
<circle cx="140" cy="44" r="5" fill="#306998"/><circle cx="270" cy="64" r="5" fill="#D9A400"/></svg>'''


# ---------------------------------------------------------------- topics

TOPICS = []
# Photo: Daniel Stroud, CC BY-SA 4.0, https://commons.wikimedia.org/wiki/File:Guido-portrait-2014-drc.jpg
PORTRAIT = ('<figure class="portrait"><img src="data:image/jpeg;base64,'
            + base64.b64encode((HERE / "assets/guido-360.jpg").read_bytes()).decode()
            + '" width="360" height="240" alt="Guido van Rossum, creator of Python, in 2014">'
            '<figcaption>Guido van Rossum in 2014. Photo: Daniel Stroud, '
            '<a href="https://creativecommons.org/licenses/by-sa/4.0">CC BY-SA 4.0</a>, via '
            '<a href="https://commons.wikimedia.org/wiki/File:Guido-portrait-2014-drc.jpg">Wikimedia Commons</a>.</figcaption></figure>')


def topic(num, slug, title, goal, body):
    TOPICS.append((num, slug, title, goal, body))


# ===== 0 =====
topic("0", "programming", "What is programming?",
      "What a program is, what code is, and why the computer needs every step spelled out.", "".join([
    concept("A program is a list of exact steps", '''
<p>A <b>program</b> is a list of instructions that a computer follows, one after another. Every app you use is a program:
WhatsApp, a calculator, a game, a website. Someone wrote each step.</p>
<p>You already know something that works this way: a recipe.</p>'''),
    d_recipe(),
    table(["In a recipe", "In a program", "Meaning"], [
        ["the steps", "the <b>code</b>", "the instructions, written down"],
        ["the cook", "the <b>computer</b>", "the thing that follows the steps"],
        ["the ingredients", "the <b>input</b>", "what goes in (a number you type, a file)"],
        ["the dish", "the <b>output</b>", "what comes out (text on screen, a saved file)"],
        ["cooking", "<b>running</b> (or <b>executing</b>)", "actually following the steps"],
    ]),
    concept("Computers are fast, but they never guess", '''
<p>A person told "make tea" fills in the gaps: they boil water, find a cup, add sugar the way you like it.
A computer cannot fill in gaps. It does <b>exactly</b> what is written, in the order it is written, and nothing else.</p>
<p>So programming is mostly this: breaking a job into steps small and exact enough that something with no common sense can still do it.</p>
<p>If one step is wrong, the computer still follows it. It will happily add the sugar before the water exists.
A mistake in a program is called a <b>bug</b>, and finding and fixing it is called <b>debugging</b>.</p>'''),
    concept("Why we need a programming language", '''
<p>Inside, a computer only understands <b>machine code</b>: long runs of 0s and 1s. Writing that by hand is slow and almost impossible to read.</p>
<p>A <b>programming language</b> lets you write steps in something close to English, like <code>print("Hi")</code>.
A translator program then turns it into instructions the machine can carry out. For Python, that translator is Python itself.</p>'''),
    d_translate(),
    concept("Syntax: the grammar of a language", '''
<p>Every language has grammar rules. In English, "the dog ran" is fine and "ran dog the" is wrong, but a person still understands it.</p>
<p>A programming language's grammar is called its <b>syntax</b>. The difference: the computer does <b>not</b> understand broken grammar at all.
One missing bracket and Python refuses to run the whole file. That is why this course shows, for every rule, what breaks it.</p>'''),
    table(["Word", "Plain meaning"], [
        ["program", "a set of steps for a computer"],
        ["code", "the written steps"],
        ["syntax", "the grammar rules for writing code"],
        ["run / execute", "make the computer follow the steps"],
        ["input / output", "what goes in / what comes out"],
        ["bug", "a mistake in the code"],
        ["debugging", "finding and fixing bugs"],
    ]),
    d_program(),
    exercises([
        {"kind": "Think", "q": "Write the steps for \"brush your teeth\" so exactly that a robot with no common sense could follow them. Then read them back: could any step be done wrongly?",
         "a": "There is no single right answer. Common gaps: you never said to open the toothpaste cap, how much paste, or to turn the tap off. Each gap is a bug. Programs need that level of detail."},
        {"kind": "Think", "q": "At an ATM: what is the input, what is the program doing, and what is the output?",
         "a": "Input: your card, PIN and the amount you type. The program checks the PIN, checks your balance and subtracts the amount. Output: the cash, the receipt and the message on screen."},
        {"kind": "Think", "q": "A recipe says: \"2. Add sugar. 1. Boil water.\" A person would fix the order. What would a computer do?",
         "a": "It does step 2 first, because that is the order written. Computers follow the written order, top to bottom. Order is part of the program."},
        {"kind": "Think", "q": "Why can't we just write programs in normal English?",
         "a": "English is full of guesses: \"a bit of sugar\", \"boil it for a while\". A computer needs one exact meaning for every step, so programming languages have strict rules (syntax) that leave nothing to guess."},
    ], "0"),
]))

# ===== 1 =====
topic("1", "python", "What is Python?",
      "Who made it, where the name comes from, and why so many people learn it first.", "".join([
    concept("Python in one line", '''
<p><b>Python is a programming language</b>: a set of words and grammar rules for writing programs, plus the program (also called Python) that reads and runs them.</p>
<p>The official Python FAQ calls it "an interpreted, interactive, object-oriented programming language" and "a high-level general-purpose programming language". Four of those words, in plain English:</p>
<dl class="terms">
<div><dt>Interpreted</dt><dd>Run your file directly with <code>python3 file.py</code>. No app to build first.</dd></div>
<div><dt>Interactive</dt><dd>Type one line and see the result straight away (Chapter 2).</dd></div>
<div><dt>High-level</dt><dd>You write <code>print("Hi")</code>, not 0s and 1s.</dd></div>
<div><dt>General-purpose</dt><dd>Not made for one job: websites, data, automation, testing, AI.</dd></div>
</dl>'''),
    concept("Compiled or interpreted: two ways to run code", '''
<p>Every language has to turn your code into machine code. They differ in <b>when</b> that happens and <b>what you end up with</b>.</p>'''),
    table(["", "Compiled", "Interpreted", "Both"], [
        ["Examples", "C, Go, Rust", "<b>Python</b>", "Java"],
        ["When it is translated", "once, <b>before</b> running", "<b>every time</b> you run it", "once to bytecode, then the JVM runs it"],
        ["What you end up with", "a separate <b>app file</b>", "nothing new: just your file", "a bytecode file (<code>.class</code>)"],
        ["After a change", "build again, then run", "just run again", "compile again, then run"],
        ["To run it you need", "only the app", "Python installed", "Java installed"],
    ]),
    d_compile(),
    '<p class="analogy"><b>Think of a speech.</b> Compiling is translating the whole speech on paper first and handing over the printed copy. Interpreting is a live interpreter translating as you speak, every time you give it.</p>',
    shell_demo({"hello.c": '#include <stdio.h>\nint main(void) {\n    printf("Hi\\n");\n    return 0;\n}\n'},
               ["ls", "clang hello.c -o hello", "ls", "./hello"],
               "C, really run on this Mac: compiling creates a new file, hello, and that app is what runs."),
    shell_demo({"hello.py": 'print("Hi")\n'},
               ["ls", "python3 hello.py", "ls"],
               "Python, really run: no build step, and no new file appears."),
    table(["Language", "How it runs", "What you type", "Source"], [
        ["C", "compiled to an app (machine code)", "<code>clang hello.c -o hello</code>, then <code>./hello</code>", "run above"],
        ["Go", "compiled to an app", "<code>go build</code>, then run the app", "<a href=\"https://go.dev/doc/tutorial/compile-install\">go.dev</a>: \"compile the code into an executable\""],
        ["Rust", "compiled to an app", "build, then run the app", "<a href=\"https://doc.rust-lang.org/book/ch01-02-hello-world.html\">The Rust Book</a>: \"an ahead-of-time compiled language\""],
        ["Java", "compiled to bytecode, run by the JVM", "<code>javac Hello.java</code>, then <code>java Hello</code>", "<a href=\"https://docs.oracle.com/javase/tutorial/getStarted/intro/definition.html\">Oracle</a>: <code>.class</code> files hold \"bytecodes\""],
        ["JavaScript", "run by the browser, no build step", "open the web page", "<a href=\"https://developer.mozilla.org/en-US/docs/Web/JavaScript\">MDN</a>: \"interpreted (or just-in-time compiled)\""],
        ["Python", "interpreted, with a hidden bytecode step", "<code>python3 hello.py</code>", "<a href=\"https://docs.python.org/3/glossary.html#term-interpreted\">Python glossary</a>"],
    ]),
    concept("Python's hidden step: bytecode", '''
<p>The Python glossary says the line is "blurry": Python first compiles your code into <b>bytecode</b>, automatically and invisibly, then runs that. "The bytecode is also cached in <code>.pyc</code> files so that executing the same file is faster the second time."
You never run a build step yourself, which is why Python still counts as interpreted. You can see the cache appear when one file imports another:</p>'''),
    example('import os\nimport greet\nprint(os.listdir("__pycache__"))', files={"greet.py": 'print("hello from greet")\n'}),
    '<p class="src">The folder held <code>greet.py</code>. Importing it ran it, then Python saved its bytecode in a <code>__pycache__</code> folder. Source: <a href="https://docs.python.org/3/glossary.html#term-bytecode">Python glossary: bytecode</a>.</p>',
    concept("Who made it", PORTRAIT + '''
<p><b>Guido van Rossum</b>, a Dutch programmer, created Python. He was working at <b>CWI</b>, a research institute in the Netherlands.</p>
<p>In his own words in the Python FAQ: "During the 1989 Christmas holidays, I had a lot of time on my hand, so I decided to give it a try."
He shared it publicly in <b>February 1991</b>. It was built as a successor to an older teaching language called <b>ABC</b>, which he had worked on.</p>
<p>Today Python is owned by the <b>Python Software Foundation</b> (PSF), a non-profit formed in 2001, and built by volunteers all over the world. It is free.</p>'''),
    d_timeline(),
    concept("Why it is called Python", '''
<p>Not after the snake. From the FAQ: Guido "was also reading the published scripts from 'Monty Python's Flying Circus', a BBC comedy series from the 1970s",
and wanted "a name that was short, unique, and slightly mysterious".</p>
<p>The snake came later, as a logo idea. The blue and yellow in this page are the colours of that logo.</p>'''),
    concept("Why people choose Python", ""),
    table(["Reason", "What it means for you"], [
        ["Reads like English", "<code>print(\"Hi\")</code> is a whole program. Less to type, easier to read your own code a month later."],
        ["Batteries included", "Comes with a big standard library: tools for maths, dates, files, the internet, random numbers. Nothing to install."],
        ["Runs everywhere", "The same file runs on Windows, macOS and Linux."],
        ["Free and open", "No licence to buy. Anyone can read how it works."],
        ["Huge community", "Thousands of free add-on packages, and an answer online for almost every error message."],
        ["Used for real work", "Web back ends, data analysis, AI and machine learning, automation scripts, and test automation (pytest, Playwright for Python)."],
    ]),
    concept("Compare: the same program in Java", '''
<p>A program that prints <code>Hello</code>. In Java you need a class and a method before you can print anything:</p>
<pre class="code"><code class="language-java">public class Main {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}</code></pre>
<p>In Python, the whole program is one line:</p>'''),
    example('print("Hello")'),
    concept("Python 2 and Python 3", '''
<p>Python 3.0 came out on <b>3 December 2008</b> and changed some rules, so old Python 2 code does not always run on it.
Python 2 was officially retired on <b>1 January 2020</b>. Always learn and use <b>Python 3</b>.
Old tutorials that write <code>print "hi"</code> without brackets are Python 2 (Chapter 3 shows the error you get).</p>
<p>This page was built with <b>Python ''' + PYVER + '''</b>. Error messages can be worded slightly differently on older versions; the error <i>type</i> stays the same.</p>'''),
    concept("Where Python is weaker", '''
<p>No language is best at everything. Python is slower than languages like C for heavy number crunching (big libraries solve this by doing the heavy part in C for you),
and it is not the usual choice for phone apps. Its spacing rules are strict (Chapter 2). None of this matters while learning.</p>'''),
    concept("Python's own philosophy", '''<p>Python has a hidden poem of design rules called <b>The Zen of Python</b>. Run this one line and Python prints it. The first lines:</p>'''),
    example('import this'),
    exercises([
        {"kind": "Think", "q": "Who created Python, and in which country did he start it?", "a": "Guido van Rossum, at CWI in the Netherlands."},
        {"kind": "Think", "q": "Python is named after: (a) the snake, (b) a BBC comedy show, (c) a Greek myth?", "a": "(b) Monty Python's Flying Circus, a BBC comedy series from the 1970s."},
        {"kind": "Think", "q": "A tutorial shows <code>print \"Hello\"</code> with no brackets. Which Python version was it written for, and should you follow it?",
         "a": "Python 2. Python 2 was retired on 1 January 2020. Use Python 3, where it is <code>print(\"Hello\")</code>."},
        {"kind": "Think", "q": "Name two kinds of work Python is used for that matter to a QA engineer.",
         "a": "Test automation (pytest, Playwright for Python), and scripts that check data, call APIs or read log files."},
        {"kind": "Think", "q": "What does \"interpreted\" mean, in your own words?", "a": "Python reads your file and runs it directly. You do not have to build it into a separate app first."},
    ], "1"),
]))

# ===== 2 =====
topic("2", "running", "Running Python, and reading errors",
      "Two ways to run code, how Python reads a file, and how to read an error message.", "".join([
    concept("Step 1: check Python is installed", '''
<p>Open the <b>Terminal</b> (on a Mac: press Cmd + Space, type Terminal, press Enter). The terminal is a window where you type commands instead of clicking.
Type this and press Enter:</p>
<pre class="code shell"><code>python3 --version</code></pre>
<p>If it prints something like <code>Python ''' + PYVER + '''</code>, you are ready. On Windows the command is usually <code>python</code> or <code>py</code>.</p>'''),
    concept("Way 1: the interactive prompt (try one line)", '''
<p>Type <code>python3</code> on its own and press Enter. You get a <code>&gt;&gt;&gt;</code> prompt. Each line you type runs immediately:</p>
<pre class="code shell"><code>&gt;&gt;&gt; 2 + 3
5
&gt;&gt;&gt; print("Hi")
Hi
&gt;&gt;&gt; exit()</code></pre>
<p>Good for testing one line. Everything is lost when you close it. Type <code>exit()</code> to leave and get back to the terminal.</p>'''),
    concept("Way 2: a file (how real programs run)", '''
<p>Make a file called <code>hello.py</code> (any text editor works; VS Code is a common free one). The name must end in <code>.py</code>. Put this in it:</p>
<pre class="code"><code class="language-python">print("Hello")
print("I am learning Python")</code></pre>
<p>In the terminal, go to the folder with the file and run it:</p>
<pre class="code shell"><code>python3 hello.py</code></pre>
<p>Python runs the lines from top to bottom and prints both. Use a file for every exercise on this page.</p>'''),
    rule("2.1", "The >>> prompt runs Python, not terminal commands",
         "<p>At <code>&gt;&gt;&gt;</code> you are inside Python. Terminal commands like <code>ls</code> or <code>cd</code> mean nothing there. "
         "And <code>python3 hello.py</code> is a terminal command, so it does not work at <code>&gt;&gt;&gt;</code> either.</p>",
         bad=("ls", "NameError"),
         why="Python sees <code>ls</code> as the name of something you never created. If you see <code>&gt;&gt;&gt;</code>, type <code>exit()</code> first, then run terminal commands."),
    concept("How Python reads your file: two passes", "<p>This one idea explains most errors you will see.</p>"),
    d_twopass(),
    rule("2.2", "Broken grammar stops the whole file, even the lines before it",
         "<p>Before running anything, Python checks the grammar of the <b>entire</b> file. If any line is broken, nothing runs.</p>",
         ok='print("line 1")\nprint("line 2")',
         bad=('print("line 1")\nprint("line 2"', "SyntaxError"),
         why="Line 2 is missing its closing bracket. Python found that in pass 1, so even line 1 never ran. Notice the error does not say <code>line 1</code> was printed: it was not."),
    rule("2.3", "Other errors stop at the line, and the lines above already ran",
         "<p>If the grammar is fine, Python runs line by line. When a line fails, Python stops there. Lines above it have already done their work.</p>",
         bad=('print("line 1")\nprint(score)\nprint("line 3")', "NameError"),
         why="Pass 1 was fine (the grammar is correct). In pass 2, line 1 printed, then line 2 failed because <code>score</code> was never created. Line 3 never ran."),
    concept("How to read an error message", '''
<p>An error message is called a <b>traceback</b>. It looks scary but has only three parts. Always read it <b>bottom up</b>.</p>'''),
    d_traceback(),
    table(["Error type", "Found in", "Plain meaning", "Chapter"], [
        ["<code>SyntaxError</code>", "pass 1", "grammar is broken: a bracket or quote missing, a word in the wrong place", "everywhere"],
        ["<code>IndentationError</code>", "pass 1", "spaces at the start of a line where they do not belong", "2"],
        ["<code>NameError</code>", "pass 2", "a name that does not exist: a typo, wrong capital letter, or used too early", "4"],
        ["<code>TypeError</code>", "pass 2", "the wrong kind of value for that action, like text + number", "4"],
        ["<code>ValueError</code>", "pass 2", "the right kind of value with bad content, like <code>int(\"abc\")</code>", "4"],
        ["<code>IndexError</code>", "pass 2", "a position that does not exist in a string or list", "5, 6"],
        ["<code>KeyError</code>", "pass 2", "a key that does not exist in a dictionary", "7"],
        ["<code>ZeroDivisionError</code>", "pass 2", "dividing by 0", "4"],
        ["<code>ModuleNotFoundError</code>", "pass 2", "<code>import</code> of a module that does not exist or is not installed", "3"],
    ]),
    rule("2.4", "Spaces at the start of a line matter",
         "<p>In Python, spaces at the <b>start</b> of a line (called <b>indentation</b>) have meaning. They are used to group lines, which you will meet later with <code>if</code> and loops. "
         "Until then, every line starts at the left edge.</p>",
         ok='x = 5\ny = 6\nprint(x + y)',
         bad=('x = 5\n  y = 6\nprint(x + y)', "IndentationError"),
         why="The two spaces before <code>y</code> tell Python a group is starting, but nothing above opened one. Spaces <b>inside</b> a line are free: <code>x=5</code> and <code>x = 5</code> mean the same."),
    rule("2.5", "One instruction per line",
         "<p>Each line holds one instruction. Two values side by side with nothing joining them is broken grammar.</p>",
         ok='x = 5\ny = 6',
         bad=('x = 5 6', "SyntaxError"),
         why="Python cannot tell what <code>5 6</code> should mean. It even guesses: perhaps you forgot a comma."),
    exercises([
        {"kind": "Predict", "q": "What prints? Write each line of output, or the error type.", "code": 'print("A")\nprint("B")\nprint("C"', "expect": "SyntaxError",
         "a": "Nothing prints. The missing bracket on line 3 is found in pass 1, before any line runs."},
        {"kind": "Predict", "q": "What prints before it stops?", "code": 'print("A")\nprint(B)\nprint("C")', "expect": "NameError",
         "a": "<code>A</code> prints, then a NameError on line 2: <code>B</code> without quotes is a name, and no such name exists. <code>C</code> never prints."},
        {"kind": "Predict", "code": 'print("start")\n   print("middle")\nprint("end")', "expect": "IndentationError",
         "a": "Nothing prints. Unexpected indentation is a grammar problem, so it is found in pass 1."},
        {"kind": "Think", "q": "You type <code>python3 hello.py</code> and get <code>NameError: name 'python3' is not defined</code>. What happened?",
         "a": "You were still inside the <code>&gt;&gt;&gt;</code> prompt. Type <code>exit()</code>, then run the command in the terminal."},
        {"kind": "Think", "q": "An error message has many lines. Which line do you read first?", "a": "The last one: it names the error type and the reason. Then go up to find the file and line number."},
    ], "2"),
]))

# ===== 3 =====
topic("3", "print", "print(), comments and modules",
      "Show things on screen, leave notes in your code, and use tools that come with Python.", "".join([
    rule("3.1", "print needs brackets",
         "<p><b><code>print()</code> shows something on the screen.</b> Whatever you put inside the brackets is what it shows.</p><p><code>print(&quot;hi&quot;)</code> shows <code>hi</code>. The brackets are how you hand it the thing to show, so they are never optional.</p>",
         ok='print("Hello")',
         bad=('print "Hello"', "SyntaxError"),
         why="Without brackets it is Python 2 grammar. Python 3 even tells you: <i>Did you mean print(...)?</i>"),
    rule("3.2", "Text goes inside quotes; without quotes it is a name",
         "<p>Quotes tell Python \"this is text, print it as it is\". Without quotes, Python thinks the word is the name of something you stored.</p>",
         ok='print("Hello")\nprint(\'Hello\')',
         bad=('print(Hello)', "NameError"),
         why="<code>Hello</code> without quotes is a name, and you never created anything called <code>Hello</code>. Single or double quotes both work; they must match."),
    rule("3.3", "Only text needs quotes",
         "<p>Numbers, <code>True</code>, <code>False</code>, <code>None</code> and names you already created are written <b>without</b> quotes. Quotes are only for text.</p>",
         ok='print(25)\nprint(True)\ncity = "Goa"\nprint(city)',
         bad=('city = Goa', "NameError"),
         why="Without quotes, <code>Goa</code> is read as a name, and no name <code>Goa</code> exists. Quotes turn it into the text <code>\"Goa\"</code>."),
    rule("3.4", "Capital letters matter",
         "<p>Python is <b>case-sensitive</b>: <code>print</code>, <code>Print</code> and <code>PRINT</code> are three different names. Only lowercase <code>print</code> exists.</p>",
         ok='print("ok")',
         bad=('Print("ok")', "NameError"),
         why="There is no tool named <code>Print</code>. Python even suggests the name you probably meant."),
    concept("Printing several things", "<p>One print can show many values, and you can choose what goes between and after them.</p>"),
    rule("3.5", "Commas print several things, with a space between",
         "<p>Give <code>print</code> several values separated by commas. It prints them on one line with one space between, and it can mix text and numbers.</p>",
         ok='print("Age:", 30)\nprint(1, 2, 3)',
         why="The comma is what separates the values. You do not need to add the space yourself."),
    rule("3.6", "sep and end change what goes between and after",
         "<p><code>sep</code> sets what goes <b>between</b> values (default: one space). <code>end</code> sets what goes <b>after</b> the last one (default: a new line).</p>",
         ok=['print("2026", "10", "15", sep="-")\nprint("a", "b", sep="")', 'print("Loading", end="...")\nprint("done")'],
         bad=('print("a", "b" sep="-")', "SyntaxError"),
         why="<code>sep=</code> is one more item in the list, so it needs a comma before it like any other item. In the second working example, <code>end=\"...\"</code> replaced the new line, so <code>done</code> landed on the same line."),
    rule("3.7", "print() with nothing prints an empty line",
         "<p>Empty brackets print just a new line. Useful to space out output.</p>",
         ok='print("one")\nprint()\nprint("two")'),
    concept("Quotes inside text, and long text", "<p>How to print a quote mark, and text that runs over several lines.</p>"),
    rule("3.8", "Quotes inside text",
         "<p>To put a quote character inside text, wrap the text in the <b>other</b> kind of quote, or put a backslash before it.</p>",
         ok='print("It\'s fine")\nprint(\'She said "hi"\')\nprint(\'It\\\'s also fine\')',
         bad=("print('It's broken')", "SyntaxError"),
         why="The <code>'</code> in <code>It's</code> closes the text early. Then <code>s broken')</code> is left over, which is not valid Python."),
    rule("3.9", "Triple quotes hold text across several lines",
         "<p>Normal quotes must open and close on the same line. Three quotes (<code>\"\"\"</code> or <code>'''</code>) can span many lines.</p>",
         ok='print("""Line one\nLine two\nLine three""")',
         bad=('print("Line one\nLine two")', "SyntaxError"),
         why="A normal string cannot continue to the next line. Python calls it an <i>unterminated string literal</i>: text that was opened and never closed."),
    concept("Comments: notes Python ignores", "<p>Anything after <code>#</code> on a line is a <b>comment</b>. Python skips it. Use comments to explain <i>why</i> a line exists.</p>", "comments"),
    rule("3.10", "Everything after # is ignored, to the end of that line",
         "<p>A comment can take a whole line or sit at the end of a line of code.</p>",
         ok='# This line is a note\nprint("Hi")  # this part is ignored\n# print("never runs")',
         why="The last line is code turned into a comment. This is the usual way to switch a line off while testing."),
    trap("a # inside quotes is just text",
         'print("Price #1 is 50")',
         "Inside quotes, <code>#</code> is an ordinary character. A comment only starts at a <code>#</code> that is outside any text."),
    rule("3.11", "A comment has no closing mark, so each line needs its own #",
         "<p>Python has no block comment. Every comment line starts with its own <code>#</code>.</p>",
         ok='# first note\n# second note\nprint("ok")',
         bad=('# first note\nsecond note\nprint("ok")', "SyntaxError"),
         why="Line 2 has no <code>#</code>, so Python tries to read <code>second note</code> as code: two names side by side is broken grammar."),
    trap("a triple-quoted string used as a multi-line note",
         '"""\nThis block is a string, not a comment.\nNothing uses it, so nothing happens.\n"""\nprint("ok")',
         "People often write multi-line notes this way. It is really a piece of text that nobody prints or stores, so Python makes it and throws it away. It works, but <code>#</code> on each line is the true comment."),
    concept("Modules: ready-made tools", '''
<p>A <b>module</b> is a file of ready-made code. Python ships with hundreds of them (the standard library). <code>import</code> loads one so you can use it.</p>
<p>After <code>import math</code>, you use its tools with a dot: <code>math.sqrt(16)</code> means "the <code>sqrt</code> tool from <code>math</code>".</p>''', "modules"),
    rule("3.12", "import a module before you use it",
         "<p>Imports go at the top of the file.</p>",
         ok='import math\nprint(math.sqrt(16))\nprint(math.pi)',
         bad=('print(math.sqrt(16))', "NameError"),
         why="Without <code>import math</code>, the name <code>math</code> does not exist yet."),
    rule("3.13", "The module name must be exact",
         "<p>Spelling and case must match the real module name.</p>",
         ok='import random\nprint(random.randint(5, 5))',
         bad=('import maths', "ModuleNotFoundError"),
         why="There is no module called <code>maths</code>; it is <code>math</code>. (<code>randint(5, 5)</code> picks a whole number from 5 to 5, so it always gives 5 here.)"),
    rule("3.14", "from ... import takes out one tool",
         "<p><code>from math import sqrt</code> loads only <code>sqrt</code>, and you then use it <b>without</b> the <code>math.</code> in front.</p>",
         ok='from math import sqrt\nprint(sqrt(25))',
         bad=('from math import sqrt\nprint(math.sqrt(25))', "NameError"),
         why="<code>from math import sqrt</code> creates the name <code>sqrt</code> only. The name <code>math</code> was never created."),
    rule("3.15", "os.listdir() lists the files in a folder",
         "<p>The <code>os</code> module talks to your computer's files and folders. <code>os.listdir(\".\")</code> gives a list of the names in the current folder (<code>.</code> means \"this folder\").</p>",
         ok='import os\nprint(os.listdir("."))',
         bad=('import os\nprint(os.listdir("no_such_folder"))', "FileNotFoundError"),
         files={"notes.txt": "hi\n"},
         why="This folder held <code>lesson.py</code> and <code>notes.txt</code>, so both names came back as a list. A folder that does not exist is a <code>FileNotFoundError</code>."),
    rule("3.16", "Modules from outside Python are installed with pip",
         "<p>The standard library comes with Python. Other modules (thousands, made by the community) must be installed first with <b>pip</b>, Python's installer, run in the terminal:</p>"
         '<pre class="code shell"><code>python3 -m pip install requests</code></pre>'
         "<p>Until it is installed, importing it fails with the same error as a misspelled name.</p>",
         bad=('import some_module_that_is_not_installed', "ModuleNotFoundError")),
    trap("naming your file after a module",
         'import random\nprint(random.__file__)',
         "This folder also holds a file named <code>random.py</code> that you wrote. Python checks your own folder first, so <code>import random</code> loaded <b>your</b> file, not the real module. "
         "Calling <code>random.randint</code> would then fail. Never name your files <code>random.py</code>, <code>math.py</code> or after any module you import.",
         files={"random.py": "# my practice file\n"}),
    rule("3.17", "Never name your own file after a module",
         "<p>Python looks in <b>your folder first</b> when you import. Think of two books with the same name on a shelf: Python grabs the one nearest to it, which is yours, and yours has none of the real tools.</p>",
         bad=('import random\nprint(random.randint(1, 6))', "AttributeError"),
         files={"random.py": 'print("this is MY random.py")\n'},
         why="Line 1 of the output shows your file ran instead of the real module. Then <code>randint</code> is missing, because your file never defined it. Python 3.14 on a computer even suggests the fix: <i>consider renaming</i> your file. (The in-browser Run leaves that hint out.)"),
    exercises([
        {"kind": "Predict", "code": 'print("a", "b", "c", sep="")', "a": "<code>sep=\"\"</code> puts nothing between the values."},
        {"kind": "Predict", "code": 'print("Hi", end=" ")\nprint("there")', "a": "<code>end=\" \"</code> replaces the new line with a space, so both words share one line."},
        {"kind": "Predict", "code": 'print(\'I\'m here\')', "expect": "SyntaxError", "a": "The <code>'</code> in <code>I'm</code> closes the text. Fix: <code>print(\"I'm here\")</code>."},
        {"kind": "Predict", "code": 'print("start")  # print("hidden")\n# print("also hidden")\nprint("end")', "a": "Everything after <code>#</code> is skipped, so only two lines print."},
        {"kind": "Predict", "code": 'print(10, "10", True)', "a": "All three print the same way. Quotes only matter in the code: <code>\"10\"</code> is text, <code>10</code> a number."},
        {"kind": "Predict", "code": 'print(Goa)', "expect": "NameError", "a": "Without quotes, <code>Goa</code> is a name nobody created."},
        {"kind": "Predict", "code": 'import math\nprint(math.sqrt(81))\nprint(Math.pi)', "expect": "NameError",
         "a": "<code>9.0</code> prints first (sqrt always gives a decimal). Then <code>Math</code> with a capital M does not exist."},
        {"kind": "Write", "q": "Print the date <code>15/10/2026</code> using three separate values <code>15</code>, <code>10</code>, <code>2026</code> and <code>sep</code>.",
         "sol": 'print(15, 10, 2026, sep="/")'},
        {"kind": "Write", "q": "Print this on three lines using one print and triple quotes:<br><code>Name: Ravi</code><br><code>Role: QA</code><br><code>Team: Payments</code>",
         "sol": 'print("""Name: Ravi\nRole: QA\nTeam: Payments""")'},
        {"kind": "Write", "q": "Use the <code>math</code> module to print the square root of 144 and the value of pi.",
         "sol": 'import math\nprint(math.sqrt(144))\nprint(math.pi)'},
    ], "3"),
]))

# ===== 4 =====
topic("4", "variables", "Variables, types and operators",
      "Store values under names, know what type each value is, and do maths with them.", "".join([
    concept("A variable is a name tag on a value", '''
<p>A <b>variable</b> is a name you give to a value so you can use it later. You create one with <code>=</code>.</p>'''),
    d_label(),
    rule("4.1", "= means \"store\", and the name goes on the left",
         "<p><code>=</code> is not \"equals\" like in maths. It means: <b>work out the right side, then put that name on the result.</b></p>",
         ok='age = 30\nage = age + 1\nprint(age)',
         bad=('30 = age', "SyntaxError"),
         why="You cannot store something inside the number 30. Only a name can go on the left. (<code>==</code>, two equals signs, is for comparing: rule 4.14.)"),
    rule("4.2", "A name must exist before you use it",
         "<p>Python runs top to bottom, so a variable must be created on a line <b>above</b> the line that uses it.</p>",
         ok='score = 10\nprint(score)',
         bad=('print(score)\nscore = 10', "NameError"),
         why="When line 1 runs, line 2 has not happened yet, so <code>score</code> does not exist."),
    rule("4.3", "Names may use letters, digits and _ only",
         "<p>No spaces, no <code>-</code>, no symbols like <code>@</code> or <code>$</code>.</p>",
         ok='user_name = "Ravi"\nprint(user_name)',
         bad=[('user-name = "Ravi"', "SyntaxError"), ('user name = "Ravi"', "SyntaxError"), ('@name = "Ravi"', "SyntaxError")],
         why="Python reads <code>-</code> as minus, so <code>user-name</code> means \"user minus name\", which cannot be on the left of <code>=</code>. A space splits it into two names."),
    rule("4.4", "A name cannot start with a digit",
         "<p>Digits are allowed, just not first. An underscore <b>can</b> come first: <code>_hidden</code> is a valid name.</p>",
         ok='player2 = "Asha"\n_hidden = 7\nprint(player2, _hidden)',
         bad=('2player = "Asha"', "SyntaxError"),
         why="Anything starting with a digit is read as a number, and <code>2player</code> is not a valid number."),
    rule("4.5", "A name cannot be a keyword",
         "<p><b>Keywords</b> are words Python reserves for its own grammar: <code>if</code>, <code>for</code>, <code>class</code>, <code>True</code>, <code>None</code>, <code>def</code>, <code>import</code> and others. This prints the full list:</p>",
         ok='import keyword\nprint(keyword.kwlist)',
         bad=('class = "10A"', "SyntaxError"),
         why="<code>class</code> already means something to Python. Use <code>class_name</code> instead."),
    rule("4.6", "Capital letters make a different name",
         "<p><code>age</code>, <code>Age</code> and <code>AGE</code> are three separate variables.</p>",
         ok='age = 30\nprint(age)',
         bad=('age = 30\nprint(Age)', "NameError"),
         why="Only <code>age</code> was created. By convention Python names are all lowercase with <code>_</code> between words (<code>total_price</code>), called <b>snake_case</b>. Breaking the convention is not an error, but everyone reading your code expects it."),
    trap("reusing a built-in name",
         'print("before")\nprint = "oops"',
         "This runs, but you just replaced the <code>print</code> tool with a piece of text. Any <code>print(...)</code> after it fails with <code>TypeError: 'str' object is not callable</code>. "
         "<code>print</code>, <code>input</code>, <code>list</code>, <code>str</code>, <code>int</code>, <code>type</code>, <code>sum</code> and <code>max</code> are not keywords, so Python allows it. Never use them as names."),
    concept("Every value has a type", "<p>The <b>type</b> says what kind of value it is, and decides what you can do with it. <code>type()</code> tells you the type.</p>", "types"),
    table(["Type", "Means", "Examples"], [
        ["<code>int</code>", "whole number", "<code>5</code>, <code>-3</code>, <code>0</code>"],
        ["<code>float</code>", "number with a decimal point", "<code>5.0</code>, <code>3.14</code>, <code>-0.5</code>"],
        ["<code>str</code>", "text (a string of characters)", "<code>\"hi\"</code>, <code>'5'</code>, <code>\"\"</code>"],
        ["<code>bool</code>", "yes or no", "<code>True</code>, <code>False</code>"],
        ["<code>NoneType</code>", "nothing, no value yet", "<code>None</code>"],
    ]),
    rule("4.7", "type() tells you what kind of value you have",
         "<p>Put any value or name inside the brackets. Use it whenever you are not sure what you are holding.</p>",
         ok='print(type(5))\nprint(type(5.0))\nprint(type("5"))\nprint(type(True))\nprint(type(None))\nage = input("Age: ")\nprint(type(age))',
         ok_typed=["25"],
         bad=('print(type())', "TypeError"),
         why="<code>type()</code> needs one value to look at. The last working line shows why it is useful: the typed age is a <code>str</code>, not an <code>int</code>."),
    rule("4.8", "Quotes make it text, even if it looks like a number",
         "<p><code>5</code> is a number. <code>\"5\"</code> is text that happens to contain the character 5. They behave differently.</p>",
         ok='print(5 + 5)\nprint("5" + "5")',
         why="Numbers add. Text joins end to end. Same symbol <code>+</code>, different job, because the types differ."),
    rule("4.9", "True, False and None start with a capital letter",
         "<p>Only the capitalised spelling exists.</p>",
         ok='done = True\nprint(done)',
         bad=('done = true', "NameError"),
         why="Lowercase <code>true</code> is treated as a variable name you never created."),
    trap("commas in big numbers",
         'salary = 1,000\nprint(salary)',
         "No error, but the value is wrong. A comma makes a <b>tuple</b> (a group of values, Chapter 6), so this is the pair <code>(1, 0)</code>. "
         "To make big numbers readable, use underscores: <code>1_000_000</code>."),
    concept("Operators: doing maths", "", "operators"),
    table(["Operator", "Does", "Example", "Result"], [
        ["<code>+</code>", "add", "<code>7 + 2</code>", "<code>9</code>"],
        ["<code>-</code>", "subtract", "<code>7 - 2</code>", "<code>5</code>"],
        ["<code>*</code>", "multiply", "<code>7 * 2</code>", "<code>14</code>"],
        ["<code>/</code>", "divide", "<code>7 / 2</code>", "<code>3.5</code>"],
        ["<code>//</code>", "divide, keep only the whole part", "<code>7 // 2</code>", "<code>3</code>"],
        ["<code>%</code>", "remainder after dividing", "<code>7 % 2</code>", "<code>1</code>"],
        ["<code>**</code>", "power", "<code>7 ** 2</code>", "<code>49</code>"],
    ]),
    example('print(7 + 2, 7 - 2, 7 * 2)\nprint(7 / 2, 7 // 2, 7 % 2, 7 ** 2)', label="The table above, actually run:"),
    rule("4.10", "/ always gives a float",
         "<p>Even when the answer is a whole number.</p>",
         ok='print(10 / 2)\nprint(10 // 2)',
         why="<code>/</code> is true division and always returns a <code>float</code>. Use <code>//</code> when you want a whole number."),
    rule("4.11", "Mixing int and float gives a float",
         "<p>If either side is a float, the answer is a float.</p>",
         ok='print(5 + 2.0)\nprint(3 * 1.5)'),
    rule("4.12", "Text and numbers do not mix with +",
         "<p>Python will not guess whether you meant maths or joining text.</p>",
         ok='age = 30\nprint("Age: " + str(age))\nprint("Age:", age)\nprint(f"Age: {age}")',
         bad=('age = 30\nprint("Age: " + age)', "TypeError"),
         why="<code>+</code> between a <code>str</code> and an <code>int</code> has no meaning. Convert with <code>str()</code>, or use a comma, or an f-string (rule 4.21)."),
    rule("4.13", "Not every operator works on text",
         "<p>Text supports <code>+</code> (join) and <code>*</code> with a whole number (repeat). Nothing else.</p>",
         ok='print("ab" * 3)\nprint("-" * 10)',
         bad=[('print("ab" - "a")', "TypeError"), ('print("ab" * "3")', "TypeError")],
         why="Removing text with <code>-</code> is not defined. And <code>*</code> on text means \"repeat\", which needs a count: a number, not the text <code>\"3\"</code>."),
    concept("Comparing and combining", "<p>Ask questions about values; the answer is always True or False.</p>"),
    rule("4.14", "Comparisons give True or False",
         "<p><code>==</code> equal, <code>!=</code> not equal, <code>&lt;</code> <code>&gt;</code> <code>&lt;=</code> <code>&gt;=</code>. The answer is always a <code>bool</code>.</p>",
         ok='print(5 == 5)\nprint(5 != 5)\nprint(3 < 10)\nprint("5" == 5)',
         why="The last one is <code>False</code>: text <code>\"5\"</code> and number <code>5</code> are different types, so they are never equal. One <code>=</code> stores; two <code>==</code> compare."),
    rule("4.15", "and, or, not combine True and False",
         "<p><code>and</code>: True only if <b>both</b> sides are True. <code>or</code>: True if <b>at least one</b> side is True. <code>not</code>: flips True to False and back.</p>",
         ok='print(True and False)\nprint(True or False)\nprint(not True)\nage = 25\nprint(age > 18 and age < 60)\nprint(age < 18 or age > 60)',
         bad=('print(True && False)', "SyntaxError"),
         why="Python uses the words <code>and</code>, <code>or</code>, <code>not</code>. The symbols <code>&amp;&amp;</code> and <code>||</code> from other languages are not Python."),
    table(["a", "b", "a and b", "a or b", "not a"], [
        ["True", "True", "True", "True", "False"],
        ["True", "False", "False", "True", "False"],
        ["False", "True", "False", "True", "True"],
        ["False", "False", "False", "False", "True"],
    ]),
    example('print(True and True, True or True, not True)\nprint(True and False, True or False, not True)\nprint(False and True, False or True, not False)\nprint(False and False, False or False, not False)', label="The table above, actually run, row by row:"),
    concept("Gotchas and shortcuts", "<p>One error to avoid, the order maths happens in, and two time-savers.</p>"),
    rule("4.16", "You cannot divide by zero",
         "",
         ok='print(10 / 4)',
         bad=('print(10 / 0)', "ZeroDivisionError"),
         why="Dividing by 0 has no answer in maths, so Python stops. <code>//</code> and <code>%</code> by 0 fail the same way."),
    rule("4.17", "Order of operations: ** first, then * / // %, then + -",
         "<p>Same as school maths. Brackets go first of all.</p>",
         ok='print(2 + 3 * 4)\nprint((2 + 3) * 4)\nprint(2 * 3 ** 2)',
         why="<code>3 * 4</code> runs before <code>+ 2</code>. When unsure, add brackets: they cost nothing and make the order obvious."),
    rule("4.18", "+= and friends update a name using its old value",
         "<p><code>count += 5</code> is short for <code>count = count + 5</code>. The same works with <code>-=</code>, <code>*=</code>, <code>/=</code>. The name must already exist.</p>",
         ok='count = 10\ncount += 5\nprint(count)\ncount -= 3\nprint(count)\ncount *= 2\nprint(count)',
         bad=('total += 5', "NameError"),
         why="<code>total += 5</code> means <code>total = total + 5</code>, and the right side needs an old <code>total</code> that was never created."),
    rule("4.19", "Several names in one line, and swapping",
         "<p>Put names on the left and values on the right, both separated by commas. The counts must match.</p>",
         ok='a, b = 1, 2\nprint(a, b)\na, b = b, a\nprint(a, b)',
         bad=('a, b = 1, 2, 3', "ValueError"),
         why="Python works out the whole right side first, then hands the values out in order. That is why <code>a, b = b, a</code> swaps them with no extra variable."),
    concept("Converting between types", "", "convert"),
    table(["Call", "Result", "Note"], [
        ["<code>int(\"42\")</code>", "<code>42</code>", "text to whole number"],
        ["<code>int(9.99)</code>", "<code>9</code>", "cuts off the decimal, does <b>not</b> round"],
        ["<code>float(\"3.5\")</code>", "<code>3.5</code>", "text to decimal"],
        ["<code>str(42)</code>", "<code>\"42\"</code>", "anything to text"],
        ["<code>round(9.99)</code>", "<code>10</code>", "this one rounds"],
        ["<code>round(3.14159, 2)</code>", "<code>3.14</code>", "round to 2 decimal places"],
        ["<code>bool(0)</code>, <code>bool(\"\")</code>", "<code>False</code>", "zero, empty text and <code>None</code> are False"],
        ["<code>bool(5)</code>, <code>bool(\"hi\")</code>", "<code>True</code>", "everything else is True"],
    ]),
    example('print(int("42"), int(9.99), float("3.5"), str(42), round(9.99), round(3.14159, 2))\nprint(bool(0), bool(""), bool(None), bool(5), bool("hi"))', label="The table above, actually run:"),
    trap("bool(\"False\") is True",
         'print(bool("False"))\nprint(bool(" "))',
         "Any text that is not empty counts as True, even the word <code>\"False\"</code> and a single space. Only <code>\"\"</code> (nothing between the quotes) is False."),
    rule("4.20", "int() only accepts text that is a whole number",
         "",
         ok='print(int("12"))\nprint(int(float("3.5")))',
         bad=[('print(int("3.5"))', "ValueError"), ('print(int("abc"))', "ValueError")],
         why="<code>int()</code> reading text needs whole-number text. For <code>\"3.5\"</code>, convert to <code>float</code> first, then to <code>int</code>."),
    concept("TypeError or ValueError?", '''
<p><b>TypeError</b>: the wrong <i>kind</i> of thing for the action. <code>"a" + 5</code>: text and a number cannot be added.</p>
<p><b>ValueError</b>: the right kind of thing, but bad <i>content</i>. <code>int("abc")</code>: <code>int()</code> does accept text, just not this text.</p>'''),
    rule("4.21", "f-strings put values inside text",
         "<p>Put an <code>f</code> before the opening quote, then a variable <b>or a calculation</b> inside <code>{ }</code>. No converting needed.</p>"
         "<p>After a <code>:</code> inside the braces you can say how to show the value. <code>:.2f</code> means \"a decimal number with exactly 2 digits after the dot\".</p>",
         ok='name = "Ravi"\nprice = 49.5\nprint(f"{name} paid {price}")\nprint(f"Total: {price * 2}")\nprint(f"Total: {price * 2:.2f}")\nprint(f"{10 / 3:.2f}")',
         bad=('price = 49.5\nprint(f"Total: {price")', "SyntaxError"),
         why="In <code>{price * 2:.2f}</code>, Python first works out <code>price * 2</code> = <code>99.0</code>, then <code>:.2f</code> shows it as <code>99.00</code>. A brace that opens must close, or the whole file fails to run."),
    rule("4.22", "Older ways to fill in text: .format() and %",
         "<p>You will meet these in older code. <code>{}</code> slots are filled by <code>.format()</code> in order; <code>%s</code> (text) and <code>%d</code> (whole number) are filled by <code>%</code>. f-strings do the same job more clearly.</p>",
         ok='name = "Ravi"\nage = 25\nprint("{} is {}".format(name, age))\nprint("%s is %d" % (name, age))\nprint(f"{name} is {age}")',
         bad=('print("{} and {}".format("tea"))', "IndexError"),
         why="Two slots but only one value: there is nothing to put in the second <code>{}</code>."),
    trap("forgetting the f",
         'name = "Ravi"\nprint("Hello {name}")',
         "Without the <code>f</code>, the braces are just characters, so Python prints them as they are."),
    trap("decimals are not always exact",
         'print(0.1 + 0.2)\nprint(round(0.1 + 0.2, 2))',
         "Computers store decimals in binary, and 0.1 cannot be stored exactly, so tiny errors appear. Round when you show money or measurements."),
    rule("4.23", "input() always gives text",
         "<p><code>input()</code> shows a message, waits for the user to type, and returns what they typed as a <code>str</code>. To do maths with it, convert it.</p>",
         ok=['age = input("Your age: ")\nprint(type(age))\nprint(int(age) + 1)', 'price = float(input("Price: "))\nprint(price * 2)'], ok_typed=["25", ],
         why="Even when the user types digits, <code>input()</code> returns text. <code>age + 1</code> would be a TypeError. In these outputs the typed value is shown after the prompt."),
    exercises([
        {"kind": "Predict", "code": 'x = 10\nx = x * 2\nx += 1\nprint(x)', "a": "10 times 2 is 20, plus 1 is 21."},
        {"kind": "Predict", "code": 'print(7 / 7)\nprint(7 // 2)\nprint(7 % 2)', "a": "<code>/</code> always gives a float, so <code>1.0</code>. Then 3 (whole part) and 1 (remainder)."},
        {"kind": "Predict", "code": 'total = "5" + "5"\nprint(total)', "a": "Both are text, so <code>+</code> joins them: <code>55</code>, not 10."},
        {"kind": "Predict", "code": 'my-score = 10', "expect": "SyntaxError", "a": "<code>-</code> is minus. Fix: <code>my_score = 10</code>."},
        {"kind": "Predict", "code": 'Name = "Ravi"\nprint(name)', "expect": "NameError", "a": "<code>Name</code> and <code>name</code> are different. Fix: use the same spelling on both lines."},
        {"kind": "Predict", "code": 'print(int("12") + 3)', "a": "Text <code>\"12\"</code> becomes the number 12, plus 3."},
        {"kind": "Predict", "code": 'print(int("12.0"))', "expect": "ValueError", "a": "<code>\"12.0\"</code> is not whole-number text. Fix: <code>int(float(\"12.0\"))</code>."},
        {"kind": "Predict", "code": 'print("hi")\nprint(10 / 0)', "expect": "ZeroDivisionError", "a": "<code>hi</code> prints first. The error happens in pass 2, on line 2."},
        {"kind": "Predict", "code": 'price = 1,500\nprint(price)', "a": "The comma made a tuple of two numbers. Fix: <code>price = 1_500</code> or <code>1500</code>."},
        {"kind": "Predict", "code": 'print(int(7.9) + 2 ** 2 * 3)', "a": "<code>int(7.9)</code> cuts to 7. <code>2 ** 2</code> is 4, times 3 is 12. 7 + 12 = 19."},
        {"kind": "Predict", "code": 'a = 5\nb = "5"\nprint(a == b, str(a) == b)', "a": "A number never equals text. After <code>str(a)</code> both are <code>\"5\"</code>."},
        {"kind": "Predict", "code": 'age = 15\nprint(age > 12 and age < 20, not age > 12)', "a": "Both sides are True, so <code>and</code> is True. <code>age > 12</code> is True, and <code>not</code> flips it."},
        {"kind": "Predict", "code": 'print(bool(""), bool("0"), bool(0))', "a": "Only empty text and zero are False. <code>\"0\"</code> is text with one character, so it is True."},
        {"kind": "Predict", "code": 'price = 7.5\nprint(f"{price * 2:.1f} and {price:.2f}")', "a": "<code>:.1f</code> shows one digit after the dot, <code>:.2f</code> shows two."},
        {"kind": "Predict", "code": 'done = true', "expect": "NameError", "a": "Lowercase <code>true</code> is read as a name that does not exist."},
        {"kind": "Write", "q": "Make <code>price = 499</code> and <code>qty = 3</code>. Print <code>Total: 1497</code> using an f-string.",
         "sol": 'price = 499\nqty = 3\nprint(f"Total: {price * qty}")'},
        {"kind": "Write", "q": "Make <code>a = \"10\"</code> and <code>b = 5</code>. Print <code>15</code>.",
         "sol": 'a = "10"\nb = 5\nprint(int(a) + b)'},
        {"kind": "Write", "q": "Ask the user for two numbers with <code>input()</code> and print their sum. (Typed here: 4 and 6.)",
         "sol": 'x = input("First: ")\ny = input("Second: ")\nprint(int(x) + int(y))', "typed": ["4", "6"]},
        {"kind": "Write", "q": "A bill is 1,234 rupees split between 3 people. Print each share rounded to 2 decimal places, using <code>:.2f</code>.",
         "sol": 'bill = 1_234\nshare = bill / 3\nprint(f"Each pays {share:.2f}")'},
        {"kind": "Write", "q": "Swap the values of <code>x = \"left\"</code> and <code>y = \"right\"</code> in one line, then print both.",
         "sol": 'x = "left"\ny = "right"\nx, y = y, x\nprint(x, y)'},
    ], "4"),
]))

# ===== 5 =====
topic("5", "strings", "Strings",
      "Work with text: pick out characters, cut pieces, change case, split and join.", "".join([
    concept("A string is a row of characters", '''
<p>A <b>string</b> (<code>str</code>) is text: a row of characters, each with a numbered position called its <b>index</b>.</p>'''),
    d_index(),
    rule("5.1", "Indexing starts at 0",
         "<p><code>word[0]</code> is the first character. <code>word[len(word) - 1]</code> is the last. <code>len()</code> gives the number of characters.</p>",
         ok='word = "Python"\nprint(word[0])\nprint(word[5])\nprint(len(word))',
         bad=('word = "Python"\nprint(word[6])', "IndexError"),
         why="There are 6 characters, at positions 0 to 5. Position 6 does not exist."),
    rule("5.2", "Negative indexes count from the end",
         "<p><code>-1</code> is the last character, <code>-2</code> the one before it.</p>",
         ok='word = "Python"\nprint(word[-1])\nprint(word[-6])',
         bad=('word = "Python"\nprint(word[-7])', "IndexError"),
         why="Negative positions go from -1 to -6 for a 6-character word."),
    rule("5.3", "Slicing [start:stop] stops BEFORE stop",
         "<p><code>word[1:4]</code> takes positions 1, 2 and 3. Leave out start to begin at 0; leave out stop to go to the end.</p>",
         ok='word = "Python"\nprint(word[1:4])\nprint(word[:2])\nprint(word[2:])\nprint(word[-3:])',
         why="Stop is not included, so <code>word[0:2]</code> gives 2 characters. A handy check: <code>stop - start</code> = how many you get."),
    rule("5.4", "Negative numbers work in slices too",
         "<p>Start and stop can both count from the end. The same \"stop is not included\" rule applies.</p>",
         ok='word = "Python"\nprint(word[-4:-1])\nprint(word[-3:])\nprint(word[:-2])',
         why="<code>-4</code> is <code>t</code> and <code>-1</code> is <code>n</code>, which is not included, so you get <code>tho</code>. <code>[:-2]</code> means \"everything except the last 2\"."),
    rule("5.5", "A third number is the step",
         "<p><code>[start:stop:step]</code>: the step is the jump size. The <b>sign</b> is the direction: no sign goes forwards, <code>-</code> goes backwards.</p>",
         ok='word = "Python"\nprint(word[::2])\nprint(word[::-1])\nprint(word[::-2])\nprint(word[::-3])\nprint("abcdefghij"[1:8:2])',
         bad=('word = "Python"\nprint(word[::0])', "ValueError"),
         why="<code>[::2]</code> takes 1, skips 1. <code>[::-2]</code> does the same from the end: <code>n</code>, <code>h</code>, <code>y</code>. With start and stop, <code>[1:8:2]</code> takes positions 1, 3, 5, 7. A step of 0 would never move, so Python refuses it."),
    trap("a slice past the end does not fail",
         'word = "Python"\nprint(word[2:100])\nprint(word[10:20])',
         "An index past the end is an IndexError, but a slice past the end just stops where the text stops. The second line gives an empty string, so an empty line prints."),
    concept("Strings never change", "<p>Once made, a string stays as it is. Every change makes a new one.</p>"),
    rule("5.6", "Strings cannot be changed in place",
         "<p>Strings are <b>immutable</b>: once made, their characters cannot be replaced. You build a new string instead.</p>",
         ok='word = "Python"\nnew = "J" + word[1:]\nprint(new)\nprint(word)',
         bad=('word = "Python"\nword[0] = "J"', "TypeError"),
         why="Reading <code>word[0]</code> is allowed; writing to it is not. Slicing and joining make a new string and leave the old one as it was."),
    rule("5.7", "Methods return a NEW string; the original stays the same",
         "<p>A <b>method</b> is a function that belongs to a value, used with a dot: <code>name.upper()</code>. String methods never change the original.</p>",
         ok='name = "ravi"\nprint(name.upper())\nprint(name)\nname = name.upper()\nprint(name)',
         why="<code>name.upper()</code> made a new string. To keep it, store it, as on line 4."),
    rule("5.8", "name = name.upper() moves the name; the old string is untouched",
         "<p>It <i>looks</i> like the string changed. Really, <code>upper()</code> built a new string in memory, and <code>=</code> moved the name over to it. Give the old string a second name first and you can still see it.</p>",
         ok='name = "ravi"\nother = name\nname = name.upper()\nprint(name)\nprint(other)\nprint(name is other)',
         why="<code>other</code> still shows <code>ravi</code>, so the original was never changed. <code>is</code> asks \"are these the exact same thing in memory?\", and the answer is <code>False</code>: two different strings now."),
    concept("Common string methods", ""),
    table(["Method", "Does", "Example", "Result"], [
        ["<code>.upper()</code> <code>.lower()</code>", "all capitals / all small", "<code>\"Hi\".upper()</code>", "<code>\"HI\"</code>"],
        ["<code>.title()</code>", "capital first letter of each word", "<code>\"ravi kumar\".title()</code>", "<code>\"Ravi Kumar\"</code>"],
        ["<code>.strip()</code>", "remove spaces at both ends", "<code>\"  hi  \".strip()</code>", "<code>\"hi\"</code>"],
        ["<code>.replace(a, b)</code>", "swap every a for b", "<code>\"a-b-c\".replace(\"-\", \"+\")</code>", "<code>\"a+b+c\"</code>"],
        ["<code>.find(x)</code>", "index of first x, or -1 if missing", "<code>\"hello\".find(\"l\")</code>", "<code>2</code>"],
        ["<code>.count(x)</code>", "how many times x appears", "<code>\"hello\".count(\"l\")</code>", "<code>2</code>"],
        ["<code>.startswith(x)</code>", "True if it begins with x", "<code>\"test_login\".startswith(\"test\")</code>", "<code>True</code>"],
        ["<code>.split(sep)</code>", "cut into a list at each sep", "<code>\"a,b,c\".split(\",\")</code>", "<code>['a', 'b', 'c']</code>"],
        ["<code>sep.join(list)</code>", "glue a list into one string", "<code>\"-\".join([\"a\", \"b\"])</code>", "<code>\"a-b\"</code>"],
    ]),
    example('print("Hi".upper(), "ravi kumar".title(), "  hi  ".strip())\nprint("a-b-c".replace("-", "+"), "hello".find("l"), "hello".count("l"))\nprint("test_login".startswith("test"), "a,b,c".split(","), "-".join(["a", "b"]))', label="The table above, actually run:"),
    concept("Changing case and cleaning", "<p>The table is a summary; from here each method gets its own rule. First: case, spaces and swapping text.</p>"),
    rule("5.9", "Five methods change the case",
         "<p><code>upper()</code> all capitals, <code>lower()</code> all small, <code>title()</code> capital at the start of each word, <code>capitalize()</code> capital at the start of the whole text only, <code>swapcase()</code> flips every letter.</p>",
         ok='s = "hello WORLD"\nprint(s.upper())\nprint(s.lower())\nprint(s.title())\nprint(s.capitalize())\nprint(s.swapcase())',
         bad=('s = "hello"\nprint(s.Upper())', "AttributeError"),
         why="Method names are lowercase like everything else. An <code>AttributeError</code> means \"this value has no tool with that name\". Note <code>capitalize()</code> also made <code>WORLD</code> small."),
    rule("5.10", "strip() cleans both ends; lstrip() and rstrip() clean one side",
         "<p>They remove spaces (and new lines and tabs) from the edges only, never from the middle. The brackets in the output below show where the text starts and ends.</p>",
         ok='s = "   hi there   "\nprint("[" + s.strip() + "]")\nprint("[" + s.lstrip() + "]")\nprint("[" + s.rstrip() + "]")\nprint("**sale**".strip("*"))',
         why="The space between <code>hi</code> and <code>there</code> stays. Give <code>strip</code> characters to remove other things from the edges, like <code>\"*\"</code>."),
    rule("5.11", "replace() swaps every match, and can be chained",
         "<p><code>replace(old, new)</code> gives a new string with every <code>old</code> swapped for <code>new</code>. Since it returns a string, you can call another method straight on the result.</p>",
         ok='s = "a-b-c"\nprint(s.replace("-", "+"))\nprint(s.replace("-", ""))\nprint(s.replace("-", "+").replace("a", "A"))\nprint("Hello hello".replace("hello", "bye"))',
         bad=('print("a-b".replace("-"))', "TypeError"),
         why="<code>replace</code> needs two things: what to find and what to put instead. It is case-sensitive, so <code>Hello</code> with a capital stayed."),
    concept("Searching inside text", "<p>Find where something is, how often it appears, and what kind of text you have.</p>"),
    rule("5.12", "find() gives -1 when missing; index() raises an error",
         "<p>Both tell you the position of the <b>first</b> match. They only differ when the text is not there.</p>",
         ok='s = "banana"\nprint(s.find("n"))\nprint(s.index("n"))\nprint(s.find("z"))',
         bad=('print("banana".index("z"))', "ValueError"),
         why="<code>find</code> answers \"not found\" with -1. <code>index</code> stops the program. Use <code>find</code> when missing is normal, <code>index</code> when missing is a real bug."),
    rule("5.13", "count() counts matches that do not overlap",
         "",
         ok='print("banana".count("a"))\nprint("banana".count("an"))\nprint("aaaa".count("aa"))\nprint("banana".count("z"))',
         why="In <code>aaaa</code>, Python finds <code>aa</code>, then carries on after it, so it finds 2, not 3. A missing piece counts as 0, with no error."),
    rule("5.14", "startswith() and endswith() are case-sensitive",
         "",
         ok='f = "report.PDF"\nprint(f.endswith(".pdf"))\nprint(f.lower().endswith(".pdf"))\nprint("test_login".startswith("test"))',
         why="<code>.PDF</code> and <code>.pdf</code> are different text. Lowercase the string first when the case should not matter."),
    rule("5.15", "The is-methods answer True or False about the whole text",
         "<p><code>isdigit()</code> only digits, <code>isalpha()</code> only letters, <code>isalnum()</code> only letters and digits, <code>isspace()</code> only spaces, <code>islower()</code> / <code>isupper()</code> all letters small / capital.</p>",
         ok='print("123".isdigit(), "abc".isalpha(), "abc123".isalnum())\nprint("   ".isspace(), "hello".islower(), "HELLO".isupper())'),
    trap("isdigit() says no to decimals and minus signs",
         'print("12.5".isdigit())\nprint("-5".isdigit())\nprint("".isdigit())',
         "The dot and the minus are not digits, so the answer is False even though these look like numbers. Empty text is False too."),
    concept("Shaping, splitting and joining", "<p>Pad text, cut it into a list, and glue a list back together.</p>"),
    rule("5.16", "center() and zfill() pad text to a width",
         "<p><code>center(width, fill)</code> puts the text in the middle of a line that many characters wide. <code>zfill(width)</code> adds zeros at the front.</p>",
         ok='print("hi".center(10, "*"))\nprint("7".zfill(3))\nprint("42".zfill(5))',
         bad=('print("hi".center("10"))', "TypeError"),
         why="The width must be a number. <code>zfill</code> is handy for ids like <code>007</code>."),
    rule("5.17", "A method needs brackets to run",
         "<p>Without <code>()</code> you are pointing at the tool, not using it.</p>",
         ok='name = "ravi"\nprint(name.upper())',
         bad=('name = "ravi"\nprint(name.upper)\nprint(name.upper + "!")', "TypeError"),
         why="Line 2 prints a description of the method, not the result (no error, just useless output). Line 3 tries to add text to a method, which is a TypeError."),
    rule("5.18", "split() with no argument splits on any spaces; split(\"\") fails",
         "<p>To get single characters, use <code>list(text)</code> instead.</p>",
         ok='print("one  two   three".split())\nprint(list("abc"))',
         bad=('print("abc".split(""))', "ValueError"),
         why="An empty separator has nothing to split on. Python calls it an <i>empty separator</i>."),
    rule("5.19", "join is called on the glue, and every item must be text",
         "<p>Write <code>\"glue\".join(items)</code>, not <code>items.join(...)</code>.</p>",
         ok='words = ["QA", "is", "fun"]\nprint(" ".join(words))',
         bad=[('words = ["QA", "is", "fun"]\nprint(words.join(" "))', "AttributeError"), ('print("-".join(["a", 1]))', "TypeError")],
         why="Lists have no <code>join</code> method (an <code>AttributeError</code> means \"this value has no tool by that name\"). And <code>join</code> only glues text, so a number in the list fails."),
    concept("Checking text, and special characters", "<p>Test what text contains, and write characters you cannot type directly.</p>"),
    rule("5.20", "in checks whether text contains something",
         "<p>Gives <code>True</code> or <code>False</code>. It is case-sensitive.</p>",
         ok='msg = "Login failed"\nprint("fail" in msg)\nprint("Fail" in msg)\nprint("fail" in msg.lower())\nprint("pass" not in msg)'),
    trap("sorted() on a string gives a list",
         'print(sorted("hello"))\nprint("".join(sorted("hello")))',
         "<code>sorted</code> always returns a list, here of single letters. Join it back with <code>\"\".join(...)</code> to get text again."),
    rule("5.21", "Escape characters start with a backslash",
         "<p><code>\\n</code> new line, <code>\\t</code> tab, <code>\\\\</code> one backslash, <code>\\\"</code> a quote. For Windows paths, put <code>r</code> before the quotes (a <b>raw</b> string) so backslashes are kept as typed.</p>",
         ok='print("one\\ntwo")\nprint("a\\tb")\nprint("C:\\\\Users")\nprint(r"C:\\new\\test")',
         why="Without the <code>r</code>, <code>\\n</code> in <code>C:\\new</code> would become a new line."),
    rule("5.22", "repr() shows a string exactly as Python stores it",
         "<p><code>print</code> shows the text the way a reader sees it. <code>repr</code> shows the quotes and turns hidden characters like tabs and new lines back into <code>\\t</code> and <code>\\n</code>.</p>",
         ok='s = "a\\tb\\n"\nprint(s)\nprint(repr(s))',
         why="Use <code>repr</code> when text looks right but behaves oddly: it reveals spaces, tabs and new lines you cannot see."),
    concept("Small programs with what you know", "<p>No new tools here, just the ones above combined.</p>"),
    example('w = "madam"\nprint(w == w[::-1])        # palindrome check: same backwards?\ns = "the quick brown fox"\nprint(len(s.split()))       # count words\nprint(s.replace(" ", ""))   # remove all spaces\nprint(s.title())            # capital first letters'),
    exercises([
        {"kind": "Predict", "code": 's = "Bengaluru"\nprint(s[0], s[-1], len(s))', "a": "First character, last character, and 9 characters in total."},
        {"kind": "Predict", "code": 'print("abcdefg"[::-2])', "a": "From the end, take one and skip one: g, e, c, a."},
        {"kind": "Predict", "code": 'print("hello world".capitalize(), "|", "hello world".title())', "a": "<code>capitalize</code> touches only the first letter of the whole text; <code>title</code> does every word."},
        {"kind": "Predict", "code": 'print("data.csv".index("x"))', "expect": "ValueError", "a": "<code>index</code> raises an error when the text is missing. <code>find</code> would give -1."},
        {"kind": "Predict", "code": 'print("2024".isdigit(), "20.24".isdigit())', "a": "The dot is not a digit."},
        {"kind": "Predict", "code": 'city = "goa"\nother = city\ncity = city.upper()\nprint(other)', "a": "<code>upper()</code> made a new string. <code>other</code> still names the old one."},
        {"kind": "Predict", "code": 's = "Bengaluru"\nprint(s[2:5])\nprint(s[:3])\nprint(s[::-1])', "a": "Positions 2, 3, 4. Then the first 3. Then reversed."},
        {"kind": "Predict", "code": 's = "hello"\ns.upper()\nprint(s)', "a": "<code>s.upper()</code> made a new string and threw it away. <code>s</code> is unchanged. Fix: <code>s = s.upper()</code>."},
        {"kind": "Predict", "code": 's = "hello"\ns[0] = "H"', "expect": "TypeError", "a": "Strings are immutable. Fix: <code>s = \"H\" + s[1:]</code>."},
        {"kind": "Predict", "code": 'print("banana".count("a"), "banana".find("n"), "banana".find("z"))', "a": "3 a's. The first n is at index 2. <code>find</code> gives -1 when it is missing (no error)."},
        {"kind": "Predict", "code": 'print("2026-10-15".split("-"))', "a": "A list of three strings. They are still text, not numbers."},
        {"kind": "Predict", "code": 'parts = ["a", "b", "c"]\nprint(parts.join(","))', "expect": "AttributeError", "a": "join belongs to the glue string: <code>\",\".join(parts)</code>."},
        {"kind": "Write", "q": "Given <code>email = \"  Ravi.Kumar@Example.com  \"</code>, print it with spaces removed and all lowercase.",
         "sol": 'email = "  Ravi.Kumar@Example.com  "\nprint(email.strip().lower())'},
        {"kind": "Write", "q": "From <code>email = \"ravi@example.com\"</code>, print only the part after <code>@</code>. Use <code>split</code>.",
         "sol": 'email = "ravi@example.com"\nprint(email.split("@")[1])'},
        {"kind": "Write", "q": "Turn <code>\"login page loads slowly\"</code> into <code>login_page_loads_slowly</code>.",
         "sol": 's = "login page loads slowly"\nprint("_".join(s.split()))'},
        {"kind": "Write", "q": "Print the first 3 and last 3 characters of <code>job = \"a1b2c3d4-e5f6\"</code> joined by <code>...</code>",
         "sol": 'job = "a1b2c3d4-e5f6"\nprint(job[:3] + "..." + job[-3:])'},
    ], "5"),
]))

# ===== 6 =====
topic("6", "lists", "Lists and tuples",
      "Keep many values in order. Lists can change; tuples cannot.", "".join([
    concept("A list holds many values in order", '''
<p>A <b>list</b> is written with square brackets and commas: <code>[10, 20, 30]</code>. It can hold any types, even mixed, and it can change after you make it.
Indexing and slicing work exactly like strings.</p>'''),
    example('marks = [72, 85, 90]\nprint(marks)\nprint(marks[0], marks[-1])\nprint(marks[1:])\nprint(len(marks))\nmixed = ["Ravi", 21, True, None]\nprint(mixed)'),
    rule("6.1", "Square brackets, with a comma between items",
         "<p>A list can hold any mix of types, or nothing at all: <code>[]</code> is an empty list.</p>",
         ok='fruits = ["apple", "mango", "kiwi"]\nempty = []\nprint(fruits, len(fruits))\nprint(empty, len(empty))',
         bad=('nums = [1 2 3]', "SyntaxError"),
         why="The commas are what separate the items. Python even asks: <i>Perhaps you forgot a comma?</i>"),
    rule("6.2", "Positions start at 0, and reading past either end fails",
         "<p>A list of 3 items has positions 0, 1, 2 from the front and -1, -2, -3 from the back. Nothing else exists.</p>",
         ok='days = ["Mon", "Tue", "Wed"]\nprint(days[0], days[-1], days[-3])',
         bad=[('days = ["Mon", "Tue", "Wed"]\nprint(days[3])', "IndexError"), ('days = ["Mon", "Tue", "Wed"]\nprint(days[-4])', "IndexError")],
         why="The last position is always <code>len(list) - 1</code>. <code>-3</code> is the first item, so <code>-4</code> is one step before the start."),
    rule("6.3", "A position must be a whole number",
         "",
         ok='nums = [10, 20, 30]\nprint(nums[1])\nprint(nums[int(1.0)])',
         bad=('nums = [10, 20, 30]\nprint(nums[1.0])', "TypeError"),
         why="<code>1.0</code> is a float. This is a <b>TypeError</b>, not an IndexError: the problem is the <i>kind</i> of value used as a position, not whether the position exists."),
    rule("6.4", "Assigning to an index REPLACES; it does not insert",
         "<p>Lists are <b>mutable</b>: you can change them in place. <code>marks[0] = 99</code> swaps the value at 0. The length stays the same.</p>",
         ok='marks = [72, 85, 90]\nmarks[0] = 99\nprint(marks)\nprint(len(marks))',
         bad=('marks = [72, 85, 90]\nmarks[3] = 60', "IndexError"),
         why="You can only replace a position that exists. To add a new item, use <code>append</code> or <code>insert</code>."),
    concept("Adding and removing items", "<p>A list grows and shrinks in place.</p>"),
    rule("6.5", "append adds to the end, insert adds at a position",
         "",
         ok='items = ["a", "b"]\nitems.append("c")\nprint(items)\nitems.insert(0, "start")\nprint(items)',
         bad=('items = ["a", "b"]\nitems.append("c", "d")', "TypeError"),
         why="<code>insert(0, x)</code> puts x at position 0 and pushes the rest right. <code>append</code> takes exactly one item; call it twice to add two."),
    trap("insert past the end does not fail",
         'items = ["a", "b"]\nitems.insert(10, "z")\nprint(items)',
         "Reading <code>items[10]</code> would be an IndexError, but <code>insert(10, ...)</code> simply puts the item at the end."),
    trap("x = list.append() stores None",
         'cart = ["milk", "bread"]\ncart = cart.append("eggs")\nprint(cart)',
         "<code>append</code> changes the list and returns <code>None</code>. Line 2 then put the name <code>cart</code> on that <code>None</code>, and the list is lost. Call <code>append</code> on its own line, with no <code>=</code>."),
    trap("append adds ONE item, even if it is a list",
         'a = [1, 2]\na.append([3, 4])\nprint(a)\nb = [1, 2]\nb.extend([3, 4])\nprint(b)\nprint(len(a), len(b))',
         "<code>append</code> put the whole list in as a single item. <code>extend</code> adds each item separately."),
    rule("6.6", "remove deletes by value; pop deletes by position",
         "<p><code>remove(x)</code> deletes the first x. <code>pop()</code> removes the last item and gives it back; <code>pop(i)</code> removes position i.</p>",
         ok='nums = [5, 7, 5, 9]\nnums.remove(5)\nprint(nums)\nlast = nums.pop()\nprint(last, nums)\nfirst = nums.pop(0)\nprint(first, nums)',
         bad=[('nums = [5, 7]\nnums.remove(8)', "ValueError"), ('empty = []\nempty.pop()', "IndexError"), ('nums = [5, 7]\nnums.pop(5)', "IndexError")],
         why="<code>remove</code> took only the <b>first</b> 5. <code>pop</code> hands the item back, so you can store it; <code>remove</code> does not. You cannot remove a value that is not there, pop from an empty list, or pop a position that does not exist."),
    rule("6.7", "clear() empties the list; del removes a position",
         "",
         ok='nums = [1, 2, 3, 4]\ndel nums[0]\nprint(nums)\nnums.clear()\nprint(nums, len(nums))',
         bad=('nums = [1, 2]\ndel nums[5]', "IndexError"),
         why="<code>del nums[0]</code> removes position 0 and gives nothing back. <code>clear()</code> keeps the list but takes every item out."),
    concept("Sorting and flipping", "<p>Put a list in order, or reverse it, and know which tools change the list.</p>"),
    rule("6.8", "sort() changes the list and returns None",
         "<p>Methods that change a list in place (<code>sort</code>, <code>reverse</code>, <code>append</code>) give back <code>None</code>. Call them on their own line.</p>",
         ok='nums = [3, 1, 2]\nnums.sort()\nprint(nums)\nnums.sort(reverse=True)\nprint(nums)',
         why="<code>reverse=True</code> sorts from biggest to smallest. To get a sorted copy while keeping the original, use <code>sorted(nums)</code> (rule 6.10)."),
    rule("6.9", "reverse() flips the order; it does not sort",
         "<p>Like <code>sort</code>, it changes the list itself and returns <code>None</code>.</p>",
         ok='nums = [3, 1, 2]\nnums.reverse()\nprint(nums)',
         why="<code>[3, 1, 2]</code> became <code>[2, 1, 3]</code>: the same items back to front, not in size order."),
    trap("storing the result of sort()",
         'nums = [3, 1, 2]\nnums = nums.sort()\nprint(nums)',
         "<code>sort()</code> sorted the list, then returned <code>None</code>, and line 2 put the name <code>nums</code> on that <code>None</code>. The list is lost. This is the most common list bug."),
    rule("6.10", "sorted() gives a new list and leaves the original alone",
         "",
         ok='nums = [3, 1, 2]\nnew = sorted(nums)\nprint(new)\nprint(nums)\nprint(sorted(nums, reverse=True))',
         why="How to tell them apart: <code>nums.sort()</code> has a dot after the list, so it changes the list and returns <code>None</code>. <code>sorted(nums)</code> has the list inside the brackets, so it returns something new and leaves the list alone."),
    table(["", "<code>nums.sort()</code>", "<code>sorted(nums)</code>"], [
        ["Changes <code>nums</code>?", "yes", "no"],
        ["Gives back", "<code>None</code>", "a new sorted list"],
        ["Write it as", "on its own line", "<code>new = sorted(nums)</code>"],
    ]),
    rule("6.11", "Sorting needs values that can be compared",
         "",
         ok='print(sorted(["pear", "apple", "fig"]))',
         bad=('print(sorted([3, "apple", 1]))', "TypeError"),
         why="Python cannot say whether 3 is bigger or smaller than <code>\"apple\"</code>. Text sorts alphabetically; numbers sort by size; a mix cannot sort."),
    trap("capital letters sort first",
         'names = ["ravi", "Meena", "arjun"]\nnames.sort()\nprint(names)',
         "Every capital letter comes before every small letter, so <code>Meena</code> goes first even though <code>a</code> comes before <code>m</code>."),
    trap("numbers stored as text sort as text",
         'print(sorted(["10", "9", "100"]))\nprint(sorted([10, 9, 100]))',
         "Text is compared character by character, and <code>\"1\"</code> comes before <code>\"9\"</code>, so <code>\"10\"</code> and <code>\"100\"</code> come first. Convert to numbers to sort by size."),
    concept("Searching and combining lists", "<p>Ask questions about a whole list, and join lists together.</p>"),
    rule("6.12", "min(), max() and sum() work on a whole list",
         "",
         ok='n = [4, 9, 1]\nprint(min(n), max(n), sum(n))\nprint(min(["pear", "apple"]))',
         bad=('print(sum(["a", "b"]))', "TypeError"),
         why="<code>min</code> and <code>max</code> work on text too (alphabetical). <code>sum</code> only adds numbers."),
    rule("6.13", "in and not in check whether an item is in the list",
         "<p>The answer is always <code>True</code> or <code>False</code>, and the match must be exact.</p>",
         ok='fruits = ["apple", "mango"]\nprint("mango" in fruits)\nprint("kiwi" in fruits)\nprint("kiwi" not in fruits)\nprint("Mango" in fruits)',
         why="<code>\"Mango\"</code> with a capital is a different string, so it is not found."),
    rule("6.14", "count() says how many; index() says where",
         "",
         ok='v = ["a", "b", "a", "a"]\nprint(v.count("a"))\nprint(v.count("z"))\nprint(v.index("a"))\nprint(v.index("b"))',
         bad=('v = ["a", "b"]\nprint(v.index("z"))', "ValueError"),
         why="<code>count</code> can answer \"0 times\". <code>index</code> gives only the <b>first</b> match, and has no position to give for a missing item, so it raises an error."),
    rule("6.15", "+ joins lists and * repeats one; both make a new list",
         "",
         ok='a = [1, 2]\nb = [3, 4]\nprint(a + b)\nprint(a * 3)\nprint(a)',
         bad=('a = [1, 2]\nprint(a + 3)', "TypeError"),
         why="<code>a</code> is unchanged: <code>+</code> and <code>*</code> build a new list. <code>+</code> on a list only joins it with another list, so write <code>a + [3]</code> or use <code>append</code>."),
    rule("6.16", "len() counts items, not characters",
         "",
         ok='print(len("Ravi"))\nprint(len(["Ravi"]))\nprint(len(["Ravi", "Meena"]))',
         why="A string's length is its characters. A list's length is its items, however long each item is."),
    trap("quotes in the output tell you the type",
         'print("hi")\nprint(["hi"])\nprint([5, "5"])',
         "<code>print</code> on a string shows no quotes. Inside a list, strings are shown <b>with</b> quotes, so you can see <code>5</code> (a number) and <code>'5'</code> (text) apart."),
    concept("Slices of a list", "<p>Taking a piece of a list, the same way as with strings.</p>"),
    rule("6.17", "A slice reads; it never changes the list",
         "<p>Slicing gives you a new list. The original is untouched.</p>",
         ok='nums = [1, 2, 3, 4]\npart = nums[1:3]\npart.append(99)\nprint(part)\nprint(nums)'),
    rule("6.18", "A slice gives back the same type",
         "<p>Slicing a list gives a list, a tuple gives a tuple, a string gives a string.</p>",
         ok='print([1, 2, 3][1:])\nprint((1, 2, 3)[1:])\nprint("abc"[1:])\nprint(type([1, 2, 3][1:]), type((1, 2, 3)[1:]))'),
    concept("Read or write: the one idea behind all of it", '''
<p>Every action on a value is either a <b>read</b> (look at it: <code>x[0]</code>, <code>len(x)</code>, <code>x[1:3]</code>, <code>in</code>, <code>print</code>) or a <b>write</b> (change it: <code>x[0] = ...</code>, <code>append</code>, <code>sort</code>, <code>del</code>).</p>
<p>All three types allow reads, and no read ever changes anything. Only a <b>list</b> allows writes. A string and a tuple refuse them, so to "change" one you build a new one and move the name to it.</p>'''),
    table(["", "list", "str", "tuple"], [
        ["Read: <code>x[0]</code>, slice, <code>len</code>, <code>in</code>", "yes", "yes", "yes"],
        ["Write: <code>x[0] = ...</code>", "yes", "TypeError", "TypeError"],
        ["Methods that change it", "<code>append</code>, <code>sort</code>, <code>pop</code>...", "none (they return new strings)", "none"],
    ]),
    concept("= does not copy a list", '''
<p>This is the trap that catches everyone once. It all happens in your computer's <b>memory</b> (RAM) while the program runs: the list is stored there once, and a name is just a way to reach it.</p>
<p>Think of a Google Doc. <code>b = a</code> is sending a friend the <b>same link</b>: when they type, you see it, because there is only one document. <code>b = a.copy()</code> is <b>File, Make a copy</b>: now there are two documents.</p>'''),
    d_alias(),
    trap("two names, one list",
         'a = [1, 2, 3]\nb = a\nb.append(99)\nprint(a)\nprint(a is b)',
         "<code>b = a</code> did not make a second list. It gave the same list a second name, so a change through <code>b</code> shows up in <code>a</code>. <code>a is b</code> asks \"is this the exact same list in memory?\" and says <code>True</code>."),
    rule("6.19", "Use .copy(), [:] or list() for a real copy",
         "",
         ok='a = [1, 2, 3]\nc = a.copy()\nc.append(99)\nprint(a)\nprint(c)\nprint(a is c)\nd = a[:]\ne = list(a)\nprint(d, e)',
         why="<code>a is c</code> is <code>False</code>: two separate lists now. All three ways make a new list."),
    trap("+= changes the list, but a = a + [...] makes a new one",
         'a = [1]\nb = a\na += [2]\nprint(b)\na = a + [3]\nprint(a)\nprint(b)',
         "<code>a += [2]</code> adds to the list itself, so <code>b</code> sees it. <code>a = a + [3]</code> builds a new list and moves only the name <code>a</code>, so <code>b</code> stays on the old one."),
    trap("a copy is shallow: lists inside are still shared",
         'a = [[1, 2], [3]]\nb = a.copy()\nb[0].append(99)\nprint(a)',
         "<code>copy()</code> made a new outer list, but both outer lists still hold the <b>same</b> inner lists. Changing an inner list through <code>b</code> shows up in <code>a</code>."),
    rule("6.20", "Lists can hold lists",
         "<p>Use two indexes: the first picks the inner list, the second picks inside it.</p>",
         ok='grid = [[1, 2, 3], [4, 5, 6]]\nprint(grid[1])\nprint(grid[1][0])',
         bad=('grid = [[1, 2, 3], [4, 5, 6]]\nprint(grid[2][0])', "IndexError"),
         why="There are only two inner lists, at positions 0 and 1."),
    trap("split() gives text, so + joins instead of adding",
         'parts = "10,20".split(",")\nprint(parts)\nprint(parts[0] + parts[1])\nprint(int(parts[0]) + int(parts[1]))',
         "The pieces are strings, even when they hold digits. <code>\"10\" + \"20\"</code> is <code>\"1020\"</code>. Convert with <code>int()</code> to add them."),
    trap("str() of a list is not a join",
         'print(str([1, 2]))\nprint(", ".join(["1", "2"]))',
         "<code>str()</code> turns the whole list into text, brackets and all. To glue the items, use <code>join</code> (and the items must be strings)."),
    concept("Tuples: lists that cannot change", '''
<p>A <b>tuple</b> uses round brackets: <code>(10, 20)</code>. You can read it, index it and slice it like a list, but you cannot change it.
Use one for values that belong together and should stay fixed: a date, a coordinate, a screen size.</p>''', "tuples"),
    rule("6.21", "A tuple cannot be changed",
         "",
         ok='size = (1920, 1080)\nprint(size[0])\nprint(size[0:1])',
         bad=[('size = (1920, 1080)\nsize[0] = 1280', "TypeError"), ('size = (1920, 1080)\nsize.append(720)', "AttributeError")],
         why="Reading is allowed; writing is not. Tuples have no methods that change them, such as <code>append</code>."),
    rule("6.22", "A one-item tuple needs a trailing comma",
         "<p>The comma makes the tuple, not the brackets.</p>",
         ok='t = (5,)\nprint(type(t))\nu = 5, 6\nprint(type(u))',
         why="<code>(5)</code> is just the number 5 in brackets, like in maths. <code>(5,)</code> is a tuple. This is also why <code>1,000</code> in Chapter 4 became a tuple."),
    trap("brackets alone do not make a tuple", 'x = (5)\nprint(type(x))', "Write <code>(5,)</code> to get a tuple with one item."),
    rule("6.23", "An empty tuple is ()",
         "",
         ok='t = ()\nprint(t, type(t), len(t))'),
    concept("Tuple tools", "<p>What you can still do with a tuple that cannot change.</p>"),
    rule("6.24", "A tuple has only two methods: count() and index()",
         "<p>They work like the list versions. Every method that would change it is missing.</p>",
         ok='t = (1, 2, 2, 3)\nprint(t.count(2))\nprint(t.index(3))',
         bad=[('t = (3, 1, 2)\nt.sort()', "AttributeError"), ('t = (1, 2)\nprint(t.index(9))', "ValueError")],
         why="No <code>sort</code>, <code>append</code> or <code>remove</code>: a tuple cannot change. <code>index</code> of a missing value fails, as with a list."),
    rule("6.25", "t = t + (9,) builds a new tuple; it does not change the old one",
         "<p>You can make a longer tuple by joining. The original stays exactly as it was; only the name moves.</p>",
         ok='t = (1, 2)\nold = t\nt = t + (9,)\nprint(t)\nprint(old)',
         bad=('t = (1, 2)\nt = t + 9', "TypeError"),
         why="<code>old</code> still shows <code>(1, 2)</code>, so nothing was changed in place. You can only join a tuple with another tuple, hence the comma in <code>(9,)</code>."),
    rule("6.26", "tuple() and list() convert between the two",
         "",
         ok='print(tuple([1, 2]))\nprint(list((1, 2)))\nprint(sorted((3, 1, 2)))',
         why="Use <code>list(t)</code> when you need to change a tuple's values, then <code>tuple(...)</code> to fix them again. <code>sorted</code> on a tuple gives back a <b>list</b>."),
    rule("6.27", "Unpacking needs exactly the right count",
         "<p>You can spread a tuple or list into separate variables in one line.</p>",
         ok='point = (3, 7)\nx, y = point\nprint(x, y)',
         bad=[('x, y = (1, 2, 3)', "ValueError"), ('x, y, z = (1, 2)', "ValueError")],
         why="Three values cannot go into two names, and two values cannot fill three."),
    trap("a tuple can hold a list, and that list can change",
         't = (1, [2, 3])\nt[1].append(4)\nprint(t)',
         "The tuple still holds the same two things. But the second one is a list, and a list can change. A tuple only stops you swapping its items."),
    exercises([
        {"kind": "Predict", "code": 'l = [10, 20, 30]\nl[1] = 99\nprint(l, len(l))', "a": "Position 1 is replaced. The length stays 3."},
        {"kind": "Predict", "code": 'l = [3, 1, 2]\nprint(l.sort())', "a": "<code>sort()</code> returns <code>None</code>, and that is what gets printed."},
        {"kind": "Predict", "code": 'l = [1, 2]\nl.append([3])\nprint(l, len(l))', "a": "The list <code>[3]</code> went in as one item, so the length is 3."},
        {"kind": "Predict", "code": 'a = ["x"]\nb = a\nb.append("y")\nprint(a)', "a": "<code>a</code> and <code>b</code> are the same list."},
        {"kind": "Predict", "code": 't = (1, 2, 3)\nt[0] = 5', "expect": "TypeError", "a": "Tuples cannot be changed."},
        {"kind": "Predict", "code": 'x = ("solo")\ny = ("solo",)\nprint(type(x), type(y))', "a": "No comma, no tuple: <code>x</code> is just a string."},
        {"kind": "Predict", "code": 'nums = [5, 3, 8]\nprint(sorted(nums), nums)', "a": "<code>sorted</code> makes a new list; <code>nums</code> is unchanged."},
        {"kind": "Predict", "code": 'a, b = [1, 2, 3]', "expect": "ValueError", "a": "Three values, two names."},
        {"kind": "Predict", "code": 'days = ["Mon", "Tue", "Wed"]\nprint(days[-4])', "expect": "IndexError", "a": "Positions run from -3 to 2."},
        {"kind": "Predict", "code": 'q = ["a", "b", "c"]\nq.pop(0)\nq.pop(0)\nq.pop(0)\nq.pop(0)\nprint(q)', "expect": "IndexError",
         "a": "After 3 pops the list is empty, so the 4th fails and <code>print</code> never runs."},
        {"kind": "Predict", "code": 'n = [5, 2, 8]\nresult = n.sort()\nprint(result)\nprint(n)', "a": "<code>sort()</code> has a dot: it changes <code>n</code> and returns <code>None</code>."},
        {"kind": "Predict", "code": 'team = ["Ravi", "Meena"]\nbackup = team\nbackup.append("Arjun")\nprint(len(team))', "a": "One list, two names: the append shows up through <code>team</code>."},
        {"kind": "Predict", "code": 'v = [1, 2, 2, 3]\nprint(v.count(2), v.index(2), 4 in v)', "a": "2 appears twice, first at position 1, and 4 is not there."},
        {"kind": "Predict", "code": 't = (1, 2)\nt.append(3)', "expect": "AttributeError", "a": "A tuple has only <code>count</code> and <code>index</code>."},
        {"kind": "Write", "q": "Start with <code>bugs = []</code>. Add <code>\"BUG-1\"</code> and <code>\"BUG-2\"</code>, insert <code>\"BUG-0\"</code> at the front, then print the list and its length.",
         "sol": 'bugs = []\nbugs.append("BUG-1")\nbugs.append("BUG-2")\nbugs.insert(0, "BUG-0")\nprint(bugs, len(bugs))'},
        {"kind": "Write", "q": "Given <code>times = [320, 150, 410, 290]</code> (load times in ms), print the fastest, the slowest and the average.",
         "sol": 'times = [320, 150, 410, 290]\nprint(min(times), max(times), sum(times) / len(times))'},
        {"kind": "Write", "q": "Make a copy of <code>original = [1, 2, 3]</code>, add 4 to the copy only, and print both to prove the original did not change.",
         "sol": 'original = [1, 2, 3]\nnew = original.copy()\nnew.append(4)\nprint(original)\nprint(new)'},
        {"kind": "Write", "q": "Turn the text <code>\"tc1,tc2,tc3\"</code> into a list, reverse it, and join it back with <code> | </code>.",
         "sol": 'cases = "tc1,tc2,tc3".split(",")\ncases.reverse()\nprint(" | ".join(cases))'},
    ], "6"),
]))

# ===== 7 =====
topic("7", "dicts", "Dictionaries and sets",
      "Look values up by name instead of position, and keep collections without repeats.", "".join([
    concept("A dictionary stores key: value pairs", '''
<p>A <b>dictionary</b> (<code>dict</code>) uses curly brackets. Each item is a <b>key</b> and its <b>value</b>, joined by a colon.
You find a value by its key, the way you find a word in a real dictionary.</p>'''),
    d_dict(),
    rule("7.1", "Read a value with its key in square brackets",
         "",
         ok='student = {"name": "Ravi", "age": 21}\nprint(student["name"])\nprint(student["age"])',
         bad=('student = {"name": "Ravi", "age": 21}\nprint(student["city"])', "KeyError"),
         why="There is no key <code>\"city\"</code>. Keys are exact: <code>\"Name\"</code> would fail too."),
    rule("7.2", "get() returns None (or your default) instead of failing",
         "",
         ok='student = {"name": "Ravi"}\nprint(student.get("city"))\nprint(student.get("city", "unknown"))',
         why="Use <code>get</code> when a key may be missing; use <code>[ ]</code> when it must be there and a missing key is a real bug."),
    rule("7.3", "Dictionaries do not use positions",
         "",
         ok='student = {"name": "Ravi"}\nprint(student["name"])',
         bad=('student = {"name": "Ravi"}\nprint(student[0])', "KeyError"),
         why="<code>0</code> is treated as a key, and there is no key 0. There is no \"first item\" lookup in a dictionary."),
    concept("Changing a dictionary", "<p>Add, replace and remove keys.</p>"),
    rule("7.4", "Assigning to a key adds it or replaces it",
         "<p>If the key exists, the value is replaced. If not, the pair is added. <code>del</code> and <code>pop</code> remove a key.</p>",
         ok='d = {"name": "Ravi"}\nd["age"] = 21\nd["name"] = "Asha"\nprint(d)\ndel d["age"]\nprint(d)',
         bad=('d = {"name": "Ravi"}\ndel d["age"]', "KeyError"),
         why="You cannot delete a key that is not there."),
    rule("7.5", "pop(key) removes a key and gives its value back",
         "<p>Like a list's <code>pop</code>, it hands you what it removed. A second value is a default for when the key is missing.</p>",
         ok='d = {"name": "Ravi", "age": 21}\nage = d.pop("age")\nprint(age, d)\nprint(d.pop("city", "none"))',
         bad=('d = {"name": "Ravi"}\nd.pop("city")', "KeyError"),
         why="Without a default, a missing key is an error. With one, you get the default back and nothing is removed."),
    rule("7.6", "update() adds or replaces several keys at once",
         "",
         ok='d = {"name": "Ravi", "age": 21}\nd.update({"age": 22, "city": "Goa"})\nprint(d)',
         bad=('d = {"name": "Ravi"}\nd.update(5)', "TypeError"),
         why="Existing keys are replaced (<code>age</code>), new keys are added (<code>city</code>). <code>update</code> needs a dictionary (or pairs), not a single number."),
    rule("7.7", "A dictionary keeps the order you added keys in",
         "",
         ok='d = {}\nd["c"] = 3\nd["a"] = 1\nd["b"] = 2\nprint(d)\nprint(list(d))',
         why="Keys come out in the order they went in, not sorted. Replacing a value keeps its key in the same place."),
    concept("Keys, and looking at the whole dictionary", "<p>The rules keys must follow, and how to see everything inside.</p>"),
    rule("7.8", "Keys are unique: a repeated key keeps the last value",
         "",
         ok='d = {"a": 1, "a": 2}\nprint(d)\nprint(len(d))',
         why="No error, and the first value is silently lost. If two of your keys look the same, one of them is gone."),
    rule("7.9", "Keys must be unchangeable values",
         "<p>Strings, numbers and tuples can be keys. Lists cannot. Values can be anything.</p>",
         ok='d = {"name": "x", 1: "one", (2, 3): "pair", "tags": ["a", "b"]}\nprint(d[(2, 3)], d["tags"])',
         bad=('d = {["a", "b"]: 1}', "TypeError"),
         why="A list can change, so it could not be found again reliably. Python calls this <i>unhashable</i>: it cannot be used as a key."),
    rule("7.10", "keys(), values() and items() show the whole dictionary",
         "<p><code>keys()</code> all the keys, <code>values()</code> all the values, <code>items()</code> each key with its value as a pair. <code>len(d)</code> counts the keys.</p>",
         ok='d = {"name": "Ravi", "age": 21}\nprint(d.keys())\nprint(d.values())\nprint(d.items())\nprint(len(d))\nprint(list(d.keys()))',
         bad=('d = {"name": "Ravi"}\nprint(d.keys()[0])', "TypeError"),
         why="What <code>keys()</code> gives back looks like a list but has no positions. Wrap it in <code>list(...)</code> first if you need <code>[0]</code>."),
    trap("in checks keys, not values",
         'd = {"name": "Ravi"}\nprint("Ravi" in d)\nprint("Ravi" in d.values())',
         "<code>in</code> on a dictionary looks only at the keys. To search values, use <code>d.values()</code>."),
    rule("7.11", "Dictionaries can hold lists and other dictionaries",
         "<p>Chain the lookups from the outside in.</p>",
         ok='job = {"id": 7, "owner": {"name": "Ravi", "team": "QA"}, "tags": ["p0", "ui"]}\nprint(job["owner"]["team"])\nprint(job["tags"][0])',
         why="<code>job[\"owner\"]</code> is itself a dictionary, so you look up <code>[\"team\"]</code> inside it. This shape is exactly what API responses (JSON) look like."),
    concept("Sets: no repeats", '''
<p>A <b>set</b> also uses curly brackets, but holds single values, not pairs. Each value appears <b>once</b>, and there is no order.
Good for removing duplicates and comparing groups.</p>''', "sets"),
    rule("7.12", "Duplicates disappear",
         "",
         ok='s = {1, 2, 2, 3, 3, 3}\nprint(s)\nprint(len(s))\nprint(set([5, 5, 6]))',
         why="A set keeps each value once. <code>set(list)</code> is the quick way to drop duplicates from a list."),
    trap("{} is an empty dictionary, not a set",
         'a = {}\nb = set()\nprint(type(a), type(b))',
         "Curly brackets with nothing inside make a dict. For an empty set, write <code>set()</code>."),
    rule("7.13", "Sets have no positions",
         "",
         ok='s = {10, 20, 30}\nprint(20 in s)',
         bad=('s = {10, 20, 30}\nprint(s[0])', "TypeError"),
         why="A set has no order, so there is no first item. Check membership with <code>in</code> instead."),
    rule("7.14", "add puts a value in; remove fails if it is missing, discard does not",
         "",
         ok='s = {1, 2}\ns.add(3)\ns.add(2)\nprint(s)\ns.discard(99)\nprint(s)',
         bad=('s = {1, 2}\ns.remove(99)', "KeyError"),
         why="Adding a value that is already there does nothing. Use <code>discard</code> when the value might not be there."),
    rule("7.15", "Sets cannot hold lists",
         "",
         ok='s = {1, "a", (2, 3)}\nprint(len(s))',
         bad=('s = {1, [2, 3]}', "TypeError"),
         why="Same reason as dictionary keys: set items must be unchangeable."),
    rule("7.16", "pop() takes out any one item; clear() empties the set",
         "<p>A set has no order, so <code>pop()</code> cannot take \"the last\" one. It removes and returns whichever item it picks.</p>",
         ok='s = {"a"}\nprint(s.pop())\nprint(s)\nt = {1, 2, 3}\nt.clear()\nprint(t, len(t))',
         bad=('s = set()\ns.pop()', "KeyError"),
         why="With one item there is only one choice, so the output is certain here. With more items, do not rely on which one comes out. An empty set has nothing to pop."),
    trap("18 and \"18\" are two different items",
         's = {18, "18"}\nprint(len(s))',
         "A number and text are different types, so the set keeps both."),
    trap("20 and 20.0 count as the same item",
         's = {20, 20.0, 30}\nprint(s, len(s))',
         "<code>20 == 20.0</code> is True, so the set sees a duplicate and keeps the first one, <code>20</code>."),
    d_venn(),
    rule("7.17", "Combine sets with | & - ^ or their method names",
         "<p>Each symbol has a method with the same meaning. Both give a <b>new</b> set.</p>",
         ok='a = {1, 2, 3, 4}\nb = {3, 4, 5, 6}\nprint(a | b, a.union(b))\nprint(a & b, a.intersection(b))\nprint(a - b, a.difference(b))\nprint(a ^ b, a.symmetric_difference(b))',
         bad=('print({1, 2} + {3})', "TypeError"),
         why="<code>|</code> union (in either), <code>&amp;</code> intersection (in both), <code>-</code> difference (in the first only), <code>^</code> symmetric difference (in exactly one). <code>+</code> is not defined for sets; use <code>|</code>."),
    table(["Symbol", "Method", "Keeps", "Here"], [
        ["<code>a | b</code>", "<code>a.union(b)</code>", "everything in either set", "<code>{1, 2, 3, 4, 5, 6}</code>"],
        ["<code>a &amp; b</code>", "<code>a.intersection(b)</code>", "only what is in both", "<code>{3, 4}</code>"],
        ["<code>a - b</code>", "<code>a.difference(b)</code>", "in a but not in b", "<code>{1, 2}</code>"],
        ["<code>a ^ b</code>", "<code>a.symmetric_difference(b)</code>", "in one but not both", "<code>{1, 2, 5, 6}</code>"],
    ]),
    table(["You want", "Use", "Written"], [
        ["values in order, may repeat, may change", "list", "<code>[1, 2, 2]</code>"],
        ["values in order that must not change", "tuple", "<code>(1, 2)</code>"],
        ["look up a value by a name", "dict", "<code>{\"a\": 1}</code>"],
        ["unique values, no order", "set", "<code>{1, 2}</code>"],
    ]),
    exercises([
        {"kind": "Predict", "code": 'd = {"a": 1, "b": 2}\nd["a"] = 10\nd["c"] = 3\nprint(d)', "a": "<code>\"a\"</code> is replaced, <code>\"c\"</code> is added."},
        {"kind": "Predict", "code": 'd = {"a": 1}\nprint(d["A"])', "expect": "KeyError", "a": "Keys are case-sensitive."},
        {"kind": "Predict", "code": 'd = {"a": 1}\nprint(d.get("z", 0))', "a": "The key is missing, so the default 0 comes back."},
        {"kind": "Predict", "code": 'd = {"x": 1, "y": 2, "x": 3}\nprint(d, len(d))', "a": "The repeated key keeps the last value. Only 2 keys exist."},
        {"kind": "Predict", "code": 'print(len({1, 1, 2, 2, 3}))', "a": "Duplicates vanish, so 3 values remain."},
        {"kind": "Predict", "code": 'x = {}\nprint(type(x))', "a": "Empty curly brackets make a dictionary."},
        {"kind": "Predict", "code": 'd = {"name": "Ravi"}\nprint("Ravi" in d, "name" in d)', "a": "<code>in</code> checks keys only."},
        {"kind": "Predict", "code": 'colours = {"red", "blue"}\nprint(colours[0])', "expect": "TypeError", "a": "Sets have no positions."},
        {"kind": "Predict", "code": 'd = {"a": 1, "b": 2}\nx = d.pop("a")\nprint(x, d)', "a": "<code>pop</code> removes the key and gives its value back."},
        {"kind": "Predict", "code": 'd = {"a": 1}\nd.update({"a": 5, "b": 2})\nprint(d)', "a": "<code>a</code> is replaced, <code>b</code> is added."},
        {"kind": "Predict", "code": 'print(len({20, 20.0, "20"}))', "a": "<code>20</code> and <code>20.0</code> are equal, so they count once. <code>\"20\"</code> is text, a different item."},
        {"kind": "Predict", "code": 'a = {1, 2, 3}\nb = {2, 3, 4}\nprint(a ^ b)', "a": "Items in exactly one of the sets."},
        {"kind": "Write", "q": "Make a dictionary for a test case with keys <code>id</code> (<code>\"TC-101\"</code>), <code>title</code> and <code>status</code> (<code>\"untested\"</code>). Then change the status to <code>\"passed\"</code> and print the dictionary.",
         "sol": 'case = {"id": "TC-101", "title": "Login works", "status": "untested"}\ncase["status"] = "passed"\nprint(case)'},
        {"kind": "Write", "q": "Given <code>resp = {\"user\": {\"email\": \"a@b.com\", \"plan\": \"pro\"}}</code>, print the plan.",
         "sol": 'resp = {"user": {"email": "a@b.com", "plan": "pro"}}\nprint(resp["user"]["plan"])'},
        {"kind": "Write", "q": "Given <code>ids = [3, 1, 3, 2, 1]</code>, print how many <b>unique</b> ids there are and the unique ids in sorted order.",
         "sol": 'ids = [3, 1, 3, 2, 1]\nunique = set(ids)\nprint(len(unique), sorted(unique))'},
        {"kind": "Write", "q": "Yesterday's failing tests were <code>{1, 2, 5}</code> and today's are <code>{2, 5, 7}</code>. Print what got fixed, what is new, and what failed both days.",
         "sol": 'yesterday = {1, 2, 5}\ntoday = {2, 5, 7}\nprint("fixed:", yesterday - today)\nprint("new:", today - yesterday)\nprint("both:", yesterday & today)'},
    ], "7"),
]))

COMING = [("8", "if, elif and else"), ("9", "Loops: for, while, range"), ("10", "Functions"),
          ("11", "Handling errors: try and except"), ("12", "Reading and writing files"),
          ("13", "Classes"), ("14", "Mini project")]


# ---------------------------------------------------------------- page

CSS = r'''
:root {
  /* Layout: a docs rail on the left, one reading column, sketches break out to full column width. Light only. */
  --paper: #F5F7FA;
  --sheet: #FFFFFF;
  --ink: #18222E;
  --muted: #5A6573;
  --line: rgba(24, 34, 46, 0.14);
  --py-blue: #306998;
  --py-yellow: #FFD43B;
  --blue-wash: #E9F0F7;
  --yellow-wash: #FFF7D6;
  --ok: #23703F;
  --ok-wash: #E8F4EC;
  --bad: #B42318;
  --bad-wash: #FCEBEA;
  --trap: #8A5A00;
  --trap-wash: #FFF4DC;
  --code-bg: #F2F4F7;
  --f-body: "IBM Plex Sans", "Segoe UI", system-ui, sans-serif;
  --f-mono: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace;
  --f-hand: "Kalam", "Comic Sans MS", cursive;
  color-scheme: light;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
body { background: var(--paper); color: var(--ink); font-family: var(--f-body); font-size: 16px; line-height: 1.6; }
.wm { position: fixed; right: 4vw; bottom: 6vh; width: 380px; height: 380px; opacity: 0.06; pointer-events: none; z-index: 2; }
.shell { position: relative; z-index: 1; display: grid; grid-template-columns: 264px minmax(0, 1fr); max-width: 1240px; margin: 0 auto; }
.rail { position: sticky; top: env(safe-area-inset-top, 0px); height: 100vh; overflow-y: auto; padding: 32px 16px 32px max(16px, env(safe-area-inset-left, 0px)); border-right: 1px solid var(--line); }
.brand { color: var(--ink); text-decoration: none; display: flex; align-items: center; gap: 10px; font-weight: 600; font-size: 18px; margin: 0 8px 24px; }
.brand svg { width: 30px; height: 30px; flex: none; }
.rail h4 { font-size: 12px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); margin: 20px 8px 6px; }
.rail ol { list-style: none; margin: 0; padding: 0; display: grid; gap: 2px; }
.rail a { display: grid; grid-template-columns: 26px minmax(0, 1fr); align-items: center; height: 34px; padding: 0 8px; border-radius: 6px; color: var(--ink); text-decoration: none; font-size: 14px; white-space: nowrap; }
.rail a span:last-child { overflow: hidden; text-overflow: ellipsis; }
.rail a .n { color: var(--muted); font-variant-numeric: tabular-nums; font-family: var(--f-mono); font-size: 12px; }
.rail a:hover { background: var(--code-bg); }
.rail a.active { background: var(--blue-wash); color: var(--py-blue); font-weight: 600; }
.rail li.soon { display: grid; grid-template-columns: 26px minmax(0, 1fr); align-items: center; height: 30px; padding: 0 8px; font-size: 14px; color: var(--muted); white-space: nowrap; overflow: hidden; }
.rail li.soon .n { font-family: var(--f-mono); font-size: 12px; }
main { min-width: 0; padding-block: 48px 120px; padding-left: max(16px, 48px); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
.col { max-width: 800px; }
.hero { position: relative; }
.hero h1 { font-size: 36px; line-height: 1.2; font-weight: 600; margin: 0 0 12px; text-wrap: balance; letter-spacing: -0.01em; }
.hero p { margin: 0 0 12px; color: var(--muted); font-size: 18px; }
.hero .how { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin-top: 24px; }
.hero .how div { background: var(--sheet); border: 1px solid var(--line); border-radius: 6px; padding: 12px 16px; font-size: 14px; color: var(--ink); }
.hero .how b { display: block; font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); margin-bottom: 4px; }
.hero .meta { font-size: 14px; color: var(--muted); margin-top: 16px; }
.hero-art { position: absolute; right: 0; top: -12px; width: 150px; opacity: 0.9; }
/* Book pages: one sheet per chapter. With JS only the current sheet shows; print puts each on a new page. */
.page { position: relative; scroll-margin-top: 16px; }
.sheet { position: relative; background-color: var(--sheet); background-repeat: no-repeat; background-position: right 28px bottom 64px; background-size: 240px; border: 1px solid var(--line); border-radius: 8px; padding: 48px 56px 20px; margin-bottom: 32px; }
.paged .page:not(.current) { display: none; }
.pager { display: grid; grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr); align-items: start; gap: 16px; margin-top: 48px; padding-top: 16px; border-top: 1px solid var(--line); font-size: 14px; }
.pager a { color: var(--py-blue); text-decoration: none; display: grid; gap: 2px; }
.pager a:hover { text-decoration: underline; }
.pager a span { font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; }
.pager .nextp { text-align: right; }
.pager .pno { font-family: var(--f-mono); font-size: 12px; color: var(--muted); }
.topic { scroll-margin-top: 16px; }
.topic-head { position: relative; margin-bottom: 24px; }
.topic-head + .concept, .topic-head + .rule { margin-top: 8px; }
.chapno { font-size: 36px; line-height: 1.2; font-weight: 600; color: var(--py-blue); padding-bottom: 12px; margin-bottom: 16px; border-bottom: 2px solid var(--py-yellow); }
.topic h2 { font-size: 28px; line-height: 1.25; font-weight: 600; margin: 4px 0 8px; text-wrap: balance; }
.topic .goal { color: var(--muted); font-size: 18px; margin: 0; }
.toc { margin: 24px 0 0; padding: 0; list-style: none; font-size: 16px; border-top: 1px solid var(--line); }
.toc li { border-bottom: 1px solid var(--line); }
.toc a { display: grid; grid-template-columns: 48px minmax(0, 1fr); align-items: baseline; padding: 8px 0; color: var(--py-blue); text-decoration: none; }
.toc a:hover { text-decoration: underline; }
.toc .rn { font-family: var(--f-mono); color: var(--muted); font-size: 14px; }
h3 { font-size: 22px; line-height: 1.3; font-weight: 600; margin: 0 0 12px; text-wrap: balance; }
.prose p, .concept p { margin: 0 0 12px; }
.prose ul, .prose ol { margin: 0 0 12px; padding-left: 22px; }
.prose li { margin-bottom: 4px; }
.prose li:last-child { margin-bottom: 0; }
code { font-family: var(--f-mono); font-size: 14px; background: var(--code-bg); padding: 1px 5px; border-radius: 4px; }
.concept, .rule { margin: 32px 0 0; scroll-margin-top: 12px; }
.rule h3 { display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 12px; }
.rnum { font-family: var(--f-mono); font-size: 14px; font-weight: 500; color: var(--py-blue); background: var(--blue-wash); padding: 2px 8px; border-radius: 4px; }
.case { background: var(--sheet); border: 1px solid var(--line); border-radius: 6px; margin: 12px 0; overflow: hidden; }
.case-h { font-size: 12px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; padding: 6px 14px; }
.case.good .case-h { background: var(--ok-wash); color: var(--ok); }
.case.bad .case-h { background: var(--bad-wash); color: var(--bad); }
.case.trap .case-h { background: var(--trap-wash); color: var(--trap); }
.case .mark { font-size: 14px; margin-right: 2px; }
.case.trap .why { padding: 0 14px 12px; }
.exlabel { margin: 0; padding: 8px 14px 0; font-size: 14px; color: var(--muted); }
pre { margin: 0; overflow-x: auto; }
pre.code { padding: 12px 14px; font-family: var(--f-mono); font-size: 14px; line-height: 1.6; background: var(--sheet); }
pre.code code { background: none; padding: 0; font-size: 14px; }
.concept pre.code, .rule .prose pre.code { border: 1px solid var(--line); border-radius: 6px; margin: 0 0 12px; }
pre.shell { background: var(--code-bg); }
.outlabel { font-size: 12px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); padding: 8px 14px 0; border-top: 1px dashed var(--line); }
pre.out { padding: 4px 14px 12px; font-family: var(--f-mono); font-size: 14px; line-height: 1.6; color: var(--ink); white-space: pre; }
pre.out .tb { color: var(--muted); }
pre.out .errline { color: var(--bad); font-weight: 600; }
pre.out .muted { color: var(--muted); font-style: italic; }
.why { margin: 8px 0 0; }
.tablewrap { overflow-x: auto; margin: 16px 0; background: var(--sheet); border: 1px solid var(--line); border-radius: 6px; }
table { border-collapse: collapse; width: 100%; font-size: 14px; }
th { text-align: left; font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); font-weight: 600; background: var(--code-bg); }
th, td { padding: 8px 14px; border-bottom: 1px solid var(--line); vertical-align: top; }
tr:last-child td { border-bottom: 0; }
td code { white-space: nowrap; }
figure.sketch { margin: 24px 0; background: var(--sheet); border: 1px solid var(--line); border-radius: 6px; }
.sketch-scroll { overflow-x: auto; padding: 12px; }
figure.sketch svg { display: block; width: 100%; height: auto; }
figure.sketch figcaption { font-size: 14px; color: var(--muted); padding: 8px 14px 12px; border-top: 1px dashed var(--line); }
svg .stroke { stroke: var(--ink); stroke-width: 1.8; stroke-linejoin: round; stroke-linecap: round; }
svg .stroke.thin { stroke-width: 0.9; opacity: 0.55; }
svg .arrow { stroke-width: 1.7; }
svg .hand { font-family: var(--f-hand); fill: var(--ink); }
svg .note { fill: var(--muted); }
svg .mono { font-family: var(--f-mono); fill: var(--ink); }
svg .mono.note { fill: var(--muted); }
svg .err { fill: var(--bad); font-weight: 600; }
.exercises { margin-top: 48px; background: var(--sheet); border: 1px solid var(--line); border-radius: 8px; padding: 24px; }
.exercises .hint { color: var(--muted); font-size: 14px; margin: 0 0 16px; }
.exlist { list-style: none; margin: 0; padding: 0; display: grid; gap: 24px; }
.ex { min-width: 0; border-top: 1px solid var(--line); padding-top: 16px; }
.ex:first-child { border-top: 0; padding-top: 0; }
.ex-h { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.ex-n { font-family: var(--f-mono); font-size: 14px; font-weight: 600; color: var(--ink); font-variant-numeric: tabular-nums; }
.ex-kind { font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); font-weight: 600; }
.ex p { margin: 0 0 8px; }
.ex pre.code { border: 1px solid var(--line); border-radius: 6px; margin-bottom: 8px; background: var(--code-bg); }
textarea.mine { width: 100%; font: 14px/1.5 var(--f-mono); color: var(--ink); background: var(--paper); border: 1px solid var(--line); border-radius: 6px; padding: 8px 12px; resize: vertical; }
textarea.mine:focus { outline: 2px solid var(--py-blue); outline-offset: 1px; background: var(--sheet); }
details { margin-top: 8px; }
summary { cursor: pointer; font-size: 14px; font-weight: 600; color: var(--py-blue); width: fit-content; padding: 4px 0; }
summary:focus-visible { outline: 2px solid var(--py-blue); outline-offset: 2px; border-radius: 4px; }
details[open] { background: var(--paper); border: 1px solid var(--line); border-radius: 6px; padding: 4px 0 12px; }
details[open] summary { padding: 4px 14px; }
details .why { padding: 0 14px; }
details pre.code { background: var(--sheet); margin: 8px 14px; border: 1px solid var(--line); border-radius: 6px; }
details .outlabel { border-top: 0; }
.sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
.next { margin-top: 56px; padding: 24px; border: 1px dashed var(--line); border-radius: 8px; color: var(--muted); }
.next h3 { color: var(--ink); }
@media print {
  .rail, .pager, .wm { display: none; }
  .shell { display: block; }
  .page { display: block !important; }
  .sheet { border: 0; padding: 0; break-before: page; }
}
a:focus-visible { outline: 2px solid var(--py-blue); outline-offset: 2px; }
/* Prism, light */
.token.comment { color: #6A737D; font-style: italic; }
.token.string { color: #0A7A3E; }
.token.number, .token.boolean { color: #B35900; }
.token.keyword { color: #7A3EB0; }
.token.builtin, .token.function { color: #1D5FA0; }
.token.operator, .token.punctuation { color: #5A6573; }
.token.class-name { color: #1D5FA0; }
@media (max-width: 900px) {
  .shell { grid-template-columns: minmax(0, 1fr); }
  .rail { position: static; height: auto; border-right: 0; border-bottom: 1px solid var(--line); padding: 20px max(16px, env(safe-area-inset-right, 0px)) 16px max(16px, env(safe-area-inset-left, 0px)); }
  .rail ol { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .rail .soonlist { display: none; }
  main { padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-top: 24px; }
  .hero .how { grid-template-columns: minmax(0, 1fr); }
  .sheet { padding: 24px 16px 16px; border-radius: 6px; background-size: 150px; background-position: right 12px bottom 56px; }
  .wm { width: 220px; height: 220px; }
  .hero h1 { font-size: 28px; }
  .chapno { font-size: 28px; }
  .pager { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); }
  .pager .pno { display: none; }
  .exercises { padding: 16px; }
}
'''

JS = r'''
(function () {
  var pages = Array.prototype.slice.call(document.querySelectorAll('.page'));
  var links = Array.prototype.slice.call(document.querySelectorAll('.rail li a, .rail h4 a'));
  document.documentElement.classList.add('paged');
  function show() {
    var id = decodeURIComponent(location.hash.slice(1));
    var el = id ? document.getElementById(id) : null;
    var pg = el ? el.closest('.page') : null;
    if (!pg) { pg = pages[0]; el = null; }
    pages.forEach(function (p) { p.classList.toggle('current', p === pg); });
    links.forEach(function (a) { a.classList.toggle('active', a.getAttribute('href') === '#' + pg.id); });
    if (el && el !== pg) el.scrollIntoView({ behavior: 'instant' }); else window.scrollTo({ top: 0, behavior: 'instant' });
  }
  window.addEventListener('hashchange', show);
  show();
  document.addEventListener('keydown', function (e) {
    if (e.target.closest('textarea, input, select') || e.metaKey || e.ctrlKey || e.altKey) return;
    var cur = document.querySelector('.page.current');
    if (!cur) return;
    var a = e.key === 'ArrowRight' ? cur.querySelector('.pager .nextp') : e.key === 'ArrowLeft' ? cur.querySelector('.pager .prev') : null;
    if (a) { e.preventDefault(); location.hash = a.getAttribute('href'); }
  });
  document.querySelectorAll('textarea.mine').forEach(function (t) {
    var k = 'pyc-' + t.id;
    try { var v = localStorage.getItem(k); if (v) t.value = v; } catch (e) {}
    t.addEventListener('input', function () { try { localStorage.setItem(k, t.value); } catch (e) {} });
  });
})();
'''

# Official Python logo (no text), from https://commons.wikimedia.org/wiki/File:Python-logo-notext.svg
PY_LOGO_INNER = '<linearGradient id="SVGID_1_" gradientUnits="userSpaceOnUse" x1="63.8159" y1="56.6829" x2="118.4934" y2="1.8225" gradientTransform="matrix(1 0 0 -1 -53.2974 66.4321)"> <stop offset="0" style="stop-color:#387EB8"/> <stop offset="1" style="stop-color:#366994"/></linearGradient><path fill="url(#SVGID_1_)" d="M55.023-0.077c-25.971,0-26.25,10.081-26.25,12.156c0,3.148,0,12.594,0,12.594h26.75v3.781 c0,0-27.852,0-37.375,0c-7.949,0-17.938,4.833-17.938,26.25c0,19.673,7.792,27.281,15.656,27.281c2.335,0,9.344,0,9.344,0 s0-9.765,0-13.125c0-5.491,2.721-15.656,15.406-15.656c15.91,0,19.971,0,26.531,0c3.902,0,14.906-1.696,14.906-14.406 c0-13.452,0-17.89,0-24.219C82.054,11.426,81.515-0.077,55.023-0.077z M40.273,8.392c2.662,0,4.813,2.15,4.813,4.813 c0,2.661-2.151,4.813-4.813,4.813s-4.813-2.151-4.813-4.813C35.46,10.542,37.611,8.392,40.273,8.392z"/><linearGradient id="SVGID_2_" gradientUnits="userSpaceOnUse" x1="97.0444" y1="21.6321" x2="155.6665" y2="-34.5308" gradientTransform="matrix(1 0 0 -1 -53.2974 66.4321)"> <stop offset="0" style="stop-color:#FFE052"/> <stop offset="1" style="stop-color:#FFC331"/></linearGradient><path fill="url(#SVGID_2_)" d="M55.397,109.923c25.959,0,26.282-10.271,26.282-12.156c0-3.148,0-12.594,0-12.594H54.897v-3.781 c0,0,28.032,0,37.375,0c8.009,0,17.938-4.954,17.938-26.25c0-23.322-10.538-27.281-15.656-27.281c-2.336,0-9.344,0-9.344,0 s0,10.216,0,13.125c0,5.491-2.631,15.656-15.406,15.656c-15.91,0-19.476,0-26.532,0c-3.892,0-14.906,1.896-14.906,14.406 c0,14.475,0,18.265,0,24.219C28.366,100.497,31.562,109.923,55.397,109.923z M70.148,101.454c-2.662,0-4.813-2.151-4.813-4.813 s2.15-4.813,4.813-4.813c2.661,0,4.813,2.151,4.813,4.813S72.809,101.454,70.148,101.454z"/>'


def py_logo(prefix):
    return ('<svg viewBox="0.21 -0.077 110 110" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
            + PY_LOGO_INNER.replace('SVGID_', prefix + '_') + '</svg>')


CSS_INTERACTIVE = r'''
/* Interactive parts: one button height (32px), radius 6px like the rest of the page. */
.btn { height: 32px; padding: 0 12px; border-radius: 6px; border: 1px solid var(--line); background: var(--sheet); color: var(--ink); font: 600 14px/1 var(--f-body); cursor: pointer; display: inline-flex; align-items: center; gap: 6px; }
.btn:hover { background: var(--code-bg); }
.btn.primary { background: var(--py-blue); border-color: var(--py-blue); color: #FFFFFF; }
.btn.primary:hover { background: #24557D; border-color: #24557D; }
.btn:focus-visible { outline: 2px solid var(--py-blue); outline-offset: 2px; }
.btn[disabled] { opacity: 0.55; cursor: default; }
.btn[hidden] { display: none; }
.runbar { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; padding: 8px 14px; border-top: 1px dashed var(--line); background: var(--sheet); }
.runstatus { font-size: 14px; color: var(--muted); }
textarea.editor { display: block; width: 100%; font: 14px/1.6 var(--f-mono); color: var(--ink); background: #FFFDF2; border: 0; border-top: 1px solid var(--line); padding: 12px 14px; resize: vertical; tab-size: 4; }
.ex textarea.editor { border: 1px solid var(--line); border-radius: 6px; }
textarea.editor:focus { outline: 2px solid var(--py-blue); outline-offset: -2px; }
.yourrun:empty, .brk-result:empty, .checkres:empty { display: none; }
.yourrun .outlabel { color: var(--py-blue); }
.typed { display: inline-flex; align-items: center; gap: 6px; font-size: 14px; color: var(--muted); }
.typed textarea { font: 14px/1.4 var(--f-mono); height: 32px; width: 160px; border: 1px solid var(--line); border-radius: 6px; padding: 5px 8px; resize: vertical; color: var(--ink); }
.checkmsg { margin: 8px 0 0; font-size: 14px; font-weight: 600; }
.checkmsg.ok { color: var(--ok); }
.checkmsg.no { color: var(--bad); }
.ex .runbar { padding: 8px 0 0; border-top: 0; background: none; }
.ex .yourrun, .brk-result { margin-top: 8px; border: 1px solid var(--line); border-radius: 6px; }
.done-btn { margin-top: 12px; }
.done-btn.is-done { background: var(--ok-wash); border-color: var(--ok-wash); color: var(--ok); }
.rail a { grid-template-columns: 26px minmax(0, 1fr) auto; }
.rail a span:nth-child(2) { overflow: hidden; text-overflow: ellipsis; }

.mod { margin-bottom: 4px; }
.brandrow { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin: 0 0 24px; }
.brandrow .brand { margin: 0 8px; }
.railhide, .chev { flex: none; width: 28px; height: 28px; border: 0; border-radius: 6px; background: none; color: var(--muted); font: 16px/1 var(--f-body); cursor: pointer; display: inline-flex; align-items: center; justify-content: center; }
.railhide { border: 1px solid var(--line); background: var(--sheet); width: 32px; height: 32px; }
.railhide:hover, .chev:hover { background: var(--code-bg); color: var(--ink); }
.railhide:focus-visible, .chev:focus-visible, .railopen:focus-visible { outline: 2px solid var(--py-blue); outline-offset: 2px; }
.chev::before { content: "▸"; transition: transform 0.15s; }
.mod.open .chev::before { transform: rotate(90deg); }
@media (prefers-reduced-motion: reduce) { .chev::before { transition: none; } }
.rail .mod h4 { display: flex; align-items: center; gap: 2px; }
.rail .mod h4 a { flex: 1; min-width: 0; }
.railopen { position: fixed; z-index: 5; top: max(12px, env(safe-area-inset-top, 0px)); left: max(12px, env(safe-area-inset-left, 0px)); height: 32px; padding: 0 12px; border: 1px solid var(--line); border-radius: 6px; background: var(--sheet); color: var(--ink); font: 600 14px/1 var(--f-body); cursor: pointer; }
.railopen[hidden] { display: none; }
html.rail-off .rail { display: none; }
html.rail-off .shell { grid-template-columns: minmax(0, 1fr); }
html.rail-off .col { margin: 0 auto; }
.cheatlink { margin-top: 16px; }
.takeaways { margin-top: 40px; padding: 20px 24px; background: var(--ok-wash); border-radius: 8px; }
.takeaways h3 { color: var(--ok); margin-bottom: 8px; }
.takeaways ul { margin: 0; padding-left: 20px; }
.takeaways li { margin: 6px 0; }
.cheat-block { margin-top: 32px; }
.cheat-block h3 { margin-bottom: 8px; }
table.cheat td { vertical-align: top; }
table.cheat td:first-child { width: 58%; }
pre.cc { margin: 0; padding: 0; background: none; font: 13px/1.55 var(--f-mono); white-space: pre-wrap; color: var(--ink); }
pre.cc code { font-size: 13px; background: none; padding: 0; }
table.cheat td code { white-space: pre-wrap; }
.sheet > section.exercises:first-child, .sheet > section.breakit:first-child, .sheet > section.takeaways:first-child { margin-top: 0; }
pre.cc.res.err { color: var(--bad); }
.rv-block { margin-top: 36px; }
.rv-block h3 { margin-bottom: 4px; }
.rv-block h3 a { color: var(--py-blue); text-decoration: none; }
.rv-block h3 a:hover { text-decoration: underline; }
.rv-item { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 8px 24px; padding: 14px 0; border-bottom: 1px solid var(--line); }
.rv-item:last-child { border-bottom: 0; }
.rv-def b { display: block; margin-bottom: 2px; }
.rv-def span { color: var(--muted); font-size: 15px; line-height: 1.5; }
.rv-ex { background: var(--code-bg); border-radius: 6px; padding: 10px 12px; display: grid; gap: 6px; align-content: start; }
.rv-ex pre.res { border-top: 1px dashed var(--line); padding-top: 6px; }
@media (max-width: 700px) { .rv-item { grid-template-columns: minmax(0, 1fr); } }
.rail .mod h4 { margin: 8px 0 0; }
.rail .mod h4 a { display: flex; justify-content: space-between; align-items: center; gap: 8px; height: 36px; padding: 0 8px; border-radius: 6px; text-decoration: none; text-transform: none; letter-spacing: 0; font-size: 14px; font-weight: 600; color: var(--muted); white-space: nowrap; }
.rail .mod h4 a > span:first-child { overflow: hidden; text-overflow: ellipsis; }
.rail .mod h4 a:hover { background: var(--code-bg); text-decoration: none; }
.rail .mod.open h4 a { color: var(--ink); }
.modprog { font-family: var(--f-mono); font-size: 12px; font-weight: 400; letter-spacing: 0; text-transform: none; color: var(--muted); }
.mod:not(.open) > ol { display: none; }
.mod.open > ol { padding-bottom: 8px; }
@media (max-width: 900px) { .rail .mod > ol { grid-template-columns: minmax(0, 1fr); } }
.rail li.qlabel { font-size: 11px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); padding: 10px 8px 2px 42px; }
.rail li.sub a { height: 30px; font-size: 13px; color: var(--muted); }
.rail li.sub .n { font-size: 11px; }
.rail li.test .n { color: #B8860B; }
.prog { font-family: var(--f-mono); font-size: 12px; color: var(--muted); font-weight: 400; margin-left: 8px; }
.toc a { grid-template-columns: 48px minmax(0, 1fr) auto; }
.toc a.done .rn { color: var(--ok); }
.toc li.tgroup { padding: 14px 0 4px; font-size: 12px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); border-bottom: 1px solid var(--line); }
.toc li.tgroup:first-child { padding-top: 4px; }
.toc a.done::after { content: "✓"; color: var(--ok); margin-left: 8px; }
.quiz, .breakit { margin-top: 48px; background: var(--sheet); border: 1px solid var(--line); border-radius: 8px; padding: 24px; }
.quiz .hint, .breakit .hint, .module .hint { color: var(--muted); font-size: 14px; margin: 0 0 16px; }
.q-count { font-size: 12px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); margin-bottom: 8px; }
.q { font-size: 18px; margin: 0 0 12px; }
.quiz pre.code { border: 1px solid var(--line); border-radius: 6px; background: var(--code-bg); margin-bottom: 12px; }
.choices { display: grid; gap: 8px; margin: 0 0 12px; }
.btn.choice { justify-content: flex-start; height: auto; min-height: 32px; padding: 7px 14px; text-align: left; font-weight: 500; line-height: 1.4; }
.btn.choice.right { background: var(--ok-wash); border-color: var(--ok); color: var(--ok); }
.btn.choice.wrong { background: var(--bad-wash); border-color: var(--bad); color: var(--bad); }
.feedback { margin-top: 12px; }
.feedback .case { margin: 8px 0; }
.feedback .why { margin: 8px 0 12px; }
.q-score { font-size: 22px; font-weight: 600; margin: 0 0 16px; }
.q-actions { display: flex; flex-wrap: wrap; gap: 8px; }
.quiz-best { margin-left: 12px; font-size: 14px; color: var(--muted); }
.cover-prog { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-top: 16px; font-size: 14px; color: var(--muted); }
textarea.q-ans { margin-bottom: 8px; }
.folio { display: flex; justify-content: space-between; gap: 16px; margin-top: 32px; padding-top: 12px; border-top: 1px solid var(--line); font-family: var(--f-mono); font-size: 12px; color: var(--muted); }
.fact { margin: 40px 0 0; padding: 20px 24px; background: var(--yellow-wash); border-radius: 8px; }
.fact-h { font-size: 12px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--trap); }
.fact h4 { font-size: 18px; margin: 4px 0 8px; }
.fact p { margin: 0 0 8px; }
.fact .case { margin: 8px 0; }
.fact pre.code { border: 1px solid var(--line); border-radius: 6px; background: var(--sheet); margin: 8px 0; }
.fact details[open] { background: var(--sheet); }
.brk-puzzle { background: var(--blue-wash); }
.brk-puzzle .fact-h { color: var(--py-blue); }
.brk-bug { background: var(--bad-wash); }
.brk-bug .fact-h { color: var(--bad); }
.brk-joke { background: var(--ok-wash); }
.brk-joke .fact-h { color: var(--ok); }
.src { font-size: 14px; color: var(--muted); margin: 8px 0 0; }
.src a, .tablewrap a { color: var(--py-blue); }
.quizlink { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 2px 16px; margin-top: 48px; padding: 16px 20px; border: 1px solid var(--line); border-radius: 8px; background: var(--blue-wash); color: var(--ink); text-decoration: none; }
.quizlink span:first-child { font-size: 18px; font-weight: 600; color: var(--py-blue); }
.quizlink span:nth-child(2) { grid-row: 2; font-size: 14px; color: var(--muted); }
.quizlink .prog { grid-row: 1 / span 2; align-self: center; }
.quizlink:hover { background: #DCE7F2; }
.hero .lead { font-size: 18px; color: var(--muted); margin: 0 0 20px; max-width: 640px; }
.hero-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; }
.hero-actions .btn { text-decoration: none; }
.prog-all { font-size: 14px; color: var(--muted); }
.tryit { margin-top: 40px; }
.tryit h3, .sample > h3 { margin-bottom: 4px; }
.tryit .runbox { border: 1px solid var(--line); border-radius: 6px; overflow: hidden; }
.sample { margin-top: 40px; }
.sample-rule { margin-top: 12px; }
.sample-rule h3 { display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 12px; }
.about { margin-top: 32px; padding: 14px 20px; font-size: 14px; color: var(--muted); }
.about summary { color: var(--muted); }
.about p { margin: 10px 0; }
.about[open] { padding: 14px 20px 16px; }
.about[open] summary { padding: 0; margin-bottom: 4px; }
.roadmap-h { margin-top: 40px; }
dl.terms { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin: 16px 0 0; }
dl.terms > div { background: var(--blue-wash); border-radius: 8px; padding: 14px 16px; }
dl.terms dt { font-weight: 600; color: var(--py-blue); margin-bottom: 4px; }
dl.terms dd { margin: 0; font-size: 15px; line-height: 1.5; }
@media (max-width: 600px) { dl.terms { grid-template-columns: minmax(0, 1fr); } }
.analogy { margin: 0 0 12px; padding: 14px 18px; background: var(--yellow-wash); border-radius: 8px; }
.portrait { float: right; width: 220px; margin: 4px 0 12px 24px; }
.portrait img { display: block; width: 100%; height: auto; border-radius: 6px; border: 1px solid var(--line); }
.portrait figcaption { font-size: 12px; line-height: 1.5; color: var(--muted); margin-top: 6px; }
.portrait a { color: var(--muted); }
.concept::after { content: ""; display: block; clear: both; }
@media (max-width: 600px) { .portrait { float: none; width: 100%; margin: 0 0 12px; } }
svg .road { stroke: #E7EDF3; stroke-width: 44; stroke-linecap: round; }
svg .road.later { stroke: #F1F3F6; }
svg .roadline { stroke: #FFFFFF; stroke-width: 2.5; stroke-dasharray: 12 12; }
svg .sign { fill: var(--py-blue); }
svg .stdot { fill: #FFFFFF; }
svg .st { cursor: pointer; }
svg .st:hover .stdot, svg .st:focus .stdot { stroke-width: 3; }
svg .st.part .stdot { fill: var(--yellow-wash); }
svg .st.done .stdot { fill: var(--ok-wash); stroke: var(--ok); }
svg .stflag { fill: #FFFFFF; }
svg .sttest.done .stflag { fill: var(--ok); }
svg .sttest.part .stflag { fill: var(--py-yellow); }
svg .pinbody { fill: var(--bad); }
svg .pintext { fill: var(--bad); }
svg .stlater { opacity: 0.6; }
svg [hidden] { display: none; }
pre.out.shellrun { padding-top: 8px; }
@media (max-width: 900px) {
  .quiz, .breakit { padding: 16px; }
}
'''

JS_INTERACTIVE = r'''
(function () {
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  var store = {
    get: function (k, d) { try { var v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} },
    del: function (k) { try { localStorage.removeItem(k); } catch (e) {} }
  };

  // ---------------- Python in the browser (Pyodide)
  var HARNESS = String.raw`
import sys, io, os, json, traceback, builtins
_n = [0]
def __run(src, typed_json, files_json):
    typed = json.loads(typed_json)
    files = json.loads(files_json)
    _n[0] += 1
    d = "/home/pyodide/run" + str(_n[0])
    os.makedirs(d, exist_ok=True)
    old_cwd = os.getcwd()
    os.chdir(d)
    for name, body in files.items():
        with open(name, "w") as fh:
            fh.write(body)
    with open("lesson.py", "w") as fh:
        fh.write(src)
    stems = [n[:-3] for n in files if n.endswith(".py")]
    saved = {s: sys.modules.pop(s) for s in stems if s in sys.modules}
    sys.path.insert(0, d)
    out = io.StringIO()
    q = list(typed)
    def inp(prompt=""):
        v = q.pop(0) if q else ""
        out.write(str(prompt) + v + "\n")
        return v
    g = {"__name__": "__main__", "__builtins__": builtins, "input": inp}
    old_out = sys.stdout
    sys.stdout = out
    before = set(sys.modules)
    sys.dont_write_bytecode = False
    err = ""
    etype = ""
    try:
        exec(compile(src, "lesson.py", "exec"), g)
    except BaseException as e:
        etype = type(e).__name__
        tb = e.__traceback__
        while tb is not None and tb.tb_frame.f_code.co_filename != "lesson.py":
            tb = tb.tb_next
        err = "".join(traceback.format_exception(type(e), e, tb))
    finally:
        sys.stdout = old_out
        if d in sys.path:
            sys.path.remove(d)
        for s in stems:
            sys.modules.pop(s, None)
        for m in set(sys.modules) - before:
            sys.modules.pop(m, None)
        sys.modules.update(saved)
        os.chdir(old_cwd)
    return json.dumps({"out": out.getvalue(), "err": err, "etype": etype})
`;
  var pyPromise = null;
  function loadPy(status) {
    if (pyPromise) return pyPromise;
    status('Loading Python in your browser (first time only, about 10 MB)...');
    pyPromise = new Promise(function (resolve, reject) {
      var s = document.createElement('script');
      s.src = PYODIDE_URL + 'pyodide.js';
      s.onload = function () {
        loadPyodide({ indexURL: PYODIDE_URL }).then(function (p) { p.runPython(HARNESS); resolve(p); }, reject);
      };
      s.onerror = function () { reject(new Error('Could not download Python. Check the internet connection and try again.')); };
      document.head.appendChild(s);
    });
    pyPromise.catch(function () { pyPromise = null; });
    return pyPromise;
  }
  function runPy(code, typed, files, status) {
    return loadPy(status).then(function (p) {
      var fn = p.globals.get('__run');
      var r = fn(code, JSON.stringify(typed || []), JSON.stringify(files || {}));
      fn.destroy();
      return JSON.parse(r);
    });
  }
  function outHTML(label, r) {
    var parts = [];
    if (r.out) parts.push('<span class="o">' + esc(r.out.replace(/\n$/, '')) + '</span>');
    if (r.err) {
      var lines = r.err.replace(/\n$/, '').split('\n');
      var last = lines.pop();
      parts.push((lines.length ? '<span class="tb">' + esc(lines.join('\n')) + '\n</span>' : '') + '<span class="errline">' + esc(last) + '</span>');
    }
    return '<div class="outlabel">' + label + '</div><pre class="out">' + (parts.join('\n') || '<span class="o muted">(nothing is printed)</span>') + '</pre>';
  }
  function codeHTML(code) { return '<pre class="code"><code class="language-python">' + esc(code) + '</code></pre>'; }
  function highlight(root) { if (window.Prism) root.querySelectorAll('code.language-python').forEach(function (c) { Prism.highlightElement(c); }); }
  function onCtrlEnter(el, fn) { el.addEventListener('keydown', function (e) { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) { e.preventDefault(); fn(); } }); }
  function makeStatus(el) { return function (t) { el.textContent = t; }; }

  // ---------------- Run / Edit on every example
  document.querySelectorAll('.runbox').forEach(function (box) {
    var pre = box.querySelector('pre.code');
    var orig = pre.textContent;
    var typed = box.dataset.typed ? JSON.parse(box.dataset.typed) : null;
    var files = box.dataset.files ? JSON.parse(box.dataset.files) : null;
    var bar = document.createElement('div');
    bar.className = 'runbar';
    bar.innerHTML = '<button type="button" class="btn primary">Run</button><button type="button" class="btn">Edit</button><button type="button" class="btn" hidden>Reset</button>'
      + (typed ? '<label class="typed">Typed input <textarea rows="1" spellcheck="false">' + esc(typed.join('\n')) + '</textarea></label>' : '')
      + '<span class="runstatus" aria-live="polite"></span>';
    pre.after(bar);
    var result = document.createElement('div');
    result.className = 'yourrun';
    box.appendChild(result);
    var btns = bar.querySelectorAll('button');
    var runB = btns[0], editB = btns[1], resetB = btns[2];
    var status = makeStatus(bar.querySelector('.runstatus'));
    var typedBox = bar.querySelector('.typed textarea');
    var ta = null;
    function go() {
      var code = ta ? ta.value : orig;
      var t = typedBox ? typedBox.value.split('\n') : [];
      runB.disabled = true;
      status('Running...');
      runPy(code, t, files, status).then(function (r) {
        result.innerHTML = outHTML('Your run (Python in your browser)', r);
        status('');
      }, function (e) { status(e.message || String(e)); }).then(function () { runB.disabled = false; });
    }
    runB.addEventListener('click', go);
    editB.addEventListener('click', function () {
      ta = document.createElement('textarea');
      ta.className = 'editor';
      ta.spellcheck = false;
      ta.value = orig;
      ta.rows = orig.split('\n').length + 1;
      ta.setAttribute('aria-label', 'Edit this example');
      pre.hidden = true;
      pre.after(ta);
      editB.hidden = true;
      resetB.hidden = false;
      onCtrlEnter(ta, go);
      ta.focus();
    });
    resetB.addEventListener('click', function () { ta.value = orig; result.innerHTML = ''; ta.focus(); });
  });

  document.querySelectorAll('.runbox[data-autoedit] .runbar .btn:nth-child(2)').forEach(function (b) {
    b.click();
    var ta = b.closest('.runbox').querySelector('textarea.editor');
    if (ta) ta.blur();
  });

  // ---------------- Continue where you left off
  function pageTitle(id) {
    var pg = document.getElementById(id);
    if (!pg) return '';
    var no = pg.querySelector('.chapno'), h = pg.querySelector('h2');
    return (no ? no.textContent + ': ' : '') + (h ? h.textContent : '');
  }
  function remember() {
    var id = location.hash.slice(1);
    var el = id && document.getElementById(id);
    var pg = el ? el.closest('.page') : null;
    if (pg && pg.id !== 'cover') store.set('pyc-last', pg.id);
  }
  window.addEventListener('hashchange', remember);
  function openModule() {
    var id = location.hash.slice(1);
    var el = id && document.getElementById(id);
    var pg = el ? el.closest('.page') : null;
    var link = pg ? document.querySelector('.rail a[href="#' + pg.id + '"]') : null;
    var mod = link ? link.closest('.mod') : null;
    if (!openModule.done) { document.querySelectorAll('.rail .mod').forEach(function (m) { m.classList.toggle('open', m === mod); }); openModule.done = true; }
    else if (mod) mod.classList.add('open');
  }
  window.addEventListener('hashchange', openModule);
  openModule();
  function syncChev() { document.querySelectorAll('.rail .mod').forEach(function (m) { m.querySelector('.chev').setAttribute('aria-expanded', m.classList.contains('open') ? 'true' : 'false'); }); }
  document.querySelectorAll('.rail .chev').forEach(function (b) {
    b.addEventListener('click', function () { b.closest('.mod').classList.toggle('open'); syncChev(); });
  });
  syncChev();
  window.addEventListener('hashchange', syncChev);
  var railOpen = document.querySelector('.railopen');
  function setRail(off) {
    document.documentElement.classList.toggle('rail-off', off);
    railOpen.hidden = !off;
    store.set('pyc-rail-off', off);
  }
  document.querySelector('.railhide').addEventListener('click', function () { setRail(true); railOpen.focus(); });
  railOpen.addEventListener('click', function () { setRail(false); document.querySelector('.railhide').focus(); });
  setRail(!!store.get('pyc-rail-off', false));
  var last = store.get('pyc-last', null);
  var cont = document.getElementById('continue');
  if (cont && last && document.getElementById(last)) {
    cont.hidden = false;
    cont.href = '#' + last;
    cont.textContent = 'Continue: ' + pageTitle(last);
  }

  function placePin() {
    var pin = document.getElementById('pin');
    var lastId = store.get('pyc-last', null);
    if (!pin || !lastId) return;
    var st = null, m;
    if ((m = lastId.match(/^q-m(\d)$/))) st = document.querySelector('svg .st[data-test="m' + m[1] + '"]');
    else if ((m = lastId.match(/^q-c(\d+)$/))) st = document.querySelector('svg .st[data-ch="' + m[1] + '"]');
    else if ((m = lastId.match(/^m(\d)$/))) { var a = document.querySelector('.rail h4 a[href="#m' + m[1] + '"]'); var first = a && a.closest('h4').nextElementSibling.querySelector('a[data-ch]'); if (first) st = document.querySelector('svg .st[data-ch="' + first.dataset.ch + '"]'); }
    else { var link = document.querySelector('.rail a[href="#' + lastId + '"][data-ch]'); if (link) st = document.querySelector('svg .st[data-ch="' + link.dataset.ch + '"]'); }
    if (!st) return;
    pin.setAttribute('transform', 'translate(' + st.dataset.x + ',' + (st.dataset.y - 20) + ')');
    pin.removeAttribute('hidden');
    var t = pin.querySelector('.pintext'); var right = +st.dataset.x > 700;
    t.setAttribute('x', right ? '-16' : '16'); t.setAttribute('text-anchor', right ? 'end' : 'start');
  }

  // ---------------- Check answers (Predict) and run answers (Write)
  function norm(s) { return s.replace(/\r/g, '').split('\n').map(function (l) { return l.replace(/\s+$/, ''); }).join('\n').replace(/^\n+|\n+$/g, ''); }
  function judge(ans, out, etype) {
    if (etype) {
      var ok = ans.toLowerCase().indexOf(etype.toLowerCase()) >= 0;
      return { ok: ok, hint: ok ? '' : 'The real answer is an error: ' + etype + '.' };
    }
    var a = norm(ans), b = norm(out);
    if (a === b) return { ok: true, hint: '' };
    if (a.replace(/"/g, "'") === b.replace(/"/g, "'")) return { ok: false, hint: 'Very close: look at the quotes.' };
    if (a.replace(/\s+/g, '') === b.replace(/\s+/g, '')) return { ok: false, hint: 'Very close: look at the spaces and line breaks.' };
    return { ok: false, hint: '' };
  }
  document.querySelectorAll('li.ex[data-out]').forEach(function (li) {
    var ta = li.querySelector('textarea.mine');
    var det = li.querySelector('details');
    var bar = document.createElement('div');
    bar.className = 'runbar';
    bar.innerHTML = '<button type="button" class="btn primary">Check</button>';
    var res = document.createElement('div');
    res.className = 'checkres';
    res.setAttribute('aria-live', 'polite');
    ta.after(bar);
    bar.after(res);
    function check() {
      if (!ta.value.trim()) { res.innerHTML = '<p class="checkmsg no">Type your answer first.</p>'; return; }
      var j = judge(ta.value, li.dataset.out, li.dataset.etype);
      res.innerHTML = '<p class="checkmsg ' + (j.ok ? 'ok">✓ Correct' : 'no">✗ Not quite') + (j.hint ? '. ' + esc(j.hint) : '') + '</p>';
      det.open = true;
    }
    bar.querySelector('button').addEventListener('click', check);
    onCtrlEnter(ta, check);
  });
  document.querySelectorAll('li.ex[data-write]').forEach(function (li) {
    var ta = li.querySelector('textarea.mine');
    ta.classList.add('editor');
    ta.spellcheck = false;
    var typed = li.dataset.typed ? JSON.parse(li.dataset.typed) : null;
    var bar = document.createElement('div');
    bar.className = 'runbar';
    bar.innerHTML = '<button type="button" class="btn primary">Run my code</button><span class="runstatus" aria-live="polite"></span>';
    var res = document.createElement('div');
    res.className = 'yourrun';
    ta.after(bar);
    bar.after(res);
    var status = makeStatus(bar.querySelector('.runstatus'));
    function go() {
      if (!ta.value.trim()) { status('Write some code first.'); return; }
      status('Running...');
      runPy(ta.value, typed, null, status).then(function (r) { res.innerHTML = outHTML('Your run', r); status(''); }, function (e) { status(e.message || String(e)); });
    }
    bar.querySelector('button').addEventListener('click', go);
    onCtrlEnter(ta, go);
  });

  // ---------------- Break it
  document.querySelectorAll('li.brk').forEach(function (li) {
    var ta = li.querySelector('.brk-code');
    var start = li.querySelector('.brk-reset').dataset.start;
    var target = li.dataset.target;
    var res = li.querySelector('.brk-result');
    var runB = li.querySelector('.brk-run');
    function go() {
      runB.disabled = true;
      res.innerHTML = '<p class="checkmsg">Running...</p>';
      runPy(ta.value, [], null, function (t) { res.innerHTML = '<p class="checkmsg">' + esc(t) + '</p>'; }).then(function (r) {
        var msg;
        if (ta.value === start) msg = '<p class="checkmsg no">Change the code first, then run it.</p>';
        else if (r.etype === target) msg = '<p class="checkmsg ok">✓ You raised ' + target + '.</p>';
        else if (r.etype) msg = '<p class="checkmsg no">✗ That raised ' + esc(r.etype) + ', not ' + target + '.</p>';
        else msg = '<p class="checkmsg no">✗ No error yet: the code still runs.</p>';
        res.innerHTML = msg + outHTML('Your run', r);
      }, function (e) { res.innerHTML = '<p class="checkmsg no">' + esc(e.message || String(e)) + '</p>'; }).then(function () { runB.disabled = false; });
    }
    runB.addEventListener('click', go);
    onCtrlEnter(ta, go);
    li.querySelector('.brk-reset').addEventListener('click', function () { ta.value = start; res.innerHTML = ''; });
  });

  // ---------------- Progress
  var done = new Set(store.get('pyc-done', []));
  var rules = Array.prototype.slice.call(document.querySelectorAll('section.rule'));
  function chOf(id) { return id.slice(1).split('-')[0]; }
  function refresh() {
    var tot = {}, got = {}, all = 0;
    rules.forEach(function (r) { var c = chOf(r.id); tot[c] = (tot[c] || 0) + 1; if (done.has(r.id)) { got[c] = (got[c] || 0) + 1; all++; } });
    document.querySelectorAll('.prog[data-ch], .rail a[data-ch] .prog').forEach(function (el) {
      var c = el.dataset.ch || el.closest('a').dataset.ch;
      el.textContent = tot[c] ? (got[c] || 0) + '/' + tot[c] : '';
    });
    document.querySelectorAll('.prog[data-best]').forEach(function (el) {
      var b = store.get('pyc-best-' + el.dataset.best, null);
      el.textContent = b ? 'best ' + b.score + '/' + b.n : '';
    });
    document.querySelectorAll('.toc a[href^="#r"]').forEach(function (a) { a.classList.toggle('done', done.has(a.getAttribute('href').slice(1))); });
    var pa = document.querySelector('.prog-all');
    if (pa) pa.textContent = all ? all + ' of ' + rules.length + ' rules marked done' : '';
    var modCh = {};
    document.querySelectorAll('.rail h4 + ol').forEach(function (ol) {
      var h = ol.previousElementSibling.querySelector('a');
      var m = h && h.getAttribute('href').match(/^#m(\d)$/);
      if (m) modCh[m[1]] = Array.prototype.map.call(ol.querySelectorAll('a[data-ch]'), function (a) { return a.dataset.ch; });
    });
    document.querySelectorAll('svg .st[data-ch]').forEach(function (a) {
      var c = a.dataset.ch, d = got[c] || 0, n = tot[c] || 0, best = store.get('pyc-best-c' + c, null);
      var full = n ? d === n : !!best;
      a.classList.toggle('done', full);
      a.classList.toggle('part', !full && (d > 0 || !!best));
      a.querySelector('.stprog').textContent = n ? d + '/' + n : (best ? 'quiz ' + best.score + '/' + best.n : '');
    });
    document.querySelectorAll('svg .st[data-test]').forEach(function (a) {
      var b = store.get('pyc-best-' + a.dataset.test, null);
      a.classList.toggle('done', !!b && b.score === b.n);
      a.classList.toggle('part', !!b && b.score < b.n);
      a.querySelector('.stprog').textContent = b ? b.score + '/' + b.n : '';
    });
    placePin();
    document.querySelectorAll('.rail .mod').forEach(function (m) {
      var d = 0, n = 0;
      m.querySelectorAll('a[data-ch]').forEach(function (a) { d += got[a.dataset.ch] || 0; n += tot[a.dataset.ch] || 0; });
      m.querySelector('.modprog').textContent = n ? d + '/' + n : '';
    });
    document.querySelectorAll('.mapprog').forEach(function (t) {
      var chs = modCh[t.dataset.mod] || [], d = 0, n = 0;
      chs.forEach(function (c) { d += got[c] || 0; n += tot[c] || 0; });
      var b = store.get('pyc-best-m' + t.dataset.mod, null);
      t.textContent = (n ? d + '/' + n + ' rules' : '') + (b ? '  ·  test ' + b.score + '/' + b.n : '');
    });
  }
  rules.forEach(function (sec) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'btn done-btn';
    sec.appendChild(b);
    function paint() { var d = done.has(sec.id); b.textContent = d ? '✓ Done' : 'Mark as done'; b.classList.toggle('is-done', d); b.setAttribute('aria-pressed', d ? 'true' : 'false'); }
    paint();
    b.addEventListener('click', function () {
      if (done.has(sec.id)) done.delete(sec.id); else done.add(sec.id);
      store.set('pyc-done', Array.from(done));
      paint();
      refresh();
    });
  });
  var resetB = document.querySelector('.reset-progress');
  if (resetB) {
    var armed = null;
    resetB.addEventListener('click', function () {
      if (!armed) {
        resetB.textContent = 'Click again to clear ticks and quiz scores';
        armed = setTimeout(function () { armed = null; resetB.textContent = 'Reset my progress'; }, 4000);
        return;
      }
      clearTimeout(armed); armed = null;
      done.clear();
      store.del('pyc-done');
      document.querySelectorAll('section.quiz').forEach(function (q) { store.del('pyc-best-' + q.dataset.quiz); });
      rules.forEach(function (sec) { var b = sec.querySelector('.done-btn'); b.textContent = 'Mark as done'; b.classList.remove('is-done'); b.setAttribute('aria-pressed', 'false'); });
      resetB.textContent = 'Reset my progress';
      document.querySelectorAll('.quiz-best').forEach(function (e) { e.textContent = ''; });
      refresh();
    });
  }
  refresh();

  // ---------------- Quizzes
  var ERRORS = ['SyntaxError', 'NameError', 'TypeError', 'ValueError', 'IndexError', 'KeyError', 'AttributeError', 'ZeroDivisionError', 'IndentationError', 'ModuleNotFoundError'];
  var WORKS = 'Works, no error';
  function shuffle(a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
  document.querySelectorAll('section.quiz').forEach(function (sec) {
    var all = JSON.parse(sec.querySelector('.quiz-data').textContent);
    var n = +sec.dataset.n;
    var id = sec.dataset.quiz;
    var body = sec.querySelector('.quiz-body');
    function showBest() {
      var el = sec.querySelector('.quiz-best');
      var b = store.get('pyc-best-' + id, null);
      if (el) el.textContent = b ? 'Best so far: ' + b.score + ' / ' + b.n : '';
    }
    showBest();
    sec.querySelector('.quiz-start').addEventListener('click', function () { begin(shuffle(all).slice(0, n), true); });
    function begin(qs, full) {
      var i = 0, score = 0, wrong = [];
      ask();
      function ask() {
        if (i >= qs.length) return finish();
        var q = qs[i];
        var h = '<div class="q-count">Question ' + (i + 1) + ' of ' + qs.length + ' · score ' + score + '</div>';
        if (q.type === 'mcq') {
          h += '<p class="q">' + esc(q.q) + '</p><div class="choices">' + shuffle(q.choices.map(function (c, k) { return k; })).map(function (k) {
            return '<button type="button" class="btn choice" data-k="' + k + '">' + esc(q.choices[k]) + '</button>'; }).join('') + '</div>';
        } else if (q.type === 'error') {
          var opts = [q.answer === 'Works' ? WORKS : q.answer, q.answer === 'Works' ? null : WORKS].filter(Boolean);
          shuffle(ERRORS.filter(function (e) { return e !== q.answer; })).slice(0, 5 - opts.length).forEach(function (e) { opts.push(e); });
          h += '<p class="q">Does this work? If not, which error does it raise?</p>' + codeHTML(q.code) + '<div class="choices">'
            + shuffle(opts).map(function (o) { return '<button type="button" class="btn choice" data-v="' + esc(o) + '">' + esc(o) + '</button>'; }).join('') + '</div>';
        } else {
          h += '<p class="q">What does this print? Type it exactly.</p>' + codeHTML(q.code)
            + '<label class="sr" for="qa-' + id + '">Your answer</label><textarea id="qa-' + id + '" class="mine q-ans" rows="2" spellcheck="false" placeholder="What it prints"></textarea>'
            + '<div class="q-actions"><button type="button" class="btn primary q-check">Check</button></div>';
        }
        h += '<div class="feedback" aria-live="polite"></div>';
        body.innerHTML = h;
        highlight(body);
        var fb = body.querySelector('.feedback');
        function answered(ok, shown, hint) {
          if (ok) score++; else wrong.push(q);
          var real = q.type === 'mcq' ? '' : '<div class="case plain">' + outHTML('Real result', { out: q.out, err: q.err }) + '</div>';
          fb.innerHTML = '<p class="checkmsg ' + (ok ? 'ok">✓ Correct' : 'no">✗ Not quite. Answer: ' + esc(shown)) + (hint ? '. ' + esc(hint) : '') + '</p>'
            + real + (q.why ? '<p class="why">' + esc(q.why) + '</p>' : '') + (q.from ? '<p class="hint">From ' + esc(q.from) + '.</p>' : '')
            + '<div class="q-actions"><button type="button" class="btn primary q-next">' + (i + 1 < qs.length ? 'Next question' : 'See my score') + '</button></div>';
          var nx = fb.querySelector('.q-next');
          nx.addEventListener('click', function () { i++; ask(); body.scrollIntoView({ block: 'nearest' }); });
          nx.focus();
        }
        body.querySelectorAll('.choice').forEach(function (b) {
          b.addEventListener('click', function () {
            var correctV = q.type === 'mcq' ? String(q.answer) : (q.answer === 'Works' ? WORKS : q.answer);
            var mine = q.type === 'mcq' ? b.dataset.k : b.dataset.v;
            body.querySelectorAll('.choice').forEach(function (c) {
              c.disabled = true;
              var v = q.type === 'mcq' ? c.dataset.k : c.dataset.v;
              if (v === correctV) c.classList.add('right');
            });
            if (mine !== correctV) b.classList.add('wrong');
            answered(mine === correctV, q.type === 'mcq' ? q.choices[q.answer] : correctV);
          });
        });
        var ck = body.querySelector('.q-check');
        if (ck) {
          var ta = body.querySelector('.q-ans');
          var doCheck = function () {
            if (!ta.value.trim()) { fb.innerHTML = '<p class="checkmsg no">Type your answer first.</p>'; return; }
            ck.disabled = true; ta.readOnly = true;
            var j = judge(ta.value, q.answer, '');
            answered(j.ok, q.answer.replace(/\n$/, ''), j.hint);
          };
          ck.addEventListener('click', doCheck);
          onCtrlEnter(ta, doCheck);
          ta.focus();
        }
      }
      function finish() {
        if (full) {
          var b = store.get('pyc-best-' + id, null);
          if (!b || score > b.score) store.set('pyc-best-' + id, { score: score, n: qs.length });
          showBestAll();
        }
        body.innerHTML = '<p class="q-score">You got ' + score + ' out of ' + qs.length + '.</p><div class="q-actions">'
          + (wrong.length ? '<button type="button" class="btn primary q-retry">Retry the ' + wrong.length + ' you missed</button>' : '')
          + '<button type="button" class="btn q-again">' + (n < all.length ? 'New mix of questions' : 'Start again') + '</button></div>';
        var r = body.querySelector('.q-retry');
        if (r) r.addEventListener('click', function () { begin(wrong, false); });
        body.querySelector('.q-again').addEventListener('click', function () { begin(shuffle(all).slice(0, n), true); });
      }
    }
  });
  function showBestAll() { refresh(); document.querySelectorAll('section.quiz').forEach(function (s) { var el = s.querySelector('.quiz-best'); var b = store.get('pyc-best-' + s.dataset.quiz, null); if (el) el.textContent = b ? 'Best so far: ' + b.score + ' / ' + b.n : ''; }); }
})();
'''

PYODIDE = "https://cdn.jsdelivr.net/pyodide/v314.0.7/full/"


# "Did you know?" boxes between pages. Code facts are run by the build;
# history facts carry their source link.
FACTS = [
    ("run", "True and False are secretly numbers", 'print(True + True)\nprint(True * 10)', "True counts as 1 and False as 0, so you can add them."),
    ("src", "The first computer bug was a real moth",
     "On 9 September 1947 the team running the Harvard Mark II found a moth stuck in the machine and taped it into their log book, next to the note \"First actual case of bug being found\". The word bug was already used for faults; this was the first real one.",
     ("Computer History Museum", "https://www.computerhistory.org/tdih/september/9/")),
    ("run", "Python has no size limit on whole numbers", 'print(2 ** 100)', "Many languages cap whole numbers at a fixed size. Python just keeps going, digit for digit."),
    ("src", "The first program was written in 1843",
     "Ada Lovelace published notes on Charles Babbage's Analytical Engine, a machine that was never finished. They set out step by step how it could calculate a series called the Bernoulli numbers, which is why they are often called the first computer program.",
     ("Science Museum", "https://www.sciencemuseum.org.uk/objects-and-stories/women-computing")),
    ("run", "An emoji is one character", 'snake = "🐍"\nprint(len(snake))\nprint(snake * 3)', "Python strings hold any character, not just English letters."),
    ("run", "round() rounds halves to the even number", 'print(round(2.5))\nprint(round(3.5))', "It does not always round .5 up. Rounding halves to the nearest even number keeps big totals fair."),
    ("run", "Comparisons can be chained", 'age = 25\nprint(18 <= age < 60)', "This reads like maths: 18 is at most age, and age is below 60."),
    ("run", "Underscores make big numbers readable", 'population = 1_400_000_000\nprint(population)', "Python ignores the underscores; they are only for your eyes."),
    ("run", "Python can show its own design rules", 'import this', "This poem, The Zen of Python, is hidden in every copy of Python."),
]
FACT_I = [0]


def fact_box():
    kind, title, body, extra = FACTS[FACT_I[0] % len(FACTS)]
    FACT_I[0] += 1
    if kind == "run":
        inner = example(body) + f'<p class="why">{extra}</p>'
    else:
        inner = f'<p>{body}</p><p class="src">Source: <a href="{extra[1]}">{extra[0]}</a></p>'
    return f'<aside class="fact"><div class="fact-h">Did you know?</div><h4>{title}</h4>{inner}</aside>'


BREAK_ORDER = ["fact", "puzzle", "bug", "fact", "puzzle", "joke"]
# chapter each item needs, so a break never uses something not taught yet
PUZZLE_CH = [4, 5, 4, 4, 6, 5, 4, 4, 4, 4, 6, 6]
BUG_CH = [6, 4, 6, 5, 7, 4]
FACT_CH = [4, 0, 4, 0, 5, 4, 4, 4, 3]
BREAK_STATE = {"all": 0, "used": {"fact": set(), "puzzle": set(), "bug": set(), "joke": set()}}
CURRENT_CH = ["0"]


CH_USED = {}


def pick(kind, items, need):
    """Next item of this kind that the chapter allows and has not shown yet.
    Prefer items never shown anywhere; None when the chapter has none left."""
    ch = int(CURRENT_CH[0])
    here = CH_USED.setdefault((CURRENT_CH[0], kind), set())
    used = BREAK_STATE["used"][kind]
    ok = [k for k in range(len(items)) if need[k] <= ch and k not in here]
    if not ok:
        return None
    k = ([k for k in ok if k not in used] or ok)[0]
    used.add(k)
    here.add(k)
    return k


def fact_at(k):
    kind, title, body, extra = FACTS[k]
    if kind == "run":
        inner = example(body) + f'<p class="why">{extra}</p>'
    else:
        inner = f'<p>{body}</p><p class="src">Source: <a href="{extra[1]}">{extra[0]}</a></p>'
    return f'<aside class="fact"><div class="fact-h">Did you know?</div><h4>{title}</h4>{inner}</aside>'


def brain_break():
    start = BREAK_STATE["all"]
    BREAK_STATE["all"] += 1
    for step in range(len(BREAK_ORDER)):
        kind = BREAK_ORDER[(start + step) % len(BREAK_ORDER)]
        if kind == "puzzle":
            k = pick("puzzle", PUZZLES, PUZZLE_CH)
            if k is None:
                continue
            code = PUZZLES[k]
            rc, out, err = run(code)
            return (f'<aside class="fact brk-puzzle"><div class="fact-h">5-second puzzle</div><h4>What does this print?</h4>{code_html(code)}'
                    f'<details><summary>Show answer</summary>{out_html(out, err, "Real output")}</details></aside>')
        if kind == "bug":
            k = pick("bug", BUGS, BUG_CH)
            if k is None:
                continue
            code, note, fix = BUGS[k]
            rc, out, err = run(code)
            rc2, out2, err2 = run(fix)
            if rc2 != 0:
                sys.exit(f"BUG FIX must run: {fix}\n{err2}")
            return (f'<aside class="fact brk-bug"><div class="fact-h">Spot the bug</div><h4>This does not do what it should. Why?</h4>{code_html(code)}'
                    f'<details><summary>Show the bug</summary>{out_html(out, err, "What it really does")}<p class="why">{esc(note)}</p>'
                    f'<div class="outlabel">Fixed</div>{code_html(fix)}{out_html(out2, "", "Output")}</details></aside>')
        if kind == "joke":
            k = pick("joke", JOKES, [0] * len(JOKES))
            if k is None:
                continue
            q, a_ = JOKES[k]
            return (f'<aside class="fact brk-joke"><div class="fact-h">Smile break</div><h4>{esc(q)}</h4>'
                    f'<details><summary>Show the answer</summary><p class="why">{esc(a_)}</p></details></aside>')
        if kind == "fact":
            k = pick("fact", FACTS, FACT_CH)
            if k is None:
                continue
            return fact_at(k)
    return ""


BLOCK_SPLIT = re.compile(r'(?=<section class="(?:rule|concept|exercises|breakit|takeaways)")')


def paginate(head, body, tail, folio_label, next_page_no):
    """Cut a chapter into book pages of about three rules each."""
    blocks = [b for b in BLOCK_SPLIT.split(body) if b.strip()]
    sheets, cur, rules = [], [head], 0
    for b in blocks:
        is_rule = b.startswith('<section class="rule"')
        starts_own = b.startswith('<section class="exercises"') or b.startswith('<section class="breakit"')
        if (starts_own or (rules >= 3 and (is_rule or b.startswith('<section class="concept"')))) and len(cur) > 1:
            sheets.append(cur)
            cur, rules = [], 0
        cur.append(b)
        rules += is_rule
    cur.append(tail)
    sheets.append(cur)
    out = []
    for k, sh in enumerate(sheets):
        no = next_page_no[0]
        next_page_no[0] += 1
        extra = brain_break() if k < len(sheets) - 1 else ""
        out.append(f'<div class="sheet">{"".join(sh)}{extra}<div class="folio"><span>{folio_label}</span><span>page {no}</span></div></div>')
    return "".join(out)


def single_sheet(inner, folio_label, next_page_no, number=True):
    if not number:
        return f'<div class="sheet">{inner}</div>'
    no = next_page_no[0]
    next_page_no[0] += 1
    return f'<div class="sheet">{inner}<div class="folio"><span>{folio_label}</span><span>page {no}</span></div></div>'


def takeaways(num):
    items = TAKEAWAYS.get(num)
    if not items:
        return ""
    return ('<section class="takeaways"><h3>Key takeaways</h3><ul>'
            + "".join(f"<li>{esc(t)}</li>" for t in items) + "</ul></section>")


def cheat_sheet():
    parts = []
    for title, codes in CHEAT:
        rows = []
        for c in codes:
            rc, out, err = run(c)
            res = out.rstrip("\n") if rc == 0 else err.strip().split("\n")[-1]
            cls = "ok" if rc == 0 else "err"
            rows.append(f'<tr><td><pre class="cc"><code class="language-python">{esc(c)}</code></pre></td>'
                        f'<td><pre class="cc res {cls}">{esc(res)}</pre></td></tr>')
        parts.append(f'<section class="cheat-block"><h3>{title}</h3><div class="tablewrap"><table class="cheat">'
                     f'<thead><tr><th>You write</th><th>Python gives</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div></section>')
    return "".join(parts)


def revision_sheet(by_num):
    parts = []
    for num, items in REVISION:
        rows = []
        for term, definition, code in items:
            ex = ""
            if code:
                typed = ["25"] if "input(" in code else None
                rc, out, err = run(code, typed)
                res = out.rstrip("\n") if rc == 0 else (out + err.strip().split("\n")[-1])
                if rc != 0 and not res:
                    sys.exit(f"REVISION example produced nothing: {code}")
                ex = (f'<div class="rv-ex"><pre class="cc"><code class="language-python">{esc(code)}</code></pre>'
                      f'<pre class="cc res {"ok" if rc == 0 else "err"}">{esc(res)}</pre></div>')
            rows.append(f'<div class="rv-item"><div class="rv-def"><b>{esc(term)}</b><span>{esc(definition)}</span></div>{ex}</div>')
        parts.append(f'<section class="rv-block"><h3><a href="#t-{by_num[num][1]}">Chapter {num} · {by_num[num][2]}</a></h3>{"".join(rows)}</section>')
    return "".join(parts)


RULE_LABEL = {}   # "6.12" -> (topic title, number inside that topic)
CONCEPT_H3 = re.compile(r'<section class="concept"[^>]*><h3>(.*?)</h3>')
RULE_H3 = re.compile(r'<section class="rule" id="r(\d+)-(\d+)"><h3><span class="rnum">Rule (\d+\.\d+)</span>')


def label_rules(num, chapter_title, body):
    """Number rules from 1 inside each topic (each concept heading starts a new topic)."""
    topic, k = chapter_title, 0
    for block in BLOCK_SPLIT.split(body):
        m = CONCEPT_H3.match(block)
        if m:
            topic, k = re.sub("<[^>]+>", "", m.group(1)), 0
            continue
        m = RULE_H3.match(block)
        if m:
            k += 1
            RULE_LABEL[m.group(3)] = (topic, k)


def relabel(body):
    body = RULE_H3.sub(lambda m: f'<section class="rule" id="r{m.group(1)}-{m.group(2)}"><h3><span class="rnum">Rule {RULE_LABEL[m.group(3)][1]}</span>', body)
    return re.sub(r"rule (\d+\.\d+)", lambda m: f'rule {RULE_LABEL[m.group(1)][1]} of &quot;{RULE_LABEL[m.group(1)][0]}&quot;', body)


def grouped_toc(num):
    rows, last = [], None
    for rid, rn, t in RULE_INDEX.get(num, []):
        topic, k = RULE_LABEL[rn]
        if topic != last:
            rows.append(f'<li class="tgroup">{esc(topic, quote=False)}</li>')
            last = topic
        rows.append(f'<li><a href="#{rid}"><span class="rn">{k}</span><span>{t}</span></a></li>')
    return '<ol class="toc">' + "".join(rows) + "</ol>" if rows else ""


def d_roadmap(by_num):
    """A winding road: one stop per chapter, a flag per module test, the next part faded ahead."""
    labels = {"0": ["What is", "programming?"], "1": ["What is", "Python?"], "2": ["Running code", "and errors"],
              "3": ["print and", "modules"], "4": ["Variables and", "operators"], "5": ["Strings"],
              "6": ["Lists and", "tuples"], "7": ["Dictionaries", "and sets"]}
    row1 = [("ch", "0"), ("ch", "1"), ("ch", "2"), ("test", "1"), ("ch", "3"), ("ch", "4"), ("test", "2")]
    row2 = [("ch", "5"), ("test", "3"), ("ch", "6"), ("ch", "7"), ("test", "4")]
    later = [("8", ["if, elif,", "else"]), ("9", ["Loops"]), ("10", ["Functions"]), ("11", ["try and", "except"]),
             ("12", ["Files"]), ("13", ["Classes"]), ("14", ["Mini", "project"])]
    stops = [(80 + k * 120, 120, st) for k, st in enumerate(row1)] + [(800 - k * 120, 320, st) for k, st in enumerate(row2)]
    s = ('<path d="M30,120 H820 C895,120 895,320 820,320 H90" class="road" fill="none"/>'
         '<path d="M90,320 C15,320 15,520 90,520 H875" class="road later" fill="none"/>'
         '<path d="M30,120 H820 C895,120 895,320 820,320 H90" class="roadline" fill="none"/>'
         '<path d="M90,320 C15,320 15,520 90,520 H875" class="roadline" fill="none"/>')
    signs = [(260, 52, "Module 1 · Foundations"), (680, 52, "Module 2 · First code"),
             (740, 252, "Module 3 · Text"), (440, 252, "Module 4 · Collections"), (470, 452, "Next part · coming soon")]
    for x, y, t in signs:
        s += stext(x, y, t, 17, "hand sign", "middle")
    s += stext(150, 290, "Part 1 ends here", 13, "hand note", "middle")
    for x, y, (kind, key) in stops:
        if kind == "ch":
            href = "#t-" + by_num[key][1]
            s += (f'<a href="{href}" class="st" data-ch="{key}" data-x="{x}" data-y="{y}"><g filter="url(#rough)">'
                  f'<circle cx="{x}" cy="{y}" r="19" class="stroke stdot"/></g>'
                  f'<circle cx="{x}" cy="{y}" r="19" fill="transparent"/>'
                  + stext(x, y + 6, key, 17, "mono", "middle"))
            for i, ln in enumerate(labels[key]):
                s += stext(x, y + 42 + i * 16, ln, 14, "hand note", "middle")
            s += f'<text x="{x}" y="{y + 42 + len(labels[key]) * 16}" class="mono note stprog" font-size="11" text-anchor="middle"></text></a>'
        else:
            s += (f'<a href="#q-m{key}" class="st sttest" data-test="m{key}" data-x="{x}" data-y="{y}"><g filter="url(#rough)">'
                  f'<path d="M{x - 6},{y + 18} L{x - 6},{y - 26}" class="stroke" fill="none"/>'
                  f'<path d="M{x - 6},{y - 26} L{x + 22},{y - 16} L{x - 6},{y - 6} Z" class="stroke stflag"/></g>'
                  f'<rect x="{x - 14}" y="{y - 30}" width="40" height="52" fill="transparent"/>'
                  + stext(x, y + 42, f"Module {key}", 14, "hand note", "middle") + stext(x, y + 58, "test", 14, "hand note", "middle")
                  + f'<text x="{x}" y="{y + 74}" class="mono note stprog" font-size="11" text-anchor="middle"></text></a>')
    for k, (num, lab) in enumerate(later):
        x, y = 80 + k * 120, 520
        s += (f'<g class="stlater"><g filter="url(#rough)"><circle cx="{x}" cy="{y}" r="17" class="stroke" fill="#FFFFFF" stroke-dasharray="5 4"/></g>'
              + stext(x, y + 5, num, 14, "mono note", "middle"))
        for i, ln in enumerate(lab):
            s += stext(x, y + 40 + i * 16, ln, 14, "hand note", "middle")
        s += '</g>'
    s += ('<g id="pin" class="pin" hidden><path d="M0,-34 C-13,-34 -13,-16 0,-4 C13,-16 13,-34 0,-34 Z" class="pinbody"/>'
          '<circle cx="0" cy="-25" r="4" fill="#FFFFFF"/>'
          '<text x="16" y="-28" class="hand pintext" font-size="14">You are here</text></g>')
    return figure(900, 580, s, "Your road through the book. Click any stop to open it. Stops turn green as you tick off rules and pass tests.", 620)


def build():
    by_num = {t[0]: t for t in TOPICS}
    for num_, slug_, title_, goal_, body_ in TOPICS:
        label_rules(num_, title_, body_)
    short = {"2": "Running code, errors", "3": "print and modules", "4": "Variables, operators"}

    pages = [("cover", "Cover")]
    for mnum, mname, mgoal, chs, n in MODULES:
        pages.append((f"m{mnum}", f"Module {mnum}: {mname}"))
        for c in chs:
            pages.append(("t-" + by_num[c][1], f"Chapter {c}: {by_num[c][2]}"))
            if QUIZ.get(c):
                pages.append((f"q-c{c}", f"Chapter {c} quiz"))
        pages.append((f"q-m{mnum}", f"Module {mnum} test"))
    pages.append(("cheat", "Part 1 cheat sheet"))
    pages.append(("revise", "Part 1 revision sheet"))
    total = len(pages)
    index = {pid: k for k, (pid, _) in enumerate(pages)}

    def pager(pid):
        k = index[pid]
        prev = f'<a class="prev" href="#{pages[k - 1][0]}"><span>Previous</span>{pages[k - 1][1]}</a>' if k > 0 else '<span></span>'
        nxt = (f'<a class="nextp" href="#{pages[k + 1][0]}"><span>Next</span>{pages[k + 1][1]}</a>' if k + 1 < total
               else '<a class="nextp" href="#cover"><span>Back to</span>Cover</a>')
        return f'<nav class="pager" aria-label="Pages">{prev}<span class="pno"></span>{nxt}</nav>'

    # ---- rail
    rail = ['<button type="button" class="railopen" aria-label="Show the menu" hidden>☰ Menu</button>'
            '<nav class="rail" id="rail" aria-label="Modules and chapters"><div class="brandrow"><a class="brand" href="#cover">' + py_logo('brand') + 'Python From Zero</a>'
            '<button type="button" class="railhide" aria-label="Hide the menu" title="Hide the menu">«</button></div>']
    for mnum, mname, mgoal, chs, n in MODULES:
        rail.append(f'<div class="mod" data-mod="{mnum}"><h4><a href="#m{mnum}"><span>Module {mnum} · {mname}</span><span class="modprog"></span></a>'
                    f'<button type="button" class="chev" aria-expanded="false" aria-label="Show or hide Module {mnum}"></button></h4><ol>')
        for c in chs:
            rail.append(f'<li><a href="#t-{by_num[c][1]}" data-ch="{c}"><span class="n">{c}</span><span>{short.get(c, by_num[c][2])}</span><span class="prog"></span></a></li>')
        rail.append('<li class="qlabel">Quizzes</li>')
        for c in chs:
            if QUIZ.get(c):
                rail.append(f'<li class="sub"><a href="#q-c{c}"><span class="n">{c}</span><span>Chapter {c} quiz</span><span class="prog" data-best="c{c}"></span></a></li>')
        rail.append(f'<li class="sub test"><a href="#q-m{mnum}"><span class="n">★</span><span>Module {mnum} test</span><span class="prog" data-best="m{mnum}"></span></a></li>')
        rail.append('</ol></div>')
    rail.append('<ol class="cheatlink"><li><a href="#cheat"><span class="n">≡</span><span>Part 1 cheat sheet</span><span class="prog"></span></a></li>'
                '<li><a href="#revise"><span class="n">✎</span><span>Part 1 revision sheet</span><span class="prog"></span></a></li></ol>')
    rail.append('<div class="soonlist"><h4>Next part</h4><ol>')
    for num, title in COMING:
        rail.append(f'<li class="soon"><span class="n">{num}</span><span>{title}</span></li>')
    rail.append('</ol></div></nav>')

    page_no = [1]
    n_quiz = 0
    sections, quiz_secs = [], []
    for mnum, mname, mgoal, chs, n in MODULES:
        rows = "".join(f'<li><a href="#t-{by_num[c][1]}"><span class="rn">{c}</span><span>{by_num[c][2]}</span>'
                       f'<span class="prog" data-ch="{c}"></span></a></li>' for c in chs)
        intro = (f'<div class="topic-head"><div class="chapno">Module {mnum}</div><h2>{mname}</h2><p class="goal">{mgoal}</p>'
                 f'<ol class="toc">{rows}<li><a href="#q-m{mnum}"><span class="rn">✓</span><span>Module {mnum} test: {n} mixed questions</span>'
                 f'<span class="prog" data-best="m{mnum}"></span></a></li></ol></div>'
                 f'<p class="hint">Work through each chapter: read a rule, press <b>Run</b> on its examples, break them, then mark the rule done. '
                 f'Each chapter ends with a link to its quiz. The module test mixes questions from all its chapters.</p>{pager(f"m{mnum}")}')
        sections.append(f'<section class="page module" id="m{mnum}">{single_sheet(intro, f"Module {mnum} · {mname}", page_no)}</section>')
        pool = []
        for c in chs:
            num, slug, title, goal, body = by_num[c]
            CURRENT_CH[0] = num
            body = relabel(body)
            toc = grouped_toc(num)
            cq = quiz_pool(num)
            n_quiz += len(cq)
            pool += cq + auto_pool(num)
            head = (f'<div class="topic-head"><div class="chapno">Chapter {num}</div><h2>{title}</h2><p class="goal">{goal}</p>{toc}</div>')
            qlink = (f'<a class="quizlink" href="#q-c{num}"><span>Chapter {num} quiz</span><span>{len(cq)} questions, one at a time</span><span class="prog" data-best="c{num}"></span></a>') if cq else ""
            sections.append(f'<section class="topic page" id="t-{slug}">'
                            + paginate(head, (body.replace('<section class="exercises"', takeaways(num) + '<section class="exercises"', 1)
                                              if '<section class="exercises"' in body else body + takeaways(num)) + breakit_section(num),
                                       qlink + pager("t-" + slug), f"Chapter {num} · {title}", page_no)
                            + '</section>')
            if cq:
                qhtml = (f'<div class="topic-head"><div class="chapno">Chapter {num} quiz</div><h2>{title}</h2>'
                         f'<p class="goal">{len(cq)} questions on this chapter. <a href="#t-{slug}">Open the chapter</a></p></div>'
                         + quiz_section(f"c{num}", "Quiz", cq, len(cq), f"One at a time. Every answer was checked by running the code in Python {PYVER}.")
                         + pager(f"q-c{num}"))
                sections.append(f'<section class="page quizpage" id="q-c{num}">{single_sheet(qhtml, f"Chapter {num} quiz", page_no)}</section>')
        n = min(n, len(pool))
        mhtml = (f'<div class="topic-head"><div class="chapno">Module {mnum} test</div><h2>{mname}</h2>'
                 f'<p class="goal">{n} questions picked at random from {len(pool)}, mixing every chapter in this module. A new mix each time.</p></div>'
                 + quiz_section(f"m{mnum}", "Module test", quiz_pool_dedupe(pool), n, "Get one wrong and you can retry just the ones you missed at the end.")
                 + pager(f"q-m{mnum}"))
        sections.append(f'<section class="page quizpage" id="q-m{mnum}">{single_sheet(mhtml, f"Module {mnum} test", page_no)}</section>')

    chtml = ('<div class="topic-head"><div class="chapno">Cheat sheet</div><h2>Part 1 at a glance</h2>'
             '<p class="goal">The most-used code from chapters 0 to 7 on one page. Every result on the right was produced by running the code on the left.</p></div>'
             + cheat_sheet() + pager("cheat"))
    sections.append(f'<section class="page cheatpage" id="cheat">{single_sheet(chtml, "Part 1 cheat sheet", page_no)}</section>')
    n_rev = sum(len(x[1]) for x in REVISION)
    rhtml = ('<div class="topic-head"><div class="chapno">Revision sheet</div><h2>Every Part 1 topic in one place</h2>'
             f'<p class="goal">{n_rev} topics from chapters 0 to 7. Each has a plain definition and one small example; every output shown was produced by running it.</p></div>'
             + revision_sheet(by_num) + pager("revise"))
    sections.append(f'<section class="page revisepage" id="revise">{single_sheet(rhtml, "Part 1 revision sheet", page_no)}</section>')

    n_rules = sum(len(v) for v in RULE_INDEX.values())
    n_runbox = "".join(sections).count('class="runbox"')
    sample = (f'<div class="sample"><h3>What every rule looks like</h3><p class="hint">A rule, then code that works, code that breaks with the real error, and why. Press Run on either.</p>'
              f'<div class="sample-rule"><h3><span class="rnum">Rule 3.2</span>Text goes inside quotes</h3>'
              f'<div class="case good"><div class="case-h"><span class="mark">&#10003;</span> Works</div>{works(chr(112) + "rint(" + chr(34) + "Hi" + chr(34) + ")")}</div>'
              f'<div class="case bad"><div class="case-h"><span class="mark">&#10007;</span> Breaks</div>{breaks("print(Hi)", "NameError")}</div>'
              f'<p class="why"><b>Why:</b> Without quotes, <code>Hi</code> is read as a name that does not exist.</p></div></div>')
    outcomes = table(["Module", "After it you can"], [
        [f'<a href="#m{m[0]}">{m[0]}. {m[1]}</a>', txt] for m, txt in zip(MODULES, [
            "explain what a program is, how Python runs a file, and read any error message",
            "print, comment, import modules, store values in names and do maths",
            "slice, search, clean, split and join text with every string method",
            "keep many values in lists, tuples, dictionaries and sets, and avoid the copy trap"])])
    tryit = runbox(code_html('name = "Ravi"\nprint("Hello,", name)\nprint("Your name has", len(name), "letters")')).replace('class="runbox"', 'class="runbox" data-autoedit="1"')
    hero = f'''<section class="page cover" id="cover"><div class="sheet">
<header class="hero">
<h1>Python From Zero</h1>
<p class="lead">A hands-on book that starts at "what is programming". Every rule shows code that works, code that breaks, and the exact error Python prints. You run it, break it and get quizzed on it, right on the page.</p>
<div class="hero-actions"><a class="btn primary" href="#m1">Start Module 1</a><a class="btn" id="continue" href="#m1" hidden>Continue</a><span class="prog-all"></span></div>
</header>
<h3 class="roadmap-h">Your roadmap</h3>
{d_roadmap(by_num)}

{outcomes}
<details class="about"><summary>About this book</summary>
<p>{len(MODULES)} modules, 8 chapters, {n_rules} rules, {EX_COUNT[0]} exercises and {n_quiz} chapter quiz questions. Every output was produced by running the code in Python {PYVER} on {TODAY}.</p>
<p>The Run button uses Python 3.14 inside your browser (Pyodide). The first run downloads it, about 10 MB. Tested on all {n_runbox} examples: the browser matched the book on all but 4, where only a memory address, a system error number, a folder path or one extra hint differs.</p>
<p>Your ticks and quiz scores are saved in this browser only. <button type="button" class="btn reset-progress">Reset my progress</button></p>
</details>
{pager("cover")}</div></section>'''

    nxt = '<section class="next"><h3>Next part: chapters 8 to 14</h3><p>if / elif / else, loops, functions, handling errors, files, classes, and a mini project. Same format.</p></section>'

    wm = "data:image/svg+xml;base64," + base64.b64encode(
        ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0.21 -0.077 110 110"><g opacity="0.07">' + PY_LOGO_INNER.replace("SVGID_", "wm_") + '</g></svg>').encode()).decode()

    favicon = "data:image/svg+xml;base64," + base64.b64encode(py_logo("fav").replace('<svg ', '<svg width="64" height="64" ', 1).encode()).decode()
    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Python From Zero</title>
<link rel="icon" type="image/svg+xml" href="{favicon}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&family=Kalam:wght@400&display=swap">
<style>{CSS}{CSS_INTERACTIVE}
.sheet {{ background-image: url("{wm}"); }}</style>
</head>
<body>
{DEFS}
<div class="shell">
{"".join(rail)}
<main><div class="col">{hero}{"".join(sections)}</div></main>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-clike.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-java.min.js"></script>
<script>{JS}</script>
<script>var PYODIDE_URL = "{PYODIDE}";</script>
<script>{JS_INTERACTIVE}</script>
</body>
</html>
'''
    OUT.write_text(page)
    print(f"wrote {OUT}  rules={n_rules} exercises={EX_COUNT[0]} quiz={n_quiz} pages={page_no[0] - 1} bytes={len(page)}")


def quiz_pool_dedupe(pool):
    seen, out = set(), []
    for q in pool:
        k = (q["type"], q.get("code"), q.get("q"))
        if k not in seen:
            seen.add(k)
            out.append(q)
    return out

build()
