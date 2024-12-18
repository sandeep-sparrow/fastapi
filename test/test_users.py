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