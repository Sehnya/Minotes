import json

def login(client, username, password):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=False)


def test_api_crud(client, user_factory):
    # Create a user and login
    (u, pwd) = user_factory(username='carol', email='carol@example.com', password='S3cret!pass')
    resp = login(client, 'carol', pwd)
    assert resp.status_code in (302, 303)  # redirect to dashboard

    # Create note
    resp = client.post('/api/notes',
                       data=json.dumps({'title': 'New Note', 'content': '<p>Body</p>'}),
                       content_type='application/json')
    assert resp.status_code == 201
    note = resp.get_json()['note']

    # List notes
    resp = client.get('/api/notes')
    assert resp.status_code == 200
    notes = resp.get_json()['notes']
    assert any(n['id'] == note['id'] for n in notes)

    # Get single note
    resp = client.get(f"/api/notes/{note['id']}")
    assert resp.status_code == 200

    # Update note (versioning)
    resp = client.put(f"/api/notes/{note['id']}",
                      data=json.dumps({'title': 'Updated', 'content': '<p>New</p>'}),
                      content_type='application/json')
    assert resp.status_code == 200
    updated = resp.get_json()['note']
    assert updated['version'] == 2

    # Delete note
    resp = client.delete(f"/api/notes/{updated['id']}")
    assert resp.status_code == 200
