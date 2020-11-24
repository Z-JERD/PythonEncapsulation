import sys
import json
import datetime
import traceback
import urllib

from werkzeug.datastructures import ImmutableMultiDict

httpcodes = [
    ("CONTINUE", 100),
    ("SWITCHING_PROTOCOLS", 101),
    ("PROCESSING", 102),
    ("OK", 200),
    ("CREATED", 201),
    ("ACCEPTED", 202),
    ("NON_AUTHORITATIVE_INFORMATION", 203),
    ("NO_CONTENT", 204),
    ("RESET_CONTENT", 205),
    ("PARTIAL_CONTENT", 206),
    ("MULTI_STATUS", 207),
    ("IM_USED", 226),
    ("MULTIPLE_CHOICES", 300),
    ("MOVED_PERMANENTLY", 301),
    ("FOUND", 302),
    ("SEE_OTHER", 303),
    ("NOT_MODIFIED", 304),
    ("USE_PROXY", 305),
    ("TEMPORARY_REDIRECT", 307),
    ("BAD_REQUEST", 400),
    ("UNAUTHORIZED", 401),
    ("PAYMENT_REQUIRED", 402),
    ("FORBIDDEN", 403),
    ("NOT_FOUND", 404),
    ("METHOD_NOT_ALLOWED", 405),
    ("NOT_ACCEPTABLE", 406),
    ("PROXY_AUTHENTICATION_REQUIRED", 407),
    ("REQUEST_TIMEOUT", 408),
    ("CONFLICT", 409),
    ("GONE", 410),
    ("LENGTH_REQUIRED", 411),
    ("PRECONDITION_FAILED", 412),
    ("REQUEST_ENTITY_TOO_LARGE", 413),
    ("REQUEST_URI_TOO_LONG", 414),
    ("UNSUPPORTED_MEDIA_TYPE", 415),
    ("REQUESTED_RANGE_NOT_SATISFIABLE", 416),
    ("EXPECTATION_FAILED", 417),
    ("UNPROCESSABLE_ENTITY", 422),
    ("LOCKED", 423),
    ("FAILED_DEPENDENCY", 424),
    ("UPGRADE_REQUIRED", 426),
    ("PRECONDITION_REQUIRED", 428),
    ("TOO_MANY_REQUESTS", 429),
    ("REQUEST_HEADER_FIELDS_TOO_LARGE", 431),
    ("INTERNAL_SERVER_ERROR", 500),
    ("NOT_IMPLEMENTED", 501),
    ("BAD_GATEWAY", 502),
    ("SERVICE_UNAVAILABLE", 503),
    ("GATEWAY_TIMEOUT", 504),
    ("HTTP_VERSION_NOT_SUPPORTED", 505),
    ("INSUFFICIENT_STORAGE", 507),
    ("NOT_EXTENDED", 510),
    ("NETWORK_AUTHENTICATION_REQUIRED", 511)
]

httpcodes_r2s = dict(httpcodes)
httpcodes_s2r = dict([(i, s) for s, i in httpcodes])


class HttpResponse(object):
    """处理响应值"""

    def __init__(self, status, reason, headers, body):

        self.exc_info = None

        self.status = status if status else httpcodes_r2s[reason]
        self.reason = reason if reason else httpcodes_s2r[status]

        if body is None:
            body = b''

        if type(body) == str:
            body = body.encode('utf-8')
        elif type(body) == bytes:
            body = body
        else:
            body = json.dumps(body, ensure_ascii=False, default=str).encode('utf-8')

        self.body = body

        return


class HttpOK(HttpResponse):
    def __init__(self, headers=[], result=None):
        super().__init__(200, None, headers, {'status': 200, 'result': result, 'error': None})

        return


class HttpBadRequest(HttpResponse):
    def __init__(self, headers=[], reason='bad request'):
        super().__init__(400, None, headers, {'status': 400, 'result': None, 'error': reason})

        return


class HttpNotFound(HttpResponse):
    def __init__(self, headers=[], reason='not found'):
        super().__init__(404, None, headers, {'status': 404, 'error': reason})
        return


class HttpForbidden(HttpResponse):
    def __init__(self, headers=[], reason='forbidden'):
        super().__init__(403, None, headers, {'status': 403, 'result': None, 'error': reason})

        return


class HttpInternalServerError(HttpResponse):
    def __init__(self, exc_info=None, reason='internal error'):
        self.exc_info = sys.exc_info() if exc_info == None else exc_info
        super().__init__(500, None, [], {'status': 500, 'result': None, 'error': reason})
        return


class JrWsgiServerobject():
    """
      对程序进行封装
      1. 根据url找到对象的函数 对请求做参数校验
      2. 异常处理
      3. 封装返回值
    """
    OK = HttpOK
    BadRequest = HttpBadRequest
    NotFound = HttpNotFound
    Forbidden = HttpForbidden
    InternalServerError = HttpInternalServerError

    def __init__(self):
        """
            实列化时：获取当前服务中所有以url开头的函数 转换如下形式
             self.rules = {
                '/chain_regulate/get_chains': 'url__chain_regulate__get_chains',
                '/chain_regulate/get_cinemas': 'url__chain_regulate__get_cinemas',
                '/chain_regulate/get_halls': 'url__chain_regulate__get_halls',
                '/inner/chain_regulate/get_chains': 'url__inner__chain_regulate__get_chains'
             }
        """
        self.rules = [(m[3:].replace('__', '/'), m) for m in dir(self) if m.startswith('url__')]
        self.rules = dict(self.rules)

        return

    @staticmethod
    def pageinfo(page=1, pagesize=20, total=0):
        """分页处理"""
        page = int(page)
        if page <= 0:
            page = 1

        pagesize = int(pagesize)
        if pagesize <= 0:
            pagesize = 20

        total = int(total)
        totalpage = abs(((-1) * total) // pagesize)
        if page > totalpage > 0:
            page = totalpage

        offset = (page - 1) * pagesize
        d = {
            "page": page,
            "pagesize": pagesize,
            "offset": offset,
            "total": total,
            "first": 1,
            "prev": page - 1 if (page > 1) else 1,
            "next": page + 1 if (page < totalpage) else totalpage,
            "last": totalpage
        }
        pagination = []
        i = -4
        while i < 5:
            if 1 <= page + i <= totalpage:
                pagination.append(page + i)
            i = i + 1
        d["links"] = pagination

        return d

    def wsgi_request_handle(self, request_path, string_parameter=None, json_parameter=None):
        """逻辑处理层"""
        wi = self.rules.get(request_path)
        wf = None

        if wi:
            wf = getattr(self, wi, None)

        if wf:
            args = string_parameter if string_parameter else dict()
            argsrcs = dict.fromkeys(string_parameter.keys(), 'qs') if string_parameter else dict()

            if json_parameter:
                args.update(json_parameter)
                argsrcs.update(dict.fromkeys(json_parameter.keys(), 'js'))

            try:
                # assert not (set(args.keys()) - set(wf.__annotations__.keys())), '不符合条件的参数错误'
                for k, p in wf.__annotations__.items():
                    if type(p) == type and k in args:
                        try:
                            if p == list:
                                if argsrcs[k] == 'qs':
                                    args[k] = json.loads(args[k]) if args[k].startswith('[') else args[k].split(',')
                            elif p == bool:
                                if argsrcs[k] == 'qs':
                                    args[k] = {'true': True, 'false': False}[args[k].lower()]
                            elif p == dict:
                                if argsrcs[k] == 'qs':
                                    args[k] = json.loads(args[k])
                            elif p == datetime.datetime:
                                fmt = "%Y-%m-%dT%H:%M:%S" if 'T' in args[k] else "%Y-%m-%d %H:%M:%S"
                                args[k] = datetime.datetime.strptime(args[k], fmt)
                            elif p == datetime.date:
                                args[k] = datetime.datetime.strptime(args[k], "%Y-%m-%d").date()
                            elif p == datetime.time:
                                args[k] = datetime.datetime.strptime(args[k], "%H:%M:%S").time()
                            elif p == int:
                                if argsrcs[k] == 'qs':
                                    args[k] = int(args[k])
                            elif p == float:
                                if argsrcs[k] == 'qs':
                                    args[k] = float(args[k])
                            elif p == str:
                                if argsrcs[k] == 'qs':
                                    args[k] = str(args[k])
                            else:
                                args[k] = p(args[k])

                            assert type(args[k]) == p

                        except Exception as e:
                            raise AssertionError('不符合条件的参数错误')

                resp = wf(**args)
            except Exception as e:
                resp = self.http_exception(e)

            if not isinstance(resp, HttpResponse):
                resp = self.OK([], resp)

        else:
            resp = self.http_notfound()

        return resp.body, resp.status

    def http_exception(self, e):

        traceback.print_exc()  # 直接给打印出来
        # traceback.format_exc()          返回字符串

        if isinstance(e, TypeError) and e.args[0].startswith('url__'):
            return self.BadRequest([], '不符合要求的参数错误')

        if isinstance(e, AssertionError):
            return self.BadRequest([], e.args[0])

        return self.InternalServerError(e)

    def http_notfound(self):
        return self.NotFound()

    def wsgi_flask_handle(self, request_obj, response_obj):
        """Flask服务处理"""
        request_path, ct_method, ct_type = request_obj.path, request_obj.method, request_obj.content_type
        args_parameter, json_parameter = ImmutableMultiDict(request.args).to_dict(), None

        if ct_method == "POST":

            if ct_type.startswith('application/json') and request.get_json():
                """json数据"""
                json_parameter = request_obj.get_json()
            elif ct_type.startswith('text/plain') and request.get_data():
                json_parameter = request.get_data().decode('utf-8')
            elif ct_type.startswith('multipart/form-data'):
                """上传文件"""
                pass

            elif ct_type.startswith('application/x-www-form-urlencoded'):
                """表单数据"""
                json_parameter = request_obj.get_data().decode('utf-8')

                qs = json_parameter.split('&')
                qs = [x.split('=', 1) for x in qs if x]

                qs = dict([(k, urllib.parse.unquote_plus(v)) for k, v in qs if not k.startswith('_')])

                args_parameter.update(qs)

                json_parameter = None

        result, status_code = self.wsgi_request_handle(request_path, args_parameter, json_parameter)

        response = response_obj(result, status_code)
        response.headers["Content-Type"] = 'text/html; charset=utf-8'

        return response


if __name__ == "__main__":
    """使用示例"""

    import fwsgi
    import datetime
    from flask import Flask, make_response, request
    from flask_restful import Resource, Api

    app = Flask(__name__)
    api = Api(app)


    class TaskListAPI(Resource, fwsgi.JrWsgiServerobject):

        def __init__(self):
            super().__init__()

        def url__tasklistapi__create_cinema(self, code: int, name: str):
            return {"name": name, "code": code}

        def url__tasklistapi__get_cinema(self, code: int, name: str, info: dict, create_date: datetime.date):
            return {"name": name, "code": code, "info": info, "create_date": create_date}

        def get(self):
            response = self.wsgi_flask_handle(request, make_response)

            return response

        def post(self):
            response = self.wsgi_flask_handle(request, make_response)

            return response


    #  endpoint需使用不同的值
    api.add_resource(TaskListAPI, '/tasklistapi/create_cinema', endpoint='create_cinema')
    api.add_resource(TaskListAPI, '/tasklistapi/get_cinema', endpoint='get_cinema')

    app.run("0.0.0.0", 8088, debug=True)


