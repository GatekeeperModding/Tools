# pylint: disable=line-too-long
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
import errno
from subprocess import CalledProcessError, run, PIPE
import os
import shutil
import json
import sys

def create_build_dir(name):
    try:
        os.mkdir(name)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

def validate_json_entry(config, name):
    try:
        _ = config[name]
    except (TypeError, KeyError) as e:
        print(e)
        print(f"ERROR: config.json is missing the 'meta/{name}' section")
        sys.exit(1)

def validate_json(config):
    if "meta" in config:
        validate_json_entry(config["meta"], "package_id")
        validate_json_entry(config["meta"], "version")
        validate_json_entry(config["meta"], "authors")
        validate_json_entry(config["meta"], "project_url")
        validate_json_entry(config["meta"], "description")
        validate_json_entry(config["meta"], "release_notes")
    else:
        print("ERROR: config.json is missing the 'meta' section")
        sys.exit(1)
    if "game" in config:
        validate_json_entry(config["game"], "game_path")
        validate_json_entry(config["game"], "exe_name")
        validate_json_entry(config["game"], "unity_libs_path")
    else:
        print("ERROR: config.json is missing the 'game' section")
        sys.exit(1)
    if "programs" in config:
        validate_json_entry(config["programs"], "cpp2il_path")
        validate_json_entry(config["programs"], "il2cppinterop_path")
    else:
        print("ERROR: config.json is missing the 'programs' section")
        sys.exit(1)

def generate_nuspec(config, build_folder, il2cpp_folder, il2cpp_path):
    nuspec_file_path = build_folder + f"/{ config["game"]["exe_name"] }.nuspec"
    package_id = config["meta"]["package_id"]
    version = config["meta"]["version"]
    authors = config["meta"]["authors"]
    project_url = config["meta"]["project_url"]
    description = config["meta"]["description"]
    release_notes = config["meta"]["release_notes"]

    content = (
         '<?xml version="1.0"?>\n'
         '<package  xmlns="http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd">\n'
         '  <metadata>\n'
        f'    <id>{package_id}</id>\n'
        f'    <version>{version}</version>\n'
        f'    <title></title>\n'
        f'    <authors>{authors}</authors>\n'
        f'    <projectUrl>{project_url}</projectUrl>\n'
         '    <requireLicenseAcceptance>false</requireLicenseAcceptance>\n'
        f'    <description>{description}</description>\n'
        f'    <releaseNotes>{release_notes}</releaseNotes>\n'
         '    <dependencies>\n'
         '    </dependencies>\n'
         '    <summary></summary>\n'
         '  </metadata>\n'
         '  <files>\n'
        f'{"".join([f'    <file src="{il2cpp_folder}/{file}" target="lib/netstandard2.0/{file}" />\n' for file in os.listdir(il2cpp_path)])}'
         '  </files>\n'
         '</package>\n'
    )

    with open(nuspec_file_path, "w", encoding="utf-8") as f:
        f.write(content)
        f.flush()

def generate_dummydlls(config, cpp2il_folder):
    cpp2il_path = config["programs"]["cpp2il_path"]
    game_path = config["game"]["game_path"]
    exe_name = config["game"]["exe_name"]
    try:
        cmd = [cpp2il_path, f'--game-path={game_path}', f'--exe-name={exe_name}', '--output-as=dummydll', f'--output-to={cpp2il_folder}']
        #import shlex
        #print(' '.join(shlex.quote(arg) for arg in cmd))
        result = run(cmd, stdout=PIPE, stderr=PIPE, check=True)
        print(result.stdout.decode())
    except CalledProcessError as e:
        print("ERROR: generating dummy dlls failed")
        print(e)

def run_il2cppinterop(config, cpp2il_folder, il2cpp_path):
    game_assembly_path = config["game"]["game_path"] + "/GameAssembly.dll"
    il2cppinterop_path = config["programs"]["il2cppinterop_path"]
    unity_libs_path = config["game"]["unity_libs_path"]
    try:
        cmd = [il2cppinterop_path, "generate", "--input", cpp2il_folder, "--output", il2cpp_path, "--unity", unity_libs_path, "--game-assembly", game_assembly_path]
        result = run(cmd, stdout=PIPE, stderr=PIPE, check=True)
        print(result.stdout.decode())
    except CalledProcessError as e:
        print("ERROR: running il2cppinterop failed")
        print(e)

def pack_package(config, build_folder):
    nuspec_file_path = build_folder + f"/{ config["game"]["exe_name"] }.nuspec"
    try:
        cmd = ["nuget", "pack", nuspec_file_path, "-OutputDirectory", build_folder]
        result = run(cmd, stdout=PIPE, stderr=PIPE, check=True)
        print(result.stdout.decode())
    except CalledProcessError as e:
        print("ERROR: packing the package failed")
        print(e)

def main():
    with open("config.json", "r", encoding="utf-8") as config_file:
        config = json.loads(config_file.read())
    if config is None:
        print("ERROR: config.json file not found")
        sys.exit(1)

    validate_json(config)

    build_folder = "./build"
    cpp2il_folder = build_folder + "/cpp2il_out"
    il2cpp_folder = "il2cpp_out"
    il2cpp_path = build_folder + "/" + il2cpp_folder

    if os.path.exists(build_folder):
        shutil.rmtree(build_folder)
    create_build_dir(build_folder)

    generate_dummydlls(config, cpp2il_folder)
    run_il2cppinterop(config, cpp2il_folder, il2cpp_path)
    generate_nuspec(config, build_folder, il2cpp_folder, il2cpp_path)
    pack_package(config, build_folder)
    #nuget push

if __name__ == "__main__":
    main()
