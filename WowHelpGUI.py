import json
import time
from threading import Thread

import wx
import wx.adv

from core.wow_helper import WowClientGuard
from conf.CONFIG import *

WELCOME_TEXT = '一区德姆塞卡尔《阿拉索帝国》公会友情提供，欢迎各位朋友加入！'
ALPHA_ONLY = 1
DIGIT_ONLY = 2
# Button definitions
ID_START = wx.NewId()
ID_STOP = wx.NewId()

# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()

FEATURE_TEXT = '''
支持功能和点特如下：
1.隐匿模式，开启后魔兽世界窗口隐藏(任务栏和系统托盘均不显示)，同时防掉线挂机动作与游戏登录均为后台执行。
2.执行随机动作防止角色暂离。(随机动作包含走路，跳跃，释放技能等动作组合，行走的时间与动作间隔休眠时间均为随机，避免被检测到挂机)
3.游戏服务器断开连接声音提醒。
4.游戏服务器断连后重新启动游戏登录。
5.网络异常检测提醒，网络异常时，触发windows消息提醒。
'''

HELP_TEXT = '''
1. 使用前请运行ctrl+2 或点击“配置”--“配置修改” 修改参数配置。
2. 请将魔兽世界设置为窗口模式，取消全屏。 系统--->图形--->显示模式--->窗口
3. 检查游戏中得截图快捷设置为"Print Screen", 主菜单--->按键设置--->其他--->截图。
4. 请先登录暴雪战网，设置战网启动游戏时"保持战网窗口开启"，保存后选择好登录游戏为魔兽世界怀旧和对应账号。设置--->综合  
    1)当我点击窗口上方X时，选择最小化战网到系统栏。
    2)当我启动一个游戏时，选择最小化战网窗口。
    3)勾选"游戏结束时恢复战网窗口"。
5. 请在“配置”--->“配置修改” 设置防掉线期间可以成功释放的技能快捷键，为了避免被检测重复动作挂机，请尽量多输入可释放技能。
6. 游戏检测到掉线后启动游戏和登录角色过程中，请不要手工干预避免出现异常。
'''

UPDATE_LOG = '''
v2.3.1
1. 增加未认证登录场景检测。
2. 增加网络异常检测与提醒。
3. 界面场景识别增加OCR支持
------------------------------------------------------------------------------
v2.2.2   (2020.02.26)
1. 屏蔽服务器连接、服务器认证、服务器刷新状态监测，避免服务器断开连接时校验出错。
------------------------------------------------------------------------------
v2.2.1   (2020.02.26)
1. 优化显示图标
2. 优化场景检查机制，避免窗口切换，正常情况下用户无感知。
3. 增加隐匿模式选项和窗口隐藏/开启功能。隐匿模式开启后游戏窗口自动隐藏，后台运行wow和防掉线守护。
4. 增加异常停止windows消息提醒
5. 优化游戏强制关闭方式，避免窗口切换。
6. 增加服务器连接、服务器认证、服务器刷新场景检测.
-------------------------------------------------------------------------------
v2.1.3   (2020.02.24)
1. 优化场景比对增加场景类型和样本文件
2. 优化场景检查机制。
3. 优化强制关闭游戏逻辑，增加窗口校验
-------------------------------------------------------------------------------
v2.1.2   (2020.02.23)
1. 修复截图比对历史文件无法清理的问题。
2. 优化强制关闭游戏逻辑, wow窗口存在时循环执行
3. 优化执行日志输出方式为追加。
4. 优化开始按钮，终止按钮以及功能勾选框得可选与不可选状态
5. 调整掉线比对的样本图片区域
6. 等待进入角色登录环节增加掉线检查
7. 后台任务异常终止时自动切换开始按钮，终止按钮以及功能勾选框得可选与不可选状态
8. 增加版本更新记录
9. 优化日志显示内容，对于检查结果正常得日志不输出
'''


def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)


class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""

    def __init__(self, data, flag=0, instance_id=-1, notifi_message='', *args, **kwargss):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data
        self.flag = flag
        self.instance_id = instance_id
        self.notifi_message = notifi_message


# Thread class that executes processing
class WorkerThread(Thread):
    """Worker Thread Class."""

    def __init__(self, notify_window, skills, is_random_action, is_warning, is_auto_login, login_loadtime,
                 clear_shoot_file, compare_value, check_offline_interval, sleep_min_time, sleep_max_time,
                 keep_alive=True, start_guard=False, *args, **kwargs):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._notify_window = notify_window
        self.instance_id = time.time()
        self.sleep_range = [sleep_min_time, sleep_max_time]

        def log_to_app(log_text, log_flag=0, notifi_message='', instance_id=self.instance_id, *args, **kwargss):
            return wx.PostEvent(self._notify_window,
                                ResultEvent(data=log_text, flag=log_flag, instance_id=instance_id,
                                            notifi_message=notifi_message, *args, **kwargs))

        self.wow_guard_instance = WowClientGuard(skills, is_random_action, is_warning, is_auto_login, login_loadtime,
                                                 clear_shoot_file, compare_value, check_offline_interval,
                                                 log_function=log_to_app, *args, **kwargs)
        self._keep_alive = keep_alive
        self._start_guard = start_guard
        self.start()

    def run(self):
        """Run Worker Thread."""
        while self._keep_alive:
            if self._start_guard:
                self.wow_guard_instance.fuck_wow_offline(self.sleep_range)
            time.sleep(1)

    def guard_client(self):
        """
        开启运行标志
        :return: 
        """
        self._start_guard = True

    def stop_guard(self):
        """
        助手停止运行入口方法
        :return: 
        """
        self.wow_guard_instance.stop()
        self.abort()

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._keep_alive = False
        self._start_guard = False

    def skip_role(self):
        """
        跳过角色校验
        :return: 
        """
        self.wow_guard_instance.check_role = self.wow_guard_instance.IS_SKIP

    def wow_show(self):
        """
        显示wow窗口
        :return: 
        """
        self.wow_guard_instance.wow_show()

    def wow_hide(self):
        """
        隐藏wow窗口
        :return: 
        """
        self.wow_guard_instance.wow_hide()




import string
class MyValidator(wx.Validator):
    def __init__(self, flag=None, pyVar=None):
        wx.Validator.__init__(self)
        self.flag = flag
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return MyValidator(self.flag)

    def Validate(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()
        print(val)

        if self.flag == ALPHA_ONLY:
            for x in val:
                if x not in string.ascii_letters:
                    return False

        elif self.flag == DIGIT_ONLY:
            for x in val:
                if x not in string.digits:
                    return False

        return True

    def OnChar(self, event):
        key = event.GetKeyCode()

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if self.flag == ALPHA_ONLY and chr(key) in string.ascii_letters:
            event.Skip()
            return

        if self.flag == DIGIT_ONLY and chr(key) in string.digits:
            event.Skip()
            return

        if not wx.Validator.IsSilent():
            wx.Bell()

        # Returning without calling even.Skip eats the event before it
        # gets to the text control
        return

class WowHelperFrame(wx.Frame):
    def __init__(self, parent, title, size):
        super(WowHelperFrame, self).__init__(parent, title=title, size=size)
        self.init_ui()
        EVT_RESULT(self, self.on_logout)
        # And indicate we don't have a worker thread yet
        self.worker = None
        self.param_dict = self.load_config_fille()
        print(self.param_dict)
        if not self.worker:
            self.param_dict.update({'is_warning': self.cb1.Value,
                                    'is_auto_login': self.cb2.Value,
                                    'is_random_action': self.cb3.Value})
            self.worker = WorkerThread(self, **self.param_dict)

    def init_wow_worker(self, start_guard=False):
        if not self.worker:
            self.param_dict.update({'is_warning': self.cb1.Value,
                                    'is_auto_login': self.cb2.Value,
                                    'is_random_action': self.cb3.Value})
            self.worker = WorkerThread(self, start_guard=start_guard, keep_alive=True, **self.param_dict)

    def init_ui(self):
        pnl = wx.Panel(self)
        self.icon = wx.Icon(ICON_FILE, wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        self.cb1 = wx.CheckBox(pnl, label='掉线提醒', name='check_warning')
        self.cb2 = wx.CheckBox(pnl, label='自动登录', name='check_login')
        self.cb3 = wx.CheckBox(pnl, label='随机动作', name='check_action')
        self.start_button = wx.Button(pnl, ID_START, label="开始运行", name='button_start')
        self.stop_button = wx.Button(pnl, ID_STOP, label="停止运行", name='button_stop')
        self.stop_button.Disable()
        display_wow_button = wx.Button(pnl, -1, label='显示WOW窗口', name='display_wow')
        self.Bind(wx.EVT_BUTTON, self.on_display_button, display_wow_button)
        hide_wow_button = wx.Button(pnl, -1, label='隐藏WOW窗口', name='hide_wow')
        self.Bind(wx.EVT_BUTTON, self.on_hide_button, hide_wow_button)
        self.log = wx.TextCtrl(pnl, -1, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        box = wx.BoxSizer(wx.HORIZONTAL)
        for i in [self.cb1, self.cb2, self.cb3, self.start_button, self.stop_button, display_wow_button,
                  hide_wow_button]:
            if i.ClassName == 'wxCheckBox':
                i.SetValue(False if i.Name == 'check_warning' else True)
            box.Add(i, 1, wx.Bottom)
        box2 = wx.BoxSizer(wx.VERTICAL)
        box2.Add(box)
        box2.Add(self.log, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE)
        pnl.SetSizer(box2)
        self.makemenu_bar()
        self.CreateStatusBar()
        self.SetStatusText(WELCOME_TEXT)
        self.Centre()

        self.Bind(wx.EVT_BUTTON, self.on_run_button, id=ID_START)
        self.Bind(wx.EVT_BUTTON, self.on_stop_button, id=ID_STOP)
        self.Bind(wx.EVT_CLOSE, self.on_close, self)
        self.Show(True)

    def makemenu_bar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        file_menu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        config_param_item = file_menu.Append(-1, "&配置修改...\tCtrl-2",
                                             "修改助手配置参数")
        self.Bind(wx.EVT_MENU, self.on_config_param, config_param_item)
        file_menu.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's
        # label
        exit_item = file_menu.Append(wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        # 定义异常场景处理
        deal_menu = wx.Menu()
        skip_role_item = deal_menu.Append(-1, "&跳过角色登录校验...\tAlt-1", "角色登录校验卡主时，手工跳过角色登录校验")
        self.Bind(wx.EVT_MENU, self.on_skip_role, skip_role_item)
        # Now a help menu for the about item
        help_menu = wx.Menu()
        feature_item = help_menu.Append(-1, '&程序功能特性')
        self.Bind(wx.EVT_MENU, self.on_feature, feature_item)
        about_item = help_menu.Append(-1, '&注意事项')
        self.Bind(wx.EVT_MENU, self.OnAbout, about_item)
        update_log_item = help_menu.Append(-1, '&版本更新内容')
        self.Bind(wx.EVT_MENU, self.on_update_log, update_log_item)

        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, "&配置")
        menu_bar.Append(deal_menu, "&异常处理")
        menu_bar.Append(help_menu, "&帮助")
        self.SetMenuBar(menu_bar)

    def on_close(self, event):
        # 关闭时停止后台线程
        if self.worker:
            self.worker.stop_guard()
        self.Destroy()

    def on_exit(self, event):
        """Close the frame, terminating the application."""
        if self.worker:
            self.worker.stop_guard()
        self.Close(True)

    def on_config_param(self, event):
        dlg = ConfigEditDialog(self, self.param_dict)
        if dlg.ShowModal() == wx.ID_OK:
            for text_name in ['sleep_min_time_text', 'sleep_max_time_text', 'check_offline_interval_text',
                              'login_loadtime_text', 'skills_text', 'compare_value_text', 'clear_shoot_file',
                              'hiden_mode', 'app_id', 'api_key', 'scret_key']:
                text_value = dlg.input_texts[text_name].Value
                if isinstance(text_value, str) and text_value.isdigit():
                    text_value = int(text_value)
                elif isinstance(text_value, str) and text_value.replace('.', '').isdigit():
                    text_value = float(text_value)
                self.param_dict[text_name.replace('_text', '')] = text_value
            # 保存配置文件
            with open('wow_help_config.json', 'w') as f:
                json.dump(self.param_dict, f, indent=4)
        dlg.Destroy()

    def on_skip_role(self, event):
        if self.worker:
            self.worker.skip_role()

    def on_feature(self, event):
        """Display an About Dialog"""
        wx.MessageBox(FEATURE_TEXT,
                      "功能特性",
                      wx.OK | wx.ICON_INFORMATION)

    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox(HELP_TEXT,
                      "注意事项",
                      wx.OK | wx.ICON_INFORMATION)

    def on_update_log(self, event):
        """Display an About Dialog"""
        wx.MessageBox(UPDATE_LOG,
                      "更新内容",
                      wx.OK | wx.ICON_INFORMATION)

    def load_config_fille(self):
        # 读取配置文件内容
        conf = PARAM_DEFAULT_DICT
        if os.path.isfile('wow_help_config.json'):
            with open('wow_help_config.json', 'r') as f:
                file_conf = json.load(f)
                conf.update(file_conf)
        return conf

    def on_run_button(self, event):
        # 启动防掉线
        self.stop_button.Enable()
        if self.worker:
            self.worker.stop_guard()
            self.worker = None
        self.init_wow_worker(start_guard=True)
        for control in [self.start_button, self.cb1, self.cb2, self.cb3]:
            control.Disable()

    def on_stop_button(self, event):
        if self.worker:
            self.worker.stop_guard()
            # self.worker = None
        for control in [self.start_button, self.cb1, self.cb2, self.cb3]:
            control.Enable()
        self.stop_button.Disable()

    def on_display_button(self, event):
        self.init_wow_worker(start_guard=True)
        self.worker.wow_show()

    def on_hide_button(self, event):
        self.init_wow_worker(start_guard=True)
        self.worker.wow_hide()

    def on_logout(self, event):
        if event.data:
            log_msg = str(event.data) + (
                '(失效任务)' if not self.worker or event.instance_id != self.worker.instance_id else '') + '\n'
            self.log.AppendText(log_msg)

        if event.flag == 1:
            if not event.instance_id == self.worker.instance_id:
                return
            if not event.notifi_message:
                event.notifi_message = "防掉线守护出现异常，请确认"
            if self.worker:
                self.worker.abort()
                self.worker = None
            for control in [self.start_button, self.cb1, self.cb2, self.cb3]:
                control.Enable()
            self.stop_button.Disable()

        if event.notifi_message:
            notify = wx.adv.NotificationMessage(
                title="WOW防掉线助手!",
                message=event.notifi_message,
                parent=None, flags=wx.ICON_ERROR)
            notify.Show(timeout=100)  # 1 for short timeout, 100 for long timeout

    def runTest(frame, nb, log):
        import wx.py as py
        win = py.shell.Shell(nb, -1, introText='command control')
        return win


class ConfigEditDialog(wx.Dialog):
    def __init__(self, parent, param_dict):
        wx.Dialog.__init__(self, parent, -1, "助手配置编辑")
        self.SetAutoLayout(True)
        VSPACE = 10
        fgs = wx.FlexGridSizer(cols=2)
        fgs.Add((1, VSPACE))
        fgs.Add((1, VSPACE))
        self.input_texts = {}

        params = (("sleep_min_time_text", "随机动作最短间隔(秒):", param_dict['sleep_min_time'], {}),
                  ("sleep_max_time_text", "随机动作最长间隔(秒):", param_dict['sleep_max_time'], {}),
                  ('check_offline_interval_text', '掉线检测间隔(秒)', param_dict['check_offline_interval'], {}),
                  ('login_loadtime_text', '角色登录加载等待时长(秒)', param_dict['login_loadtime'], {}),
                  ('skills_text', '释放技能按键(使用|分割,如1|2|3)', param_dict['skills'], {}),
                  ('compare_value_text', '离线匹配相似度(0到1,越接近1匹配越严格)', param_dict['compare_value'], {}),
                  ('app_id_text', 'app_id(OCR识别场景时必须填写)', param_dict['app_id'], {}),
                  ('api_key_text', 'api_key(OCR识别场景时必须填写)', param_dict['api_key'], {}),
                  ('scret_key_text', 'scret_key(OCR识别场景时必须填写)', param_dict['scret_key'], {}),
                  )
        for input_text_name, lable_text, input_default, param_args in params:
            label = wx.StaticText(self, -1, lable_text)
            tc = wx.TextCtrl(self, -1, str(input_default))
            self.input_texts.update({input_text_name: tc})
            fgs.Add(label, 0, wx.ALIGN_LEFT)
            fgs.Add(tc, 0, wx.ALIGN_RIGHT)
            fgs.Add((1, VSPACE))
            fgs.Add((1, VSPACE))
        cb_clear_shoot = wx.CheckBox(self, -1, label='清理截图快照')
        # cb_clear_shoot.SetValue(param_dict.get('clear_shoot_file', True))
        self.input_texts.update({'clear_shoot_file': cb_clear_shoot})
        fgs.Add(cb_clear_shoot, 0, wx.ALIGN_LEFT)
        open_hiden_mode = wx.CheckBox(self, -1, label='开启沉浸模式')
        # open_hiden_mode.SetValue(param_dict.get('hiden_mode', False))
        self.input_texts.update({'hiden_mode': open_hiden_mode})
        fgs.Add(open_hiden_mode, 0, wx.ALIGN_LEFT)
        # Default Web links:
        import wx.lib.agw.hyperlink as hl
        self._hyper1 = hl.HyperLinkCtrl(self, wx.ID_ANY, "百度AI注册地址",
                                        URL="https://ai.baidu.com/")
        fgs.Add(self._hyper1, 0, wx.ALL, 10)
        buttons = wx.StdDialogButtonSizer()  # wx.BoxSizer(wx.HORIZONTAL)
        b = wx.Button(self, wx.ID_OK, "确认")
        b.SetDefault()
        buttons.AddButton(b)
        buttons.AddButton(wx.Button(self, wx.ID_CANCEL, "取消"))
        buttons.Realize()
        border = wx.BoxSizer(wx.VERTICAL)
        border.Add(fgs, 1, wx.GROW | wx.ALL, 25)
        border.Add(buttons, 0, wx.GROW | wx.BOTTOM, 5)
        self.SetSizer(border)
        border.Fit(self)


        self.Layout()


if __name__ == '__main__':
    app = wx.App()
    frm = WowHelperFrame(None, title='魔兽防掉线小助手', size=(640, 480))
    frm.Show()
    app.MainLoop()
