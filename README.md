# Movie Recommender System

## Overview
This project is a content-based movie recommendation system built using Python, Streamlit, Natural Language Processing (NLP), and Machine Learning techniques. The system suggests similar movies based on the user's selection, utilizing movie metadata and similarity scores to provide personalized recommendations.

## Features
- Interactive web interface built with Streamlit
- Movie selection from a dropdown menu containing thousands of titles
- Display of top 5 movie recommendations based on content similarity
- Movie posters fetched from The Movie Database (TMDB) API
- Responsive layout showing movie titles and corresponding posters

## Technologies Used
- **Natural Language Processing (NLP)**: Used for processing and analyzing textual movie features like plot summaries, keywords, and descriptions to create meaningful feature vectors.
- **Machine Learning**: Applied to calculate similarity between movies and generate recommendations based on content features.
- **Cosine Similarity**: A machine learning technique used to measure the similarity between movies based on their feature vectors.
- **Python**: Core programming language for the implementation.
- **Streamlit**: Framework for building the interactive web application.
- **TMDB API**: External API for fetching movie posters and metadata.

## How It Works
1. **Content-Based Filtering**: The system uses content-based filtering to recommend movies similar to the one selected by the user. This approach analyzes movie features such as genre, cast, crew, and plot keywords to calculate similarity between movies.

2. **NLP Processing**: Movie textual features are processed using NLP techniques such as:
   - Text tokenization
   - Stop word removal
   - Stemming/lemmatization
   - TF-IDF vectorization to convert text into numerical features

3. **Similarity Calculation**: Machine learning algorithms are used to compute similarity scores between movies based on their feature vectors. These similarity scores are stored in the `similarity.pkl` file.

4. **Recommendation Process**: When a user selects a movie, the system:
   - Finds the index of the selected movie in the dataset
   - Retrieves the top 5 most similar movies based on pre-calculated similarity scores
   - Fetches movie posters from TMDB API
   - Displays the recommendations with titles and posters

## Installation

### Prerequisites
- Python 3.7+
- pip package manager

### Setup
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/movie-recommender-system.git
   cd movie-recommender-system
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Download the required dataset files:
   - `movie_list.pkl`: Contains movie metadata
   - `similarity.pkl`: Contains pre-computed similarity scores

   Place these files in the project directory.

### Running the Application
Execute the following command in the terminal:
```
streamlit run app.py
```

The application will launch in your default web browser.

## Dataset
The recommendation system uses a preprocessed dataset of movies. The dataset includes:
- Movie titles
- Movie IDs (for TMDB API)
- Feature vectors representing movie characteristics derived from NLP processing

## API Integration
The system integrates with The Movie Database (TMDB) API to fetch movie posters. You'll need to:
1. Register for a TMDB API key at https://www.themoviedb.org/settings/api
2. Replace the API key in the code if necessary

## Project Structure
```
movie-recommender-system/
│
├── app.py                  # Main Streamlit application file
├── movie_list.pkl          # Preprocessed movie metadata
├── similarity.pkl          # Pre-computed similarity matrix
├── requirements.txt        # Required Python packages
└── README.md               # Project documentation
```

## Requirements
- streamlit
- pickle
- requests
- pandas
- numpy
- scikit-learn (for ML algorithms)
- nltk (for NLP processing)

## Future Improvements
- User authentication and profile management
- Saving user ratings and previously watched movies
- Hybrid recommendation system combining content-based and collaborative filtering
- Advanced filtering options (by genre, year, etc.)
- Detailed movie information display
- Implementing more advanced NLP techniques like word embeddings or BERT
- Incorporating deep learning models for improved similarity calculations

