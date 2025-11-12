from fastapi.testclient import TestClient
import urllib.parse

import src.app as app_module


client = TestClient(app_module.app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # basic smoke check
    assert "Chess Club" in data


def test_signup_and_unregister():
    activity = "Chess Club"
    email = "test.user+pytest@example.com"
    activities = app_module.activities

    # snapshot and ensure cleanup
    original = activities[activity]["participants"].copy()
    try:
        # remove if already present to ensure a clean start
        if email in activities[activity]["participants"]:
            activities[activity]["participants"].remove(email)

        # signup
        signup_url = f"/activities/{urllib.parse.quote(activity)}/signup?email={urllib.parse.quote(email)}"
        resp = client.post(signup_url)
        assert resp.status_code == 200
        j = resp.json()
        assert "Signed up" in j.get("message", "")

        # verify present
        resp2 = client.get("/activities")
        assert resp2.status_code == 200
        data = resp2.json()
        assert email in data[activity]["participants"]

        # unregister
        del_url = f"/activities/{urllib.parse.quote(activity)}/participants?email={urllib.parse.quote(email)}"
        resp3 = client.delete(del_url)
        assert resp3.status_code == 200
        j3 = resp3.json()
        assert "Unregistered" in j3.get("message", "")

        # verify removed
        resp4 = client.get("/activities")
        data2 = resp4.json()
        assert email not in data2[activity]["participants"]
    finally:
        # restore original participants to avoid side effects
        activities[activity]["participants"] = original
