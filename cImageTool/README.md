# cImageTool v1.1

把多张 PNG 一键打包成精灵表（长条 / 竖条 / 图集），并自动生成裁剪描述文件。

## 用法
1. 下载 [Releases](../../releases) 里的 `cit.exe`，双击运行。  
2. 按提示选择图片 → 选择打包方式 → 选择输出目录 → 完成。  

## 自己编译
```bash
pip install pillow pyinstaller
pyinstaller -F -w pack_tex.py
```

## 不算小技巧的小技巧
选择多图时可以按住Ctrl再选择