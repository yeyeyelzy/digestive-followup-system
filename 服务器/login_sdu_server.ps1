# ========== 配置区：只需要改这里，下面的代码不用动 ==========
$serverUser = "lnsdu"          # 正确用户名：小写L开头，不是大写i
$serverIP = "211.87.232.205"   # 服务器IP
$targetDir = "/home/common/lnsdu/ljllzydc"  # 目标目录
# ============================================================

Write-Host "=== 一键登录服务器 ===" -ForegroundColor Green
Write-Host "服务器地址: $serverIP" -ForegroundColor Cyan
Write-Host "登录用户: $serverUser" -ForegroundColor Cyan
Write-Host "登录密码: sdu321@lnsdu" -ForegroundColor Cyan
Write-Host "将自动进入目录: $targetDir" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "提示：弹出password:提示时，直接Ctrl+V粘贴密码，回车即可登录" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

# 构建最稳定的SSH命令，无任何花里胡哨的逻辑
$sshCommand = "ssh -o StrictHostKeyChecking=no -t $serverUser@$serverIP `"cd $targetDir; exec bash`""

# 执行SSH连接，不管成功失败，窗口都不会闪退
try {
    Invoke-Expression $sshCommand
} catch {
    Write-Host "`n❌ 连接失败！错误信息：$_" -ForegroundColor Red
    Write-Host "排查建议：1.检查用户名/IP是否正确 2.检查学校局域网是否连通" -ForegroundColor Yellow
}

# 【关键兜底】强制窗口停留，绝对不会闪退
Write-Host "`n操作完成，按回车键关闭窗口..." -ForegroundColor Gray
Read-Host