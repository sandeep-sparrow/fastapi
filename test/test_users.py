from .utils import *
from ..routers.users import get_db, get_current_user
from fastapi import status

# Apply dependency overrides
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(test_user):
    response = client.get('/user')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'sandy1311'
    assert response.json()['email'] == 'sandeep.p@gmail.com'
    assert response.json()['first_name'] == 'Sandeep'
    assert response.json()['last_name'] == 'Prajapati'
    assert response.json()['role'] == 'user'

def test_change_password_success(test_user):
    response = client.put('/user/password', json={'password': "user123",
                                                  "new_password": "user12345"})
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_change_password_invalid(test_user):
    response = client.put('/user/password', json={'password': "admin",
                                                  "new_password": "user12345"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Error on password change'}