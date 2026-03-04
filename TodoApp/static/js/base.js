    function showToast(message, type = 'info') {
        const container = document.getElementById('appToastContainer');
        if (!container) {
            return;
        }

        const toast = document.createElement('div');
        toast.className = `alert alert-${type} shadow-sm mb-2`;
        toast.role = 'alert';
        toast.textContent = message;
        container.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }


    function setButtonLoading(button, isLoading, loadingText) {
        if (!button) {
            return;
        }

        if (isLoading) {
            button.dataset.originalText = button.innerHTML;
            button.disabled = true;
            button.innerHTML = loadingText;
            return;
        }

        button.disabled = false;
        if (button.dataset.originalText) {
            button.innerHTML = button.dataset.originalText;
        }
    }


    async function parseErrorMessage(response) {
        try {
            const errorData = await response.json();
            if (Array.isArray(errorData.detail)) {
                return errorData.detail
                    .map(item => {
                        const field = item.loc && item.loc.length ? item.loc[item.loc.length - 1] : 'field';
                        return `${field}: ${item.msg}`;
                    })
                    .join(', ');
            }
            return errorData.detail || errorData.message || 'Request failed.';
        } catch {
            return 'Request failed.';
        }
    }


    // Add Todo JS
    const todoForm = document.getElementById('todoForm');
    if (todoForm) {
        todoForm.addEventListener('submit', async function (event) {
            event.preventDefault();

            const form = event.target;
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            const payload = {
                title: (data.title || '').trim(),
                description: (data.description || '').trim(),
                priority: parseInt(data.priority),
                complete: false
            };

            if (payload.title.length < 3 || payload.description.length < 3) {
                showToast('Title and description must be at least 3 characters.', 'danger');
                return;
            }

            if (data.owner_id) {
                payload.owner_id = parseInt(data.owner_id);
            }

            const submitButton = form.querySelector('button[type="submit"]');
            setButtonLoading(submitButton, true, 'Saving...');

            try {
                const response = await fetch('/todos/todo', {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    form.reset(); // Clear the form
                    showToast('Todo created successfully.', 'success');
                } else {
                    if (response.status === 401) {
                        window.location.href = '/auth/login-page';
                        return;
                    }
                    const errorMessage = await parseErrorMessage(response);
                    showToast(`Error: ${errorMessage}`, 'danger');
                }
            } catch (error) {
                console.error('Error:', error);
                showToast('An error occurred. Please try again.', 'danger');
            } finally {
                setButtonLoading(submitButton, false, 'Saving...');
            }
        });
    }

    // Edit Todo JS
    const editTodoForm = document.getElementById('editTodoForm');
    if (editTodoForm) {
        editTodoForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        const pathParts = window.location.pathname.split('/').filter(Boolean);
        const todoId = pathParts[pathParts.length - 1];

        const payload = {
            title: (data.title || '').trim(),
            description: (data.description || '').trim(),
            priority: parseInt(data.priority),
            complete: data.complete === "on"
        };

        if (payload.title.length < 3 || payload.description.length < 3) {
            showToast('Title and description must be at least 3 characters.', 'danger');
            return;
        }

        if (data.owner_id) {
            payload.owner_id = parseInt(data.owner_id);
        }

        const submitButton = form.querySelector('button[type="submit"]');
        setButtonLoading(submitButton, true, 'Updating...');

        try {
            const response = await fetch(`/todos/todo/${todoId}`, {
                method: 'PUT',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                showToast('Todo updated successfully.', 'success');
                window.location.href = '/todos/todo-page'; // Redirect to the todo page
            } else {
                // Handle error
                const errorData = await response.json();
                showToast(`Error: ${errorData.detail}`, 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            showToast('An error occurred. Please try again.', 'danger');
        } finally {
            setButtonLoading(submitButton, false, 'Updating...');
        }
    });

        document.getElementById('deleteButton').addEventListener('click', async function () {
            const pathParts = window.location.pathname.split('/').filter(Boolean);
            const todoId = pathParts[pathParts.length - 1];
            const deleteButton = document.getElementById('deleteButton');
            setButtonLoading(deleteButton, true, 'Deleting...');

            try {
                const response = await fetch(`/todos/todo/${todoId}`, {
                    method: 'DELETE',
                    credentials: 'same-origin'
                });

                if (response.ok) {
                    // Handle success
                    showToast('Todo deleted successfully.', 'success');
                    window.location.href = '/todos/todo-page'; // Redirect to the todo page
                } else {
                    // Handle error
                    const errorData = await response.json();
                    showToast(`Error: ${errorData.detail}`, 'danger');
                }
            } catch (error) {
                console.error('Error:', error);
                showToast('An error occurred. Please try again.', 'danger');
            } finally {
                setButtonLoading(deleteButton, false, 'Deleting...');
            }
        });

        
    }

    // Login JS
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function (event) {
            event.preventDefault();

            const form = event.target;
            const formData = new FormData(form);

            const payload = new URLSearchParams();
            for (const [key, value] of formData.entries()) {
                payload.append(key, value);
            }

            const submitButton = form.querySelector('button[type="submit"]');
            setButtonLoading(submitButton, true, 'Signing in...');

            try {
                const response = await fetch('/auth/token', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: payload.toString()
                });

                if (response.ok) {
                    // Handle success (e.g., redirect to dashboard)
                    await response.json();
                    showToast('Login successful.', 'success');
                    window.location.href = '/todos/todo-page'; // Change this to your desired redirect page
                } else {
                    // Handle error
                    const errorData = await response.json();
                    showToast(`Error: ${errorData.detail}`, 'danger');
                }
            } catch (error) {
                console.error('Error:', error);
                showToast('An error occurred. Please try again.', 'danger');
            } finally {
                setButtonLoading(submitButton, false, 'Signing in...');
            }
        });
    }

    // Register JS
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async function (event) {
            event.preventDefault();

            const form = event.target;
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            if (data.password !== data.password2) {
                showToast('Passwords do not match.', 'danger');
                return;
            }

            const payload = {
                email: data.email,
                username: data.username,
                first_name: data.firstname,
                last_name: data.lastname,
                role: data.role,
                phone_number: data.phone_number,
                password: data.password
            };

            const submitButton = form.querySelector('button[type="submit"]');
            setButtonLoading(submitButton, true, 'Registering...');

            try {
                const response = await fetch('/auth/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    showToast('Registration successful. Please login.', 'success');
                    window.location.href = '/auth/login-page';
                } else {
                    // Handle error
                    const errorData = await response.json();
                    showToast(`Error: ${errorData.message || errorData.detail}`, 'danger');
                }
            } catch (error) {
                console.error('Error:', error);
                showToast('An error occurred. Please try again.', 'danger');
            } finally {
                setButtonLoading(submitButton, false, 'Registering...');
            }
        });
    }




    async function logout() {
        await fetch('/auth/logout', { method: 'POST' });
        window.location.href = '/auth/login-page';
    };