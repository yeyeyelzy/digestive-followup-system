﻿# ========== 配置区：固定参数，队长不用动 ==========
$serverUser = "lnsdu"
$serverIP = "211.87.232.205"
$remoteTargetDir = "/home/common/lnsdu/ljllzydc"
# ==================================================

# 【强制修复1】临时放行执行策略，解决权限问题
try {
    Set-ExecutionPolicy Bypass -Scope Process -Force -ErrorAction Stop
} catch {
    Write-Host "❌ 权限不足，请右键以「管理员身份」运行！" -ForegroundColor Red
    Read-Host "按回车关闭窗口"
    exit 1
}

# 初始化界面
Clear-Host
Write-Host "========================================" -ForegroundColor Green
Write-Host "        服务器一键上传工具" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "服务器地址: $serverIP" -ForegroundColor Cyan
Write-Host "登录用户: $serverUser" -ForegroundColor Cyan
Write-Host "上传目标目录: $remoteTargetDir" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "使用方法：粘贴本地文件/文件夹完整路径，回车即可" -ForegroundColor Yellow
Write-Host "示例：D:\code\main.py 或 D:\code\my_project" -ForegroundColor Gray
Write-Host "----------------------------------------" -ForegroundColor Gray

# 【全局兜底】任何错误都不会闪退
try {
    # 1. 输入路径+循环校验，直到路径有效
    while ($true) {
        $localPath = Read-Host "请输入本地文件/文件夹路径"
        $localPath = $localPath.Trim('"').Trim("'") # 自动去掉粘贴带的引号
        
        if (-not (Test-Path -Path $localPath)) {
            Write-Host "❌ 路径不存在，请检查后重新输入！" -ForegroundColor Red
            continue
        }
        break
    }

    # 2. 自动区分文件/文件夹，自动加-r参数
    $isFolder = Test-Path -Path $localPath -PathType Container
    $scpArgs = @()
    if ($isFolder) {
        $scpArgs += "-r"
        Write-Host "✅ 已识别为【文件夹】，自动启用递归上传" -ForegroundColor Green
    } else {
        Write-Host "✅ 已识别为【单文件】，启用普通上传" -ForegroundColor Green
    }

    # 3. 构建scp参数（数组方式，彻底解决解析歧义）
    $scpArgs += @(
        "-o", "StrictHostKeyChecking=no",
        $localPath,
        "${serverUser}@${serverIP}:${remoteTargetDir}" # 用${}明确包裹变量，彻底解决冒号解析问题
    )

    Write-Host "----------------------------------------" -ForegroundColor Gray
    Write-Host "即将开始上传，请输入服务器密码，回车确认" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Gray

    # 4. 【核心修复】直接调用scp.exe，不用Invoke-Expression，零解析错误
    & scp.exe $scpArgs

    # 校验上传结果
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n🎉 上传成功！文件已保存到服务器目录" -ForegroundColor Green
    } else {
        Write-Host "`n❌ 上传失败！" -ForegroundColor Red
        Write-Host "请检查：1.服务器密码是否正确 2.网络是否连通 3.路径是否正确" -ForegroundColor Yellow
    }

} catch {
    # 任何异常都捕获，显示错误详情
    Write-Host "`n❌ 程序异常！" -ForegroundColor Red
    Write-Host "错误信息：$($_.Exception.Message)" -ForegroundColor Red
}

# 【强制窗口停留】绝对不会闪退
finally {
    Write-Host "`n----------------------------------------" -ForegroundColor Gray
    Write-Host "操作完成，按回车键关闭窗口..." -ForegroundColor Gray
    Read-Host | Out-Null
}