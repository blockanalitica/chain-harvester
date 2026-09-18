import pytest

from chain_harvester.utils.url import REDACTED, redact_credentials

API_KEY = "K72AKUBWUYX8RCRXD17S4EC9NXQBF4HZVS"


def test_redacts_etherscan_api_key():
    url = (
        "https://api.etherscan.io/v2/api?chainid=1&module=block"
        f"&action=getblocknobytime&timestamp=1789656076&closest=before&apikey={API_KEY}"
    )
    result = redact_credentials(url)
    assert API_KEY not in result
    assert f"apikey={REDACTED}" in result


def test_keeps_non_sensitive_params_for_debugging():
    url = "https://api.etherscan.io/v2/api?chainid=1&action=getabi&apikey=hunter2"
    result = redact_credentials(url)
    assert "chainid=1" in result
    assert "action=getabi" in result
    assert "hunter2" not in result


@pytest.mark.parametrize(
    "param",
    [
        "apikey",
        "api_key",
        "API-KEY",
        "key",
        "token",
        "access_token",
        "auth",
        "authorization",
        "secret",
        "client_secret",
        "password",
        "passwd",
        "pwd",
        "signature",
        "sig",
        "bearer",
        "sessionid",
        "nonce",
        "hmac",
        "credential",
        "Ok-Access-Key",
    ],
)
def test_redacts_every_credential_param_name(param):
    result = redact_credentials(f"https://example.com/api?{param}=hunter2")
    assert "hunter2" not in result
    assert REDACTED in result


def test_leaves_urls_without_a_query_string_untouched():
    url = "https://api.etherscan.io/v2/api"
    assert redact_credentials(url) == url


def test_redacts_repeated_occurrences_of_the_same_param():
    result = redact_credentials("https://example.com/?apikey=one&apikey=two")
    assert "one" not in result
    assert "two" not in result
    assert result.count(REDACTED) == 2


def test_redacts_a_param_embedded_in_surrounding_prose():
    """The caller passes log messages, not bare URLs."""
    result = redact_credentials("GET https://e.com/?apikey=hunter2 failed after 3 tries")
    assert "hunter2" not in result
    assert result.endswith("failed after 3 tries")


def test_redacts_a_url_quoted_inside_an_exception_repr():
    text = "429, message='Too Many Requests', url='https://e.com/api?apikey=hunter2'"
    result = redact_credentials(text)
    assert "hunter2" not in result
    assert result.endswith("'")


def test_keeps_a_url_fragment():
    result = redact_credentials("https://e.com/?apikey=hunter2#trace-1")
    assert "hunter2" not in result
    assert result.endswith("#trace-1")


def test_redacts_basic_auth_userinfo():
    result = redact_credentials("https://user:hunter2@rpc.example.com/v1?chainid=1")
    assert "hunter2" not in result
    assert "@rpc.example.com/v1" in result


def test_redacts_legacy_semicolon_separated_params():
    result = redact_credentials("https://example.com/?a=1;apikey=hunter2")
    assert "hunter2" not in result
    assert "a=1" in result


def test_does_not_mangle_the_params_it_keeps():
    """A logged URL should stay copy-pasteable."""
    result = redact_credentials("https://e.com/api?filter=a,b:c/d&apikey=hunter2")
    assert "filter=a,b:c/d" in result
    assert "hunter2" not in result


def test_fails_closed_on_a_malformed_url():
    """urlsplit raises on this; the redactor must not hand the secret back."""
    result = redact_credentials("https://[::1/?apikey=hunter2")
    assert "hunter2" not in result


def test_fails_closed_when_the_value_cannot_be_stringified():
    class Exploding:
        def __str__(self):
            raise RuntimeError("boom")

    assert redact_credentials(Exploding()) == REDACTED
