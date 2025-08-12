import json
from .conftest import extract_csrf_token


def test_e2e_signup_create_edit_delete(client):
    # Load signup page and extract CSRF token
    resp = client.get('/signup')
    assert resp.status_code == 200
    token = extract_csrf_token(resp.get_data(as_text=True))

    # Submit signup form
    data = {
        'csrf_token': token,
        'username': 'e2e_user',
        'email': 'e2e@example.com',
        'password': 'MyStrongPassw0rd!'
    }
    resp = client.post('/signup', data=data, follow_redirects=False)
    assert resp.status_code in (302, 303)

    # Create note
    resp = client.post('/api/notes',
                       data=json.dumps({'title': 'E2E', 'content': '<p>Start</p>'}),
                       content_type='application/json')
    assert resp.status_code == 201
    note = resp.get_json()['note']

    # Edit note (PUT -> new version)
    resp = client.put(f"/api/notes/{note['id']}",
                      data=json.dumps({'title': 'E2E updated', 'content': '<p>Updated</p>'}),
                      content_type='application/json')
    assert resp.status_code == 200
    updated = resp.get_json()['note']
    assert updated['version'] == 2

    # Delete
    resp = client.delete(f"/api/notes/{updated['id']}")
    assert resp.status_code == 200
