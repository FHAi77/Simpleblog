import os
import unittest
from app import app, db, BlogPost, OPERATION_PASSWORD # OPERATION_PASSWORD is a global in app.py
from io import BytesIO

class AppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SECRET_KEY'] = 'test_secret_key' # Added secret key
        app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for testing forms
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_upload_valid_md_file(self):
        # Simulate a POST request with a valid .md file
        # Check for success flash message and redirection
        data = {
            'markdown_file': (BytesIO(b'---\ntitle: Test MD\ntags: test\n---\n# Hello MD'), 'test.md'),
            'upload_password': OPERATION_PASSWORD
        }
        response = self.app.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 302) # Should redirect
        # Check for flash message indicating success
        with self.app.session_transaction() as session:
            flashes = session.get('_flashes', [])
            self.assertIn(('success', '文章上传成功！'), flashes)

    def test_upload_valid_markdown_file(self):
        # Simulate a POST request with a valid .markdown file
        # Check for success flash message and redirection
        data = {
            'markdown_file': (BytesIO(b'---\ntitle: Test Markdown\ntags: test\n---\n# Hello Markdown'), 'test.markdown'),
            'upload_password': OPERATION_PASSWORD
        }
        response = self.app.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 302) # Should redirect
        # Check for flash message indicating success
        with self.app.session_transaction() as session:
            flashes = session.get('_flashes', [])
            self.assertIn(('success', '文章上传成功！'), flashes)

    def test_upload_invalid_txt_file(self):
        # Simulate a POST request with an invalid .txt file
        # Check for error flash message and redirection back to upload page
        data = {
            'markdown_file': (BytesIO(b'This is a text file.'), 'test.txt'),
            'upload_password': OPERATION_PASSWORD
        }
        # For this test, we want to inspect the session for flashes *before* follow_redirects might clear them or change context
        # So, we don't use follow_redirects=True here initially for the flash check.
        response = self.app.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 302) # Should redirect back to upload_markdown

        # Check for flash message indicating invalid file type in the session
        with self.app.session_transaction() as session:
            flashes = session.get('_flashes', [])
            self.assertIn(('danger', 'Invalid file type. Only Markdown files (.md, .markdown) are allowed.'), flashes)

        # Optionally, you can then check the response after following the redirect
        response_followed = self.app.get(response.location)
        self.assertEqual(response_followed.status_code, 200) # Should be on upload page
        # And verify the message is displayed on the page (more complex, requires parsing HTML)
        # For now, checking the flash message in session is sufficient for this unit test.

    def test_upload_no_file(self):
        # Simulate a POST request with no file
        data = {
            'upload_password': OPERATION_PASSWORD
            # 'markdown_file': No file here
        }
        response = self.app.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(response.status_code, 200) 
        # Expecting to stay on the upload page.
        # The original code has `if file:`, so if no file is sent, it just re-renders the template.
        # We can check that no "success" or "invalid file type" flash message appeared.
        with self.app.session_transaction() as session:
            flashes = session.get('_flashes', [])
            self.assertFalse(any('文章上传成功！' in message for category, message in flashes))
            self.assertFalse(any('Invalid file type' in message for category, message in flashes))

    def test_upload_wrong_password(self):
        # Simulate a POST request with a valid .md file but wrong password
        data = {
            'markdown_file': (BytesIO(b'---\ntitle: Test MD\ntags: test\n---\n# Hello MD'), 'test.md'),
            'upload_password': 'WRONG_PASSWORD'
        }
        response = self.app.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 302) # Should redirect
        with self.app.session_transaction() as session:
            flashes = session.get('_flashes', [])
            self.assertIn(('danger', '操作密码错误，请重试'), flashes)
        
        response_followed = self.app.get(response.location)
        self.assertEqual(response_followed.status_code, 200) # Should be on upload page

if __name__ == "__main__":
    unittest.main()
