import pandas as pd
from deepface import DeepFace

playlist_df = pd.read_csv('data/final_mood.csv')


def predict_mood(photo_path) -> str:
    predefined_moods = ['energetic', 'sad', 'angry', 'calm']
    try:
        analysis = DeepFace.analyze(photo_path, actions=['emotion'])
        analysis_dict = analysis[0]
        dominant_emotion = analysis_dict['dominant_emotion']

        if dominant_emotion == 'neutral':
            dominant_emotion = 'calm'

        if dominant_emotion == 'happy':
            dominant_emotion = 'energetic'

        if dominant_emotion in predefined_moods:
            return dominant_emotion
        else:
            return "emotion_not_in_list"
    except Exception as e:
        print(f"Error in emotion prediction: {e}")
        return None


def get_playlist(mood, year_interval):
    start_year, end_year = map(int, year_interval.split('-'))
    filtered_songs = playlist_df[
        (playlist_df['mood'] == mood) & (playlist_df['Year'] >= start_year) & (playlist_df['Year'] <= end_year)]
    sorted_songs = filtered_songs.sort_values(by='popularity', ascending=False)
    selected_songs = sorted_songs.sample(n=5) if len(sorted_songs) >= 5 else sorted_songs
    return selected_songs.to_dict(orient='records')
