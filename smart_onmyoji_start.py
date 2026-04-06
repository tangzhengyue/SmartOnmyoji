# -*- coding: utf-8 -*-
# @Link    : https://github.com/aicezam/SmartOnmyoji
# @Version : Python3.7.6
# @MIT License Copyright (c) 2022 ACE

import json
import os
import pathlib
import re
import subprocess
import sys
from ctypes import windll
from os.path import abspath, dirname
from time import sleep
import urllib.request

import PyQt5.QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog

from modules.ModuleGetConfig import ReadConfigFile
from modules.ModuleRunThread import MatchingThread, GetActiveWindowThread
from modules.ui import Ui_MainWindow

now_tag = "v0.43"


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, ui_info, target_file_name_list):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        super(MainWindow).__init__()
        self.setupUi(self)  # 继承UI类，下面进行信号与槽的绑定和修改

        # 使用配置文件参数
        self.target_path_mode_value = ui_info[0]
        self.handle_title_value = ui_info[1]
        self.click_deviation_value = ui_info[2]
        self.interval_seconds_value = ui_info[3]
        self.loop_min_value = ui_info[4]
        self.img_compress_val_value = ui_info[5]
        self.match_method_value = ui_info[6]
        self.run_mode_value = ui_info[7]
        self.custom_target_path_value = ui_info[8]
        self.process_num_value = ui_info[9]
        self.handle_num_value = ui_info[10]
        self.if_end_value = ui_info[11]
        self.debug_status_value = ui_info[12]
        self.set_priority_status_value = ui_info[13]
        self.interval_seconds_value_max = ui_info[14]
        self.screen_scale_rate_value = ui_info[15]
        self.times_mode = ui_info[16]

        # 控制台消息捕获并输出到运行日志
        sys.stdout = EmitStr(text_writ=self.output_write)  # 输出结果重定向
        sys.stderr = EmitStr(text_writ=self.output_write)  # 错误输出重定向

        # 继承重新设置GUI初始状态
        self.btn_pause.setEnabled(False)
        self.btn_pause.hide()
        self.btn_resume.setEnabled(False)
        self.btn_resume.hide()
        self.btn_stop.setEnabled(False)
        self.btn_stop.hide()
        self.btn_exit.show()
        self.loop_progress.setValue(0)
        self.select_targetpic_path_btn.hide()
        self.setWindowIcon(QIcon('img/logo.ico'))
        manual_url = pathlib.PureWindowsPath(abspath(dirname(__file__)) + r'\modules\tools\manual.html')
        self.log_analysis_url = pathlib.PureWindowsPath(abspath(dirname(__file__)) + r'\modules\tools\log_analysis.html')
        update_tips = ''
        update_status = self.get_update_status(now_tag)
        if update_status:
            update_tips = update_status[1] + update_status[2]
        self.run_log.setText("<br>"
                             "<p>本软件完全开源免费，不盈利不接受捐赠，作者不对使用该软件产生的一切后果负责！</p>"
                             "<p>本软件仅作学习用途，请勿用于其他非法途径！</p>"
                             "<p>本软件未对任何游戏或程序进行任何程度的修改，仅做辅助手段，帮助处理大量重复且乏味的操作！</p>"
                             "<br>"
                             "<p style='font-weight:bold;color:rgb(255, 136, 17);'>" + update_tips + "</p>"
                             "<p>你可以在以下地址下载：</p>"
                             "<p>脚本源码(git)："
                             "<a href='https://github.com/aicezam/SmartOnmyoji'>"
                             "https://github.com/aicezam/SmartOnmyoji</a></p>"
                             "<p>蓝奏云(密码yys)："
                             "<a href='https://isu.ink/yys'>"
                             "https://wwu.lanzouq.com/b03d5mdli</a></p>"
                             "<p>使用方法说明：<a href=" + manual_url.as_posix() + ">->点击查看</a></p> "
                             "<p>日志分析工具：<a href=" + self.log_analysis_url.as_posix() + ">->点击使用</a></p> "
                             "<br>"
                             "<p>🌟🌟🌟感谢你的使用，支持请 <a href='https://github.com/aicezam/SmartOnmyoji'>点star</a> 🌟🌟🌟</p>"
                             )

        # 加载config.ini文件中的默认参数
        self.click_deviation.setValue(self.click_deviation_value)  # 设置默认偏移量
        self.image_compression.setSliderPosition(int(self.img_compress_val_value * 100))  # 压缩截图默认值
        self.set_priority.setChecked(self.set_priority_status_value)
        self.debug.setChecked(self.debug_status_value)
        self.show_handle_title.setText(str(self.handle_title_value))
        self.show_handle_num.setText(str(self.handle_num_value))
        self.select_target_path_mode_combobox.setCurrentText(self.target_path_mode_value)
        if self.target_path_mode_value == '自定义':
            self.select_targetpic_path_btn.show()
        else:
            self.select_targetpic_path_btn.hide()
        self.interval_seconds.setValue(float(self.interval_seconds_value))
        self.interval_seconds_max.setValue(float(self.interval_seconds_value_max))
        self.loop_min.setValue(float(self.loop_min_value))
        self.show_target_path.setText(self.custom_target_path_value)
        self.screen_rate.setValue(float(self.screen_scale_rate_value))
        if self.run_mode_value == '正常-可后台':
            self.runmod_nomal.setChecked(True)
        else:
            self.runmod_compatibility.setChecked(True)
        if self.match_method_value == '模板匹配':
            self.template_matching.setChecked(True)
        else:
            self.sift_matching.setChecked(True)
        if self.process_num_value == '单开':
            self.process_num_one.setChecked(True)
            self.show_handle_title.show()
            self.show_handle_num.hide()
        else:
            self.process_num_more.setChecked(True)
            self.show_handle_num.show()
            self.show_handle_title.hide()
        if self.times_mode == "按分钟计算":
            self.run_by_min.setChecked(True)
        else:
            self.run_by_rounds.setChecked(True)

        # 设置界面上显示的匹配目标文件夹的选项名称
        for i in range(len(target_file_name_list)):
            self.select_target_path_mode_combobox.setItemText(i, target_file_name_list[i][0])

        # 绑定信号
        self.btn_start.clicked.connect(self.__on_clicked_btn_begin)
        self.btn_pause.clicked.connect(self.__on_clicked_btn_pause)
        self.btn_resume.clicked.connect(self.__on_clicked_btn_resume)
        self.btn_stop.clicked.connect(self.__on_clicked_btn_cancel)
        self.btn_exit.clicked.connect(self.__on_clicked_exit)
        self.select_target_path_mode_combobox.currentIndexChanged.connect(
            lambda: self.select_target_path_mode_btn_enable(self.select_target_path_mode_combobox.currentIndex()))
        self.btn_select_handle.clicked.connect(self.__on_click_btn_select_handle)
        self.select_targetpic_path_btn.clicked.connect(self.__on_click_btn_select_custom_path)
        self.config_set_btn.clicked.connect(self.__on_click_btn_config_set)
        self.targetpic_path_btn.clicked.connect(self.__on_click_btn_target_pic_folder_open)

    # 控制台消息重定向槽函数，控制台字符追加到 run_log中
    def output_write(self, text):
        # self.run_log.insertPlainText(text)
        # self.run_log.append(text)
        cursor = self.run_log.textCursor()
        # cursor.insertText(text)
        cursor.insertHtml(text)
        self.run_log.setTextCursor(cursor)
        self.run_log.ensureCursorVisible()

    # 根据下拉框内容，设置自定义文件夹按钮是否可点击
    def select_target_path_mode_btn_enable(self, tag):
        if tag == 7:
            self.select_targetpic_path_btn.show()
        else:
            self.select_targetpic_path_btn.hide()
            self.show_target_path.setText('')

    # 开始按钮被点击的槽函数
    def __on_clicked_btn_begin(self):
        # self.run_log.setTextInteractionFlags(PyQt5.QtCore.Qt.NoTextInteraction)  # 禁止选中
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_resume.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.btn_start.hide()
        self.btn_pause.show()
        self.btn_resume.hide()
        self.btn_stop.show()
        self.set_edit_enabled(False)
        self.run_log.setText('')
        self.thread = MatchingThread(self)  # 创建线程
        self.thread.finished_signal.connect(self.thread_finished)  # 线程信号和槽连接，任务正常结束重置按钮状态
        self.thread.progress_val_signal.connect(self.loop_progress.setValue)  # 线程信号和槽连接，设置进度条
        self.thread.clean_run_log_signal.connect(self.run_log.setText)  # 线程信号和槽连接，清空日志
        sleep(0.1)
        self.thread.start()

    # 暂停按钮被点击的槽函数
    def __on_clicked_btn_pause(self):
        print("<br>---已暂停!---")
        print("<br>日志分析工具：<a href=" + self.log_analysis_url.as_posix() + ">->点击使用</a><br>")
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(False)
        self.btn_resume.setEnabled(True)
        self.btn_stop.setEnabled(True)
        self.btn_resume.show()
        self.btn_pause.hide()
        sleep(0.1)
        self.thread.pause()

    # 恢复按钮被点击的槽函数
    def __on_clicked_btn_resume(self):
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_resume.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.btn_resume.hide()
        self.btn_pause.show()
        sleep(0.1)
        self.thread.resume()

    # 停止按钮被点击的槽函数
    def __on_clicked_btn_cancel(self):
        print("<br>---已终止!---")
        print("<br>日志分析工具：<a href=" + self.log_analysis_url.as_posix() + ">->点击使用</a><br>")
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_resume.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.set_edit_enabled(True)
        self.btn_start.show()
        self.btn_pause.hide()
        self.btn_resume.hide()
        self.btn_stop.hide()
        sleep(0.1)
        self.thread.cancel()

    # 正常完成后的槽函数
    def thread_finished(self):
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_resume.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.set_edit_enabled(True)
        self.btn_start.show()
        self.btn_pause.hide()
        self.btn_resume.hide()
        self.btn_stop.hide()

    # 获取目标窗体的槽函数
    def __on_click_btn_select_handle(self):
        self.run_log.setText('')  # 清空运行日志
        self.thread_1 = GetActiveWindowThread(self)
        if self.process_num_one.isChecked():  # 如果单开
            self.thread_1.active_window_signal.connect(self.show_handle_title.setText)
        else:  # 如果多开
            self.thread_1.active_window_signal.connect(self.show_handle_num.setText)
        self.thread_1.start()

    # 点击选择自定义文件夹
    def __on_click_btn_select_custom_path(self):
        current_path = abspath(dirname(__file__))  # 当前路径
        custom_path = QFileDialog.getExistingDirectory(None, "选择文件夹", current_path + r'\img')  # 起始路径
        self.show_target_path.setText(custom_path)  # 显示路径

    # 配置文件修改按钮
    @staticmethod
    def __on_click_btn_config_set():
        current_path = abspath(dirname(__file__))  # 当前路径
        cmd = 'notepad ' + current_path + r'\modules\config.ini'
        # os.system(cmd)  # 使用cmd命令打开配置文件,使用subprocess替换system后，打包成exe不会弹出cmd窗口
        subprocess.call(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # 打开模板文件夹按钮
    @staticmethod
    def __on_click_btn_target_pic_folder_open():
        folder_path = abspath(dirname(__file__)) + r'\img'  # 当前路径
        os.startfile(folder_path)

    @staticmethod
    def get_update_status(now_tag1):
        """从github获取更新状态"""
        url = r"https://api.github.com/repos/aicezam/SmartOnmyoji/releases/latest"
        url2 = r"https://isu.ink/stats"

        try:
            header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42"}
            try:
                request2 = urllib.request.Request(url2, headers=header)
                urllib.request.urlopen(request2, timeout=0.5)
            finally:
                request = urllib.request.Request(url, headers=header)
                response = urllib.request.urlopen(request, timeout=1).read().decode('utf8')
                tag_name = json.loads(response)["tag_name"]  # 将 JSON 对象转换为 Python 字典后，取tag_name字段值

                latest_tag = re.findall(r"\d+\.?\d*", tag_name)
                now_tag1 = re.findall(r"\d+\.?\d*", now_tag1)

                if latest_tag[0] > now_tag1[0]:
                    return True, "检测到更新，当前最新版：", tag_name
                else:
                    return False
        except Exception as e:
            return False

    # 退出程序的槽函数
    def __on_clicked_exit(self):
        if self.btn_start.isHidden():
            self.thread.cancel()
        sys.exit(0)

    # 开始运行后，禁用编辑
    def set_edit_enabled(self, bool_val=False):
        self.if_end_do.setEnabled(bool_val)
        self.template_matching.setEnabled(bool_val)
        self.sift_matching.setEnabled(bool_val)
        self.runmod_nomal.setEnabled(bool_val)
        self.runmod_compatibility.setEnabled(bool_val)
        self.debug.setEnabled(bool_val)
        self.select_target_path_mode_combobox.setEnabled(bool_val)
        self.show_handle_title.setEnabled(bool_val)
        self.show_handle_num.setEnabled(bool_val)
        self.btn_select_handle.setEnabled(bool_val)
        self.process_num_one.setEnabled(bool_val)
        self.process_num_more.setEnabled(bool_val)
        self.show_target_path.setEnabled(bool_val)
        self.select_targetpic_path_btn.setEnabled(bool_val)
        self.interval_seconds.setEnabled(bool_val)
        self.interval_seconds_max.setEnabled(bool_val)
        self.loop_min.setEnabled(bool_val)
        self.click_deviation.setEnabled(bool_val)
        self.image_compression.setEnabled(bool_val)
        self.set_priority.setEnabled(bool_val)
        self.config_set_btn.setEnabled(bool_val)
        self.targetpic_path_btn.setEnabled(bool_val)
        self.screen_rate.setEnabled(bool_val)
        self.run_by_min.setEnabled(bool_val)
        self.run_by_rounds.setEnabled(bool_val)


class EmitStr(PyQt5.QtCore.QObject):
    """
    定义一个信号类，sys.stdout有个write方法，通过重定向，
    每当有新字符串输出时就会触发下面定义的write函数，进而发出信号
    """
    text_writ = PyQt5.QtCore.pyqtSignal(str)

    def write(self, text):
        self.text_writ.emit(str(text))


def except_out_config(exc_type, value, tb):
    print('<br>Error Information:')
    print('<br>Type:', exc_type)
    print('<br>Value:', value)
    print('<br>Traceback:', tb)


if __name__ == '__main__':

    if windll.shell32.IsUserAnAdmin():  # 是否以管理员身份运行
        sys.excepthook = except_out_config  # 错误信息输出

        app = QApplication(sys.argv)

        # 加载配置文件参数
        config_ini = ReadConfigFile()
        default_info = config_ini.read_config_ui_info()
        target_file_name = config_ini.read_config_target_path_files_name()
        myWindow = MainWindow(default_info, target_file_name)

        myWindow.setWindowTitle(now_tag)  # 设置窗口标题
        myWindow.show()
        sys.exit(app.exec_())
    else:
        windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)  # 调起UAC以管理员身份重新执行
        sys.exit(0)
