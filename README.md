# 便利贴

一个简洁的桌面便利贴应用，无边框、可拖动、持久化存储。

## 功能

- **无边框窗口** - 深黄色顶部可拖动，浅黄色区域可输入
- **多个便利贴** - 右键新建
- **右键菜单**
  - 新建便签
  - 销毁（删除该便签）
  - 置顶（保持在最前方）
- **托盘菜单**
  - 新建便签
  - 展示（将所有便签提升到窗口上方）
  - 隐藏（带勾选标记）
  - 关闭
- **启动通知** - Windows 通知提示已启动
- **内容保存** - 自动保存到 `~/.sticky_notes/notes.json`

## 安装

```bash
uv sync
```

## 运行

```bash
uv run python main.py
```

## 打包

```bash
uv run pyinstaller --onefile --windowed --name=sticky_notes main.py
```

exe 文件在 `dist/sticky_notes.exe`
