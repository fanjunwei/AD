# coding=utf-8
# Date: 11-12-8
# Time: 下午10:28
import json
import threading

from django.http import HttpResponse
from django.core.cache import cache
from wechat_sdk import WechatBasic
from wechat_sdk.exceptions import OfficialAPIError

__author__ = u'王健'

wechatObjLock = threading.RLock()


def getResult(success, message=None, result=None, status_code=200, cachename=None):
    '''
    200 正常返回 code
    404 登录过期，需要重新登录
    '''
    map = {'success': success, 'message': message, 'status_code': status_code}
    if result:
        map['result'] = result
    jsonstr = json.dumps(map)
    if cachename:
        cache.set(cachename, jsonstr, 3600 * 24 * 31)
    return HttpResponse(jsonstr)


def getCachedAccessWechatObj(appID=None, appSecret=None, token=None):
    wechatObjLock.acquire()
    try:
        if not appID or not appSecret:
            return None
        access_token = cache.get('access_token_%s' % appID, None)
        access_token_expires_at = cache.get('access_token_expires_at_%s' % appID, None)
        wechatObj = WechatBasic(token=token, appid=appID, appsecret=appSecret,
                                access_token=access_token,
                                access_token_expires_at=access_token_expires_at)
        access_token_info = wechatObj.get_access_token()  # 检测access_token,更新access_token
        cache.set('access_token_%s' % appID, access_token_info['access_token'])
        cache.set('access_token_expires_at_%s' % appID, access_token_info['access_token_expires_at'])
        return wechatObj
    except OfficialAPIError:
        return None
    finally:
        wechatObjLock.release()