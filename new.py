import string
from flask import Flask, render_template, request, redirect, url_for
from collections import Counter
import os
import matplotlib.pyplot as plt
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/bts_lyric_repeat"
# Initialize the app with the extension
db = SQLAlchemy(app)

@app.route('/')
def index():
    songs = lyrics_v6.query.all()
    return render_template('index.html', songs=songs)

# Define the BTS Lyrics model
class lyrics_v6(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_name = db.Column(db.String(100), unique=True, nullable=False)
    lyrics = db.Column(db.Text, nullable=False)

@app.route('/analyze', methods=['POST'])
def analyze():
    song_name = request.form.get('song_name')
    song = lyrics_v6.query.filter_by(song_name=song_name).first()

    if song:
        lyrics = song.lyrics
        lower_case = lyrics.lower()
        cleaned_text = lower_case.translate(str.maketrans('', '', string.punctuation))

        tokenized_words = cleaned_text.split()
        stop_words = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself",
              "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself",
              "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these",
              "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do",
              "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while",
              "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before",
              "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again",
              "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each",
              "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than",
              "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]
        final_words = []
        
        for word in tokenized_words:
            if word not in stop_words:
                final_words.append(word)



        emotion_list = []
        with open('emotion.txt', 'r') as file:
            for line in file:
                  # Remove leading/trailing whitespaces and newlines
                clear_line = line.replace("\n", '').replace(",", '').replace("'", '').strip()
                parts = clear_line.split(':')
                if len(parts) == 2:
                    word, emotion = parts
                    if word in final_words:
                        emotion_list.append(emotion)
                    else:
                        print(f"Skipping line: {clear_line} - It does not contain the expected format (word: emotion)")
       
        emotion_words = []  # To store emotion words found in the lyrics
          # Add HTML tags to emotion words
        for word in tokenized_words:
                if word in emotion_words:
                    word = f"<u>{word}</u>"  # Underline emotion words
                emotion_words.append(word)

                modified_lyrics = ' '.join(emotion_words)


        count_of_emo = Counter(emotion_list)
        
        fig, ax1 = plt.subplots()
        ax1.bar(count_of_emo.keys(), count_of_emo.values())
        fig.autofmt_xdate()
        plt.savefig('static/graph.png')  # Save the image in the 'static' directory
        plt.close()  # Close the matplotlib plot to prevent displaying it in the console

    songs = lyrics_v6.query.all()

    # Pass the image URL to the template
    image_url = url_for('static', filename='graph.png')
        
    songs = lyrics_v6.query.all()
    return render_template('result.html', songs=songs, song_name=song_name, emotion_list=emotion_list,modified_lyrics=modified_lyrics, emotion_counts=count_of_emo, image_url=image_url)

if __name__ == '__main__':
    app.run()
