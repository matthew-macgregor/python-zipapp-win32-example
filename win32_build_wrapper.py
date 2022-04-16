from distutils.ccompiler import new_compiler
import distutils.sysconfig
import sys
import os
from pathlib import Path
import zipapp
import argparse

class Mode:
    Console = 'console'
    Windows = 'windows'

def create_zipapp(src_dir: str, pyz_output_path: str):
    zipapp.create_archive(src_dir, pyz_output_path)

def compile(src_c_filename: str, dest_exe_filename: str, output_dir: str, mode: Mode):
    src = Path(src_c_filename)
    dest = Path(dest_exe_filename)
    cc = new_compiler()
    exe = dest.stem
    cc.output_dir = output_dir
    inc_dir = distutils.sysconfig.get_python_inc()
    print(f"Include dir: {inc_dir}")
    cc.add_include_dir(inc_dir)
    libs_dir = os.path.join(sys.base_exec_prefix, 'libs')
    print(f"Libs dir: {libs_dir}")
    cc.add_library_dir(libs_dir)

    if mode == Mode.Console:
        # Compile the CLI executable
        objs = cc.compile([str(src)])
        cc.link_executable(objs, exe)
    elif mode == Mode.Windows:
        # Compile the GUI executable
        cc.define_macro('WINDOWS')
        objs = cc.compile([str(src)])
        cc.link_executable(objs, exe + 'w')
    else:
        raise f"Invalid compilation mode: {mode}"

def combine(input_exe_path: str, pyz_path: str, output_exe_path: str):
    with open(output_exe_path, 'wb') as outf:
        with open(input_exe_path, 'rb') as f:
            outf.write(f.read())
        with open(pyz_path, 'rb') as f:
            outf.write(f.read())
        
if __name__ == "__main__":
    output_dir = "output"
    os.makedirs("output", exist_ok=True)
    
    parser = argparse.ArgumentParser(prog='windows_build_wrapper.py', allow_abbrev=True)
    parser.add_argument('--no-zipapp', action='store_true')
    parser.add_argument('--no-compile', action='store_true')
    parser.add_argument('--no-combine', action='store_true')
    args = parser.parse_args()

    if args.no_zipapp:
        print("--no-zipapp: Skipping creation of zipapp bundle.")
    else:
        create_zipapp("src", f"{output_dir}/zipapp.pyz")
        create_zipapp("srcw", f"{output_dir}/zipappw.pyzw")

    if args.no_compile:
        print("--no-compile: Skipping compilation of wrappers.")
    else:
        compile("wrapper.c", "wrapperc.exe", output_dir, mode=Mode.Console)
        compile("wrapper.c", "wrapperw.exe", output_dir, mode=Mode.Windows)

    if args.no_combine:
        print("--no-combine: Skipping combination of wrapper+zipapp.")
    else:
        combine(f"{output_dir}/wrapperc.exe", f"{output_dir}/zipapp.pyz", "osrc.exe")
        combine(f"{output_dir}/wrapperw.exe", f"{output_dir}/zipappw.pyzw", "osrcw.exe")
