# -*- coding: utf-8 -*-
"""
description: 封装了各类执行命令方法
"""

import os
import subprocess
import sre_constants
import fcntl
from time import sleep
import psutil
# from serial_base import Serial, Timeout
from serial import Serial, Timeout


def read_stdout(stdout, fragment):
    """
    description: 读取stdout处理为未成行数据和各行数据列表
    arguments:
        stdout:
            description: 标准输出对象
            type: any
        fragment:
            description: 上次未满一行的数据
            type: str
    return:
        description: 返回本次未满一行的数据和本次各行数据的列表
        type: tuple
    """
    try:
        buffer = stdout.read()
    except (OSError, TypeError):
        buffer = ""
    if buffer:
        lines = buffer.splitlines()
        if fragment:
            lines[0] = fragment + lines[0]
        if buffer.endswith(("\n", "\r\n", "\r")):
            fragment = ""
        else:
            fragment = lines[-1]
            lines.pop(-1)

        # for line in lines:
        #     logger.info(line)

        return fragment, lines
    return fragment, []


def kill_process(pid, kill_self=True):
    """
    description: 杀掉指定pid进程以及其子进程
    arguments:
        pid:
            description: 需杀死的进程pid
            type: int
        kill_self:
            description: 是否杀掉自己
            type: bool
    return:
        description: 对应的网口，失败为空
        type: bool
    """
    try:
        proc = psutil.Process(pid)
        child_proc_list = proc.children(recursive=True)
        for p in child_proc_list:
            try:
                p.kill()
                # logger.info("%s kill成功" % p)
            except psutil.NoSuchProcess:
                # logger.info("%s已经被杀死" % p)
                pass
        if kill_self:
            try:
                proc.kill()
                # logger.info("%s kill成功" % proc)
            except psutil.NoSuchProcess:
                # logger.info("%s已经被杀死" % proc)
                pass
    except Exception:  # pylint: disable=broad-except
        # logger.error("kill过程出现异常%s" % str(Exception))
        return False
    return True


def run_shell(cmd="", cwd=None, timeout=None):
    """
    description: 执行指定的shell命令
    arguments:
        cmd:
            description: 想要执行的shell命令，如ls
            type: str
        cwd:
            description: 运行命令的工作目录
            type: str
            allow_none: True
        timeout:
            description: 运行命令的超时时间
            type:
                - int
                - float
            allow_none: True
    return:
        description: 返回命令退出码和命令执行回显列表
        type: dict
        properties:
            status:
                description: 命令退出码
                type: int
                allow_none: True
            output:
                description: 命令回显
                type: list
                items:
                    type: str
    """
    try:
        t = Timeout(timeout)
        expired = False
        # logger.info("run shell: %s" % cmd)
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             close_fds=True, cwd=cwd, universal_newlines=True, bufsize=0)
        flags = fcntl.fcntl(p.stdout, fcntl.F_GETFL)
        flags |= os.O_NONBLOCK
        fcntl.fcntl(p.stdout, fcntl.F_SETFL, flags)
        output = []

        fragment = ""
        while True:
            fragment, lines = read_stdout(stdout=p.stdout, fragment=fragment)
            if lines:
                output += lines

            if p.poll() is not None:
                fragment, lines = read_stdout(stdout=p.stdout, fragment=fragment)
                if lines:
                    output += lines
                if fragment:
                    # logger.info(fragment)
                    output += [fragment]
                break

            if t.expired():
                expired = True
                break

        p.stdout.close()
        if expired:
            # logger.info("命令 %s 执行超时" % cmd)
            kill_process(p.pid)
            status = -1
        else:
            p.wait()
            status = p.returncode
        return {"status": status, "output": output}
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        # logger.error("run shell fail: %s" % str(e))
        return {"status": -1, "output": str(e).splitlines()}


def run_serial(port="",
               cmd="",
               size=None,
               expected=None,
               baud_rate=115200,
               exclusive=True,
               timeout=1,
               need_return=True,
               delay=0):
    """
    description: 在指定的串口执行命令
    arguments:
        port:
            description: 执行命令的串口
            type: str
        cmd:
            description: 想要执行的串口命令
            type: str
        size:
            description: 最小想要读取的字节数，当need_return为False时不生效
            type: int
            allow_none: True
        expected:
            description: 回显出现指定关键词则直接返回,当读取字节大于指定字节或者超时也会返回,多关键词传入tuple
            type:
                - str
                - tuple
            allow_none: True
        baud_rate:
            description: 波特率，默认115200
            type: int
        exclusive:
            description: 是否独占，默认True，打开时不可再次被打开
            type: bool
        timeout:
            description: 超时时间，默认1秒
            type:
                - int
                - float
            allow_none: True
        need_return:
            description: 是否需要回显，默认为True
            type: bool
        delay:
            description: 完成读写后的延迟等待时间，默认0秒
            type:
                - int
                - float
    return:
        description: 返回命令退出码和命令执行回显列表
        type: dict
        properties:
            status:
                description: 命令是否执行成功
                type: bool
            output:
                description: 命令回显
                type: str
    """

    try:
        with Serial(port=port, baudrate=baud_rate, exclusive=exclusive, timeout=timeout) as s:
            s.reset_buffer()
            buffer_size = s.in_waiting
            if buffer_size != 0:
                s.read(buffer_size)
            s.write(cmd.encode(encoding="utf-8", errors="ignore"))
            # logger.info("%s write: %s" % (port, cmd))
            if not need_return:
                s.close()
                sleep(delay)
                return {"status": True, "output": ""}
            if expected:
                output = s.read_until(expected=expected, size=size)
            else:
                output = s.read_min_size(size=size)
        # logger.info("%s read: %s" % (port, output))
        sleep(delay)
        return {"status": True, "output": output}
    except (IOError, ValueError, TypeError, sre_constants.error) as e:
        # logger.error("run_serial: %s" % str(e))
        return {"status": False, "output": str(e)}
