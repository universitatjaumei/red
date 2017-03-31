import os
import json
import red
import unittest
import tempfile

class RedTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, red.app.config['DATABASE'] = tempfile.mkstemp()
        red.app.config['TESTING'] = True
        self.app = red.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(red.app.config['DATABASE'])

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_sqlite_ready(self):
        rv = self.app.get('/api/red')
        d = json.loads(rv.get_data())
        print d
        assert b'No entries here so far' in rv.data

if __name__ == '__main__':
    unittest.main()
