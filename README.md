# Lockally for FastAPI

Official [Lockally](https://lockally.com) integration for FastAPI. Inject a Lockally
client into any route with FastAPI's dependency system.

## Install

```bash
pip install lockally-fastapi
```

## Configure

Construct a provider and use it directly as a dependency:

```python
from fastapi import Depends, FastAPI
from lockally_fastapi import Lockally, LockallyClient

app = FastAPI()
lockally = Lockally(api_key="lk_live_xxx")      # lk_test_xxx runs in sandbox
# lockally = Lockally(api_key="lk_live_xxx", base_url="https://api.lockally.com")

@app.post("/signup", status_code=202)
def signup(client: LockallyClient = Depends(lockally)):
    client.send_email(
        from_="alerts@yourdomain.com",
        to="user@example.com",
        subject="Welcome",
        html="<b>Thanks for signing up.</b>",
        reply_to="support@yourdomain.com",
    )
```

Prefer configuration from the environment? Set `LOCKALLY_API_KEY` (and optionally
`LOCKALLY_BASE_URL`) and use the ready-made annotated dependency:

```python
from lockally_fastapi import LockallyDep

@app.post("/signup", status_code=202)
def signup(client: LockallyDep):
    client.send_email(from_="alerts@yourdomain.com", to="user@example.com", subject="Hi")
```

`to`/`cc`/`bcc`/`reply_to` accept a single address or a list; `attachments` is a list
of `(filename, content, content_type)` (content is bytes or str).

### Mapping notes

- **Reply-To** is sent as a header (Lockally has no `reply_to` field).
- **Attachments** are base64-encoded as `{filename, content_type, content_base64}`.
- One `Idempotency-Key` is generated per send (24 h dedupe window).

## License

MIT © Lockally
