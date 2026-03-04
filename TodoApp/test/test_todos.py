from ..routers.todos import get_db, get_current_user
from fastapi import status
from ..models import Todos
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_todo):
    response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'complete': False, 'title': 'Learn to code!',
                                'description': 'Need to learn everyday!', 'id': 1,
                                'priority': 5, 'owner_id': 1}]


def test_read_one_authenticated(test_todo):
    response = client.get("/todos/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'complete': False, 'title': 'Learn to code!',
                                'description': 'Need to learn everyday!', 'id': 1,
                                'priority': 5, 'owner_id': 1}


def test_read_one_authenticated_not_found():
    response = client.get("/todos/todo/999")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}


def test_create_todo(test_todo):
    request_data={
        'title': 'New Todo!',
        'description':'New todo description',
        'priority': 5,
        'complete': False,
    }

    response = client.post('/todos/todo/', json=request_data)
    assert response.status_code == 201

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')


def test_create_todo_admin_assign_owner(test_todo, test_user):
    request_data={
        'title': 'Admin assigned todo',
        'description':'Assigned by admin',
        'priority': 4,
        'complete': False,
        'owner_id': 1,
    }

    response = client.post('/todos/todo/', json=request_data)
    assert response.status_code == 201

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model is not None
    assert model.owner_id == 1


def test_create_todo_non_admin_cannot_assign_owner(test_todo):
    def override_get_current_user_non_admin():
        return {'username': 'normaluser', 'id': 1, 'user_role': 'user'}

    app.dependency_overrides[get_current_user] = override_get_current_user_non_admin

    request_data={
        'title': 'Should fail',
        'description':'Non-admin assignment attempt',
        'priority': 3,
        'complete': False,
        'owner_id': 2,
    }

    response = client.post('/todos/todo/', json=request_data)
    assert response.status_code == 403
    assert response.json() == {'detail': 'Only admins can assign todos to other users.'}

    app.dependency_overrides[get_current_user] = override_get_current_user


def test_update_todo(test_todo):
    request_data={
        'title':'Change the title of the todo already saved!',
        'description': 'Need to learn everyday!',
        'priority': 5,
        'complete': False,
    }

    response = client.put('/todos/todo/1', json=request_data)
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == 'Change the title of the todo already saved!'


def test_admin_update_other_users_todo(test_todo):
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    model.owner_id = 2
    db.add(model)
    db.commit()

    request_data={
        'title':'Admin can update this todo',
        'description': 'Updated by admin',
        'priority': 4,
        'complete': True,
    }

    response = client.put('/todos/todo/1', json=request_data)
    assert response.status_code == 204

    updated_model = db.query(Todos).filter(Todos.id == 1).first()
    assert updated_model.title == 'Admin can update this todo'
    assert updated_model.complete is True


def test_admin_reassign_existing_todo(test_todo, test_user):
    db = TestingSessionLocal()
    second_user = db.query(Users).filter(Users.username == "assignee2").first()
    if second_user is None:
        second_user = Users(
            username="assignee2",
            email="assignee2@email.com",
            first_name="Assign",
            last_name="Target",
            hashed_password=bcrypt_context.hash("testpassword"),
            role="user",
            phone_number="(222)-222-2222"
        )
        db.add(second_user)
        db.commit()
        db.refresh(second_user)

    request_data={
        'title':'Reassigned todo',
        'description': 'Reassigned by admin',
        'priority': 4,
        'complete': False,
        'owner_id': second_user.id,
    }

    response = client.put('/todos/todo/1', json=request_data)
    assert response.status_code == 204

    updated_model = db.query(Todos).filter(Todos.id == 1).first()
    assert updated_model.owner_id == second_user.id


def test_update_todo_not_found(test_todo):
    request_data={
        'title':'Change the title of the todo already saved!',
        'description': 'Need to learn everyday!',
        'priority': 5,
        'complete': False,
    }

    response = client.put('/todos/todo/999', json=request_data)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}


def test_delete_todo(test_todo):
    response = client.delete('/todos/todo/1')
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_delete_todo_not_found():
    response = client.delete('/todos/todo/999')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}













