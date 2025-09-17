# 小米钱包签到脚本配置说明

## 配置文件说明

脚本现在支持从配置文件读取账号信息，无需在代码中硬编码敏感信息。

### 配置文件格式

配置文件为 `config.json`，格式如下：

```json
{
    "accounts": [
        {
            "name": "账号1描述",
            "passToken": "您的passToken",
            "userId": "您的userId"
        },
        {
            "name": "账号2描述", 
            "passToken": "您的passToken",
            "userId": "您的userId"
        }
    ],
    "settings": {
        "max_delay_seconds": 600,
        "execution_time_start": 8,
        "execution_time_end": 9
    }
}
```

### 参数说明

#### accounts 数组
- `name`: 账号的描述名称，方便识别（可选）
- `passToken`: 从抓包获取的 passToken
- `userId`: 从抓包获取的 userId

#### settings 配置
- `max_delay_seconds`: 最大随机延迟时间（秒），默认600秒（10分钟）
- `execution_time_start`: 开始执行时间（小时），默认8点
- `execution_time_end`: 结束执行时间（小时），默认9点

### 获取 passToken 和 userId

1. 访问以下链接：
   ```
   https://account.xiaomi.com/pass/serviceLogin?callback=https%3A%2F%2Fapi.jr.airstarfinance.net%2Fsts%3Fsign%3D1dbHuyAmee0NAZ2xsRw5vhdVQQ8%253D%26followup%3Dhttps%253A%252F%252Fm.jr.airstarfinance.net%252Fmp%252Fapi%252Flogin%253Ffrom%253Dmipay_indexicon_TVcard%2526deepLinkEnable%253Dfalse%2526requestUrl%253Dhttps%25253A%25252F%25252Fm.jr.airstarfinance.net%25252Fmp%25252Factivity%25252FvideoActivity%25253Ffrom%25253Dmipay_indexicon_TVcard%252526_noDarkMode%25253Dtrue%252526_transparentNaviBar%25253Dtrue%252526cUserId%25253Dusyxgr5xjumiQLUoAKTOgvi858Q%252526_statusBarHeight%25253D137&sid=jrairstar&_group=DEFAULT&_snsNone=true&_loginType=ticket
   ```

2. 使用浏览器开发者工具抓包获取 `passToken` 和 `userId`

### 使用方法

1. 复制 `config_template.json` 为 `config.json`
2. 填入您的账号信息
3. 根据需要调整设置参数
4. 运行脚本：`python xiaomi.py`

### 注意事项

- 请妥善保管配置文件，不要泄露账号信息
- 可以将 `config.json` 添加到 `.gitignore` 中避免意外提交
- 支持配置多个账号，脚本会依次处理
- 如果某个账号配置为空或无效，会自动跳过