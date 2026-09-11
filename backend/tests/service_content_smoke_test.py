from __future__ import annotations

import http.cookiejar
import json
import sys
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend import core
from backend.server import DentalRequestHandler


def request(opener, base_url: str, path: str, method: str = "GET", payload=None, csrf=""):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Accept": "application/json", "X-Requested-With": "DentalSystem"}
    if body is not None:
        headers.update({"Content-Type": "application/json", "Origin": base_url})
    if csrf:
        headers["X-CSRF-Token"] = csrf
    target = urllib.request.Request(base_url + path, data=body, headers=headers, method=method)
    try:
        response = opener.open(target, timeout=10)
        return response.status, json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read() or b"{}")


def expect(status: int, expected: int, label: str) -> None:
    if status != expected:
        raise AssertionError(f"{label}: expected HTTP {expected}, received HTTP {status}")


def main() -> None:
    original_store = core.DATA_STORE
    original_file = core.DATA_FILE
    test_data_file = Path(__file__).with_name(".service_content_test.json")
    server = None
    thread = None

    try:
        try:
            core.DATA_STORE = None
            core.DATA_FILE = test_data_file
            data = core.seed_data()
            data["users"].append(
                {
                    "id": "usr_service_content_test",
                    "name": "Service Content Administrator",
                    "email": "service.content.admin@example.test",
                    "phone": "",
                    "role": "doctor",
                    "password_hash": core.hash_password("ServiceContentTest#2026"),
                    "created_at": core.utc_now(),
                }
            )
            core.save_data(data)

            server = ThreadingHTTPServer(("127.0.0.1", 0), DentalRequestHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base_url = f"http://127.0.0.1:{server.server_port}"
            opener = urllib.request.build_opener(
                urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
            )

            status, login = request(
                opener,
                base_url,
                "/api/login",
                "POST",
                {
                    "email": "service.content.admin@example.test",
                    "password": "ServiceContentTest#2026",
                    "_website": "",
                },
            )
            expect(status, 200, "doctor login")
            csrf = login["csrf_token"]

            service_payload = {
                "name": "Service Popup Test",
                "description": "A temporary service used to verify editable popup content.",
                "detail_tagline": "A custom popup introduction.",
                "detail_items": "First included item\nSecond included item",
                "detail_duration": "45 minutes",
                "detail_audience": "Adults",
                "detail_care_note": "Gentle approach",
                "_website": "",
            }
            status, created = request(
                opener, base_url, "/api/services", "POST", service_payload, csrf
            )
            expect(status, 201, "service creation")
            service_id = created["service"]["id"]

            update_payload = {
                **service_payload,
                "id": service_id,
                "detail_tagline": "Updated popup introduction.",
                "detail_items": "Updated first item\nUpdated second item\nNew third item",
            }
            status, updated = request(
                opener, base_url, "/api/services", "PATCH", update_payload, csrf
            )
            expect(status, 200, "service update")
            if updated["service"]["detail_tagline"] != "Updated popup introduction.":
                raise AssertionError("service popup introduction was not updated")
            if updated["service"]["detail_items"].count("\n") != 2:
                raise AssertionError("service popup items were not updated")

            status, _ = request(
                opener,
                base_url,
                "/api/services",
                "DELETE",
                {"id": "svc_oral_prophylaxis"},
                csrf,
            )
            expect(status, 200, "built-in service deletion")
            status, services = request(opener, base_url, "/api/services")
            expect(status, 200, "service listing after deletion")
            if any(item["id"] == "svc_oral_prophylaxis" for item in services["services"]):
                raise AssertionError("deleted built-in service was restored")

            status, updated_promo = request(
                opener,
                base_url,
                "/api/promos",
                "PATCH",
                {
                    "id": "promo_family_smile",
                    "title": "Updated Family Smile Day",
                    "description": "An updated temporary promo description for this test.",
                    "_website": "",
                },
                csrf,
            )
            expect(status, 200, "promo update")
            if updated_promo["promo"]["title"] != "Updated Family Smile Day":
                raise AssertionError("promo title was not updated")

            status, _ = request(
                opener,
                base_url,
                "/api/promos",
                "DELETE",
                {"id": "promo_family_smile"},
                csrf,
            )
            expect(status, 200, "built-in promo deletion")
            status, promos = request(opener, base_url, "/api/promos")
            expect(status, 200, "promo listing after deletion")
            if any(item["id"] == "promo_family_smile" for item in promos["promos"]):
                raise AssertionError("deleted built-in promo was restored")

            status, _ = request(
                opener, base_url, "/api/services", "DELETE", {"id": service_id}, csrf
            )
            expect(status, 200, "custom service deletion")
            print("Service and promo content smoke test passed.")
        finally:
            test_data_file.unlink(missing_ok=True)
            test_data_file.with_suffix(".tmp").unlink(missing_ok=True)
    finally:
        if server is not None:
            server.shutdown()
            server.server_close()
        if thread is not None:
            thread.join(timeout=2)
        core.DATA_STORE = original_store
        core.DATA_FILE = original_file


if __name__ == "__main__":
    main()
