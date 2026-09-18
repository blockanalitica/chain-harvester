import re

REDACTED = "[REDACTED]"

# Substrings, not exact names, so unseen spellings of the same secret
# (`apikey`, `api_key`, `Ok-Access-Key`, ...) are all covered. Over-redacting a
# harmless param costs nothing; under-redacting leaks a credential.
CREDENTIAL_MARKERS = (
    "key",
    "token",
    "secret",
    "password",
    "passwd",
    "pwd",
    "auth",
    "signature",
    "sig",
    "bearer",
    "session",
    "nonce",
    "hmac",
    "credential",
)
_MARKERS = "|".join(CREDENTIAL_MARKERS)

# Deliberately regex over free text rather than urlsplit: callers pass log
# messages and exception reprs, where a URL is embedded in prose and often
# malformed. `;` is a legacy param separator.
_NAME_CHAR = r"[^?&;=\s'\"<>]"
_QUERY_PARAM_RE = re.compile(
    rf"((?:^|[?&;]){_NAME_CHAR}*(?:{_MARKERS}){_NAME_CHAR}*=)[^&;#\s'\"<>]*",
    re.IGNORECASE,
)
_USERINFO_RE = re.compile(r"(://[^/@\s:'\"<>]+:)[^/@\s'\"<>]+(?=@)")


def redact_credentials(text):
    """Blank credential-shaped query params and basic-auth userinfo in `text`.

    Fails closed -- an unreadable value is dropped rather than passed through.
    Does not cover credentials in the URL *path* (Alchemy, Infura): those are
    only known to the caller, so redact them at the Sentry boundary instead.
    """
    try:
        text = str(text)
        text = _USERINFO_RE.sub(rf"\1{REDACTED}", text)
        return _QUERY_PARAM_RE.sub(rf"\1{REDACTED}", text)
    except Exception:
        return REDACTED
