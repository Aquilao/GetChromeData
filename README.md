# GetChromeData
**由于 python 糟糕的可移植性，该项目停止更新和维护。现在用 Go 实现了一个新的工具，功能和支持的浏览器比市面上开源的大多数工具强些，由于目前在工作上使用，考虑到免杀，暂无开源计划。需要浏览器解密的工具推荐使用[HackBrowserData](https://github.com/moonD4rk/HackBrowserData)。**

Windows 下获取 Chrome、Chromium Edge 浏览器的账号密码、Cookie、历史记录、下载记录、书签等信息

2021.1.14 v0.7 dev 新增 Chromium Edge 数据获取

## 使用

### GetLocalChromeData.py

使用目标用户的权限在目标系统下执行，即可输出结果至 Results/ 文件夹。

### GetSourseData.py

使用目标用户的权限在目标系统下执行，可获取 Sourse_Data.zip，将其传输回本地放有 GetRemoveChromeData.py 的文件夹中，再使用 GetRemoveChromeData.py 处理。

### GetRemoveChromeData.py

确保脚本目录下存在 Sourse_Data.zip，运行即可输出结果至 Results/ 文件夹。

## Q&A

Q: Windows 上运行 python 脚本？  
A: 在 Windows中、脚本所需要的第三方库安装完成的条件下，可以使用`pyinstaller`等方式打包为 exe。

Q: 免杀？  
A: 截至`2020.12.30`，在未做免杀的情况下，直接使用`pyinstaller -F -w GetLocalChromeData.py` 生成的 exe 文件只能绕过小部分杀软。而 GetSourseData.py 可以绕过包括 360、Windows Definder、天擎、电脑管家等大部分杀软，建议使用。

欢迎交流留 issues 或者邮件交流。

