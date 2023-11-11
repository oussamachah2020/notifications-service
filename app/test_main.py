import os
import pytest
from fastapi.testclient import TestClient
from pydantic import model_rebuild  # Import model_rebuild

# Import the FastAPI app from your main module (update the import path accordingly)
from main import app

client = TestClient(app)

@pytest.fixture
def test_notification_body():
    return {
        "userId": "aadfd0d2-b113-48b1-8e40-bf86686b6031",
        "title": "Test Title",
        "content": "Test Content"
    }

# Apply model_rebuild to Pydantic models to suppress the warnings
test_notification_body = model_rebuild(test_notification_body)

def test_send_notification(test_notification_body):
    response = client.post("/send-notification", json=test_notification_body)
    assert response.status_code == 200
    assert response.json() == {"message": "Notifications sent successfully"}

if __name__ == "__main__":
    pytest.main()
