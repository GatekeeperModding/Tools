# pylint: disable=line-too-long
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
import sys
import glob
import re
import os.path

def main():
    seperator = "|"
    projects = glob.glob("*.csproj")
    if len(projects) != 1:
        print("ERROR: no .csproj file found")
        sys.exit(1)
    with open(projects[0], "r", encoding="utf-8") as f:
        content = f.read()

        version_res = re.compile(r"<Version>([0-9\.]*)<\/Version>").findall(content)
        if len(version_res) != 1:
            print(f"ERROR: version not found in {projects[0]}")
            sys.exit(1)

        nuget_package_name_res = re.compile(r"<AssemblyName>(.*)<\/AssemblyName>").findall(content)
        if len(nuget_package_name_res) != 1:
            print(f"ERROR: assembly name not found in {projects[0]}")
            sys.exit(1)

    toml_name = "thunderstore.toml"
    if not os.path.exists(toml_name):
        print(f"ERROR: no {toml_name} file found")
        sys.exit(1)
    with open(toml_name, "r", encoding="utf-8") as f:
        content = f.read()

        package_name_res = re.compile(r"name = \"(.*)\"").findall(content)
        if len(package_name_res) != 1:
            print(f"ERROR: name not found in {toml_name}")
            sys.exit(1)

        namespace_res = re.compile(r"namespace = \"(.*)\"").findall(content)
        if len(namespace_res) != 1:
            print(f"ERROR: namespace not found in {toml_name}")
            sys.exit(1)
    print(version_res[0] + seperator + nuget_package_name_res[0] + seperator + package_name_res[0] + seperator + namespace_res[0])

if __name__ == "__main__":
    main()
