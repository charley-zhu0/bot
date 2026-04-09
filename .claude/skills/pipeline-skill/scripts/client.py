"""项目系统 API 客户端实现，包含签名逻辑。"""

import time
import urllib.parse
from hashlib import md5
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import load_env, validate_config

# 默认超时时间（秒）
REQUEST_TIMEOUT = 30


def url_encoder(params):
    """特殊的 URL 编码方式，用于生成签名"""
    g_encode_params = []

    def _encode_params(params, p_key=None):
        encode_params = {}
        if isinstance(params, dict):
            for key in params:
                encode_key = '{}[{}]'.format(p_key, key)
                encode_params[encode_key] = params[key]
        elif isinstance(params, (list, tuple)):
            for offset, value in enumerate(params):
                encode_key = '{}[{}]'.format(p_key, offset)
                encode_params[encode_key] = value
        else:
            g_encode_params.append((p_key, params))
            
        for key in encode_params:
            value = encode_params[key]
            _encode_params(value, key)

    if isinstance(params, dict):
        params = params.items()
        
    for key, value in params:
        _encode_params(value, key)
        
    return urllib.parse.urlencode(g_encode_params)


def generate_sign(params: dict, token: str) -> str:
    """生成签名
    
    1. 组合所有参数
    2. 按 key 字母升序排序
    3. 拼接成 GET 参数格式并 urlencode
    4. 取 MD5
    5. 拼接 token 后再取 MD5
    """
    verify_params = sorted(params.items(), key=lambda d: d[0], reverse=False)
    encoded_str = url_encoder(verify_params)
    
    first_md5 = md5(encoded_str.encode("utf-8")).hexdigest()
    final_md5 = md5((first_md5 + token).encode("utf-8")).hexdigest()
    
    return final_md5


class ProjectClient:
    """项目系统 API 客户端"""

    def __init__(self, url: str, user_mail: str, token: str, default_sub_id: str = None):
        self.base_url = url.rstrip("/")
        self.user_mail = user_mail
        self.token = token
        self.default_sub_id = default_sub_id

        # 配置 session 和重试机制
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _prepare_params(self, params: dict) -> dict:
        """准备请求参数：添加必须的固定参数并计算签名"""
        final_params = params.copy() if params else {}
        
        # 添加通用参数
        final_params.update(
            t=int(time.time()),
            user_mail=self.user_mail
        )

        # 生成并添加签名
        final_params["sign"] = generate_sign(final_params, self.token)
        return final_params

    def _handle_response(self, response: requests.Response) -> dict:
        """处理接口响应"""
        response.raise_for_status()
        result = response.json()
        
        # 判断业务错误码
        if result.get("errno", 0) != 2000:
            error_msg = result.get("errmsg", "未知错误")
            raise Exception(f"API 业务异常 (errno: {result.get('errno')}): {error_msg}")
            
        return result.get("data", {})

    def get(self, path: str, params: dict = None) -> dict:
        """发送 GET 请求"""
        final_params = self._prepare_params(params)
        url = f"{self.base_url}{path}"
        
        # 按照极库云的要求，GET 请求需要自己编码好拼在 url 后面
        # 不要直接交给 requests.get(url, params) 处理，防止 requests 默认 urlencode 和其自定义的不一致
        query_string = url_encoder(final_params)
        full_url = f"{url}?{query_string}"
        
        response = self.session.get(
            full_url,
            headers={"From-App": self.user_mail},
            timeout=REQUEST_TIMEOUT
        )
        return self._handle_response(response)

    def post(self, path: str, data: dict = None) -> dict:
        """发送 POST 请求"""
        final_params = self._prepare_params(data)
        url = f"{self.base_url}{path}"

        response = self.session.post(
            url,
            json=final_params,
            headers={"From-App": self.user_mail},
            timeout=REQUEST_TIMEOUT
        )
        return self._handle_response(response)


class LazyProjectClient:
    """延迟初始化的客户端，方便在 Click CLI 中使用"""

    def __init__(self, env_file: str | None = None):
        object.__setattr__(self, "_env_file", env_file)
        object.__setattr__(self, "_client", None)

    def __getattr__(self, name):
        client = object.__getattribute__(self, "_client")
        if client is None:
            client = get_project_client(env_file=object.__getattribute__(self, "_env_file"))
            object.__setattr__(self, "_client", client)
        return getattr(client, name)


def get_project_client(env_file: str | None = None) -> ProjectClient:
    """初始化并返回项目系统客户端"""
    config = load_env(env_file=env_file)
    
    errors = validate_config(config)
    if errors:
        raise ValueError("配置错误:\n  " + "\n  ".join(errors))
        
    return ProjectClient(
        url="https://geelib.qihoo.net",
        user_mail=config["USER_MAIL"],
        token=config["TOKEN"],
        default_sub_id=config.get("DEFALT_PIPELINE_ID")
    )
