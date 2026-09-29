"""Persist account responses before interpreting them; never replay unknown calls."""
import hashlib
import json
from pathlib import Path
import jsonschema
from .coordinator import _atomic_json


class AccountCallPending(RuntimeError):
    pass


def invoke_saved(prompt, schema, workspace, timeout=480):
    from scripts.agy_pipeline import invoke
    root = Path(workspace)
    root.mkdir(parents=True, exist_ok=True)
    request = {'prompt': prompt, 'schema': schema}
    identity = hashlib.sha256(json.dumps(request, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    request_path, response_path = root / 'account-request.json', root / 'account-response.json'
    if request_path.exists():
        saved = json.loads(request_path.read_text())
        if saved['identity'] != identity:
            raise AccountCallPending('Đầu vào lời gọi khác hồ sơ đã lưu; không gửi lại.')
        if not response_path.exists():
            raise AccountCallPending('Lời gọi tài khoản chưa có kết quả lưu; cần đối chiếu phiên cũ, không gửi trùng.')
        result = json.loads(response_path.read_text())
    else:
        _atomic_json(request_path, {'identity': identity, **request})
        result = invoke(prompt, schema, root, timeout=timeout)
        _atomic_json(response_path, result)
    if not isinstance(result, dict) or not isinstance(result.get('structured_output'), dict):
        raise ValueError('Tài khoản không trả JSON có cấu trúc.')
    jsonschema.validate(result['structured_output'], schema)
    return result
