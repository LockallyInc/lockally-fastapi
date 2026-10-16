import unittest

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from lockally_fastapi import Lockally, LockallyClient


class FakeSendApi:
    def __init__(self):
        self.calls = []

    def v1_send_post(self, idempotency_key, request):
        self.calls.append((idempotency_key, request))
        return {"id": "m_1", "status": "queued"}


class LockallyProviderTest(unittest.TestCase):
    def test_provider_call_returns_client(self):
        lockally = Lockally(api_key="lk_test_abc")
        client = lockally()
        self.assertIsInstance(client, LockallyClient)
        self.assertIs(lockally(), client)  # same shared instance

    def test_depends_injects_client_and_sends(self):
        fake = FakeSendApi()
        lockally = Lockally(client=LockallyClient(send_api=fake))

        app = FastAPI()

        @app.post("/signup", status_code=202)
        def signup(client: LockallyClient = Depends(lockally)):
            client.send_email(
                from_="alerts@acme.com",
                to="user@example.com",
                subject="Welcome",
                html="<b>hi</b>",
            )
            return {"ok": True}

        resp = TestClient(app).post("/signup")
        self.assertEqual(resp.status_code, 202)
        self.assertEqual(len(fake.calls), 1)
        key, request = fake.calls[0]
        self.assertTrue(key.startswith("lk-"))
        self.assertEqual(request.to_dict()["from"], "alerts@acme.com")
        self.assertEqual(request.to_dict()["html"], "<b>hi</b>")


if __name__ == "__main__":
    unittest.main()
