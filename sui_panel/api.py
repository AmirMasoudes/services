import json
from typing import Any, Dict, Optional

import requests
from django.conf import settings


class SUIPanelAPI:
    """
    لایه ارتباطی ساده با S-UI REST API (مسیر /apiv2)

    مستندات مرجع: https://github.com/alireza0/s-ui/wiki/API-Documentation
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        base_path: Optional[str] = None,
        use_ssl: Optional[bool] = None,
        token: Optional[str] = None,
    ) -> None:
        self.host = host or getattr(settings, "SUI_HOST", "localhost")
        self.port = port or getattr(settings, "SUI_PORT", 2095)
        self.base_path = (base_path or getattr(settings, "SUI_BASE_PATH", "/app")).rstrip(
            "/"
        )
        self.use_ssl = use_ssl if use_ssl is not None else getattr(
            settings, "SUI_USE_SSL", False
        )
        self.token = token or getattr(settings, "SUI_API_TOKEN", "")

        protocol = "https" if self.use_ssl else "http"
        self.base_url = f"{protocol}://{self.host}:{self.port}{self.base_path}/apiv2"

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "Django-SUI-Client/1.0",
            }
        )

    # --------- Low level helpers ---------
    def _headers(self) -> Dict[str, str]:
        headers = {}
        if self.token:
            headers["Token"] = self.token
        return headers

    def _handle_response(self, resp: requests.Response) -> Dict[str, Any]:
        try:
            data = resp.json()
        except Exception:
            resp.raise_for_status()
            return {}

        # طبق مستندات s-ui: {success, msg, obj}
        if not data.get("success", False):
            # خطا را به صورت استثنا بالا می‌بریم تا در لایه بالاتر مدیریت شود
            raise RuntimeError(data.get("msg") or "S-UI API error")

        return data

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = self.session.get(url, params=params or {}, headers=self._headers(), timeout=30)
        return self._handle_response(resp)

    def post(
        self, path: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        # طبق مستندات می‌توان بدنه را فرم یا JSON فرستاد؛ اینجا JSON استفاده می‌کنیم.
        resp = self.session.post(
            url,
            headers={**self._headers(), "Content-Type": "application/json"},
            data=json.dumps(data or {}),
            timeout=30,
        )
        return self._handle_response(resp)

    # --------- High level helpers (مطابق مستندات) ---------
    def get_inbounds(self, inbound_id: Optional[str] = None) -> Any:
        """
        GET /apiv2/inbounds
        """
        params: Dict[str, Any] = {}
        if inbound_id is not None:
            params["id"] = str(inbound_id)
        data = self.get("inbounds", params=params)
        return data.get("obj")

    def get_clients(self, client_id: Optional[str] = None) -> Any:
        """
        GET /apiv2/clients
        """
        params: Dict[str, Any] = {}
        if client_id is not None:
            params["id"] = str(client_id)
        data = self.get("clients", params=params)
        return data.get("obj")

    def get_users(self) -> Any:
        """
        GET /apiv2/users
        """
        data = self.get("users")
        return data.get("obj")

    def get_status(self, resources: str) -> Any:
        """
        GET /apiv2/status?r=cpu,mem,net,sys,...
        """
        data = self.get("status", params={"r": resources})
        return data.get("obj")

    def save(
        self,
        obj: str,
        action: str,
        data: Dict[str, Any],
        init_users: Optional[str] = None,
    ) -> Any:
        """
        POST /apiv2/save

        مطابق مستندات:
          object (string), action (string), data (JSON), initUsers (optional string)
        """
        payload: Dict[str, Any] = {
            "object": obj,
            "action": action,
            "data": data,
        }
        if init_users is not None:
            payload["initUsers"] = init_users

        resp_data = self.post("save", data=payload)
        return resp_data.get("obj")


