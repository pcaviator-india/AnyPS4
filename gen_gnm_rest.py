
def generate_preserve_exports(imports_path, output_path):
    imports = read_imports(imports_path)
    count = 0
    with open(output_path, chr(119)) as f:
        for func_name in GNM_FUNCTIONS:
            n = compute_nid(func_name)
            if n in imports:
                f.write(n + chr(10))
                count += 1
    return count