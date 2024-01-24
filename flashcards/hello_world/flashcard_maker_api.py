from flask import Flask, request, jsonify
from flask_cors import CORS
from .flashcard_maker import FlashCardMaker

flask_app = Flask(__name__)
CORS(flask_app)


@flask_app.route('/create_flashcards', methods=['POST'])
def create_flashcards():
    # Check for API key in the request
    if not request.json or 'api_key' not in request.json:
        return jsonify({'error': 'Invalid or missing API key'}), 400

    # Check for text in the request
    if 'text' not in request.json:
        return jsonify({'error': 'No text provided'}), 400


    text = request.json['text']
    flashcard_maker = FlashCardMaker(request.json['api_key'])
    flashcards = flashcard_maker.create_flashcards(text)

    return jsonify(flashcards)

if __name__ == '__main__':
    flask_app.run(debug=True)


# usage:
# {
#     "api_key": "your_api_key",
#     "text": "Your long string of text goes here..."
# }
