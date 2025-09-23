#抓包下面链接的passToken和userId，填在脚本的后面
#https://account.xiaomi.com/pass/serviceLogin?callback=https%3A%2F%2Fapi.jr.airstarfinance.net%2Fsts%3Fsign%3D1dbHuyAmee0NAZ2xsRw5vhdVQQ8%253D%26followup%3Dhttps%253A%252F%252Fm.jr.airstarfinance.net%252Fmp%252Fapi%252Flogin%253Ffrom%253Dmipay_indexicon_TVcard%2526deepLinkEnable%253Dfalse%2526requestUrl%253Dhttps%25253A%25252F%25252Fm.jr.airstarfinance.net%25252Fmp%25252Factivity%25252FvideoActivity%25253Ffrom%25253Dmipay_indexicon_TVcard%252526_noDarkMode%25253Dtrue%252526_transparentNaviBar%25253Dtrue%252526cUserId%25253Dusyxgr5xjumiQLUoAKTOgvi858Q%252526_statusBarHeight%25253D137&sid=jrairstar&_group=DEFAULT&_snsNone=true&_loginType=ticket


import os
import time
import requests
import urllib3
import random
import pytz
import json
from datetime import datetime
from typing import Optional, Dict, Any, Union

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class RnlRequest:
    def __init__(self, cookies: Union[str, dict]):
        self.session = requests.Session()
        self._base_headers = {
            'Host': 'm.jr.airstarfinance.net',
            'User-Agent': 'Mozilla/5.0 (Linux; U; Android 14; zh-CN; M2012K11AC Build/UKQ1.230804.001; AppBundle/com.mipay.wallet; AppVersionName/6.89.1.5275.2323; AppVersionCode/20577595; MiuiVersion/stable-V816.0.13.0.UMNCNXM; DeviceId/alioth; NetworkType/WIFI; mix_version; WebViewVersion/118.0.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Mobile Safari/537.36 XiaoMi/MiuiBrowser/4.3',
        }
        self.update_cookies(cookies)

    def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        headers = {**self._base_headers, **kwargs.pop('headers', {})}
        try:
            resp = self.session.request(
                verify=False,
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json,
                headers=headers,
                **kwargs
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.log(f"[请求错误] {e}", level='error')
        except ValueError as e:
            logger.log(f"[JSON解析错误] {e}", level='error')
        return None

    def update_cookies(self, cookies: Union[str, dict]) -> None:
        if cookies:
            if isinstance(cookies, str):
                dict_cookies = self._parse_cookies(cookies)
            else:
                dict_cookies = cookies
            self.session.cookies.update(dict_cookies)
            self._base_headers['Cookie'] = self.dict_cookie_to_string(dict_cookies)

    @staticmethod
    def _parse_cookies(cookies_str: str) -> Dict[str, str]:
        return dict(
            item.strip().split('=', 1)
            for item in cookies_str.split(';')
            if '=' in item
        )

    @staticmethod
    def dict_cookie_to_string(cookie_dict):
        cookie_list = []
        for key, value in cookie_dict.items():
            cookie_list.append(f"{key}={value}")
        return "; ".join(cookie_list)

    def get(self, url: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[Dict[str, Any]]:
        return self.request('GET', url, params=params, **kwargs)

    def post(self, url: str, data: Optional[Union[Dict[str, Any], str, bytes]] = None,
             json: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[Dict[str, Any]]:
        return self.request('POST', url, data=data, json=json, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()


class RNL:
    def __init__(self, c, account_name="未知账号"):
        self.t_id = None
        self.account_name = account_name
        self.options = {
            "task_list": True,
            "complete_task": True,
            "receive_award": True,
            "task_item": True,
            "UserJoin": True,
        }
        self.activity_code = '2211-videoWelfare'
        self.rr = RnlRequest(c)

    def get_task_list(self):
        data = {
            'activityCode': self.activity_code,
        }
        try:
            response = self.rr.post(
                'https://m.jr.airstarfinance.net/mp/api/generalActivity/getTaskList',
                data=data,
            )
            if not response or response.get('code') != 0:
                logger.log(f"获取任务列表失败: {response}", level='error')
                return None
            target_tasks = []
            for task in response.get('value', {}).get('taskInfoList', []):
                if '浏览组浏览任务' in task.get('taskName', ''):
                    target_tasks.append(task)
            return target_tasks
        except Exception as e:
            logger.log(f'获取任务列表异常：{e}', level='error')
            return None

    def get_task(self, task_code):
        try:
            data = {
                'activityCode': self.activity_code,
                'taskCode': task_code,
                'jrairstar_ph': '98lj8puDf9Tu/WwcyMpVyQ==',
            }
            response = self.rr.post(
                'https://m.jr.airstarfinance.net/mp/api/generalActivity/getTask',
                data=data,
            )
            if not response or response.get('code') != 0:
                logger.log(f'获取任务信息失败：{response}', level='error')
                return None
            logger.log("获取任务信息成功。")
            return response.get('value', {}).get('taskInfo', {}).get('userTaskId')
        except Exception as e:
            logger.log(f'获取任务信息异常：{e}', level='error')
            return None

    def complete_task(self, task_id, t_id, brows_click_urlId):
        try:
            response = self.rr.get(
                f'https://m.jr.airstarfinance.net/mp/api/generalActivity/completeTask?activityCode={self.activity_code}&app=com.mipay.wallet&isNfcPhone=true&channel=mipay_indexicon_TVcard&deviceType=2&system=1&visitEnvironment=2&userExtra=%7B%22platformType%22:1,%22com.miui.player%22:%224.27.0.4%22,%22com.miui.video%22:%22v2024090290(MiVideo-UN)%22,%22com.mipay.wallet%22:%226.83.0.5175.2256%22%7D&taskId={task_id}&browsTaskId={t_id}&browsClickUrlId={brows_click_urlId}&clickEntryType=undefined&festivalStatus=0',
            )
            if not response or response.get('code') != 0:
                logger.log(f'完成任务失败：{response}', level='error')
                return None
            return response.get('value')
        except Exception as e:
            logger.log(f'完成任务异常：{e}', level='error')
            return None

    def receive_award(self, user_task_id):
        try:
            response = self.rr.get(
                f'https://m.jr.airstarfinance.net/mp/api/generalActivity/luckDraw?imei=&device=manet&appLimit=%7B%22com.qiyi.video%22:false,%22com.youku.phone%22:true,%22com.tencent.qqlive%22:true,%22com.hunantv.imgo.activity%22:true,%22com.cmcc.cmvideo%22:false,%22com.sankuai.meituan%22:true,%22com.anjuke.android.app%22:false,%22com.tal.abctimelibrary%22:false,%22com.lianjia.beike%22:false,%22com.kmxs.reader%22:true,%22com.jd.jrapp%22:false,%22com.smile.gifmaker%22:true,%22com.kuaishou.nebula%22:false%7D&activityCode={self.activity_code}&userTaskId={user_task_id}&app=com.mipay.wallet&isNfcPhone=true&channel=mipay_indexicon_TVcard&deviceType=2&system=1&visitEnvironment=2&userExtra=%7B%22platformType%22:1,%22com.miui.player%22:%224.27.0.4%22,%22com.miui.video%22:%22v2024090290(MiVideo-UN)%22,%22com.mipay.wallet%22:%226.83.0.5175.2256%22%7D'
            )
            if response and response['code'] != 0:
                logger.log(f'领取奖励失败：{response}', level='error')
                return False
            logger.log("领取奖励成功。")
            return True
        except Exception as e:
            logger.log(f'领取奖励异常：{e}', level='error')
            return False

    def queryUserJoinListAndQueryUserGoldRichSum(self, collect_summary=False):
        try:
            total_res = self.rr.get('https://m.jr.airstarfinance.net/mp/api/generalActivity/queryUserGoldRichSum?app=com.mipay.wallet&deviceType=2&system=1&visitEnvironment=2&userExtra={"platformType":1,"com.miui.player":"4.27.0.4","com.miui.video":"v2024090290(MiVideo-UN)","com.mipay.wallet":"6.83.0.5175.2256"}&activityCode=2211-videoWelfare')
            if not total_res or total_res['code'] != 0:
                logger.log(f'获取兑换视频天数失败：{total_res}', level='error')
                return False if not collect_summary else (False, None)
            total = f"{int(total_res['value']) / 100:.2f}天" if total_res else "未知"

            response = self.rr.get(
                f'https://m.jr.airstarfinance.net/mp/api/generalActivity/queryUserJoinList?&userExtra=%7B%22platformType%22:1,%22com.miui.player%22:%224.27.0.4%22,%22com.miui.video%22:%22v2024090290(MiVideo-UN)%22,%22com.mipay.wallet%22:%226.83.0.5175.2256%22%7D&activityCode={self.activity_code}&pageNum=1&pageSize=20',
            )
            if not response or response['code'] != 0:
                logger.log(f'查询任务完成记录失败：{response}', level='error')
                return False if not collect_summary else (False, None)

            history_list = response['value']['data']
            current_date = datetime.now().strftime("%Y-%m-%d")
            logger.log(f"当前用户兑换视频天数：{total}")
            logger.log(f"------------ {current_date} 当天任务记录 ------------")

            found_today_record = False
            today_total_days = 0.0
            for a in history_list:
                record_time = a['createTime']
                record_date = record_time[:10]
                if record_date == current_date:
                    days = int(a['value']) / 100
                    hours = days * 24
                    today_total_days += days
                    logger.log(f"{record_time} 领到视频会员，+{days:.2f}天（{hours:.1f}小时）")
                    found_today_record = True
            
            if not found_today_record:
                logger.log("今天暂无新的任务完成记录。")

            # 如果需要收集汇总信息，返回今日领取的时长
            if collect_summary:
                return True, today_total_days
            
            return True
        except Exception as e:
            logger.log(f'获取任务记录异常：{e}', level='error')
            return False if not collect_summary else (False, None)

    def main(self):
        logger.log("开始执行任务...")
        
        # 检查是否成功获取任务记录，这也可以作为账号是否有效的初步判断
        if not self.queryUserJoinListAndQueryUserGoldRichSum():
            return False, 0.0

        for i in range(2):
            logger.log(f"--- 正在执行第 {i+1} 个任务循环 ---")
            
            # 获取任务列表
            tasks = self.get_task_list()
            if not tasks:
                return False, 0.0
            task = tasks[0]
            
            try:
                t_id = task['generalActivityUrlInfo']['id']
                self.t_id = t_id
            except:
                t_id = self.t_id
            task_id = task['taskId']
            task_code = task['taskCode']
            brows_click_url_id = task['generalActivityUrlInfo']['browsClickUrlId']
            
            logger.log("等待13秒以完成任务浏览...")
            time.sleep(13)

            # 完成任务
            user_task_id = self.complete_task(
                t_id=t_id,
                task_id=task_id,
                brows_click_urlId=brows_click_url_id,
            )
            
            if not user_task_id:
                logger.log("尝试重新获取任务数据以领取奖励...")
                user_task_id = self.get_task(task_code=task_code)
                if not user_task_id:
                    return False, 0.0
            
            logger.log("等待2秒...")
            time.sleep(2)
            
            # 领取奖励
            if not self.receive_award(user_task_id=user_task_id):
                return False, 0.0

            logger.log("等待2秒...")
            time.sleep(2)

        # 获取今日领取记录用于汇总
        success, today_days = self.queryUserJoinListAndQueryUserGoldRichSum(collect_summary=True)
        if success:
            return True, today_days if today_days else 0.0
        else:
            return False, 0.0

class Logger:
    def __init__(self, log_file='xiaomi_wallet_log.txt', max_size_mb=2, backup_count=3):
        """
        初始化日志器
        
        Args:
            log_file (str): 日志文件名
            max_size_mb (int): 单个日志文件最大大小（MB），默认10MB
            backup_count (int): 保留的备份日志文件数量，默认3个
        """
        self.log_file = log_file
        self.max_size_bytes = max_size_mb * 1024 * 1024  # 转换为字节
        self.backup_count = backup_count
        
        # 在初始化时检查并清理日志
        self._check_and_rotate_log()

    def _check_and_rotate_log(self):
        """检查日志文件大小并进行轮转"""
        if not os.path.exists(self.log_file):
            return
            
        try:
            file_size = os.path.getsize(self.log_file)
            if file_size > self.max_size_bytes:
                self._rotate_log_files()
        except OSError as e:
            print(f"检查日志文件大小时出错: {e}")
    
    def _rotate_log_files(self):
        """轮转日志文件"""
        try:
            # 删除最旧的备份文件
            oldest_backup = f"{self.log_file}.{self.backup_count}"
            if os.path.exists(oldest_backup):
                os.remove(oldest_backup)
            
            # 重命名现有的备份文件
            for i in range(self.backup_count - 1, 0, -1):
                old_backup = f"{self.log_file}.{i}"
                new_backup = f"{self.log_file}.{i + 1}"
                if os.path.exists(old_backup):
                    os.rename(old_backup, new_backup)
            
            # 将当前日志文件重命名为第一个备份
            if os.path.exists(self.log_file):
                os.rename(self.log_file, f"{self.log_file}.1")
                
            print(f"日志文件已轮转，备份文件已更新")
            
        except OSError as e:
            print(f"轮转日志文件时出错: {e}")

    def log(self, message: str, level: str = 'info'):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}][{level.upper()}] {message}"
        
        # 打印到控制台
        print(log_message)
        
        # 在写入前检查文件大小
        self._check_and_rotate_log()
        
        # 写入日志文件
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + '\n')
        except IOError as e:
            print(f"无法写入日志文件: {e}")

def check_execution_time(start_hour=8, end_hour=9):
    """检查当前是否为北京时间指定的执行时间范围内"""
    # 设置北京时区
    beijing_tz = pytz.timezone('Asia/Shanghai')
    # 获取当前北京时间
    beijing_time = datetime.now(beijing_tz)
    current_hour = beijing_time.hour
    
    # 判断是否在指定时间范围内
    if start_hour <= current_hour < end_hour:
        return True, beijing_time
    else:
        return False, beijing_time

def random_delay(max_delay_seconds=600):
    """随机延迟函数
    
    Args:
        max_delay_seconds (int): 最大延迟秒数，默认600秒（10分钟）
    """
    delay_seconds = random.randint(0, max_delay_seconds)
    
    time.sleep(delay_seconds)

def get_xiaomi_cookies(pass_token, user_id):
    session = requests.Session()
    login_url = 'https://account.xiaomi.com/pass/serviceLogin?callback=https%3A%2F%2Fapi.jr.airstarfinance.net%2Fsts%3Fsign%3D1dbHuyAmee0NAZ2xsRw5vhdVQQ8%253D%26followup%3Dhttps%253A%252F%252Fm.jr.airstarfinance.net%252Fmp%252Fapi%252Flogin%253Ffrom%253Dmipay_indexicon_TVcard%2526deepLinkEnable%253Dfalse%2526requestUrl%253Dhttps%25253A%25252F%25252Fm.jr.airstarfinance.net%25252Fmp%25252Factivity%25252FvideoActivity%25253Ffrom%25253Dmipay_indexicon_TVcard%252526_noDarkMode%25253Dtrue%252526_transparentNaviBar%25253Dtrue%252526cUserId%25253Dusyxgr5xjumiQLUoAKTOgvi858Q%252526_statusBarHeight%25253D137&sid=jrairstar&_group=DEFAULT&_snsNone=true&_loginType=ticket'
    
    # 随机化User-Agent列表
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0'
    ]
    
    # 为每个账号随机选择User-Agent
    user_agent = random.choice(user_agents)
    
    # 完整的浏览器Headers
    headers = {
        'user-agent': user_agent,
        'cookie': f'passToken={pass_token}; userId={user_id};'
    }

    # 重试机制：最多重试3次，使用指数退避
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.log(f"🔄 {account_name} 正在尝试获取Cookie (第{attempt+1}次)")
            response = session.get(url=login_url, headers=headers, verify=False, timeout=30)
            # 记录响应状态
            logger.log(f"📡 {account_name} 响应状态码: {response.status_code}")
            if response.status_code != 200:
                logger.log(f"❌ {account_name} HTTP状态码异常: {response.status_code}", level='error')
                if attempt < max_retries - 1:
                    delay = (2 ** attempt) + random.uniform(1, 3)  # 指数退避 + 随机抖动
                    logger.log(f"⏰ {account_name} 等待 {delay:.1f} 秒后重试...")
                    time.sleep(delay)
                    continue
                else:
                    return None
            
            cookies = session.cookies.get_dict()
            # logger.log(f"🍪 {account_name} 获取到的Cookie数量: {len(cookies)}")
            
            # 检查关键Cookie
            if not cookies.get('cUserId'):
                logger.log(f"❌ {account_name} 缺少关键Cookie: cUserId", level='error')
                if attempt < max_retries - 1:
                    delay = (2 ** attempt) + random.uniform(1, 3)
                    logger.log(f"⏰ {account_name} 等待 {delay:.1f} 秒后重试...")
                    time.sleep(delay)
                    continue
                else:
                    return None
            
            result_cookie = f"cUserId={cookies.get('cUserId')};jrairstar_serviceToken={cookies.get('serviceToken')}"
            return result_cookie
            
        except requests.exceptions.Timeout:
            logger.log(f"⏰ {account_name} 请求超时", level='error')
        except requests.exceptions.ConnectionError as e:
            logger.log(f"🌐 {account_name} 连接错误: {str(e)}", level='error')
        except requests.exceptions.RequestException as e:
            logger.log(f"📡 {account_name} 请求异常: {str(e)}", level='error')
        except Exception as e:
            logger.log(f"💥 {account_name} 未知异常: {str(e)}", level='error')
        
        # 如果不是最后一次尝试，等待后重试
        if attempt < max_retries - 1:
            delay = (2 ** attempt) + random.uniform(1, 3)  # 指数退避策略
            logger.log(f"⏰ {account_name} 等待 {delay:.1f} 秒后重试...")
            time.sleep(delay)
    
    logger.log(f"❌ {account_name} Cookie获取失败，已达到最大重试次数", level='error')
    return None

def get_execution_count():
    """从文件中读取执行次数，如果文件不存在则返回0"""
    file_path = "run_count.txt"
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return int(f.read().strip())
        except (IOError, ValueError):
            return 0
    return 0

def update_execution_count(count):
    """将新的执行次数写入文件"""
    file_path = "run_count.txt"
    try:
        with open(file_path, 'w') as f:
            f.write(str(count + 1))
    except IOError as e:
        logger.log(f"无法更新执行次数文件: {e}", level='error')

def load_config(config_file='config.json'):
    """从配置文件加载账号信息和设置"""
    if not os.path.exists(config_file):
        logger.log(f"配置文件 {config_file} 不存在，请创建配置文件", level='error')
        return None
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 验证配置文件结构
        if 'accounts' not in config:
            logger.log("配置文件缺少 'accounts' 字段", level='error')
            return None
        
        if 'settings' not in config:
            logger.log("配置文件缺少 'settings' 字段，使用默认设置", level='warning')
            config['settings'] = {
                'max_delay_seconds': 600,
                'execution_time_start': 8,
                'execution_time_end': 9
            }
        
        # logger.log(f"成功加载配置文件，共找到 {len(config['accounts'])} 个账号")
        return config
        
    except json.JSONDecodeError as e:
        logger.log(f"配置文件JSON格式错误: {e}", level='error')
        return None
    except IOError as e:
        logger.log(f"读取配置文件失败: {e}", level='error')
        return None

def print_summary_table(account_results):
    """打印账号汇总表格"""
    if not account_results:
        logger.log("\n🔍 没有账号执行成功，无法生成汇总表格")
        return
    
    logger.log("\n" + "=" * 80)
    logger.log("📊 账号执行汇总表格")
    logger.log("=" * 80)
    
    # 计算最大列宽以对齐表格
    max_name_len = max(len(result['name']) for result in account_results)
    max_name_len = max(max_name_len, 10)  # 最小列宽设为10，适配中文"账号名称"
    
    # 定义各列的宽度
    name_width = max_name_len
    status_width = 12  # "执行状态" + 状态内容
    days_width = 14    # "今日领取天数" + 数值
    hours_width = 14   # "今日领取小时" + 数值
    
    # 打印表头
    header = f"| {'账号名称':<{name_width}} | {'执行状态':<{status_width}} | {'今日领取天数':<{days_width}} | {'今日领取小时':<{hours_width}} |"
    separator = "+" + "-" * (name_width + 2) + "+" + "-" * (status_width + 2) + "+" + "-" * (days_width + 2) + "+" + "-" * (hours_width + 2) + "+"
    
    logger.log(separator)
    logger.log(header)
    logger.log(separator)
    
    # 打印每个账号的数据
    total_days = 0.0
    successful_accounts = 0
    failed_accounts = 0
    
    for result in account_results:
        name = result['name']
        success = result['success']
        days = result['days']
        hours = days * 24
        
        status = "✅ 成功" if success else "❌ 失败"
        if success:
            successful_accounts += 1
            total_days += days
        else:
            failed_accounts += 1
        
        days_str = f"{days:.2f}" if success else "0.00"
        hours_str = f"{hours:.1f}" if success else "0.0"
        
        row = f"| {name:<{name_width}} | {status:<{status_width}} | {days_str:<{days_width}} | {hours_str:<{hours_width}} |"
        logger.log(row)
    
    logger.log(separator)
    
    # 打印汇总统计
    total_hours = total_days * 24
    logger.log(f"📈 汇总统计:")
    logger.log(f"   • 成功账号: {successful_accounts} 个")
    logger.log(f"   • 失败账号: {failed_accounts} 个")
    # logger.log(f"   • 总计领取: {total_days:.2f} 天 ({total_hours:.1f} 小时)")
    # logger.log(f"   • 平均每成功账号: {total_days/successful_accounts:.2f} 天" if successful_accounts > 0 else "   • 平均每成功账号: 0.00 天")
    logger.log("=" * 80)


if __name__ == "__main__":
    logger = Logger()
    
    # 加载配置文件
    config = load_config()
    if not config:
        logger.log("无法加载配置文件，脚本退出", level='error')
        exit(1)
    
    settings = config['settings']
    accounts = config['accounts']
    
    # 检查执行时间
    is_target_time, current_time = check_execution_time(
        settings['execution_time_start'], 
        settings['execution_time_end']
    )
    
    if not is_target_time:
        logger.log("正在测试")
        logger.log(f"当前时间不在{settings['execution_time_start']}:00-{settings['execution_time_end']}:00范围内，脚本结束执行")
        time.sleep(5)
        exit(0)
    else:
        # 随机延迟
        random_delay(settings.get('max_delay_seconds', 600))
    
    # 获取并更新执行次数
    run_count = get_execution_count() + 1
    update_execution_count(run_count)
    
    logger.log(f"脚本已执行 {run_count} 次", level='info')
    logger.log(">>>>>>>>>> 脚本开始执行 <<<<<<<<<<")

    cookie_list = []
    for i, account in enumerate(accounts):
        if not account.get('passToken') or account.get('passToken') == 'xxxxx':
            logger.log(f"⚠️ 检测到账号 {account.get('name', account.get('userId', '未知'))} 配置为空，跳过此账号。")
            continue

        account_name = account.get('name', account.get('userId', '未知账号'))
        logger.log(f"\n>>>>>>>>>> 正在处理 {account_name} <<<<<<<<<<")
        
        # 在账号间添加延迟，避免并发请求
        if i > 0:  # 第一个账号不需要延迟
            delay = random.uniform(3, 8)  # 3-8秒随机延迟
            time.sleep(delay)
        
        new_cookie = get_xiaomi_cookies(account['passToken'], account['userId'])
        if new_cookie:
            cookie_list.append(new_cookie)
        else:
            logger.log(f"❌ {account_name} Cookie获取失败，请检查配置")

    logger.log(f"\n>>>>>>>>>> 共获取到{len(cookie_list)}个有效Cookie <<<<<<<<<<")

    # 用于收集账号执行结果的列表
    account_results = []
    
    for index, c in enumerate(cookie_list):
        logger.log(f"\n--------- 开始执行第{index+1}个账号 ---------")
        
        # 获取账号名称（从配置中找到对应的账号）
        account_name = f"账号{index+1}"
        for account in accounts:
            if account.get('passToken') and account.get('passToken') != 'xxxxx':
                if accounts.index(account) == index:
                    account_name = account.get('name', account.get('userId', f"账号{index+1}"))
                    break
        
        try:
            success, today_days = RNL(c, account_name).main()
            account_results.append({
                'name': account_name,
                'success': success,
                'days': today_days
            })
            
            if success:
                logger.log(f"✅ 第{index+1}个账号任务执行成功！")
            else:
                logger.log(f"❌ 第{index+1}个账号任务执行失败。", level='error')
        except Exception as e:
            logger.log(f"⚠️ 第{index+1}个账号执行异常: {str(e)}", level='error')
            account_results.append({
                'name': account_name,
                'success': False,
                'days': 0.0
            })
        logger.log(f"--------- 第{index+1}个账号执行结束 ---------")

    # 显示汇总表格
    print_summary_table(account_results)
    
    logger.log("\n>>>>>>>>>> 脚本执行完毕 <<<<<<<<<<\n")
