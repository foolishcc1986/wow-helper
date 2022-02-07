import time
import traceback

import win32gui
from PIL import Image, ImageGrab
from win32api import keybd_event, GetSystemMetrics
from win32con import KEYEVENTF_KEYUP, SM_CXCURSOR, SM_CYCURSOR, SM_CYCAPTION, SW_RESTORE, SW_MINIMIZE

from CONFIG import ShootError


class ComparePicture:
    """
    图片识别
    """

    @staticmethod
    def get_windows_sider():
        return GetSystemMetrics(SM_CYCAPTION)

    @staticmethod
    def get_image_from_file(file_name, cut_size=None, offset_x=0, offset_y=0):
        """
        读取文件切割后返回image对象
        :param file_name:文件名
        :param cut_size: (左，上，右，下)
        :param offset_x
        :param offset_y
        :return: image object
        """
        img = Image.open(file_name)
        if isinstance(cut_size, (list, tuple)) and len(cut_size) == 4 and all(
                map(lambda x: isinstance(x, int), cut_size)):
            cut_box = [cut_size[0] + offset_x, cut_size[1] + offset_y, cut_size[2] + offset_x, cut_size[3] + offset_y]
            img = img.crop(cut_box)
        return img

    @staticmethod
    def shoot_picture(wid, windows_move_param, shot_box_pos, file_name):
        try:
            current_winid = win32gui.GetForegroundWindow()
            # 事先发送加键盘事件，否则可能无法设置激活窗口
            keybd_event(17, 0, 0, 0)
            keybd_event(17, 0, KEYEVENTF_KEYUP, 0)
            is_mini = win32gui.IsIconic(wid)
            if is_mini:
                win32gui.ShowWindow(wid, SW_RESTORE)
            win32gui.SetForegroundWindow(wid)
            win32gui.MoveWindow(wid, *windows_move_param)
            time.sleep(1)
            bbox = shot_box_pos
            im = ImageGrab.grab(bbox)
            im.save(file_name, 'png')
            time.sleep(1)
            if is_mini:
                win32gui.ShowWindow(wid, SW_MINIMIZE)
            win32gui.SetForegroundWindow(current_winid)

        except Exception:
            raise ShootError('窗口%s截图保存文件%s失败，异常信息如下:\n%s' % (str(wid), file_name, traceback.format_exc()))

    # 计算图片的局部哈希值--pHash

    def phash(self, img):
        """
        :param img: 图片
        :return: 返回图片的局部hash值
        """
        from functools import reduce
        img = img.resize((8, 8), Image.ANTIALIAS).convert('L')
        avg = reduce(lambda x, y: x + y, img.getdata()) / 64.
        hash_value = reduce(lambda x, y: x | (y[1] << y[0]),
                            enumerate(map(lambda i: 0 if i < avg else 1, img.getdata())), 0)
        return hash_value

    # 计算两个图片相似度函数局部敏感哈希算法
    def phash_img_similarity(self, img1, img2):
        """
        :param img1_path: 图片1路径
        :param img2_path: 图片2路径
        :return: 图片相似度
        """
        # img1 = self.convert_image_to_point(img1, point_value=100)
        # img2 = self.convert_image_to_point(img2, point_value=100)
        # 计算汉明距离
        distance = bin(self.phash(img1) ^ self.phash(img2)).count('1')
        similary = 1 - distance / max(len(bin(self.phash(img1))), len(bin(self.phash(img1))))
        return similary


    @staticmethod
    def calculate(image1, image2):
        g = image1.histogram()
        s = image2.histogram()
        assert len(g) == len(s), "error"
        data = []
        for index in range(0, len(g)):
            if g[index] != s[index]:
                data.append(1 - abs(g[index] - s[index]) / max(g[index], s[index]))
            else:
                data.append(1)

        return sum(data) / len(g)

    @staticmethod
    def split_image(image, part_size):
        pw, ph = part_size
        w, h = image.size

        sub_image_list = []

        assert w % pw == h % ph == 0, "error"

        for i in range(0, w, pw):
            for j in range(0, h, ph):
                sub_image = image.crop((i, j, i + pw, j + ph)).copy()
                sub_image_list.append(sub_image)

        return sub_image_list

    def compare_image_file(self, file_image1, file_image2, *args, **kwargs):
        '''
        'file_image1'和'file_image2'是传入的文件路径
         可以通过'Image.open(path)'创建'image1' 和 'image2' Image 对象.
         'size' 重新将 image 对象的尺寸进行重置，默认大小为256 * 256 .
         'part_size' 定义了分割图片的大小.默认大小为64*64 .
         返回值是 'image1' 和 'image2'对比后的相似度，相似度越高，图片越接近，达到1.0说明图片完全相同。
        '''
        image1 = Image.open(file_image1)
        image2 = Image.open(file_image2)
        return self.compare_image_object(image1, image2, *args, **kwargs)

    def open_file_to_point(self, file_name, point_value=100, save_file_name=''):
        img = Image.open(file_name)
        return self.convert_image_to_point(img, point_value=point_value, save_file_name=save_file_name)
    @staticmethod
    def convert_image_to_gree(file_name, file_name2):
        img = Image.open(file_name)
        img = img.convert('L')
        img.save(file_name2)

    @staticmethod
    def convert_image_to_point(image, point_value=20, save_file_name=''):
        img_gree = image.convert('L')
        table = [0 if i < point_value else 1 for i in range(256)]
        img_point = img_gree.point(table, '1')
        if save_file_name:
            img_point.save(save_file_name)
        return img_point

    # TODO: 优化比对机制
    def compare_image_object_use_point(self, image1, image2, point_value=20, *args, **kwargs):
        """
        比对 image对象二值化后得相似度
        :param image1: image对象
        :param image2: image对象
        :param point_value: 灰化后二值化得分割值
        :return:
        """
        gree_image1 = image1.convert('L')
        gree_image2 = image2.convert('L')
        table = [0 if i < point_value else 1 for i in range(256)]
        image1 = gree_image1.point(table, '1')
        image2 = gree_image2.point(table, '1')
        return self.compare_image_object(image1, image2, *args, **kwargs)

    def compare_image_object(self, image1, image2, image1_size=None, image2_size=None, size=(256, 256),
                             part_size=(64, 64),*args, **kwargs):
        if image1_size:
            image1.crop(image1_size)
        if image2_size:
            image2.crop(image2_size)
        img1 = image1.resize(size).convert("RGB")
        sub_image1 = self.split_image(img1, part_size)

        img2 = image2.resize(size).convert("RGB")
        sub_image2 = self.split_image(img2, part_size)

        sub_data = 0
        for im1, im2 in zip(sub_image1, sub_image2):
            sub_data += self.calculate(im1, im2)

        x = size[0] / part_size[0]
        y = size[1] / part_size[1]

        pre = round((sub_data / (x * y)), 6)
        return pre
