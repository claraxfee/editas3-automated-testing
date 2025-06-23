import os, re, csv, argparse, sys
import javalang
import pandas as pd
import subprocess as sp
from tree_hugger.core import JavaParser
from collections import defaultdict
from copy import copy


SAMPLE_PROJECTS = ('Chart', 'Cli', 'Csv', 'Gson', 'Lang')

jp = JavaParser("/tmp/tree-sitter-repos/my-languages.so")

assert_re = re.compile("assert\w*\(.*\)")
# Modified regex for SF110 structure
sf110_path_re = re.compile(r"(\d+_\w+).*?([^/]+)EvoSuiteTest\.java$")
whitespace_re = re.compile(r'\s+')

test_name_re = re.compile("public void (test[0-9]*)\(\)")
extract_package_re = re.compile(r'package\s+(\S+);')
fail_catch_re = re.compile(r"fail\(.*\).*}\s*catch", re.MULTILINE|re.DOTALL)

errs = defaultdict(int)

# NEW: Find SF110 projects
def find_sf110_projects(sf110_dir):
    """Find all SF110 projects matching pattern number_name"""
    projects = []
    for item in os.listdir(sf110_dir):
        if os.path.isdir(os.path.join(sf110_dir, item)) and re.match(r'\d+_\w+', item):
            projects.append(item)
    return projects

# NEW: Get Evosuite test files  
def get_evosuite_test_files(project_dir):
    """Find all *EvoSuiteTest.java files in evosuite-tests/"""
    test_files = []
    evosuite_dir = os.path.join(project_dir, 'evosuite-tests')
    if os.path.exists(evosuite_dir):
        for root, dirs, files in os.walk(evosuite_dir):
            for f in files:
                if f.endswith('EvoSuiteTest.java'):
                    test_files.append(os.path.join(root, f))
    return test_files

# NEW: Resolve source path from test path
def resolve_source_path(test_file_path, project_dir):
    """Convert test file path to corresponding source file path"""
    # Extract package from test file
    with open(test_file_path) as f:
        content = f.read()
    
    package = ''
    for line in content.split('\n'):
        if m := extract_package_re.match(line.strip()):
            package = m[1]
            break
    
    # Get class name without EvoSuiteTest suffix
    class_name = os.path.basename(test_file_path).replace('EvoSuiteTest.java', '')
    
    # Build source path
    if package:
        package_path = package.replace('.', '/')
        source_path = os.path.join(project_dir, 'src/main/java', package_path, class_name + '.java')
    else:
        source_path = os.path.join(project_dir, 'src/main/java', class_name + '.java')
    
    return source_path

# NEW: Normalize code with spaces between tokens
def normalize_code(code_text, remove_access_modifiers=False, remove_semicolon=False):
    """Format code with space between tokens"""
    if not code_text or not code_text.strip():
        return code_text
        
    try:
        tokens = javalang.tokenizer.tokenize(code_text)
        normalized = ' '.join(token.value for token in tokens)
        
        if remove_access_modifiers:
            normalized = re.sub(r'\b(public|private|protected)\s+', '', normalized)
        
        if remove_semicolon:
            normalized = normalized.rstrip(' ;')
            
        return normalized
    except:
        return code_text  # fallback to original if tokenization fails

# REMOVED: checkout_project, get_active_bugs, get_project_layout (Defects4J specific)

def extract_focal_class(class_dec):
    return class_dec.name.strip("EvoSuiteTest")


def extract_focal_methods(class_dec, tests, all_focal_class_methods):
    focal_class_name = extract_focal_class(class_dec)
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




def get_class_dec(test_file):
    try:
        with open(test_file) as f:
            class_txt = f.read()

        with open(test_file) as f:
            class_lines = f.readlines()

    except Exception as e:
        print('ERROR READING:', test_file)
        raise e

    try:
        tree = javalang.parse.parse(class_txt)
    except Exception as e:
        print("error parsing", test_file)
        raise e

    class_dec = tree.types[0]

    return class_dec, class_lines


def get_classes_with_inherited(full_class_path, src_path):

    ret_list = []

    while full_class_path:

        try:
            class_dec, class_lines = get_class_dec(full_class_path)
        except Exception as e:
            print('ERROR parsing', full_class_path)
            if ret_list:
                return ret_list
            else:
                raise e

        ret_list += [(class_dec, class_lines)]

        full_class_path = None

        # get import list
        imports = {}
        for line in class_lines:
            if line.strip().startswith('import'):
                imported = line.strip().strip(';').split()[-1]
                import_cls = imported.split('.')[-1]
                imports[import_cls] = imported

        if hasattr(class_dec, 'extends') and class_dec.extends and class_dec.extends.name:
            extend_cls = class_dec.extends.name
            if extend_cls in imports:
                extend_full_cls = imports[extend_cls]
                full_class_path = src_path +'/'+ extend_full_cls.replace('.', '/') + '.java'

    return ret_list


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


def split_test(test, line_nums, assert_line_no=None):
    # split by asserts
    split_tests = []
    split_test_line_nums = []

    relevant_lines = []
    relevant_line_nums = []
    for line, line_no in zip(test.split('\n'), line_nums):
        if not line.strip():
            continue

        if 'assert' in line:
            if assert_line_no is not None:
                if line_no == assert_line_no:
                    relevant_lines += [line]
                    relevant_line_nums += [line_no]
                    relevant_lines += ['}']
                    split_tests += ['\n'.join(relevant_lines)]
                    split_test_line_nums += [copy(relevant_line_nums)]
                    break

            else: # no assert_line specified, keep all asserts
                next_test = '\n'.join(relevant_lines + [line, '}'])
                next_test_lines = copy(relevant_line_nums + [line_no])
                split_tests += [next_test]
                split_test_line_nums += [next_test_lines]

        else: # non assert line
            relevant_lines += [line]
            relevant_line_nums += [line_no]

    split_tests += ['\n'.join(relevant_lines)]
    split_test_line_nums += [relevant_line_nums]

    return split_tests, split_test_line_nums


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('sf110_dir', help='Path to SF110 directory')  # CHANGED from test_corpus_dir
    parser.add_argument('--bug_tests_only', action='store_true')  # KEPT but not used
    parser.add_argument('--sample_5projects', action='store_true')
    parser.add_argument('--projects', nargs='+', help='Filter to specific project names')  # NEW
    parser.add_argument('-o', '--output_dir', default='.')
    args = parser.parse_args()

    sf110_dir = args.sf110_dir  # CHANGED

    # NEW: Find all SF110 projects
    projects = find_sf110_projects(sf110_dir)
    
    # Filter projects if specified
    if args.projects:
        projects = [p for p in projects if any(proj_name in p for proj_name in args.projects)]
    
    if args.sample_5projects:
        projects = [p for p in projects if any(sample in p for sample in SAMPLE_PROJECTS)]

    print(f"Found {len(projects)} projects to process")

    # NEW: Open output files
    assert_file = open(os.path.join(args.output_dir, 'assert.txt'), 'w')
    prefix_focal_file = open(os.path.join(args.output_dir, 'prefix_focal.txt'), 'w')

    input_data = []
    metadata = []

    # CHANGED: Main loop now iterates over SF110 projects
    for project in projects:
        project_dir = os.path.join(sf110_dir, project)
        print(f"Processing project: {project}")
        
        test_files = get_evosuite_test_files(project_dir)
        print(f"Found {len(test_files)} test files")
        
        for full_fname in test_files:
            # CHANGED: Extract project info from SF110 structure
            match = sf110_path_re.search(full_fname)
            if not match:
                errs['file_name_not_matched'] += 1
                continue
            project_name = match.group(1)
            class_name = match.group(2)

            print(full_fname)

            # CHANGED: Resolve source file path directly
            full_class_path = resolve_source_path(full_fname, project_dir)
            if not os.path.exists(full_class_path):
                errs['cannot_find_focal_unit_file'] += 1
                print('ERROR: cannot get file:')
                print(full_class_path)
                continue

            try:
                class_dec, class_text = get_class_dec(full_fname)
            except Exception as e:
                errs['err_parse_test_file'] += 1
                print("ERROR:couldn't parse test_class", full_fname)
                continue

            try:
                src_path = os.path.join(project_dir, 'src/main/java')  # CHANGED: Standard Maven structure
                focal_dec_text_pairs = get_classes_with_inherited(full_class_path, src_path)
            except Exception as e:
                errs['err_parse_focal_file'] += 1
                print("ERROR:couldn't parse focal class", project_name, full_class_path)
                continue

            package = ''
            for line in class_text:
                if m := extract_package_re.match(line.strip()):
                    package = m[1]
                    break

            jp.parse_file(full_fname)
            class_test_methods = jp.get_all_method_bodies()

            if len(class_test_methods) != 1:
                errs['unexpected_class_structure'] += 1
                continue

            class_name_from_parser, _ = list(class_test_methods.items())[0]

            test_methods = extract_all_methods(class_dec, class_text)
            split_test_methods = []
            split_test_line_nums = []
            for obj, test_method, line_nums, _ in test_methods:
                m2 = test_name_re.search(test_method)
                if not m2:
                    errs['test_name_not_matched'] += 1
                    continue
                test_name = m2.group(1)
                full_test_name = package +'.' + class_name_from_parser + '::' + test_name

                split_tests, split_test_lines = split_test(test_method, line_nums)

                if not split_tests: # should always have at least one
                    errs['no_split_tests'] += 1
                    continue

                split_test_methods += split_tests
                split_test_line_nums += split_test_lines

            focal_class_methods = [extract_all_methods(fdec, ftxt) for fdec, ftxt in focal_dec_text_pairs]
            focal_methods = extract_focal_methods(class_dec, split_test_methods, focal_class_methods)

            if len(split_test_methods) != len(focal_methods):
                errs['length_mismatch'] += 1
                continue
            if len(split_test_methods) != len(split_test_line_nums):
                errs['length_mismatch'] += 1
                continue

            for test_method, focal_method_docstring, test_lines in zip(split_test_methods, focal_methods, split_test_line_nums):
                focal_method, docstring = "", ""
                if focal_method_docstring:
                    focal_method, docstring = focal_method_docstring

                # Extract assertion using original logic
                assertion = ''
                try:
                    m = assert_re.search(test_method)
                except Exception as e:
                    print('ERROR cannot regex search test:')
                    print(test_method)
                    raise e
                if m:
                    assertion = m[0]
                
                if not assertion:
                    errs['no_assertion'] += 1
                    continue

                # Extract prefix (everything before the assertion)
                prefix = test_method[:test_method.find(assertion)] if assertion else test_method

                m2 = test_name_re.search(test_method)
                if not m2:
                    errs['test_name_not_matched_in_split'] += 1
                    continue
                test_name = m2.group(1)

                full_test_name = package +'.' + class_name_from_parser + '::' + test_name

                # NEW: Normalize code parts
                norm_prefix = normalize_code(prefix, remove_access_modifiers=True)
                norm_assertion = normalize_code(assertion, remove_semicolon=True)
                norm_focal = normalize_code(focal_method)

                # NEW: Write to output files
                assert_file.write(norm_assertion + '\n')
                
                combined = f'{norm_prefix} "<AssertPlaceHolder>" ; }} "<FocalMethod>" {norm_focal}\n'
                prefix_focal_file.write(combined)

                # Keep original data structure for compatibility
                exception_lbl = bool(fail_catch_re.search(test_method))
                assertion_lbl = assertion

                metadata += [(project_name, '0', full_test_name, 0, 0, exception_lbl, assertion_lbl, '')]
                input_data += [(focal_method, test_method, docstring)]

    # Close output files
    assert_file.close()
    prefix_focal_file.close()

    print('collected inputs:', len(input_data))
    print(f'writing to {args.output_dir}/inputs.csv and {args.output_dir}/meta.csv')

    # KEPT: Original CSV output for compatibility
    with open(args.output_dir + '/inputs.csv', 'w') as f1, open(args.output_dir + '/meta.csv', 'w') as f2:
        input_w = csv.writer(f1)
        meta_w = csv.writer(f2)

        input_w.writerow(['focal_method', 'test_prefix', 'docstring'])
        meta_w.writerow('project,bug_num,test_name,exception_bug,assertion_bug,exception_lbl,assertion_lbl,assert_err'.split(','))

        for input_pair, meta in zip(input_data, metadata):
            input_w.writerow(input_pair)
            meta_w.writerow(meta)

    # Print error statistics
    print("\nError Statistics:")
    for error_type, count in errs.items():
        print(f"{error_type}: {count}")
