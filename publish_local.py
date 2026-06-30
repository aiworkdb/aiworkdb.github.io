#!/usr/bin/env python3
"""
团建文章公众号批量发布脚本
使用 wenyan-mcp 发布文章到微信公众号

使用方法：
1. 在本地电脑安装 wenyan-mcp：npm install -g @wenyan-md/mcp
2. 设置环境变量（或直接修改下面的配置）
3. 运行脚本：python publish_local.py

作者：AIWorkDB
日期：2026-06-30
"""

import subprocess
import os
import time

# ============ 配置区域 ============
# 微信公众号配置
WECHAT_APP_ID = "wxdbde7df46734aaa6"
WECHAT_APP_SECRET = "3e989fe9b3222bbe92ff3af2b91d42ca"

# wenyan-mcp 路径（根据您的安装位置修改）
# Windows: wenyan-mcp.cmd
# Mac/Linux: wenyan-mcp
WENYAN_PATH = "wenyan-mcp.cmd"  # Windows
# WENYAN_PATH = "wenyan-mcp"  # Mac/Linux

# 主题选择
THEME_ID = "pie"  # 科技风主题

# 核心文章列表（按优先级排序）
ARTICLES = [
    {
        "file": "teambuilding/README.md",
        "name": "团建游戏库介绍",
        "priority": 1
    },
    {
        "file": "teambuilding/guide.md",
        "name": "教练使用指南",
        "priority": 2
    },
    {
        "file": "teambuilding/flows/one-day/01-schedule.md",
        "name": "一天活动流程",
        "priority": 3
    },
    {
        "file": "teambuilding/flows/half-day/01-schedule.md",
        "name": "半天活动流程",
        "priority": 4
    },
    {
        "file": "teambuilding/flows/online/01-schedule.md",
        "name": "线上活动流程",
        "priority": 5
    }
]

# ============ 函数定义 ============

def publish_article(article_file, theme_id="pie"):
    """
    发布单篇文章到公众号
    
    Args:
        article_file: 文章文件路径
        theme_id: 主题 ID
    
    Returns:
        (success, message): 是否成功，消息
    """
    print(f"\n{'='*60}")
    print(f"📤 正在发布: {article_file}")
    print(f"{'='*60}")
    
    # 构建 MCP 请求
    payload = f'''{{"jsonrpc":"2.0","id":1,"method":"initialize","params":{{"protocolVersion":"2024-11-05","capabilities":{{}},"clientInfo":{{"name":"workbuddy","version":"1.0.0"}}}}}}
{{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{{"name":"publish_article","arguments":{{"file":"{article_file}","theme_id":"{theme_id}"}}}}}}
'''
    
    # 设置环境变量
    env = os.environ.copy()
    env["WECHAT_APP_ID"] = WECHAT_APP_ID
    env["WECHAT_APP_SECRET"] = WECHAT_APP_SECRET
    
    try:
        # 调用 wenyan-mcp
        result = subprocess.run(
            [WENYAN_PATH],
            input=payload,
            capture_output=True,
            text=True,
            env=env,
            timeout=120
        )
        
        output = result.stdout + result.stderr
        
        # 检查是否成功
        if "media_id" in output.lower():
            # 提取 media_id
            import re
            match = re.search(r'"media_id"\s*:\s*"([^"]+)"', output)
            if match:
                media_id = match.group(1)
                print(f"✅ 发布成功!")
                print(f"   Media ID: {media_id}")
                print(f"   请登录公众号后台查看草稿")
                return True, f"Media ID: {media_id}"
            else:
                print(f"✅ 发布成功! (未提取到 Media ID)")
                return True, "成功"
        else:
            # 提取错误信息
            error_msg = "未知错误"
            if "执行工具失败" in output:
                import re
                match = re.search(r'执行工具失败:\s*([^\n]+)', output)
                if match:
                    error_msg = match.group(1)
            
            print(f"❌ 发布失败")
            print(f"   错误: {error_msg}")
            print(f"\n详细输出:")
            print(output[-800:])
            return False, error_msg
            
    except subprocess.TimeoutExpired:
        print(f"❌ 发布超时（120秒）")
        return False, "超时"
    except FileNotFoundError:
        print(f"❌ 找不到 wenyan-mcp 命令")
        print(f"   请确保已安装: npm install -g @wenyan-md/mcp")
        print(f"   或修改 WENYAN_PATH 为完整路径")
        return False, "wenyan-mcp 未安装"
    except Exception as e:
        print(f"❌ 发生异常: {e}")
        return False, str(e)

def main():
    """主函数"""
    print("="*60)
    print("团建文章公众号批量发布工具")
    print("="*60)
    print(f"\n配置信息:")
    print(f"  微信公众号 ID: {WECHAT_APP_ID}")
    print(f"  主题: {THEME_ID} (科技风)")
    print(f"  待发布文章数: {len(ARTICLES)}")
    print(f"\n开始发布...")
    
    # 统计
    success_count = 0
    failed_articles = []
    
    # 逐篇发布
    for i, article in enumerate(ARTICLES, 1):
        print(f"\n[{i}/{len(ARTICLES)}] 处理中...")
        
        success, message = publish_article(
            article["file"],
            THEME_ID
        )
        
        if success:
            success_count += 1
            # 避免频率限制，等待 3 秒
            if i < len(ARTICLES):
                print(f"\n⏳ 等待 3 秒...")
                time.sleep(3)
        else:
            failed_articles.append({
                "file": article["file"],
                "name": article["name"],
                "error": message
            })
    
    # 输出总结
    print(f"\n{'='*60}")
    print("发布完成!")
    print(f"{'='*60}")
    print(f"\n📊 统计:")
    print(f"   成功: {success_count} 篇")
    print(f"   失败: {len(failed_articles)} 篇")
    
    if failed_articles:
        print(f"\n❌ 失败文章列表:")
        for item in failed_articles:
            print(f"   - {item['name']} ({item['file']})")
            print(f"     错误: {item['error']}")
    
    print(f"\n📝 下一步:")
    print(f"   1. 登录微信公众号后台: https://mp.weixin.qq.com")
    print(f"   2. 进入: 素材管理 → 草稿箱")
    print(f"   3. 查看刚发布的 {success_count} 篇文章")
    print(f"   4. 预览并发布")
    
    if failed_articles:
        print(f"\n💡 失败处理建议:")
        print(f"   1. 检查文章内容是否符合要求")
        print(f"   2. 确保有封面图或正文图片")
        print(f"   3. 重新运行脚本发布失败的文章")

if __name__ == "__main__":
    main()
