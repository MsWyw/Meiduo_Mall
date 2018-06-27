from . import constants
from .yuntongxun.sms import CCP
from celery_tasks.main import app


# 发送短信
@app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    sms_code_time = str(constants.SMS_CODE_REDIS_EXPIRES // 60)
    ccp = CCP()
    ccp.send_template_sms(mobile, [sms_code, sms_code_time], constants.SMS_TEMP_ID)