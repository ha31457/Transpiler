import re
import sys
import os

def convert_comments(code):
    result = []
    i = 0
    while i < len(code):
        if code[i:i+2] == '/*':
            end = code.find('*/', i+2)
            if end == -1:
                comment_body = code[i+2:]
                i = len(code)
            else:
                comment_body = code[i+2:end]
                i = end + 2
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
    vars_part = m.group(2).strip()
    vars_list = [v.strip().replace('&', '') for v in vars_part.split(',')]
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

DEFAULTS = {
    'int': '0', 'long': '0', 'short': '0',
    'float': '0.0', 'double': '0.0',
    'char': "''", 'bool': 'False'
}

INT_TYPES = {'int', 'long', 'short'}

def smart_divide(expr, known_int_vars=None):
    """Replace / with // if both sides are integer expressions."""
    if known_int_vars is None:
        known_int_vars = set()

    def is_int_expr(e):
        e = e.strip()
        if re.match(r'^\d+$', e):
            return True
        if e in known_int_vars:
            return True
        if re.match(r'^\w+$', e):
            return False
        return False

    tokens = re.split(r'(/)', expr)
    result = []
    j = 0
    while j < len(tokens):
        if tokens[j] == '/' and j > 0 and j < len(tokens) - 1:
            lhs = result[-1].strip() if result else ''
            rhs = tokens[j + 1].strip()
            # extract rightmost token of lhs
            lhs_token = re.split(r'[\s\+\-\*\(]', lhs)[-1].strip()
            rhs_token = re.split(r'[\s\+\-\*\)]', rhs)[0].strip()
            if is_int_expr(lhs_token) and is_int_expr(rhs_token):
                result.append('//')
            else:
                result.append('/')
        else:
            result.append(tokens[j])
        j += 1
    return ''.join(result)

def handle_define(line):
    m = re.match(r'#define\s+(\w+)\s+(.*)', line.strip())
    if m:
        name = m.group(1)
        val = m.group(2).strip()
        val = val.replace('true', 'True').replace('false', 'False')
        return '{} = {}'.format(name, val)
    return None

def convert(c_code):
    c_code = convert_comments(c_code)

    c_code = c_code.replace('{', '\n{\n').replace('}', '\n}\n')
    lines = c_code.splitlines()

    out = []
    indent = 0
    known_int_vars = set()
    block_labels = []  # stack to track what block we opened

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1

        if not line:
            continue

        # Handle #define
        if line.startswith('#define'):
            result = handle_define(line)
            if result:
                out.append(result)
            continue

        # Skip other preprocessor directives
        if line.startswith('#'):
            continue

        if line == '{':
            if out and out[-1].rstrip().endswith(':'):
                indent += 1
                # label from last out line
                last = out[-1].strip()
                if last.startswith('def '):
                    block_labels.append('def ' + last.split('(')[0][4:])
                elif last.startswith('if '):
                    block_labels.append('if')
                elif last.startswith('elif '):
                    block_labels.append('elif')
                elif last.startswith('else'):
                    block_labels.append('else')
                elif last.startswith('while '):
                    block_labels.append('while')
                elif last.startswith('for '):
                    block_labels.append('for')
                else:
                    block_labels.append('block')
            else:
                block_labels.append('block')
            continue

        if line == '}':
            label = block_labels.pop() if block_labels else 'block'
            indent = max(0, indent - 1)
            pad = '    ' * indent
            out.append('{}# end {}'.format(pad, label))
            continue

        pad = '    ' * indent

        # Inline comment lines (already converted to # by convert_comments)
        if line.startswith('#') and not line.startswith('#define'):
            out.append(pad + line)
            continue

        # Multiline string comments (''')
        if line.startswith("'''"):
            out.append(pad + line)
            continue

        func_m = re.match(
            r'^(int|float|void|double|char|bool)\s+(\w+)\s*\((.*?)\)\s*$', line)
        if func_m:
            name = func_m.group(2)
            raw = func_m.group(3).strip()
            params = '' if raw in ('', 'void') \
                else ', '.join(strip_type(p) for p in raw.split(','))
            if out:
                out.append('')
            out.append('def {}({}):'.format(name, params))
            indent = 0
            block_labels = []
            continue

        if re.match(r'^else\s+if\s*\(', line):
            cond = re.search(r'else\s+if\s*\((.*?)\)', line).group(1)
            out.append('{}elif {}:'.format(pad, convert_condition(cond)))
            continue

        if re.match(r'^else\s*$', line):
            out.append('{}else:'.format(pad))
            continue

        if re.match(r'^if\s*\(', line):
            cond = re.search(r'if\s*\((.*?)\)', line).group(1)
            out.append('{}if {}:'.format(pad, convert_condition(cond)))
            continue

        if re.match(r'^while\s*\(', line):
            cond = re.search(r'while\s*\((.*?)\)', line).group(1)
            out.append('{}while {}:'.format(pad, convert_condition(cond)))
            continue

        if line == 'do':
            out.append('{}while True:'.format(pad))
            continue

        if re.match(r'^for\s*\(', line):
            m = re.search(r'for\s*\(\s*(.*?);\s*(.*?);\s*(.*?)\s*\)', line)
            if m:
                init = strip_type(m.group(1).strip())
                cond = convert_condition(m.group(2).strip())
                upd = re.sub(r'(\w+)\+\+', r'\1 += 1', m.group(3).strip())
                upd = re.sub(r'(\w+)--', r'\1 -= 1', upd)
                if init:
                    out.append('{}{}'.format(pad, init))
                out.append('{}while {}:'.format(pad, cond))
                j = i
                while j < len(lines) and lines[j].strip() == '':
                    j += 1
                if j < len(lines) and lines[j].strip() == '{':
                    i = j + 1
                    indent += 1
                    block_labels.append('for')
                    out.append('{}# update: {}'.format('    ' * indent, upd))
            continue

        if re.match(r'^return\b', line):
            expr = line[6:].rstrip(';').strip()
            out.append('{}return{}'.format(pad, ' ' + expr if expr else ''))
            continue

        if line.rstrip(';') == 'break':
            out.append('{}break'.format(pad))
            continue

        if line.rstrip(';') == 'continue':
            out.append('{}continue'.format(pad))
            continue

        if re.match(r'printf\s*\(', line):
            out.append(pad + convert_printf(line))
            continue

        if re.match(r'scanf\s*\(', line):
            converted = convert_scanf(line)
            for cl in converted.split('\n'):
                out.append(pad + cl)
            continue

        single_m = re.match(
            r'^(int|float|double|char|bool|long|short)\s+(\w+)\s*(?:=\s*(.+?))?;$', line)
        if single_m:
            vtype, vname = single_m.group(1), single_m.group(2)
            val = single_m.group(3)
            if vtype in INT_TYPES:
                known_int_vars.add(vname)
            val = DEFAULTS.get(vtype, '0') if val is None \
                else val.strip().replace('true', 'True').replace('false', 'False')
            out.append('{}{} = {}'.format(pad, vname, val))
            continue

        multi_m = re.match(r'^(int|float|double|char|bool)\s+([\w\s,=.]+);$', line)
        if multi_m:
            vtype = multi_m.group(1)
            default = DEFAULTS.get(vtype, '0')
            for v in multi_m.group(2).split(','):
                v = v.strip()
                if not v:
                    continue
                if vtype in INT_TYPES:
                    known_int_vars.add(v.split('=')[0].strip())
                if '=' in v:
                    name_, val_ = v.split('=', 1)
                    out.append('{}{} = {}'.format(pad, name_.strip(), val_.strip()))
                else:
                    out.append('{}{} = {}'.format(pad, v, default))
            continue

        # Array declaration: int arr[N] or int arr[N][M]
        arr_m = re.match(r'^(int|float|double)\s+(\w+)\[(\w+)\](?:\[(\w+)\])?\s*;$', line)
        if arr_m:
            vtype = arr_m.group(1)
            vname = arr_m.group(2)
            dim1 = arr_m.group(3)
            dim2 = arr_m.group(4)
            default = DEFAULTS.get(vtype, '0')
            if vtype in INT_TYPES:
                known_int_vars.add(vname)
            if dim2:
                out.append('{}{} = [[{} for _ in range({})] for _ in range({})]'.format(
                    pad, vname, default, dim2, dim1))
            else:
                out.append('{}{} = [{} for _ in range({})]'.format(
                    pad, vname, default, dim1))
            continue

        expr = line.rstrip(';')
        if re.match(r'^\w+\+\+$', expr):
            out.append('{}{} += 1'.format(pad, expr[:-2]))
            continue
        if re.match(r'^\w+--$', expr):
            out.append('{}{} -= 1'.format(pad, expr[:-2]))
            continue
        if expr:
            expr = expr.replace('true', 'True').replace('false', 'False')
            expr = smart_divide(expr, known_int_vars)
            out.append('{}{}'.format(pad, convert_condition(expr)))

    out.append('\n\nmain()')
    return '\n'.join(out)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python c_to_python.py input.c")
        sys.exit(1)

    input_file = sys.argv[1]
    base = os.path.splitext(input_file)[0]
    output_file = base + '.py'

    with open(input_file, 'r') as f:
        c_code = f.read()

    py_code = convert(c_code)

    with open(output_file, 'w') as f:
        f.write(py_code)

    print("Converted successfully: {}".format(output_file))