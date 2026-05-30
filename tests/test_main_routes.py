# tests/test_main_routes.py
import pytest


def test_index(client):
    assert client.get('/').status_code == 200


def test_about(client):
    assert client.get('/about').status_code == 200


def test_faq(client):
    assert client.get('/faq').status_code == 200


def test_contact(client):
    assert client.get('/contact').status_code == 200


def test_privacy_policy(client):
    assert client.get('/privacy-policy').status_code == 200


def test_ping(client):
    resp = client.get('/ping')
    assert resp.status_code == 200
    assert b'pong' in resp.data


def test_health_check_ok(client):
    resp = client.get('/health')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'healthy'


def test_sdg_information_hub(client):
    resp = client.get('/sdg-information-hub')
    assert resp.status_code == 200
    assert b'SDG' in resp.data


def test_debug_endpoints_removed(client):
    # These unauthenticated schema-disclosure endpoints were removed for security.
    assert client.get('/debug/database').status_code == 404
    assert client.get('/debug/db').status_code == 404


def test_sdg_hub_contains_all_17_goals(client):
    resp = client.get('/sdg-information-hub')
    assert resp.status_code == 200
    # Each SDG number 1-17 should appear in the rendered HTML
    for i in range(1, 18):
        assert str(i).encode() in resp.data
