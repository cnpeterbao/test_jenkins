print('hello world')
print('hello world')
print('hello world')
import os, re
import time
import threading
import subprocess

path = os.path.abspath('./resource')


class mythread(threading.Thread):
    def __init__(self, deviceid):
        threading.Thread.__init__(self)
        self.threadid = deviceid

    def run(self):
        flag = True
        print("Starting--" + self.threadid)
        self.remount()
        self.reboot()
        time.sleep(30)
        while flag:
            print(self.threadid + "--reboot result:" + self.reboot_result())
            if '1' in self.reboot_result():
                flag = False
            else:
                time.sleep(10)
        self.remount()
        self.pushfile()
        self.kill_audio()
        print("Exiting--" + self.threadid)

    def remount(self):
        shellcmd = []
        shellcmd.append("adb -s " + self.threadid + " wait-for-device")
        shellcmd.append("adb -s " + self.threadid + " root")
        shellcmd.append("adb -s " + self.threadid + " remount")
        shellcmd.append("adb -s " + self.threadid + " shell svc power stayon true")
        for cmd in shellcmd:
            os.system(cmd)
        time.sleep(5)

    def reboot(self):
        os.system("adb -s " + self.threadid + " reboot")

    def pushfile(self):
        platform = os.popen('adb -s ' + self.threadid + ' shell "getprop ro.board.platform"').read().strip()
        model = os.popen('adb -s ' + self.threadid + ' shell getprop ro.build.product').read().strip()
        print(self.threadid + "--platform:" + platform + ";model:" + model)
        if 'mt' in platform:
            os.system(
                "adb -s " + self.threadid + " push resource/PlaybackVolDigi_AudioParam.xml vendor/etc/audio_param")
        else:
            if 'thor' in model or 'zeus' in model or 'cupid' in model or 'ingres' in model or 'zizhan' in model:
                os.system(
                    "adb -s " + self.threadid + " push resource/audio_policy_engine_stream_volumes.xml /vendor/etc")
            else:
                os.system(
                    "adb -s " + self.threadid + " push resource/audio_policy_engine_stream_volumes_mi.xml /vendor/etc")

    def kill_audio(self):
        audiopid = os.popen('adb -s ' + self.threadid + ' shell "pgrep audioserver"').read().strip()
        print(self.threadid + "--audiopid:" + audiopid)
        os.system('adb -s ' + self.threadid + ' shell "kill -9 "' + audiopid)
        time.sleep(5)

    def reboot_result(self):
        result = "adb -s " + self.threadid + " shell getprop sys.boot_completed"
        reboot_result = subprocess.Popen(result, shell=True,
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        getResult = reboot_result.stdout.readline().decode("utf-8")
        return getResult


def get_device():
    global deviceList
    deviceList = []
    for i in range(1):
        try:
            pout1 = subprocess.Popen('adb devices', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            getDevice = pout1.stdout.readlines()
            a = int(len(getDevice))
            for j in range(1, a - 1):
                deviceId = getDevice[j].split()
                device = deviceId[0]
                deviceList.append(device)
            print(deviceList)
        except(IndexError, e):
            print("没有发现测试需要的设备，设备未连接或者已经断开！！！")


def start_run():
    for k in range(int(len(deviceList))):
        deviceid = str(deviceList[k].decode("utf-8"))
        thread = mythread(deviceid)
        thread.start()


if __name__ == '__main__':
    get_device()
    start_run()
