import unittest
import json
from hello_world.flashcard_maker_api import flask_app

class FlaskAppTests(unittest.TestCase):

    def setUp(self):
        self.app = flask_app.test_client()
        self.app.testing = True

    def test_create_flashcards(self):
        response = self.app.post('/create_flashcards',
                                 data=json.dumps({"api_key": "put the key here!",
                                                  "text": "San Fransisco is a city in California. It is known for the Golden Gate Bridge. It is also known for its steep hills."}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        print(response.data)
        # Add more assertions here based on expected response

if __name__ == '__main__':
    unittest.main()
