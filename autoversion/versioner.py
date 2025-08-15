# pylint: disable=line-too-long
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
import re
import sys
import fileinput

def main():
    args = sys.argv

    if len(args) < 2:
        print("ERROR: project_name argument is missing")
        sys.exit(1)
    project_name = args[1]
    with open(f"{project_name}.csproj", "r", encoding="utf-8") as f:
        patt = re.compile(r"<Version>([0-9\.]*)<\/Version>")
        res = patt.findall(f.read())
        if len(res) != 1:
            print(f"ERROR: version not found in {project_name}.csproj")
            sys.exit(1)
        version = res[0]

    with fileinput.FileInput("thunderstore.toml", inplace=True) as file:
        for line in file:
            if line.startswith("versionNumber = "):
                line = f'versionNumber = "{version}"\n'
            print(line, end='')

if __name__ == "__main__":
    main()
