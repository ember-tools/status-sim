import unittest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from main import app


class TestStaffelfuehrer(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def _create(self):
        resp = self.client.post("/api/leitstelle", json={"name": "Test Leitstelle"})
        d = resp.json()
        return d["admin_code"], d["vehicle_code"], d["staffelfuehrer_code"]

    def _poll(self, code, name=None):
        params = {"name": name} if name else {}
        return self.client.get(f"/api/poll/{code}", params=params).json()

    def test_staffelfuehrer_flow(self):
        admin_code, vehicle_code, sf_code = self._create()

        self._poll(vehicle_code, "Car1")
        self._poll(sf_code, "SF1")

        self.client.post(f"/api/staffelfuehrer/{sf_code}/claim", json={
            "target_name": "Car1", "sf_name": "SF1",
        })

        resp = self.client.post(f"/api/staffelfuehrer/{sf_code}/notice", json={
            "target_name": "Car1", "text": "Anfordern", "sf_name": "SF1",
        })
        self.assertEqual(resp.status_code, 200)

        data = self._poll(vehicle_code, "Car1")
        self.assertIn("Car1", data["notices"])
        self.assertEqual(data["notices"]["Car1"]["status"], "pending")

        data = self._poll(sf_code, "SF1")
        self.assertEqual(data["notices"]["Car1"]["status"], "pending")

        self.client.post(f"/api/vehicle/{vehicle_code}/action", json={
            "name": "Car1", "action": "confirm_notice",
        })

        data = self._poll(sf_code, "SF1")
        self.assertEqual(data["notices"]["Car1"]["status"], "confirmed")

        resp = self.client.post(f"/api/staffelfuehrer/{sf_code}/acknowledge", json={"target_name": "Car1"})
        self.assertEqual(resp.status_code, 200)

        data = self._poll(sf_code, "SF1")
        self.assertNotIn("Car1", data["notices"])

    def test_notes_sync(self):
        admin_code, vehicle_code, sf_code = self._create()

        self._poll(vehicle_code, "CarNote")

        resp = self.client.post(f"/api/leitstelle/{admin_code}/update_note", json={
            "target_name": "CarNote", "note": "LS Note",
        })
        self.assertEqual(resp.status_code, 200)

        data = self._poll(admin_code)
        car = next(c for c in data["connections"] if c["name"] == "CarNote")
        self.assertEqual(car["note"], "LS Note")
        self.assertEqual(car["sf_note"], "")

        resp = self.client.post(f"/api/leitstelle/{sf_code}/update_note", json={
            "target_name": "CarNote", "note": "SF Overwrite",
        })
        self.assertEqual(resp.status_code, 200)

        data = self._poll(admin_code)
        car = next(c for c in data["connections"] if c["name"] == "CarNote")
        self.assertEqual(car["note"], "LS Note")
        self.assertEqual(car["sf_note"], "SF Overwrite")


if __name__ == "__main__":
    unittest.main()
