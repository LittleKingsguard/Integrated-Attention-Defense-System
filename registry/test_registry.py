import httpx
import time
import subprocess
import os
import signal

BASE_URL = "http://127.0.0.1:8000/api/v1/registry"

def test_registry():
    with httpx.Client() as client:
        # 1. Register a new user
        user_data = {
            "user_id": "alice@example.com",
            "address": "http://alice-node:5000",
            "public_key": "rsa-pub-alice-key",
            "protocols": ["ads-v1"],
            "interaction_skills": {
                "relationship_type": "friend",
                "tone_preference": "casual",
                "rules": ["Don't interrupt during lunch"],
                "permissions": {}
            }
        }
        print("Registering Alice...")
        response = client.post(f"{BASE_URL}/", json=user_data)
        print(f"Status: {response.status_code}")
        assert response.status_code == 201
        
        # 2. Lookup Alice
        print("Looking up Alice...")
        response = client.get(f"{BASE_URL}/alice@example.com")
        print(f"Status: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "alice@example.com"
        assert data["interaction_skills"]["tone_preference"] == "casual"
        
        # 3. Update Alice
        print("Updating Alice's tone...")
        user_data["interaction_skills"]["tone_preference"] = "formal"
        response = client.post(f"{BASE_URL}/", json=user_data)
        print(f"Status: {response.status_code}")
        assert response.status_code == 200
        
        # 4. Verify Update
        print("Verifying Alice's update...")
        response = client.get(f"{BASE_URL}/alice@example.com")
        data = response.json()
        assert data["interaction_skills"]["tone_preference"] == "formal"
        
        # 5. Lookup non-existent user
        print("Looking up Bob (doesn't exist)...")
        response = client.get(f"{BASE_URL}/bob@example.com")
        print(f"Status: {response.status_code}")
        assert response.status_code == 404

        print("\nAll tests passed!")

if __name__ == "__main__":
    test_registry()
