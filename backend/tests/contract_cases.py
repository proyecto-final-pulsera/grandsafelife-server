"""Requests independientes del framework; no derivar expectativas del código migrado."""
from copy import deepcopy

PREFIX = "/grandsafelife/api/v1"


def cases():
    result = []

    def add(name, method, path, **kwargs):
        case = dict(name=name, method=method, path=PREFIX + path,
                    headers={"Authorization": "Bearer contract-test"}, **kwargs)
        result.append(case)
        return case

    operations = [
        ("GET", "/users/me", None),
        ("GET", "/users/by-email?email=maria.gomez@example.com", None),
        ("GET", "/users/user_002", None),
        ("POST", "/users/me", {"name": "Juan", "email": "juan@example.com", "avatar": "avatar"}),
        ("PATCH", "/users/user_002", {"name": "Nuevo"}),
        ("GET", "/homes/home_7f3a92", None),
        ("POST", "/homes", {"name": "Casa"}),
        ("PATCH", "/homes/home_7f3a92", {"name": "Nueva"}),
        ("DELETE", "/homes/home_7f3a92", None),
        ("POST", "/homes/home_7f3a92/monitoring-requests", {"email": "maria@example.com", "role": "observer"}),
        ("GET", "/users/me/monitoring-requests", None),
        ("POST", "/monitoring-requests/request_001/answer", {"answer": "accepted"}),
        ("GET", "/devices/dev_a81f23", None),
        ("POST", "/devices/dev_a81f23/association", {"home_id": "home_7f3a92"}),
        ("PATCH", "/devices/dev_a81f23", {"name": "Sensor", "connection_by": "-1"}),
        ("DELETE", "/devices/dev_a81f23/association", None),
        ("GET", "/users/user_admin_001/devices", None),
        ("GET", "/homes/home_7f3a92/devices", None),
        ("GET", "/devices/dev_a81f23/location", None),
        ("GET", "/devices/dev_a81f23/stats/daily?date=2026-09-01", None),
        ("GET", "/devices/dev_a81f23/stats/monthly?month=2026-09", None),
        ("GET", "/devices/dev_a81f23/stats/monthly/previous", None),
        ("GET", "/devices/dev_a81f23/stats/daily/last-week", None),
        ("GET", "/devices/dev_a81f23/alarms", None),
        ("PUT", "/devices/dev_a81f23/alarms", {"alarm_1": {"name": "Medicación", "time_in_minutes": 600, "days": 127, "is_active": True}}),
        ("POST", "/fall-detection/requests", {"samples": [1, None, {"x": True}]}),
        ("GET", "/fall-detection/requests/1", None),
    ]
    for index, (method, path, body) in enumerate(operations):
        base = add(f"operation-{index:02}", method, path, **({"json": body} if body is not None else {}))
        missing = deepcopy(base)
        missing.update(name=base["name"] + "-no-auth", headers={})
        result.append(missing)
        if body is not None:
            for suffix, payload in [("missing-body", None), ("array", []), ("null", None), ("empty", {})]:
                variant = deepcopy(base)
                variant["name"] += "-" + suffix
                variant.pop("json")
                if suffix != "missing-body":
                    import json
                    variant["content"] = json.dumps(payload)
                    variant["headers"]["Content-Type"] = "application/json"
                result.append(variant)
            invalid = deepcopy(base)
            invalid.update(name=base["name"] + "-extra", json={**body, "unexpected": 1})
            result.append(invalid)
            malformed = deepcopy(base)
            malformed.pop("json")
            malformed.update(name=base["name"] + "-malformed", content='{"name":')
            malformed["headers"]["Content-Type"] = "application/json"
            result.append(malformed)
        if method == "PATCH":
            for field in body:
                for suffix, value in [("null", None), ("empty", ""), ("number", 12)]:
                    add(f"patch-{index}-{field}-{suffix}", method, path, json={field: value})

    for query, values in [("daily?date=", ["2026-02-31", "2026-09-00", "2026-13-01", "bad", ""]),
                          ("monthly?month=", ["2026-00", "2026-9", "", "2026-12"])]:
        for i, value in enumerate(values):
            add(f"date-{query}-{i}", "GET", "/devices/d/stats/" + query + value)
    for path in ["/users/by-email", "/users/by-email?email=", "/users/by-email?email=not-an-email",
                 "/devices/d/stats/daily", "/devices/d/stats/monthly"]:
        add("query-" + path, "GET", path)
    for value in ["0", "-1", "abc", "1.5", "001", "999999"]:
        add("request-id-" + value, "GET", "/fall-detection/requests/" + value)
    for field, values in [("name", ["", None]), ("time_in_minutes", [-1, 1440, 0, 1439, "600", 1.5]),
                          ("days", [-1, 999, "7"]), ("is_active", ["true", "bad"])]:
        for i, value in enumerate(values):
            alarm = {"name": "Alarma", "time_in_minutes": 600, "days": 127, "is_active": True}
            alarm[field] = value
            add(f"alarm-{field}-{i}", "PUT", "/devices/d/alarms", json={"a": alarm})
    for role in ["admin", "pending", "", None]:
        add(f"role-{role}", "POST", "/homes/h/monitoring-requests", json={"email": "x", "role": role})
    for answer in ["rejected", "pending", "", None]:
        add(f"answer-{answer}", "POST", "/monitoring-requests/r/answer", json={"answer": answer})
    for method in ["GET", "POST", "OPTIONS"]:
        add("unknown-" + method, method, "/not-registered")
    for method in ["PUT", "HEAD", "OPTIONS"]:
        add("wrong-method-" + method, method, "/users/me")
    add("trailing-slash", "GET", "/users/me/")
    for name, headers in [("empty-auth", {"Authorization": ""}), ("arbitrary-auth", {"authorization": "anything"})]:
        case = add(name, "GET", "/users/me")
        case["headers"] = headers
    add("multiple-errors", "POST", "/users/me", json={"name": "", "email": 5, "extra": True})["headers"] = {}
    add("extra-query", "GET", "/users/me?unexpected=1")
    add("repeated-query", "GET", "/users/by-email?email=first&email=last")
    return result
