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
    def __init__(self, c):
        self.t_id = None
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
            if response and response['code'] != 0:
                logger.log(f"获取任务列表失败: {response}", level='error')
                return None
            target_tasks = []
            for task in response['value']['taskInfoList']:
                if '浏览组浏览任务' in task['taskName']:
                    target_tasks.append(task)
            logger.log("获取任务列表成功。")
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
            if response and response['code'] != 0:
                logger.log(f'获取任务信息失败：{response}', level='error')
                return None
            logger.log("获取任务信息成功。")
            return response['value']['taskInfo']['userTaskId']
        except Exception as e:
            logger.log(f'获取任务信息异常：{e}', level='error')
            return None

    def complete_task(self, task_id, t_id, brows_click_urlId):
        try:
            response = self.rr.get(
                f'https://m.jr.airstarfinance.net/mp/api/generalActivity/completeTask?activityCode={self.activity_code}&app=com.mipay.wallet&isNfcPhone=true&channel=mipay_indexicon_TVcard&deviceType=2&system=1&visitEnvironment=2&userExtra=%7B%22platformType%22:1,%22com.miui.player%22:%224.27.0.4%22,%22com.miui.video%22:%22v2024090290(MiVideo-UN)%22,%22com.mipay.wallet%22:%226.83.0.5175.2256%22%7D&taskId={task_id}&browsTaskId={t_id}&browsClickUrlId={brows_click_urlId}&clickEntryType=undefined&festivalStatus=0',
            )
            if response and response['code'] != 0:
                logger.log(f'完成任务失败：{response}', level='error')
                return None
            logger.log("完成任务成功。")
            return response['value']
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

    def queryUserJoinListAndQueryUserGoldRichSum(self):
        try:
            total_res = self.rr.get('https://m.jr.airstarfinance.net/mp/api/generalActivity/queryUserGoldRichSum?app=com.mipay.wallet&deviceType=2&system=1&visitEnvironment=2&userExtra={"platformType":1,"com.miui.player":"4.27.0.4","com.miui.video":"v2024090290(MiVideo-UN)","com.mipay.wallet":"6.83.0.5175.2256"}&activityCode=2211-videoWelfare')
            if not total_res or total_res['code'] != 0:
                logger.log(f'获取兑换视频天数失败：{total_res}', level='error')
                return False
            total = f"{int(total_res['value']) / 100:.2f}天" if total_res else "未知"

            response = self.rr.get(
                f'https://m.jr.airstarfinance.net/mp/api/generalActivity/queryUserJoinList?&userExtra=%7B%22platformType%22:1,%22com.miui.player%22:%224.27.0.4%22,%22com.miui.video%22:%22v2024090290(MiVideo-UN)%22,%22com.mipay.wallet%22:%226.83.0.5175.2256%22%7D&activityCode={self.activity_code}&pageNum=1&pageSize=20',
            )
            if not response or response['code'] != 0:
                logger.log(f'查询任务完成记录失败：{response}', level='error')
                return False

            history_list = response['value']['data']
            current_date = datetime.now().strftime("%Y-%m-%d")
            logger.log(f"当前用户兑换视频天数：{total}")
            logger.log(f"------------ {current_date} 当天任务记录 ------------")

            found_today_record = False
            for a in history_list:
                record_time = a['createTime']
                record_date = record_time[:10]
                if record_date == current_date:
                    days = int(a['value']) / 100
                    hours = days * 24
                    logger.log(f"{record_time} 领到视频会员，+{days:.2f}天（{hours:.1f}小时）")
                    found_today_record = True
            
            if not found_today_record:
                logger.log("今天暂无新的任务完成记录。")

            return True
        except Exception as e:
            logger.log(f'获取任务记录异常：{e}', level='error')
            return False

    def main(self):
        logger.log("开始执行任务...")
        
        # 检查是否成功获取任务记录，这也可以作为账号是否有效的初步判断
        if not self.queryUserJoinListAndQueryUserGoldRichSum():
            return False

        for i in range(2):
            logger.log(f"--- 正在执行第 {i+1} 个任务循环 ---")
            
            # 获取任务列表
            tasks = self.get_task_list()
            if not tasks:
                return False
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
                    return False
            
            logger.log("等待2秒...")
            time.sleep(2)
            
            # 领取奖励
            if not self.receive_award(user_task_id=user_task_id):
                return False

            logger.log("等待2秒...")
            time.sleep(2)

        # 记录
        self.queryUserJoinListAndQueryUserGoldRichSum()
        logger.log("所有任务执行完毕。")
        return True

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
    delay_minutes = delay_seconds // 60
    delay_seconds_remainder = delay_seconds % 60
    
    if delay_minutes > 0:
        logger.log(f"随机延迟 {delay_minutes} 分 {delay_seconds_remainder} 秒后开始执行...")
    else:
        logger.log(f"随机延迟 {delay_seconds} 秒后开始执行...")
    
    time.sleep(delay_seconds)
    logger.log("延迟结束，开始执行任务")

def get_xiaomi_cookies(pass_token, user_id):
    session = requests.Session()
    login_url = 'https://account.xiaomi.com/pass/serviceLogin?callback=https%3A%2F%2Fapi.jr.airstarfinance.net%2Fsts%3Fsign%3D1dbHuyAmee0NAZ2xsRw5vhdVQQ8%253D%26followup%3Dhttps%253A%252F%252Fm.jr.airstarfinance.net%252Fmp%252Fapi%252Flogin%253Ffrom%253Dmipay_indexicon_TVcard%2526deepLinkEnable%253Dfalse%2526requestUrl%253Dhttps%25253A%25252F%25252Fm.jr.airstarfinance.net%25252Fmp%25252Factivity%25252FvideoActivity%25253Ffrom%25253Dmipay_indexicon_TVcard%252526_noDarkMode%25253Dtrue%252526_transparentNaviBar%25253Dtrue%252526cUserId%25253Dusyxgr5xjumiQLUoAKTOgvi858Q%252526_statusBarHeight%25253D137&sid=jrairstar&_group=DEFAULT&_snsNone=true&_loginType=ticket'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
        'cookie': f'passToken={pass_token}; userId={user_id};'
    }

    try:
        session.get(url=login_url, headers=headers, verify=False)
        cookies = session.cookies.get_dict()
        if not cookies.get('cUserId'):
            return None
        return f"cUserId={cookies.get('cUserId')};jrairstar_serviceToken={cookies.get('serviceToken')}"
    except Exception as e:
        logger.log(f"获取Cookie失败: {e}", level='error')
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
        
        logger.log(f"成功加载配置文件，共找到 {len(config['accounts'])} 个账号")
        return config
        
    except json.JSONDecodeError as e:
        logger.log(f"配置文件JSON格式错误: {e}", level='error')
        return None
    except IOError as e:
        logger.log(f"读取配置文件失败: {e}", level='error')
        return None


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
    logger.log(f"当前北京时间：{current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not is_target_time:
        logger.log("正在测试")
        logger.log(f"当前时间不在{settings['execution_time_start']}:00-{settings['execution_time_end']}:00范围内，脚本结束执行")
        time.sleep(5)
        exit(0)
    else:
        logger.log(f"当前时间在{settings['execution_time_start']}:00-{settings['execution_time_end']}:00范围内，准备执行任务")
        # 随机延迟
        random_delay(settings.get('max_delay_seconds', 600))
    
    # 获取并更新执行次数
    run_count = get_execution_count() + 1
    update_execution_count(run_count)
    
    logger.log(f"脚本已执行 {run_count} 次", level='info')
    logger.log(">>>>>>>>>> 脚本开始执行 <<<<<<<<<<")

    cookie_list = []
    for account in accounts:
        if not account.get('passToken') or account.get('passToken') == 'xxxxx':
            logger.log(f"⚠️ 检测到账号 {account.get('name', account.get('userId', '未知'))} 配置为空，跳过此账号。")
            continue

        account_name = account.get('name', account.get('userId', '未知账号'))
        logger.log(f"\n>>>>>>>>>> 正在处理 {account_name} <<<<<<<<<<")
        new_cookie = get_xiaomi_cookies(account['passToken'], account['userId'])
        if new_cookie:
            cookie_list.append(new_cookie)
            logger.log(f"✅ {account_name} Cookie获取成功")
        else:
            logger.log(f"❌ {account_name} Cookie获取失败，请检查配置")

    logger.log(f"\n>>>>>>>>>> 共获取到{len(cookie_list)}个有效Cookie <<<<<<<<<<")

    for index, c in enumerate(cookie_list):
        logger.log(f"\n--------- 开始执行第{index+1}个账号 ---------")
        try:
            success = RNL(c).main()
            if success:
                logger.log(f"✅ 第{index+1}个账号任务执行成功！")
            else:
                logger.log(f"❌ 第{index+1}个账号任务执行失败。", level='error')
        except Exception as e:
            logger.log(f"⚠️ 第{index+1}个账号执行异常: {str(e)}", level='error')
        logger.log(f"--------- 第{index+1}个账号执行结束 ---------")

    logger.log("\n>>>>>>>>>> 脚本执行完毕 <<<<<<<<<<")
