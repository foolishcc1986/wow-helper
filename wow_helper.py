import time
import traceback
from datetime import datetime
from random import randint, choice
from functools import partialmethod, wraps

from win32gui import ShowWindow, EnumWindows, GetClassName, MoveWindow, SetForegroundWindow, GetForegroundWindow, \
    SendMessage, FindWindow, \
    IsIconic  # 是否最小化
from win32api import keybd_event, MapVirtualKey, SetCursorPos, OpenProcess, CloseHandle
from win32con import (KEYEVENTF_KEYUP, WM_KEYDOWN, WM_KEYUP, WM_SYSKEYDOWN, WM_SYSKEYUP,
                      VK_SHIFT, VK_CONTROL, VK_MENU, VK_SNAPSHOT, PROCESS_ALL_ACCESS,
                      SW_SHOW, SW_HIDE, SW_MINIMIZE, SW_RESTORE  # 窗口隐藏与最小化控制
                      )
from win32process import EnumProcessModules, GetModuleFileNameEx, GetWindowThreadProcessId, GetExitCodeProcess, \
    TerminateProcess
from CONFIG import *
from image_compare import ComparePicture
from ocr import OcrClientBaiDu


class KeyClient:
    """
    键盘控制客户端
    """
    KEY_MAP = {'SHIFT': VK_SHIFT, 'CTRL': VK_CONTROL, 'ALT': VK_MENU, 'BACKSPACE': 32, 'ESC': 27, 'ENTER': 13,
               'PRINTSCREEN': VK_SNAPSHOT,
               ',': 44, '.': 46, '/': 47, '-': 45, '=': 61, '[': 91, ']': 93, '\\': 92, ';': 59, ",": 39,
               '0': 48, '1': 49, '2': 50, '3': 51, '4': 52, '5': 53, '6': 54, '7': 55, '8': 56, '9': 57,
               ':': 58, ';': 59, '<': 60, '=': 61, '>': 62, '?': 63, '@': 64, '`': 96,
               'A': 65, 'B': 66, 'C': 67, 'D': 68, 'E': 69, 'F': 70, 'G': 71, 'H': 72, 'I': 73, 'J': 74, 'K': 75,
               'L': 76, 'M': 77, 'N': 78, 'O': 79, 'P': 80, 'Q': 81, 'R': 82, 'S': 83, 'T': 84, 'U': 85, 'V': 86,
               'W': 87, 'X': 88, 'Y': 89, 'Z': 90, 'F4': 115}
    VAILD_SKILL_KEYS = [',', '.', '/', '-', '=', '[', ']', '\\', ';', "'", '`',
                        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                        'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    def __init__(self, *args, **kwargs):
        super(KeyClient, self).__init__(*args, **kwargs)

    def press_key(self, key_letter, extend_key=(0, 0, 0)):
        """
        :param key_letter:
        :param extend_key: (ctrl,alt,shift)
        :return:
        """
        key_id = self.KEY_MAP.get(key_letter.upper())
        if extend_key[0]:
            keybd_event(VK_CONTROL, MapVirtualKey(VK_CONTROL, 0), 0, 0)
            time.sleep(0.1)
        if extend_key[1]:
            keybd_event(VK_MENU, MapVirtualKey(VK_MENU, 0), 0, 0)
            time.sleep(0.1)
        if extend_key[2]:
            keybd_event(VK_SHIFT, MapVirtualKey(VK_SHIFT, 0), 0, 0)
            time.sleep(0.1)
        keybd_event(key_id, MapVirtualKey(key_id, 0), 0, 0)
        keybd_event(key_id, MapVirtualKey(key_id, 0), KEYEVENTF_KEYUP, 0)
        if extend_key[0]:
            keybd_event(VK_CONTROL, MapVirtualKey(VK_CONTROL, 0), KEYEVENTF_KEYUP, 0)
            time.sleep(0.1)
        if extend_key[1]:
            keybd_event(VK_MENU, MapVirtualKey(VK_MENU, 0), KEYEVENTF_KEYUP, 0)
            time.sleep(0.1)
        if extend_key[2]:
            keybd_event(VK_SHIFT, MapVirtualKey(VK_SHIFT, 0), KEYEVENTF_KEYUP, 0)
            time.sleep(0.1)

    def press_key_to_window(self, key_letter, wid, press_down_time=0.5, press_type=3, extend_key=(0, 0, 0)):
        """
        窗口发送按键
        :param key_letter:
        :param wid:
        :param press_down_time:
        :param press_type: 1 按下, 2弹起, 3按下+弹起
        :param extend_key: (ctrl,alt,shift)
        :return:
        """
        key_id = self.KEY_MAP.get(key_letter.upper())
        if press_type in (1, 3):
            # PostMessage(wid, WM_KEYDOWN, key_id, int(0x160001))
            if extend_key[0]:
                SendMessage(wid, WM_KEYDOWN, VK_CONTROL, int(0x160001))
                time.sleep(0.1)
            if extend_key[1]:
                SendMessage(wid, WM_SYSKEYDOWN, VK_MENU, int(0x160001))
                time.sleep(0.1)
            if extend_key[2]:
                SendMessage(wid, WM_KEYDOWN, VK_SHIFT, int(0x160001))
                time.sleep(0.1)
            SendMessage(wid, WM_KEYDOWN, key_id, int(0x160001))
        if press_type == 3:
            time.sleep(press_down_time)

        if press_type in (2, 3):
            # PostMessage(wid, WM_KEYUP, key_id, int(0x160001))
            SendMessage(wid, WM_KEYUP, key_id, int(0x160001))
            if extend_key[0]:
                SendMessage(wid, WM_KEYUP, VK_CONTROL, int(0x160001))
                time.sleep(0.1)
            if extend_key[1]:
                SendMessage(wid, WM_SYSKEYUP, VK_MENU, int(0x160001))
                time.sleep(0.1)
            if extend_key[2]:
                SendMessage(wid, WM_KEYUP, VK_SHIFT, int(0x160001))
                time.sleep(0.1)


class WowActionFactory(KeyClient):
    """
    封装WOW挂机随机动作
    """

    DO_NOTING = 0
    DO_NOT_FUCK = 1
    DO_ALL = 2

    def __init__(self, skills, log_function=print, *args, **kwargs):
        """
        :param skills:  技能释放按键列表
        """
        super(WowActionFactory, self).__init__(*args, **kwargs)
        if isinstance(skills, str):
            self.skills = skills.split('|')
        elif isinstance(skills, (list, tuple)):
            self.skills = skills
        else:
            raise WowKeeperValueError('skills参数格式错误，应该是list,tuple或以|分割得字符串!')
        self.log_function = log_function
        self._wow_win_status = 'none'
        self._run_mode = self.DO_NOT_FUCK

    @property
    def systime(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def is_vaild_skill_key(self, key):
        if len(key) != 1:
            self.log_function('%s: 输入错误，输入长度必须为1' % (self.systime,))
            return False
        if key.upper() not in self.VAILD_SKILL_KEYS:
            self.log_function('%s: 输入错误，输入的按键%s不在允许范围内' % (self.systime, key))
            self.log_function('%s: 允许的按键范围如下  ' % (self.systime,))
            self.log_function(
                '%s: %s' % (self.systime, '  '.join(self.VAILD_SKILL_KEYS)))
            return False
        return True

    def stop(self):
        if self._run_mode == self.DO_ALL:
            self._run_mode = self.DO_NOTING
            self.log_function('%s: 开始停止防掉线保护' % (self.systime,))
        if self.wow_win_status == 'hide':
            self.wow_show()

    def check_stop_siginal(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self._run_mode != self.DO_NOTING:
                func_result = func(self, *args, **kwargs)
                return func_result
        return wrapper

    @staticmethod
    def get_wow_win_id():
        wow_win_id_list = []
        EnumWindows(
            lambda wid, param: param.append(wid) if GetClassName(wid) == WOW_CLASS_NAME else None,
            wow_win_id_list)
        return wow_win_id_list

    @property
    def wow_is_running(self):
        return bool(len(self.get_wow_win_id()))

    @property
    def wow_win_id(self):
        # TODO: 多个窗口暂时取第一个
        try:
            _wow_win_id = self.get_wow_win_id()[0]
        except IndexError:
            _wow_win_id = None
            self.log_function('%s: 未检测到wow运行' % (self.systime,))
        return _wow_win_id

    @property
    def wow_win_status(self):
        return self._wow_win_status

    def cmd_windows(self, sw_flag):
        if self.wow_is_running:
            ShowWindow(self.wow_win_id, sw_flag)
            sw_dict = {SW_SHOW: 'show', SW_HIDE: 'hide', SW_MINIMIZE: 'minisize', SW_RESTORE: 'show'}
            self._wow_win_status = sw_dict.get(sw_flag, '')
            return True
        else:
            self.log_function('%s: 未检测到wow运行' % (self.systime,))
            self._wow_win_status = 'none'
            return False

    # 显示窗口
    wow_show = partialmethod(cmd_windows, sw_flag=SW_SHOW)
    # 隐藏窗口
    wow_hide = partialmethod(cmd_windows, sw_flag=SW_HIDE)
    # 窗口最小化
    wow_mini = partialmethod(cmd_windows, sw_flag=SW_MINIMIZE)
    # 窗口恢复
    wow_restore = partialmethod(cmd_windows, sw_flag=SW_RESTORE)

    def press_key_to_wow(self, key_letter, press_down_time=0.5, press_type=3, extend_key=(0, 0, 0)):
        """
        向WOW发送按键
        :param key_letter:
        :param press_down_time:
        :return:
        """
        self.press_key_to_window(key_letter, self.wow_win_id, press_down_time, press_type, extend_key)

    @check_stop_siginal
    def _action_forward_start(self):
        self.log_function('%s: 执行"前进"指令' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.press_key_to_wow(key_letter='W', press_type=1)

    def _action_forward_stop(self):
        self.log_function('%s: 执行"停止前进"指令' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.press_key_to_wow(key_letter='W', press_type=2)

    @check_stop_siginal
    def _action_backward_start(self):
        self.log_function('%s: 执行"后退"指令' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.press_key_to_wow(key_letter='S', press_type=1)

    def _action_backward_stop(self):
        self.log_function('%s: 执行"停止后退"指令' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.press_key_to_wow(key_letter='S', press_type=2)

    @check_stop_siginal
    def action_jump(self):
        self.log_function('%s: 执行"跳跃"指令' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.press_key_to_wow('BACKSPACE', randint(10, 50) / 100)

    @check_stop_siginal
    def action_forward(self):
        keep_down_time = randint(1, 5)
        self.log_function('%s: 执行"前进"指令%d秒' % (self.systime, keep_down_time))
        self.press_key_to_wow('W', press_down_time=keep_down_time)

    @check_stop_siginal
    def action_backward(self):
        keep_down_time = randint(1, 5)
        self.log_function('%s: 执行"后退"指令%d秒' % (self.systime, keep_down_time))
        self.press_key_to_wow('S', press_down_time=keep_down_time)

    @check_stop_siginal
    def action_forward_skill(self):
        self._action_forward_start()
        time.sleep(randint(10, 50) / 100)
        self.action_skill()
        time.sleep(randint(1, 5))
        self._action_forward_stop()

    @check_stop_siginal
    def action_backward_skill(self):
        self._action_backward_start()
        time.sleep(randint(10, 50) / 100)
        self.action_skill()
        time.sleep(randint(1, 5))
        self._action_backward_stop()

    @check_stop_siginal
    def action_forward_jump(self):
        self._action_forward_start()
        time.sleep(randint(10, 50) / 100)
        self.action_jump()
        time.sleep(randint(1, 5))
        self._action_forward_stop()

    @check_stop_siginal
    def action_backward_jump(self):

        self._action_backward_start()
        time.sleep(randint(10, 50) / 100)
        self.action_jump()
        time.sleep(randint(1, 5))
        self._action_backward_stop()

    @check_stop_siginal
    def action_skill(self):
        random_skill = choice(self.skills)
        self.log_function('%s: 执行"按键%s"指令' % (self.systime, random_skill))
        self.press_key_to_wow(random_skill, randint(10, 50) / 100)

    @check_stop_siginal
    def doing_random_action(self):
        return self.__getattribute__(choice([target_name for target_name, target in WowActionFactory.__dict__.items() if
                                             callable(target) and target_name.startswith('action')]))()


class WowClientGuard(WowActionFactory, ComparePicture, OcrClientBaiDu):
    """
    防掉线
    """
    IS_STARTING = False
    NOT_FINISH = 0
    IS_FINISH = 1
    IS_SKIP = 2
    SCENE_OFFLINE = 1
    SCENE_ROLE_LOGIN = 2
    SCENE_CHANNEL_CHOICE = 3
    SCENE_UNAUTH = 4
    SCENE_NOT_RUNNING = 5
    SCENE_SERVICE_REFRESH = 11
    SCENE_SERVICE_WATING = 12
    SCENE_SERVICE_CONNECT = 13
    SCENE_SERVICE_LOGIN = 14
    SCENE_PARAMS = {'offline': {'scene_name': '已从服务器断开', 'sample_file': OFFLINE_SAMPLE_FILE_NAME,
                                'scene_id': SCENE_OFFLINE, 'shoot_position': OFFLINE_BOX_POS,
                                'text': ['已从服务器断开WOW519000319', '确定']},
                                # 'text': ['你已断开连接(W51900308)', '帐名称', '帮助', '确定']},
                    # TODO: 还有一种正常掉线 ['你已断开连接(W51900308)', '帐名称', '帮助', '确定']
                    'role_login': {'scene_name': '角色登录', 'sample_file': ROLE_SAMPLE_FILE_NAME,
                                   'scene_id': SCENE_ROLE_LOGIN, 'shoot_position': ROLE_LOGIN_BOX_POS,
                                   'text': ['进入魔兽世界']},
                    'channel': {'scene_name': '服务器连接选择', 'sample_file': CHANNEL_SAMPLE_FILE_NAME,
                                'shoot_position': CHANNEL_BOX_POS, 'scene_id': SCENE_CHANNEL_CHOICE,
                                'text': ['服务器名称', '类型', '角色', '服务器负载'], 'check_ln': (0, 1, 2, 3)},
                    'serv_connect': {'scene_name': '服务器连接', 'sample_file': SERVICE_CONNECT_SAMPLE_FILE_NAME,
                                     'scene_id': SCENE_SERVICE_CONNECT, 'shoot_position': SERVICE_CONNECT_BOX_POS,
                                     'text': ['正在连接', '取消']},
                    'serv_wait': {'scene_name': '服务器排队等待', 'sample_file': SERVICE_WATING_SAMPLE_FILE_NAME,
                                  'scene_id': SCENE_SERVICE_WATING, 'shoot_position': SERVICE_WATING_BOX_POS,
                                  'text': ['德姆塞卡尔巳满', '队列位置', '预计时间'], 'check_ln': (1, 2)},
                    'serv_refresh': {'scene_name': '正在刷新服务器列表', 'sample_file': SERVICE_REFRESH_SAMPLE_FILE_NAME,
                                     'scene_id': SCENE_SERVICE_REFRESH, 'shoot_position': SERVICE_REFRESH_BOX_POS,
                                     'text': ['正在刷新服务器列表', '取消']},
                    'serv_login': {'scene_name': '正在登陆服务器', 'sample_file': SERVICE_LOGIN_SAMPLE_FILE_NAME,
                                   'scene_id': SCENE_SERVICE_LOGIN, 'shoot_position': SERVICE_LOGIN_BOX_POS,
                                   'text': ['正在登陆游戏服务器', '取消']},
                    'unauth': {'scene_name': '账号未认证', 'sample_file': UNAUTH_SAMPLE_FILE_NAME,
                               'scene_id': SCENE_UNAUTH, 'shoot_position': SERVICE_LOGIN_BOX_POS,
                               'text': ['账号名称']},
                    'in_game': {'scene_name': '游戏中'},
                    'not_running': {'scene_name': '未启动', 'scene_id': SCENE_NOT_RUNNING}
                    }

    def __init__(self, skills, is_random_action=True, is_warning=False, is_auto_login=False, login_loadtime=10,
                 clear_shoot_file=False, compare_value=0.65, check_offline_interval=30, hiden_mode=False, *args,
                 **kwargs):
        """
        :param skills:  技能释放按键列表
        :param is_warning: 掉线提醒
        """
        super(WowClientGuard, self).__init__(skills, *args, **kwargs)
        self.is_random_action = is_random_action
        self.is_warning = is_warning
        self.is_auto_login = is_auto_login
        self.check_role = self.NOT_FINISH
        self.login_loadtime = login_loadtime
        self.clear_shoot_file = clear_shoot_file
        self.compare_value = compare_value
        self.check_offline_interval = check_offline_interval
        self.hiden_mode = hiden_mode
        self._scene = 'not_running'
        self._wow_print_screen_path = ''

    @property
    def wow_print_screen_path(self):
        """
        获取wow默认截图路径
        :return:
        """
        if self._wow_print_screen_path:
            return self._wow_print_screen_path
        else:
            thread_id, process_id = GetWindowThreadProcessId(self.wow_win_id)
            handle = OpenProcess(PROCESS_ALL_ACCESS, False, process_id)
            hModule = EnumProcessModules(handle)
            for i in hModule:
                name = GetModuleFileNameEx(handle, i)
                if name.endswith(WOW_EXE_NAME):
                    CloseHandle(handle)
                    self._wow_print_screen_path = os.path.join(os.path.split(name)[0], 'Screenshots')
                    return self._wow_print_screen_path

    @property
    def scene(self):
        return self._scene

    @scene.setter
    def scene(self, scene_args):
        if scene_args[1] >= self.compare_value and scene_args[0] != self._scene:
            self._scene = scene_args[0]
            self.log_function('%s: 游戏场景切换为%s(匹配度%f)' %
                              (self.systime,
                               self.SCENE_PARAMS.get(scene_args[0]).get('scene_name'),
                               scene_args[1])
                              )

    @property
    def wow_win_id(self):
        _wow_win_id = super().wow_win_id
        if not _wow_win_id:
            if self.is_auto_login and not self.IS_STARTING:
                self.login_wow()
                return
            else:
                raise WowNotRunError('未检测到wow运行')
        return _wow_win_id

    def wow_show(self):
        before_status = self.wow_win_status
        if super().wow_show():
            self.hiden_mode = False
            if before_status != self.wow_win_status:
                self.log_function('%s: 显示WOW窗口，退出沉浸模式' % (self.systime,))

    def wow_hide(self):
        before_status = self.wow_win_status
        if super().wow_hide():
            self.hiden_mode = True
            if before_status != self.wow_win_status:
                self.log_function('%s: 隐藏WOW窗口，开启沉浸模式' % (self.systime,))

    def resize_wow_windows(self):
        self.log_function('%s: 设置魔兽世界窗口大小为%s' %
                          (self.systime,
                           '*'.join(map(str, WOW_WINDOWS_MOVE_PARAM[2:4]))))
        if IsIconic(self.wow_win_id):
            self.wow_restore()
        MoveWindow(self.wow_win_id, *WOW_WINDOWS_MOVE_PARAM)
        if self.hiden_mode:
            self.wow_hide()
        else:
            self.wow_mini()

    def shoot_by_game(self):
        shoot_time = time.time()
        if IsIconic(self.wow_win_id):
            self.wow_restore()
        if self.hiden_mode:
            self.wow_hide()
        self.press_key_to_wow('PRINTSCREEN')
        time.sleep(2)
        for file in os.listdir(self.wow_print_screen_path):
            sc_file = os.path.join(self.wow_print_screen_path, file)
            ctime = os.path.getctime(sc_file)
            if ctime >= shoot_time:
                # print('找到系统截图%s' % sc_file)
                return sc_file
        return False

    def check_stop_siginal(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self._run_mode != self.DO_NOTING:
                func_result = func(self, *args, **kwargs)
                return func_result
        return wrapper

    @check_stop_siginal
    def get_wow_scene(self, check_scene=[value.get('scene_id', -1) for key, value in SCENE_PARAMS.items()],
                      check_type=2):
        """
        检测当前游戏场景
        :param: check_type 1 图片识别 2 ocr识别
        :return: (场景名称, 匹配相似度)  场景名称为offline,role_login,channel
        """
        # print(check_scene)
        shoot_file_name = self.shoot_by_game()
        scene_value = 0
        scene_name = 'in_game'
        box_text = {}
        if not shoot_file_name:
            self.wow_restore()
            self.shoot_picture(self.wow_win_id, WOW_WINDOWS_MOVE_PARAM, SHOOT_BOX_POS, SHOOT_FILE_NAME)
            if self.hiden_mode:
                self.wow_hide()
            shoot_file_name = SHOOT_FILE_NAME
            scene_name = ''
        # 依次比对样本文件保留可能性最高得一个
        for scene, param in self.SCENE_PARAMS.items():
            # print(scene, param)
            # 指定校验场景时，不在范围中得跳过, 没有配置匹配参数得也跳过
            if param.get('scene_id', -1) not in check_scene or \
                    (not all([key in param for key in ['shoot_position', 'sample_file']])):
                continue
            check_img = self.get_image_from_file(shoot_file_name, param['shoot_position'])

            if check_type == 1:
                # 图片相似度直方图校验
                if not self.clear_shoot_file:
                    check_img.save(scene + '_shoot.png', 'png')
                if isinstance(param['sample_file'], str):
                    sample_files = (param['sample_file'],)
                else:
                    sample_files = param['sample_file']

                for sample_file in sample_files:
                    # print(sample_file)
                    sample_img = self.get_image_from_file(sample_file)
                    # value = self.phash_img_similarity(sample_img, check_img)
                    value = self.compare_image_object(sample_img, check_img)
                    # print(scene, value)
                    if value > scene_value:
                        scene_name = scene
                        scene_value = value
            elif check_type == 2:
                # 文字OCR识别校验
                if 'text' not in param:
                    print(f'{scene}未定义ocr识别匹配文字')
                    continue
                if param['shoot_position'] not in box_text:
                    scene_img_name = scene + '_shoot.png'
                    check_img.save(scene_img_name, 'png')
                    ocr_result = self.get_text_from_image_file(scene_img_name)
                    if self.clear_shoot_file:
                        os.remove(scene_img_name)
                    box_text[param['shoot_position']] = [row['words'] for row in ocr_result['words_result']]
                ocr_text = [text for seq, text in enumerate(box_text[param['shoot_position']]) if
                            seq in param.get('check_ln', (seq,))]
                tmp_scene_value = []
                print(f"ocr_text:{ocr_text}, sample_text: {param['text']}")
                for seq, sample_text in enumerate(param['text']):
                    import difflib
                    try:
                        tmp_scene_value.append(difflib.SequenceMatcher(None, sample_text, ocr_text[seq]).quick_ratio())
                    except IndexError:
                        tmp_scene_value.append(0)
                value = sum(tmp_scene_value)/len(tmp_scene_value)
                if value > scene_value:
                    scene_name = scene
                    scene_value = value
            print(f'识别方式{check_type}, 识别场景{scene}, 匹配度{value}')
        if self.clear_shoot_file:
            os.remove(shoot_file_name)
        self.scene = (scene_name, scene_value)
        return scene_name, scene_value

    @check_stop_siginal
    def deal_scene(self, deal_scenes=[]):
        """
        场景处理
        :param deal_scenes:
        :return:
        """
        scene_name, scene_value = self.get_wow_scene(deal_scenes)
        # print('检测场景%s:%s' % (scene_name, str(scene_value)))
        deal_flag = self.NOT_FINISH
        if scene_name == 'offline' and self.SCENE_OFFLINE in deal_scenes:
            if scene_value >= self.compare_value:
                self.log_function(
                    '%s: 检测到游戏可能掉线(匹配度%f)' % (self.systime, scene_value))
                self.deal_offline()
                deal_flag = self.IS_FINISH
        elif scene_name == 'unauth' and self.SCENE_UNAUTH in deal_scenes:
            if scene_value >= self.compare_value:
                check_network_sleep_time = 10
                while os.system('ping www.baidu.com'):
                    self.log_function(
                        '%s: 检测到网络异常导致游戏登录未账号认证，请确认网络是否正常，%d秒后重试!' % (self.systime, check_network_sleep_time),
                        0, '检测到网络异常导致游戏登录未账号认证，请确认网络是否正常!')
                    time.sleep(check_network_sleep_time)
                self.log_function(
                    '%s: 检测到游戏登录可能未账号认证(匹配度%f)，重新启动游戏' % (
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'), scene_value))
                self.deal_offline()
                deal_flag = self.IS_FINISH
        elif scene_name == 'role_login' and self.SCENE_ROLE_LOGIN in deal_scenes:
            if scene_value >= self.compare_value:
                self.log_function(
                    '%s: 检测到游戏在角色登录界面(匹配度%f)' % (self.systime, scene_value))
                self.login_role()
                deal_flag = self.IS_FINISH
        elif scene_name == 'channel' and self.SCENE_CHANNEL_CHOICE in deal_scenes:
            pass
        elif scene_name == 'serv_wait' and self.SCENE_SERVICE_WATING in deal_scenes and scene_value >= self.compare_value:
            self.log_function(
                '%s: 检测到游戏在排队等待界面(匹配度%f)' % (self.systime, scene_value))
        return scene_name, scene_value, deal_flag

    @check_stop_siginal
    def deal_offline(self):
        """
        处理掉线
        """
        try:
            if self.is_warning:
                if os.path.isfile(WARNING_MP3_FILE):
                    self.log_function('%s: 触发掉线提醒，播放声音文件!' % (self.systime,))
                    os.system(WARNING_MP3_FILE)
                    time.sleep(5)
                else:
                    self.log_function('%s: 未查找到提醒音乐文件%s缺失，无法正常触发声音提醒！' %
                                      (self.systime, WARNING_MP3_FILE))
            if self.is_auto_login:
                self.kill_wow()
                time.sleep(0.5)
                self.login_wow()
        except:
            self.log_function('%s: 处理掉线出错！' % (self.systime,))
            self.log_function('-' * 40)
            self.log_function('异常信息:')
            self.log_function(traceback.format_exc())
            self.log_function('-' * 40)

    @check_stop_siginal
    def open_wow_from_battle(self):
        """
        通过战网启动游戏
        :return: None
        """
        self.IS_STARTING = True
        self.log_function('%s: 通过战网启动游戏！' % (self.systime,))
        keybd_event(17, 0, 0, 0)
        keybd_event(17, 0, KEYEVENTF_KEYUP, 0)
        battle_win_id = FindWindow('Qt5QWindowOwnDCIcon', '暴雪战网')
        if not battle_win_id:
            self.log_function('%s: 未检测到战网运行，请检查是否未启动或被最小化到系统托盘！' % (self.systime,),
                              0, '未检测到战网运行，请检查是否未启动或被最小化到系统托盘')
            raise WowKeeperError('未查找战网窗口句柄')
        self.press_key_to_window('ENTER', battle_win_id)
        out_time = time.time() + 30
        while not self.wow_is_running and self._run_mode == self.DO_ALL:
            time.sleep(0.1)
            if time.time() > out_time:
                self.log_function('%s: 启动游戏超时！' % (self.systime,))
                self.IS_STARTING = False
                return False
        # time.sleep(2)
        self.resize_wow_windows()
        return True

    @check_stop_siginal
    def login_role(self):
        """
        角色登录界面时登入游戏
        :return:  None
        """
        self.log_function('%s: 选择角色登入游戏！' % (self.systime,))
        self.press_key_to_wow('ENTER')
        self.log_function('%s: 等待%d秒游戏加载' % (self.systime, self.login_loadtime))
        time.sleep(self.login_loadtime)

    @staticmethod
    def terminal_process_by_hwid(hwnd):
        """
        结束窗口句柄对应的进程
        :param: hwnd 窗口句柄
        :return:
        """
        thread_id, process_id = GetWindowThreadProcessId(hwnd)
        wow_handle = OpenProcess(PROCESS_ALL_ACCESS, False, process_id)
        if wow_handle:
            TerminateProcess(wow_handle, GetExitCodeProcess(wow_handle))
        CloseHandle(wow_handle)

    @check_stop_siginal
    def kill_wow(self):
        while self.wow_is_running:
            self.log_function('%s: 强制关闭游戏！' % (self.systime,))
            self.terminal_process_by_hwid(self.wow_win_id)

    @check_stop_siginal
    def login_wow(self):
        """
        登录WOW进入游戏
        """
        if self.open_wow_from_battle():
            self.check_role = self.NOT_FINISH
            # 服务器认证等样本会被误识别为断开连接，所以一分钟之后才开始加入断开连接检查
            begin_check_offline_time = time.time() + 60
            while self.check_role == self.NOT_FINISH and self._run_mode != self.DO_NOTING:
                self.log_function('%s: 等待进入角色选择界面！' % (self.systime,))
                scene_name, scene_value, self.check_role = self.deal_scene(
                    deal_scenes=[self.SCENE_OFFLINE, self.SCENE_UNAUTH, self.SCENE_SERVICE_WATING,
                                 self.SCENE_ROLE_LOGIN] if time.time() > begin_check_offline_time else [
                        self.SCENE_ROLE_LOGIN, self.SCENE_SERVICE_WATING])
                if self.check_role == self.IS_SKIP:
                    self.log_function('%s: 跳过角色校验登录环节！' % (self.systime,))
                time.sleep(5)

    def fuck_wow_offline(self, sleep_time_range=[300, 600]):
        """
        挂机防掉线流程控制方法
        :param sleep_time_range:
        :return:
        """
        try:
            start_delay_time = 5
            self._run_mode = self.DO_ALL
            self.log_function('-' * 100)
            self.log_function('%s: 开始启动防掉线助手' % (self.systime,))
            self.log_function(f'动作循环间隔随机范围: {sleep_time_range[0]}秒-{sleep_time_range[1]}秒,按键列表为: {self.skills}')
            self.log_function(
                f'掉线提醒开关状态：{self.is_warning}, 掉线检查间隔: {self.check_offline_interval}秒, '
                f'游戏自动登录开关状态: {self.is_auto_login},\n 自动清理文件: {self.clear_shoot_file}, 沉浸模式开关状态: {self.hiden_mode}')
            self.log_function('')
            if not self.wow_is_running:
                self.login_wow()
            self.resize_wow_windows()
            self.log_function('-' * 100)
            self.log_function('%s: %d秒后开始防掉线保护...' % (self.systime, start_delay_time))
            time.sleep(start_delay_time)
            sleep_begin_time = time.time()
            sleep_time = 5
            next_check_scene_time = 0
            while self._run_mode == self.DO_ALL:
                # 执行前定时检查游戏场景是否掉线或返回角色
                while time.time() < sleep_begin_time + sleep_time and self._run_mode == self.DO_ALL:
                    if time.time() > next_check_scene_time:
                        try:
                            a, b, is_deal = self.deal_scene(
                                deal_scenes=[self.SCENE_OFFLINE, self.SCENE_UNAUTH, self.SCENE_SERVICE_WATING,
                                             self.SCENE_ROLE_LOGIN])
                            next_check_scene_time = time.time() + self.check_offline_interval
                            if is_deal:
                                break
                        except ShootError:
                            time.sleep(1)
                    time.sleep(1)
                try:
                    if self.is_random_action:
                        self.doing_random_action()
                except:
                    self.log_function('%s: 执行随机动作出错!' % (self.systime,))
                    self.log_function('-' * 40)
                    self.log_function('异常信息:')
                    self.log_function(traceback.format_exc())
                    self.log_function('-' * 40)
                sleep_begin_time = time.time()
                sleep_time = randint(*sleep_time_range)
                self.log_function('%s: 休眠%d秒后继续执行指令' % (self.systime, sleep_time))
                next_check_scene_time = sleep_begin_time + self.check_offline_interval
        except:
            self.log_function('%s: 防掉线助手异常终止!' % (self.systime,), 1)
            self.log_function('-' * 40)
            self.log_function('异常信息:')
            self.log_function(traceback.format_exc())
            self.log_function('-' * 40)
        finally:
            self.wow_restore()
            self.log_function('%s: 防掉线保护已停止。' % (self.systime,))
