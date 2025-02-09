# Based on https://github.com/Womsxd/MihoyoBBSTools/blob/master/docker.py

import os
import time
import datetime
from loghelper import log
import runpy

from crontab import CronTab
from captcha import stop_inference_server, bring_up_inference_server

time_format = "%Y-%m-%d %H:%M:%S"


def main():
    log.info("使用DOCKER运行米游社签到")
    env = os.environ
    cron_signin = env["CRON_SIGNIN"]
    cron = CronTab(cron_signin, loop=True, random_seconds=True)

    def next_run_time():
        nt = datetime.datetime.now().strftime(time_format)
        delayt = cron.next(default_utc=False)
        nextrun = datetime.datetime.now() + datetime.timedelta(seconds=delayt)
        nextruntime = nextrun.strftime(time_format)
        log.info(f"Current running datetime: {nt}")
        log.info(f"Next run datetime: {nextruntime}")

    def sign():
        bring_up_inference_server()

        log.info("Starting signing")
        multi = env["MULTI"].upper()
        if multi == 'TRUE':
            raise Exception('MULTI mode is unsupported in this branch')
            # os.system("python3 ./main_multi.py autorun")
        else:
            runpy.run_path('./main.py', run_name='__main__')

        stop_inference_server()

    sign()
    next_run_time()
    while True:
        ct = cron.next(default_utc=False)
        time.sleep(ct)
        sign()
        next_run_time()


if __name__ == '__main__':
    main()