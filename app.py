import streamlit as st
import re
import os
import io

# ── paste your full converter here ──────────────────────────────────────────

def convert_comments(code):
    result = []
    i = 0
    while i < len(code):
        if code[i:i+2] == '/*':
            end = code.find('*/', i+2)
            comment_body = code[i+2:end] if end != -1 else code[i+2:]
            i = end + 2 if end != -1 else len(code)
            lines = comment_body.split('\n')
            result.append("'''" + '\n'.join(lines) + "'''")
        elif code[i:i+2] == '//':
            end = code.find('\n', i+2)
            if end == -1:
                result.append('#' + code[i+2:])
                i = len(code)
            else:
                result.append('#' + code[i+2:end])
                i = end
        else:
            result.append(code[i])
            i += 1
    return ''.join(result)

def convert_condition(cond):
    cond = cond.replace('&&', 'and').replace('||', 'or')
    cond = re.sub(r'(?<![=!<>])!(?!=)', 'not ', cond)
    return cond.strip()

def convert_printf(line):
    m = re.search(r'printf\s*\(\s*"(.*)"\s*(,\s*(.*))?\s*\)', line)
    if not m:
        return line
    fmt = m.group(1).replace('\\n', '').replace('\\t', '    ')
    args = m.group(3)
    if args:
        fmt = re.sub(r'%[difsco]', '{}', fmt)
        return 'print("{}".format({}))'.format(fmt, ', '.join(a.strip() for a in args.split(',')))
    return 'print("{}")'.format(fmt)

def convert_scanf(line):
    m = re.search(r'scanf\s*\(\s*"(.*)"\s*,\s*(.*)\s*\)', line)
    if not m:
        return line
    fmt = m.group(1)
    vars_list = [v.strip().replace('&', '') for v in m.group(2).strip().split(',')]
    specifiers = re.findall(r'%[a-zA-Z]+', fmt)
    result_lines = []
    for idx, var in enumerate(vars_list):
        spec = specifiers[idx] if idx < len(specifiers) else '%s'
        if '%d' in spec or '%i' in spec:
            result_lines.append('{} = int(input())'.format(var))
        elif '%f' in spec or '%lf' in spec:
            result_lines.append('{} = float(input())'.format(var))
        else:
            result_lines.append('{} = input()'.format(var))
    return '\n'.join(result_lines)

def strip_type(s):
    return re.sub(r'^(int|float|double|char|bool|long|short|void)\s+\*?', '', s).strip()

DEFAULTS = {'int':'0','long':'0','short':'0','float':'0.0','double':'0.0','char':"''",'bool':'False'}
INT_TYPES = {'int','long','short'}

def smart_divide(expr, known_int_vars=None):
    if known_int_vars is None:
        known_int_vars = set()
    def is_int_expr(e):
        e = e.strip()
        if re.match(r'^\d+$', e): return True
        if e in known_int_vars: return True
        return False
    tokens = re.split(r'(/)', expr)
    result = []
    for j, tok in enumerate(tokens):
        if tok == '/' and j > 0 and j < len(tokens)-1:
            lhs_token = re.split(r'[\s\+\-\*\(]', ''.join(result))[-1].strip()
            rhs_token = re.split(r'[\s\+\-\*\)]', tokens[j+1])[0].strip()
            result.append('//' if is_int_expr(lhs_token) and is_int_expr(rhs_token) else '/')
        else:
            result.append(tok)
    return ''.join(result)

def handle_define(line):
    m = re.match(r'#define\s+(\w+)\s+(.*)', line.strip())
    if m:
        val = m.group(2).strip().replace('true','True').replace('false','False')
        return '{} = {}'.format(m.group(1), val)
    return None

def convert(c_code):
    c_code = convert_comments(c_code)
    c_code = c_code.replace('{', '\n{\n').replace('}', '\n}\n')
    lines = c_code.splitlines()
    out, indent, known_int_vars, block_labels = [], 0, set(), []
    i = 0
    while i < len(lines):
        line = lines[i].strip(); i += 1
        if not line: continue
        if line.startswith('#define'):
            r = handle_define(line)
            if r: out.append(r)
            continue
        if line.startswith('#'): continue
        if line == '{':
            if out and out[-1].rstrip().endswith(':'):
                indent += 1
                last = out[-1].strip()
                if last.startswith('def '): block_labels.append('def ' + last.split('(')[0][4:])
                elif last.startswith('if '): block_labels.append('if')
                elif last.startswith('elif '): block_labels.append('elif')
                elif last.startswith('else'): block_labels.append('else')
                elif last.startswith('while '): block_labels.append('while')
                elif last.startswith('for '): block_labels.append('for')
                else: block_labels.append('block')
            else:
                block_labels.append('block')
            continue
        if line == '}':
            label = block_labels.pop() if block_labels else 'block'
            indent = max(0, indent-1)
            out.append('{}# end {}'.format('    '*indent, label))
            continue
        pad = '    '*indent
        if line.startswith('#') and not line.startswith('#define'):
            out.append(pad+line); continue
        if line.startswith("'''"):
            out.append(pad+line); continue
        func_m = re.match(r'^(int|float|void|double|char|bool)\s+(\w+)\s*\((.*?)\)\s*$', line)
        if func_m:
            name = func_m.group(2)
            raw = func_m.group(3).strip()
            params = '' if raw in ('','void') else ', '.join(strip_type(p) for p in raw.split(','))
            if out: out.append('')
            out.append('def {}({}):'.format(name, params))
            indent=0; block_labels=[]; continue
        if re.match(r'^else\s+if\s*\(', line):
            cond = re.search(r'else\s+if\s*\((.*?)\)', line).group(1)
            out.append('{}elif {}:'.format(pad, convert_condition(cond))); continue
        if re.match(r'^else\s*$', line):
            out.append('{}else:'.format(pad)); continue
        if re.match(r'^if\s*\(', line):
            cond = re.search(r'if\s*\((.*?)\)', line).group(1)
            out.append('{}if {}:'.format(pad, convert_condition(cond))); continue
        if re.match(r'^while\s*\(', line):
            cond = re.search(r'while\s*\((.*?)\)', line).group(1)
            out.append('{}while {}:'.format(pad, convert_condition(cond))); continue
        if line == 'do':
            out.append('{}while True:'.format(pad)); continue
        if re.match(r'^for\s*\(', line):
            m = re.search(r'for\s*\(\s*(.*?);\s*(.*?);\s*(.*?)\s*\)', line)
            if m:
                init = strip_type(m.group(1).strip())
                cond = convert_condition(m.group(2).strip())
                upd = re.sub(r'(\w+)\+\+', r'\1 += 1', m.group(3).strip())
                upd = re.sub(r'(\w+)--', r'\1 -= 1', upd)
                if init: out.append('{}{}'.format(pad, init))
                out.append('{}while {}:'.format(pad, cond))
                j = i
                while j < len(lines) and lines[j].strip() == '': j += 1
                if j < len(lines) and lines[j].strip() == '{':
                    i = j+1; indent += 1; block_labels.append('for')
                    out.append('{}# update: {}'.format('    '*indent, upd))
            continue
        if re.match(r'^return\b', line):
            expr = line[6:].rstrip(';').strip()
            out.append('{}return{}'.format(pad, ' '+expr if expr else '')); continue
        if line.rstrip(';') == 'break':
            out.append('{}break'.format(pad)); continue
        if line.rstrip(';') == 'continue':
            out.append('{}continue'.format(pad)); continue
        if re.match(r'printf\s*\(', line):
            out.append(pad+convert_printf(line)); continue
        if re.match(r'scanf\s*\(', line):
            for cl in convert_scanf(line).split('\n'): out.append(pad+cl)
            continue
        single_m = re.match(r'^(int|float|double|char|bool|long|short)\s+(\w+)\s*(?:=\s*(.+?))?;$', line)
        if single_m:
            vtype, vname = single_m.group(1), single_m.group(2)
            val = single_m.group(3)
            if vtype in INT_TYPES: known_int_vars.add(vname)
            val = DEFAULTS.get(vtype,'0') if val is None else val.strip().replace('true','True').replace('false','False')
            out.append('{}{} = {}'.format(pad, vname, val)); continue
        multi_m = re.match(r'^(int|float|double|char|bool)\s+([\w\s,=.]+);$', line)
        if multi_m:
            vtype = multi_m.group(1); default = DEFAULTS.get(vtype,'0')
            for v in multi_m.group(2).split(','):
                v = v.strip()
                if not v: continue
                if vtype in INT_TYPES: known_int_vars.add(v.split('=')[0].strip())
                if '=' in v:
                    n_, v_ = v.split('=',1)
                    out.append('{}{} = {}'.format(pad, n_.strip(), v_.strip()))
                else:
                    out.append('{}{} = {}'.format(pad, v, default))
            continue
        arr_m = re.match(r'^(int|float|double)\s+(\w+)\[(\w+)\](?:\[(\w+)\])?\s*;$', line)
        if arr_m:
            vtype, vname, dim1, dim2 = arr_m.group(1), arr_m.group(2), arr_m.group(3), arr_m.group(4)
            default = DEFAULTS.get(vtype,'0')
            if vtype in INT_TYPES: known_int_vars.add(vname)
            if dim2:
                out.append('{}{} = [[{} for _ in range({})] for _ in range({})]'.format(pad,vname,default,dim2,dim1))
            else:
                out.append('{}{} = [{} for _ in range({})]'.format(pad,vname,default,dim1))
            continue
        expr = line.rstrip(';')
        if re.match(r'^\w+\+\+$', expr):
            out.append('{}{} += 1'.format(pad, expr[:-2])); continue
        if re.match(r'^\w+--$', expr):
            out.append('{}{} -= 1'.format(pad, expr[:-2])); continue
        if expr:
            expr = expr.replace('true','True').replace('false','False')
            expr = smart_divide(expr, known_int_vars)
            out.append('{}{}'.format(pad, convert_condition(expr)))
    out.append('\n\nmain()')
    return '\n'.join(out)

# ── Streamlit UI ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="C → Python Converter",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Syne:wght@400;600;700;800&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #080c10;
    color: #e8eaf0;
}

.stApp {
    background: #080c10;
}

/* ── Hide Streamlit chrome ── */
footer { visibility: hidden; }
#MainMenu { visibility: visible; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1400px; }

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 3.5rem 0 2.5rem;
    position: relative;
}
.hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, #00ffe0 0%, #0090ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    margin-bottom: 1rem;
    font-family: 'JetBrains Mono', monospace;
}
.hero-title {
    font-size: clamp(2.4rem, 5vw, 3.8rem);
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.05;
    color: #f0f4ff;
    margin: 0 0 1rem;
}
.hero-title span {
    background: linear-gradient(135deg, #00ffe0 0%, #0090ff 60%, #a855f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    color: #6b7a99;
    font-size: 1rem;
    font-weight: 400;
    letter-spacing: 0.01em;
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.6;
}
.hero-rule {
    width: 60px;
    height: 2px;
    background: linear-gradient(90deg, #00ffe0, #0090ff);
    margin: 2rem auto 0;
    border: none;
}

/* ── Panel cards ── */
.panel-card {
    background: #0d1420;
    border: 1px solid #1a2236;
    border-radius: 20px;
    padding: 1.5rem;
    box-shadow: 0 24px 80px rgba(0,0,0,0.18);
    margin-bottom: 1.5rem;
}
.panel-card:hover {
    border-color: #00ffe0;
}
.sidebar-card {
    background: #0d1420;
    border: 1px solid #1a2236;
    border-radius: 18px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 18px 50px rgba(0,0,0,0.16);
}
.sidebar-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    color: #f0f4ff;
    margin-bottom: 0.75rem;
}
.sidebar-text {
    color: #9bb2d1;
    font-size: 0.95rem;
    line-height: 1.75;
}
.sidebar-text strong {
    color: #00ffe0;
}

.panel-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #3d4d6b;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.panel-label::before {
    content: '';
    display: inline-block;
    width: 18px;
    height: 1px;
    background: #3d4d6b;
}

/* ── Textareas ── */
.stTextArea textarea {
    background: #0d1420 !important;
    border: 1px solid #1a2236 !important;
    border-radius: 12px !important;
    color: #c8d8f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
    line-height: 1.7 !important;
    padding: 1.25rem !important;
    resize: vertical !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
.stTextArea textarea:focus {
    border-color: #00ffe0 !important;
    box-shadow: 0 0 0 2px rgba(0,255,224,0.08), 0 4px 24px rgba(0,255,224,0.04) !important;
    outline: none !important;
}
.stTextArea label { display: none !important; }

/* ── File uploader ── */
.stFileUploader {
    background: #0d1420 !important;
    border: 1px dashed #1e2d45 !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    transition: border-color 0.2s;
}
.stFileUploader:hover {
    border-color: #00ffe0 !important;
}
[data-testid="stFileUploader"] label { display: none !important; }
[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
    border: none !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] p {
    color: #3d5070 !important;
    font-size: 0.82rem !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] span {
    color: #00ffe0 !important;
}

/* ── Convert button ── */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #00ffe0 0%, #0090ff 100%) !important;
    color: #050810 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.04em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 2.5rem !important;
    cursor: pointer !important;
    width: 100% !important;
    transition: opacity 0.2s, transform 0.15s !important;
    box-shadow: 0 4px 24px rgba(0,255,224,0.18) !important;
}
div[data-testid="stButton"] > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 32px rgba(0,255,224,0.28) !important;
}
div[data-testid="stButton"] > button:active {
    transform: translateY(0) !important;
}

/* ── Download button ── */
div[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    color: #00ffe0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 500 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.06em !important;
    border: 1px solid #00ffe0 !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.5rem !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    background: rgba(0,255,224,0.06) !important;
    box-shadow: 0 0 20px rgba(0,255,224,0.12) !important;
}

/* ── Stats strip ── */
.stats-strip {
    display: flex;
    gap: 1px;
    background: #131b2a;
    border-radius: 12px;
    overflow: hidden;
    margin: 2rem 0;
    border: 1px solid #1a2236;
}
.stat-cell {
    flex: 1;
    padding: 1.1rem 1rem;
    background: #0d1420;
    text-align: center;
}
.stat-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #00ffe0, #0090ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stat-key {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #3d4d6b;
    margin-top: 0.25rem;
}

/* ── Success / error banners ── */
.banner {
    border-radius: 10px;
    padding: 0.85rem 1.25rem;
    margin: 1rem 0;
    font-size: 0.82rem;
    font-family: 'JetBrains Mono', monospace;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.banner-ok {
    background: rgba(0,255,224,0.06);
    border: 1px solid rgba(0,255,224,0.2);
    color: #00ffe0;
}
.banner-err {
    background: rgba(255,60,60,0.06);
    border: 1px solid rgba(255,60,60,0.2);
    color: #ff6060;
}

/* ── Column divider ── */
.col-divider {
    display: flex;
    justify-content: center;
    align-items: center;
    padding-top: 3.5rem;
    color: #1e2d45;
    font-size: 1.4rem;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #0d1420; }
::-webkit-scrollbar-thumb { background: #1e2d45; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #00ffe0; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-badge">⚡ Transpiler v2.0</div>
  <h1 class="hero-title">C <span>→</span> Python</h1>
  <p class="hero-sub">Paste your C source or upload a <code>.c</code> file and get clean, idiomatic Python in one click.</p>
  <hr class="hero-rule"/>
</div>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "c_code" not in st.session_state:
    st.session_state.c_code = ""
if "py_code" not in st.session_state:
    st.session_state.py_code = ""
if "converted" not in st.session_state:
    st.session_state.converted = False

# ── Sidebar help ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">How to use</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-text">Paste C code in the editor, upload a <code>.c</code> file, then click <strong>Convert</strong>. The app converts common C patterns into readable Python and preserves comments.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">Quick features</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-text"><ul style="margin:0; padding-left:1.2rem; color:#9bb2d1;"><li>Structured loops & conditionals</li><li>printf/scanf conversion</li><li>Array initialization support</li><li>Live preview + download output</li></ul></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Upload ────────────────────────────────────────────────────────────────────
up_col, _, _ = st.columns([2, 1, 1])
with up_col:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-label">Upload .c file (optional)</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("upload", type=["c"], label_visibility="collapsed")
    if uploaded:
        content = uploaded.read().decode("utf-8", errors="replace")
        st.session_state.c_code = content
    st.markdown('</div>', unsafe_allow_html=True)

# ── Main columns ──────────────────────────────────────────────────────────────
left, mid, right = st.columns([5, 0.3, 5])

with left:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-label">C Source Code</div>', unsafe_allow_html=True)
    c_input = st.text_area(
        "c_input",
        value=st.session_state.c_code,
        height=520,
        placeholder="// Paste your C code here…\n#include <stdio.h>\n\nint main() {\n    printf(\"Hello, World!\\n\");\n    return 0;\n}",
        label_visibility="collapsed",
    )
    st.session_state.c_code = c_input
    st.markdown('</div>', unsafe_allow_html=True)

with mid:
    st.markdown('<div class="col-divider">⟶</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-label">Python Output</div>', unsafe_allow_html=True)
    output_placeholder = st.empty()

    if st.session_state.converted and st.session_state.py_code:
        output_placeholder.text_area(
            "py_output",
            value=st.session_state.py_code,
            height=520,
            label_visibility="collapsed",
        )
    else:
        output_placeholder.text_area(
            "py_output",
            value="",
            height=520,
            placeholder="# Converted Python will appear here…",
            label_visibility="collapsed",
        )
    st.markdown('</div>', unsafe_allow_html=True)

# ── Convert button ────────────────────────────────────────────────────────────
_, btn_col, _ = st.columns([3, 2, 3])
with btn_col:
    convert_clicked = st.button("⚡  Convert")

if convert_clicked:
    code = st.session_state.c_code.strip()
    if not code:
        st.markdown('<div class="banner banner-err">✕  No C code found — paste something or upload a file.</div>', unsafe_allow_html=True)
    else:
        try:
            result = convert(code)
            st.session_state.py_code = result
            st.session_state.converted = True
            output_placeholder.text_area(
                "py_output",
                value=result,
                height=520,
                label_visibility="collapsed",
            )
        except Exception as e:
            st.markdown(f'<div class="banner banner-err">✕  Conversion error: {e}</div>', unsafe_allow_html=True)
            st.session_state.converted = False

# ── Stats + download ──────────────────────────────────────────────────────────
if st.session_state.converted and st.session_state.py_code:
    c_lines  = len([l for l in st.session_state.c_code.splitlines() if l.strip()])
    py_lines = len([l for l in st.session_state.py_code.splitlines() if l.strip()])
    ratio    = round(py_lines / c_lines * 100) if c_lines else 0

    st.markdown(f"""
    <div class="stats-strip">
      <div class="stat-cell">
        <div class="stat-val">{c_lines}</div>
        <div class="stat-key">C lines</div>
      </div>
      <div class="stat-cell">
        <div class="stat-val">{py_lines}</div>
        <div class="stat-key">Python lines</div>
      </div>
      <div class="stat-cell">
        <div class="stat-val">{ratio}%</div>
        <div class="stat-key">Line ratio</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="banner banner-ok">✓  Conversion successful — ready to download.</div>', unsafe_allow_html=True)

    _, dl_col, _ = st.columns([3, 2, 3])
    with dl_col:
        st.download_button(
            label="↓  Download  output.py",
            data=st.session_state.py_code.encode("utf-8"),
            file_name="output.py",
            mime="text/x-python",
        )