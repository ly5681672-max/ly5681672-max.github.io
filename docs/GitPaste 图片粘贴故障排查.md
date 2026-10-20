# GitPaste 图片粘贴故障排查

## 1. Windows 桌面版 VS Code 的正确操作

GitPaste 在桌面版与 Web 版的快捷键不同：

- **桌面版 VS Code：** 复制图片本身，在 Markdown/MDX 编辑器中将光标放到插入位置，按 `Ctrl+Alt+U`，或在命令面板运行 `GitPaste: Upload Image from Clipboard`。
- **VS Code Web：** 在 Markdown/MDX 编辑器中使用 `Ctrl+V`。
- `gitpaste.uploadOnPaste` 只适用于 Web 版，桌面版会忽略该设置。
- 必须复制图片本身，而不是图片网址；确认右下角语言模式是 Markdown 或 MDX。

## 2. 本项目的防覆盖设置

`.vscode/settings.json` 固定使用：

- `gitpaste.fileNameStrategy: timestamp`：每次上传生成独立文件名，不因图片内容相同而复用同一个远端路径。
- `gitpaste.fileNameFormat` 包含日期、时间和随机后缀。
- `gitpaste.github.conflictStrategy: rename`：路径冲突时改名，不覆盖已有文件。

修改配置后，先同步最新仓库，再在 VS Code 中执行 **Developer: Reload Window**，然后运行 **GitPaste: Check Configuration**。

## 3. 出现“overwrote the remote image, but could not update the editor”

这表示上传结果已返回，但扩展未能把最终 Markdown 图片引用写回编辑器。它不等于一定发生了内容覆盖：GitPaste 在复用同一内容哈希对应的远端文件时，也会将其标记为 `created: false`，并可能显示同样的提示。

发生此提示时：

1. **不要连续重试，也不要选择覆盖。**
2. 打开 VS Code 的 **View → Output**，在右侧下拉框选择 **GitPaste**。
3. 查找 `Uploading ... to owner/repository@branch:path` 和 `Uploaded ...: URL`，记录远端路径与图片 URL。
4. 如果编辑器留下 `![Uploading ...]()` 占位符，确认已记录远端 URL 后再删除该占位符；可手动插入 `![图片说明](图片URL)`，避免重复上传。
5. 如果确定远端原文件确实被覆盖，进入 GitHub 对应文件的 **History** 查看覆盖前版本，再恢复旧版本。GitPaste 本身不会保存被覆盖文件的旧内容，不能自动回滚。

## 4. 仍无法插入时

先更新 Marketplace 中的 GitPaste 至最新版，再重新加载 VS Code。若问题仍复现，请提供：

- VS Code 版本与 GitPaste 扩展版本；
- **View → Output → GitPaste** 中出错时间前后的日志；
- 当时打开的文件是否为 Markdown/MDX；
- 使用的操作是 `Ctrl+V`、`Ctrl+Alt+U` 还是命令面板。

日志可能包含仓库路径和文件名，分享前可遮蔽不希望公开的信息。不要提供 GitHub Token 或任何凭据。
