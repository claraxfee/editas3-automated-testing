import os
import re
import javalang

from collections import defaultdict
errs = defaultdict(int)


assert_re = re.compile(r'assert\w*\(.*?\);')
test_name_re = re.compile(r'public void (test\w*)\(\)')

def format(code):
    # Remove access modifiers
    code = re.sub(r'\b(public|private|protected|static|final|synchronized|abstract|native|transient|volatile|strictfp)\b', '', code)
    
    # Add space around symbols
    code = re.sub(r'([{}();.,=+\-*/<>!&|?:\[\]])', r' \1 ', code)

    # Collapse multiple spaces
    code = re.sub(r'\s+', ' ', code).strip()
    
    return code


def get_class_dec(java_file_path):
    with open(java_file_path, 'r') as f:
        text = f.read()
    with open(java_file_path, 'r') as f:
        lines = f.readlines()
    tree = javalang.parse.parse(text)
    class_dec = tree.types[0]
    return class_dec, lines


def get_method_txt(lines, start_line):
    """
    lines: lines of file, assume each ends with \n
    start_line: first line of method decl
    """
    method_def = ''
    method_sig = ''
    depth = 0
    method_collected = False
    in_string = False
    escape = False


    line_nums = []
    for i in range(start_line, len(lines)):
        prev_char = ''
        line = lines[i]

        for col, char in enumerate(line):
            next_char = line[col+1] if col+1 < len(line) else ''

            # escape
            if escape:
                escape = False
            elif char == '\\':
                escape = True

            # comment
            elif char == '/' and prev_char == '/' and not in_string:
                prev_char = ''
                break

            # single chars
            elif not in_string and prev_char == "'" and next_char == "'":
                pass

            # strings, curlys
            elif char == "\"":
                in_string = not in_string
            elif char == '{' and not in_string:
                depth += 1

                if depth == 1: # open def, grab signature
                    method_sig = method_def + line[:col].strip() + ';'
            elif char == '}' and not in_string:
                depth -= 1
                if depth == 0: # end of method def
                    method_def += line[:col+1]
                    line_nums += [i+1]
                    method_collected = True
                    break

            prev_char = char
        if method_collected:
            break

        method_def += line
        line_nums += [i+1]

    return method_sig, method_def, line_nums

def extract_all_methods(class_dec, class_lines):
    methods = []

    for method in class_dec.constructors:
        method_sig, method_def, line_nums = get_method_txt(class_lines, method.position.line-1)
        if method_def.count("@Test") > 1:
            continue

        methods.append((method, method_def, line_nums, method.documentation))

    for method in class_dec.methods:
        method_sig, method_def, line_nums = get_method_txt(class_lines, method.position.line-1)
        if method_def.count("@Test") > 1:
            continue

        methods.append((method, method_def, line_nums, method.documentation))


    return methods



def collect_all_src_methods(src_root): 
    all_methods = []
    for root, _, files in os.walk(src_root): 
        for file in files: 
            if not file.endswith(".java"):
                continue
            path=os.path.join(root,file)
            try:
                class_dec, lines = get_class_dec(path)
                methods = extract_all_methods(class_dec, lines)
                all_methods.append(methods)
            except Exception:
                continue

    return all_methods


def split_test(test_txt):
    lines = test_txt.splitlines()
    prefix = []
    assertion = ''
    for line in lines:
        if assert_re.search(line):
            assertion = assert_re.search(line).group(0)
            break
        prefix.append(line.strip())
    return ' '.join(prefix), assertion



def extract_focal_methods(class_dec, tests, all_focal_class_methods):
    focal_class_name = "" # don't need this i think ?? 
    focal_methods = []

    for test_txt in tests:

        focal_method_name = None
        try:
            try:
                tokens = javalang.tokenizer.tokenize(test_txt)
                parser = javalang.parser.Parser(tokens)
                test_obj = parser.parse_member_declaration()
            except Exception as e:
                print('ERROR parsing test:')
                print(test_txt)
                errs['unable_to_parse_test'] += 1

                focal_methods += [('', '')]
                continue

            nodes = [n for n in test_obj]

            fm_names = []
            for p, n in reversed(nodes):
                if isinstance(n, javalang.tree.MethodInvocation):
                    if n.member == 'fail' or n.member == 'verifyException' or\
                            'assert' in n.member:
                        continue
                    focal_method_name = n.member
                    fm_names += [focal_method_name]

                if isinstance(n, javalang.tree.ClassCreator):
                    focal_method_name = n.type.name
                    fm_names += [focal_method_name]

            added = False
            for focal_method_name in fm_names:
                for focal_class_methods in all_focal_class_methods:
                    for (f_method_dec, f_method_text, line_nums, docstring) in focal_class_methods:

                        if f_method_dec.name == focal_method_name:
                            focal_methods += [(f_method_text, docstring)]
                            added = True
                            break

                    if added: break
                if added: break

            if not added:
                focal_methods += [('', '')]
        except Exception as e:
            added = False
            raise e

    return focal_methods

def extract_project(project_dir):
    TEST_DIR = os.path.join(project_dir, "evosuite-tests")
    SRC_DIR = os.path.join(project_dir, "src/main/java")

    assertions = []
    prefix_focal_pairs = []

    all_focal_class_methods = collect_all_src_methods(SRC_DIR)

    for root, _, files in os.walk(TEST_DIR):
        for file in files:
            if not file.endswith("EvoSuiteTest.java"):
                continue

            test_file_path = os.path.join(root, file)
            src_file_path = test_file_path.replace("evosuite-tests", "src/main/java").replace("EvoSuiteTest", "")[:-5] + ".java"

            if not os.path.exists(src_file_path):
                print(f"Missing src: {src_file_path}")
                continue

            try:
                test_class_dec, test_class_lines = get_class_dec(test_file_path)
                src_class_dec, src_class_lines = get_class_dec(src_file_path)
            except Exception as e:
                print(f"Failed to parse: {test_file_path} or {src_file_path}")
                continue

            test_methods = extract_all_methods(test_class_dec, test_class_lines)

            for _, test_method_txt, *_ in test_methods:
                prefix, assertion = split_test(test_method_txt)
                if not assertion:
                    continue

                # Normalize
                assertion = assertion.rstrip().rstrip(';')
                formatted_assert = format(assertion)
                assertions.append(formatted_assert)

                focal_pairs = extract_focal_methods(None, [test_method_txt], all_focal_class_methods)
                if focal_pairs and focal_pairs[0][0]:
                    focal_txt = format(focal_pairs[0][0])
                else:
                    focal_txt = "<UnknownFocalMethodText>"

                formatted_prefix = format(prefix)
                prefix_focal_pairs.append(f"{formatted_prefix} \"<AssertPlaceHolder>\" ; }} \"<FocalMethod>\" {focal_txt}")

    # Determine project ID from folder name
    project_id = os.path.basename(project_dir).split('_')[0]

    # Write outputs
    with open(f"{project_id}_assert.txt", "w") as f:
        for a in assertions:
            f.write(a + "\n")

    with open(f"{project_id}_prefix_focal.txt", "w") as f:
        for line in prefix_focal_pairs:
            f.write(line + "\n")


# main 

ROOT_DIR = "SF110"

for project in os.listdir(ROOT_DIR):
    project_path = os.path.join(ROOT_DIR, project)
    if not os.path.isdir(project_path):
        continue
    print(f"Processing {project_path}")
    try:
        extract_project(project_path)
    except Exception as e:
        print(f"Error in {project_path}: {e}")

