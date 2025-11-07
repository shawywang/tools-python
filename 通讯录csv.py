import calendar
import csv
import os
import os.path
import re
import sys
from datetime import date
from datetime import datetime
from typing import List, Dict, Tuple

import lunardate
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# C:\ProgramData\miniconda3\python.exe -m pip install --upgrade pip
# C:\ProgramData\miniconda3\python.exe -m pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client dotenv
# 我的项目：https://console.cloud.google.com/welcome?project=shawywang
# 打开网页登录谷歌账号被拦截后，点高级，强行允许访问
# 联系人.txt注意：邮箱最多2个，电话最多3个，生日和纪念日仅支持农历
# 复制打印的结果到excel中，使用"；"分列后，xlsx改名为csv，从以下网页导入到谷歌联系人中
# https://contacts.google.com/?hl=zh-CN&tab=CC

oauth_token = r'C:\Users\wangxiao\不参与同步文件\github\谷歌桌面客户端1凭据.json'
from dotenv import load_dotenv

load_dotenv()  # 从.env文件加载配置
# 强制设置外网代理环境变量（Clash默认端口）
PROXY_URL = os.getenv('PROXY_URL', 'http://127.0.0.1:7890')  # 优先使用系统设置中的代理配置
os.environ['HTTP_PROXY'] = PROXY_URL
os.environ['HTTPS_PROXY'] = PROXY_URL
os.environ['http_proxy'] = PROXY_URL
os.environ['https_proxy'] = PROXY_URL

file_path = r"C:\Users\wangxiao\Nutstore\1\我的坚果云\我的文档\个人\联系人.txt"
out_csv_file = r"C:\Users\wangxiao\Downloads\contact.csv"
google_csv_title: List[str] = [
    "First Name", "Middle Name", "Last Name", "Phonetic First Name",
    "Phonetic Middle Name", "Phonetic Last Name", "Name Prefix", "Name Suffix",
    "Nickname", "File As", "Organization Name", "Organization Title",
    "Organization Department", "Birthday", "Notes", "Photo",
    "Labels", "E-mail 1 - Label", "E-mail 1 - Value", "E-mail 2 - Label",
    "E-mail 2 - Value", "Phone 1 - Label", "Phone 1 - Value", "Phone 2 - Label",
    "Phone 2 - Value", "Phone 3 - Label", "Phone 3 - Value"
]

month_map: Dict[str, int] = {
    '正': 1, '一': 1, '二': 2, '三': 3, '四': 4,
    '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
    '十': 10, '冬': 11, '腊': 12
}
day_map: Dict[str, int] = {
    '初一': 1, '初二': 2, '初三': 3, '初四': 4, '初五': 5,
    '初六': 6, '初七': 7, '初八': 8, '初九': 9, '初十': 10,
    '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
    '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
    '廿一': 21, '廿二': 22, '廿三': 23, '廿四': 24, '廿五': 25,
    '廿六': 26, '廿七': 27, '廿八': 28, '廿九': 29, '三十': 30
}


def withdraw(items: List[str], key_word: str) -> str:
    han = [i for i in items if key_word in i]
    if han:
        return han[0].lstrip(key_word)
    else:
        return ""


def div_str(item_str: str) -> List[str]:
    item = item_str.split(',')
    return [i for i in item if i]


def phone_num(num: str) -> str:
    if num == "0":
        return num
    elif len(num) <= 12:
        return f"+86 {num[:3]} {num[3:7]} {num[7:]}"  # +86 184 8275 7919
    else:
        print(f"号码有误：{num}")
        sys.exit(-1)


class GoogleCSV:
    def __init__(self, name: str):
        self.first_name = name
        self.middle_name = ""
        self.last_name = ""
        self.phonetic_first_name = ""
        self.phonetic_middle_name = ""
        self.phonetic_last_name = ""
        self.name_prefix = ""
        self.name_suffix = ""
        self.nickname = ""
        self.file_as = ""
        self.organization_name = ""
        self.organization_title = ""
        self.organization_department = ""
        self.birthday = ""
        self.notes = ""
        self.photo = ""
        self.labels = ""
        self.email_1_label = "住宅"
        self.email_1_value = ""
        self.email_2_label = "公司"
        self.email_2_value = ""
        self.phone_1_label = "主要"
        self.phone_1_value = ""
        self.phone_2_label = "手机"
        self.phone_2_value = ""
        self.phone_3_label = "其它"
        self.phone_3_value = ""


class Person:
    def __init__(self):
        self.name: str = ""
        self.nums: List[str] = []
        self.emails: List[str] = []
        self.birth: str = ""
        self.memorial: str = ""
        self.notes: str = ""


class GoogleCalendar:
    def __init__(self):
        pass

    def get_calendar_service(self):
        creds = None
        # 步骤1: 检查是否已有谷歌短期凭据.json (之前认证过1次)
        if os.path.exists(r'C:\Users\wangxiao\不参与同步文件\github\谷歌短期凭据.json'):
            print("✅ 找到现有的 谷歌短期凭据.json 文件")
            creds = Credentials.from_authorized_user_file(
                r'C:\Users\wangxiao\不参与同步文件\github\谷歌短期凭据.json',
                ['https://www.googleapis.com/auth/calendar']
            )
            print("已加载现有凭据")
        else:
            print("❌ 未找到 谷歌短期凭据.json 文件，需要重新认证")
        # 步骤2: 检查凭据是否有效
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("🔄 令牌已过期，正在刷新...")
                creds.refresh(Request())
                print("✅ 令牌刷新成功")
            else:
                print("🚀 开始OAuth 2.0认证流程...")
                # 检查谷歌桌面客户端1凭据.json是否存在
                if not os.path.exists(r'C:\Users\wangxiao\不参与同步文件\github\谷歌桌面客户端1凭据.json'):
                    print("❌ 错误: 未找到 谷歌桌面客户端1凭据.json 文件")
                    print("请从Google Cloud Console下载OAuth 2.0凭据文件")
                    sys.exit(-1)
                print("✅ 找到 谷歌桌面客户端1凭据.json 文件，开始认证...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    r'C:\Users\wangxiao\不参与同步文件\github\谷歌桌面客户端1凭据.json',
                    ['https://www.googleapis.com/auth/calendar']
                )
                print("🌐 正在打开浏览器进行Google账号认证...")
                creds = flow.run_local_server(port=0)
                print("✅ 认证成功！")
            # 步骤3: 保存令牌供下次使用
            print("💾 保存认证令牌到 谷歌短期凭据.json...")
            with open(r'C:\Users\wangxiao\不参与同步文件\github\谷歌短期凭据.json', 'w') as token:
                token.write(creds.to_json())
            print("✅ 谷歌短期凭据.json 文件已生成")
        # 步骤4: 创建API服务
        service = build('calendar', 'v3', credentials=creds)
        print("🎉 API服务创建成功！")
        return service

    def event_exists_by_summary(self, service, summary: str):  # 根据summary字段检查事件是否已存在
        try:  # 查询所有包含该summary的事件
            events_result = service.events().list(
                calendarId='primary',  # 我的日历中，"王骁"日历
                q=summary,  # 搜索关键词
                singleEvents=True,
                maxResults=10  # 限制结果数量
            ).execute()
            events = events_result.get('items', [])
            # 检查是否有完全匹配summary的事件
            for event in events:
                if event.get('summary') == summary:
                    print(f"⚠️ 事件已存在: {summary} (ID: {event.get('id')})，请先手动删除已存在的事件！")
                    sys.exit(-1)
        except Exception as e:
            print(f"❌ 检查事件存在性时出错: {e}")
            sys.exit(-1)

    def create_all_day_event(self, service, summary, event_date, description=""):
        self.event_exists_by_summary(service, summary)  # 检查是否有重复的
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'date': event_date.isoformat(),  # 使用'date'而不是'dateTime'表示全天事件
                'timeZone': 'Asia/Shanghai',
            },
            'end': {
                'date': event_date.isoformat(),  # 全天事件结束日期是同一天
                'timeZone': 'Asia/Shanghai',
            },
        }
        try:
            created_event = service.events().insert(calendarId='primary', body=event).execute()
            print(f"✅ 全天事件创建成功: {summary} ({event_date})")
            print(created_event.get('htmlLink'))
        except Exception as e:
            print(f"❌ 创建事件 {summary} 失败: {e}")
            sys.exit(-1)

    def clear_all_events(self, service):  # 清除日历中的所有事件
        try:
            events_result = service.events().list(
                calendarId='primary',
                maxResults=2500,  # 最大数量
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            if not events:
                print("📅 日历中没有任何事件")
                return 0

            print(f"🗑️ 找到 {len(events)} 个事件，开始删除...")

            deleted_count = 0
            for event in events:
                try:
                    event_id = event['id']
                    event_summary = event.get('summary', '无标题')
                    # 删除事件
                    service.events().delete(
                        calendarId='primary',
                        eventId=event_id
                    ).execute()

                    deleted_count += 1
                    print(f"✅ 已删除: {event_summary}")

                except Exception as e:
                    print(f"❌ 删除事件失败 {event.get('summary', '未知')}: {e}")

            print(f"🎉 删除完成！共删除了 {deleted_count} 个事件")
            return deleted_count

        except Exception as e:
            print(f"💥 清除事件时出错: {e}")
            return 0


class CulDate:
    def __init__(self, calendar: GoogleCalendar):
        self.cal = calendar

    def cul_date(self, pers: List[Person]):
        mention_info: List[List[str]] = []
        # ["还有x天", "下次生日年份", "下次生日月份", "下次生日天", "姓名", "生日or纪念日", "原生日字符串", "生日当年当天", "生日or纪念日距今x年x月x日"]
        for per in pers:
            if per.birth != "":
                per_birth = self.parse_lunar_date(per.birth)  # 输出也是农历
                days_to, date_new = self.days_to(per_birth)

                ment_info: List[str] = [days_to, date_new.year, date_new.month, date_new.day, per.name, "生日", per.birth, per_birth.toSolarDate().isoformat()]
                if per_birth.year < date.today().year:
                    y, m, d = self.date_diff(per_birth, date.today())
                    ment_info.extend([f"{y}", f"{m}", f"{d}"])
                mention_info.append(ment_info)

            if per.memorial != "":
                per_memo = self.parse_lunar_date(per.memorial)  # 输出也是农历
                days_to, date_new = self.days_to(per_memo)

                ment_info: List[str] = [days_to, date_new.year, date_new.month, date_new.day, per.name, "纪念日", per.memorial, per_memo.toSolarDate().isoformat()]
                if per_memo.year < date.today().year:
                    y, m, d = self.date_diff(per_memo, date.today())
                    ment_info.extend([f"{y}", f"{m}", f"{d}"])
                mention_info.append(ment_info)

        mention_info.sort(key=lambda x: int(x[0]))

        for m in mention_info:
            print(f"{m[0]}天后（{m[1]}-{m[2]}-{m[3]}），{m[4]}{m[5]}：{m[6]}（{m[7]}）", end='')
            if len(m) == 8:
                print("")
            else:
                print(f"，距今{m[8]}年{m[9]}个月{m[10]}天")

        print("\n\n=========谷歌日历========\n\n")
        service = self.cal.get_calendar_service()
        print("\n\n=========清除谷歌日历所有事件========\n\n")
        self.cal.clear_all_events(service)
        print("\n\n=========清除完成，开始添加========\n\n")
        for m in mention_info:
            summary: str = f"{m[4]}{m[5]}"
            if len(m) != 8:
                summary += f"（满{int(m[8]) + 1}年）"
            self.cal.create_all_day_event(
                service,
                summary,
                date(int(m[1]), int(m[2]), int(m[3])),
                f"{m[6]}（{m[7]}）"
            )
        print("🎉 ALL DONE !!!")

    def parse_lunar_date(self, date_str: str) -> lunardate.LunarDate:  # 解析农历日期字符串，支持格式："正月初五"、"1990年四月廿三"、"1999年腊月初三"、"冬月十三"
        year: int = 0
        year_match = re.search(r'(\d{4})年', date_str)
        if year_match:
            year = int(year_match.group(1))
            date_str = date_str.lstrip(f"{year}年")  # 移除年份部分
        else:
            year = datetime.now().year  # 默认当前年份

        lunar_month = month_map[date_str.split('月')[0][-1:]]
        lunar_day = day_map[date_str[-2:]]
        leap_month: bool = "闰" in date_str  # 是否闰月

        valid, lunar_date, _ = self.validate_lunar_date(year, lunar_month, lunar_day, leap_month)
        if valid:
            return lunar_date
        else:
            sys.exit(-1)

    def validate_lunar_date(self, year, month, day, is_leap) -> Tuple[bool, lunardate.LunarDate, date]:  # 验证农历日期是否存在
        try:
            lunar_date = lunardate.LunarDate(year, month, day, is_leap)
            solar_date = lunar_date.toSolarDate()
            return True, lunar_date, solar_date
        except Exception as e:
            return False, lunardate.LunarDate.today(), date.today()

    def find_day_solar_date(self, target_year, lunar_month, lunar_day: int, leap_month: bool) -> date:  # 在目标年份找到对应的生日公历日期
        valid, _, solar_leap = self.validate_lunar_date(target_year, lunar_month, lunar_day, leap_month)
        if valid:
            return solar_leap
        else:
            # 如果闰月不存在或不是闰月出生，使用普通月份
            valid_normal, _, solar_normal = self.validate_lunar_date(target_year, lunar_month, lunar_day, False)
            if valid_normal:
                return solar_normal
            else:
                print(f"日期有误，{target_year}找不到{lunar_month}{lunar_day}")
                sys.exit(-1)

    def days_to(self, per_d: lunardate.LunarDate):  # 今天，到x月x日还有多少天
        today = date.today()
        this_year_day = self.find_day_solar_date(today.year, per_d.month, per_d.day, per_d.isLeapMonth)

        if this_year_day >= today:
            return (this_year_day - today).days, this_year_day
        else:  # 如果今年的同月同日已经过去，计算明年的
            this_year_day = self.find_day_solar_date(today.year + 1, per_d.month, per_d.day, per_d.isLeapMonth)
            return (this_year_day - today).days, this_year_day

    def date_diff(self, old_date: lunardate.LunarDate, newr_date: date):
        old_date_solar = old_date.toSolarDate()
        if old_date_solar > newr_date:
            print(f"日期不能反向相减")
            sys.exit(-1)
        years = newr_date.year - old_date_solar.year
        months = newr_date.month - old_date_solar.month
        days = newr_date.day - old_date_solar.day
        if days < 0:  # 借月
            months -= 1
            if newr_date.month == 1:
                _, last_month_days = calendar.monthrange(newr_date.year - 1, 12)
            else:
                _, last_month_days = calendar.monthrange(newr_date.year, newr_date.month - 1)
            days += last_month_days
        if months < 0:  # 借年
            years -= 1
            months += 12
        return years, months, days


class Handle:
    def __init__(self, calendar: GoogleCalendar):
        self.csvs: List[GoogleCSV] = []
        self.cal = calendar

    def get_persons(self) -> List[Person]:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
            content = infile.read()
            da: List[str] = content.split('\n')
        da = [item for item in da if item]

        persons: List[Person] = []
        for s in da:
            items: List[str] = s.split('；')

            person = Person()
            person.name = items[0]
            person.nums = div_str(items[1])
            person.emails = div_str(withdraw(items, "邮箱："))
            person.birth = withdraw(items, "生日：")
            person.memorial = withdraw(items, "纪念日：")
            person.notes = withdraw(items, "备注：")
            persons.append(person)

        return persons

    def show_csv(self, persons: List[Person]):
        for per in persons:
            csv = GoogleCSV(per.name)
            if len(per.nums) == 1:
                csv.phone_1_value = phone_num(per.nums[0])
            elif len(per.nums) == 2:
                csv.phone_1_value = phone_num(per.nums[0])
                csv.phone_2_value = phone_num(per.nums[1])
            elif len(per.nums) == 3:
                csv.phone_1_value = phone_num(per.nums[0])
                csv.phone_2_value = phone_num(per.nums[1])
                csv.phone_3_value = phone_num(per.nums[2])
            else:
                print(f"{per.name} 电话信息有误，退出！")
                sys.exit(-1)

            if len(per.emails) == 0:
                pass
            elif len(per.emails) == 1:
                csv.email_1_value = per.emails[0]
            elif len(per.emails) == 2:
                csv.email_1_value = per.emails[0]
                csv.email_2_value = per.emails[1]
            else:
                print(f"{per.name} 邮箱信息有误，退出！")
                sys.exit(-1)

            if per.birth:
                csv.notes += f"生日：{per.birth}，"
            if per.memorial:
                csv.notes += f"纪念日：{per.memorial}，"
            if per.notes:
                csv.notes += f"备注：{per.notes}"
            self.csvs.append(csv)

        print("；".join(google_csv_title))
        for p in self.csvs:
            print(f"{p.first_name}；{p.middle_name}；{p.last_name}；{p.phonetic_first_name}；{p.phonetic_middle_name}；{p.phonetic_last_name}；{p.name_prefix}；{p.name_suffix}；{p.nickname}；{p.file_as}；{p.organization_name}；{p.organization_title}；{p.organization_department}；{p.birthday}；{p.notes}；{p.photo}；{p.labels}；{p.email_1_label}；{p.email_1_value}；{p.email_2_label}；{p.email_2_value}；{p.phone_1_label}；{p.phone_1_value}；{p.phone_2_label}；{p.phone_2_value}；{p.phone_3_label}；{p.phone_3_value}")

    def write_csv(self):
        csv_data: List[List[str]] = []
        for p in self.csvs:
            csv_d: List[str] = [
                p.first_name, p.middle_name, p.last_name, p.phonetic_first_name,
                p.phonetic_middle_name, p.phonetic_last_name, p.name_prefix, p.name_suffix,
                p.nickname, p.file_as, p.organization_name, p.organization_title,
                p.organization_department, p.birthday, p.notes, p.photo,
                p.labels, p.email_1_label, p.email_1_value, p.email_2_label,
                p.email_2_value, p.phone_1_label, p.phone_1_value, p.phone_2_label,
                p.phone_2_value, p.phone_3_label, p.phone_3_value
            ]
            csv_data.append(csv_d)
        # 创建并写入.csv文件
        with open(out_csv_file, mode='w', newline='', encoding='utf-8-sig') as csv_file:
            # csv文件，保存格式必须utf-8-sig带签名（BOM），因为excel通过BOM判断内容
            # 如果没有BOM，导致汉字乱码
            writer = csv.writer(csv_file)
            writer.writerow(google_csv_title)  # 写入表头
            writer.writerows(csv_data)  # 写入多行数据，会自动覆写
        print(f"完成！{out_csv_file}")


def main():
    g = GoogleCalendar()
    c = Handle(calendar=g)
    pers = c.get_persons()
    print("\n========以下是google通讯录csv格式打印，可复制到csv表格中导入google========\n")
    c.show_csv(pers)
    print("\n========以下写入.csv文件========\n")
    c.write_csv()
    print("\n========以下是联系人日期提醒========\n")

    d = CulDate(calendar=g)
    d.cul_date(pers)
    print("")


if __name__ == '__main__':
    main()
