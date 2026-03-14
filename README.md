
# TodoApp – FastAPI Task Management API

A simple task management API built with **FastAPI**.

The application allows users to create and manage tasks while administrators can assign tasks to other users, set priorities, and add descriptions.

The API uses **JWT authentication and OAuth2 security** to protect endpoints.

---

## Features

- User authentication with **JWT**
- Secure login using **OAuth2**
- Admin users can assign tasks to regular users
- Create, update, delete, and view tasks
- Set **task priority**
- Add **task descriptions**
- RESTful API design
- Automatic API documentation with Swagger

---

## Tech Stack

- Python
- FastAPI
- JWT Authentication
- OAuth2
- Pydantic
- Uvicorn

---

## Installation

Clone the repository

```bash
git clone https://github.com/NeofytosIoannou/TodoApp.git
cd TodoApp
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Run the Application

Start the FastAPI server

```bash
uvicorn main:app --reload
```

The API will run at:

http://127.0.0.1:8000

---

## API Documentation

Swagger UI:
http://127.0.0.1:8000/docs

ReDoc:
http://127.0.0.1:8000/redoc

---

## Authentication

The API uses **JWT tokens with OAuth2**.

### Admin Login
username: neo  
password: 1234

## Regular User Login
username: user1  
password: 1234

After logging in you will receive a **JWT token** which must be used to access protected endpoints.

---

## Author

Neofytos Ioannou  
Computer Science Student – University of Cyprus
