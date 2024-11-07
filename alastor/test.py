import re

text = '"/home/app/node_modules/side-channel/index.js", O_RDONLY|O_CLOEXEC'
pattern = r'"([^"]+)"'
match = re.search(pattern, text)
if match:
    print(match.group(1))
else:
    print("匹配失败")
