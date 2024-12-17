from fastapi.testclient import TestClient
from TodoApp import main
from starlette import status

client = TestClient(main.app)

# create a fake db - test db
# create testing dependencies
def test_return_health_check():
    print('test_return_health_check')
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == { 'status': "Up and Running!" }