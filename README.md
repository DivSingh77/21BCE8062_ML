# Document Retrieval System for Chat Applications

This repository contains a Flask-based document retrieval system for chat applications, designed to efficiently provide context-sensitive results from news articles. The system integrates caching, background scraping, rate limiting, and logging for robust API performance. 

## Features

- **News Article Scraping**: Automatically scrapes the top articles from sources like Hacker News every hour and indexes them for search.
- **Document Search**: Provides a `/search` endpoint that performs similarity searches on indexed documents.
- **Rate Limiting**: Limits the number of API requests a user can make to prevent abuse.
- **Caching**: Stores search results temporarily to speed up repeated queries.
- **Background Processing**: Runs web scraping in the background to keep the document store updated.
- **Dockerization**: Supports containerized deployment with Docker.
- **API Logging**: Logs user search queries and response times.

## Getting Started

### Prerequisites

Before running this application, ensure you have the following installed:

- Python 3.8+
- Docker (optional for containerized deployment)
- An OpenAI API key

### Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/your-username/document-retrieval-system.git
   cd document-retrieval-system
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:

   Create a `.env` file in the root directory and add the following:

   ```bash
   OPENAI_API_KEY=your_openai_api_key
   CHROMA_PERSIST_DIRECTORY=path_to_persistence_directory
   RATE_LIMIT=5  # Set the rate limit for users
   CACHE_EXPIRATION=3600  # Cache expiration time in seconds
   ```

4. Run the Flask app:

   ```bash
   python app.py
   ```

The app will be accessible at `http://127.0.0.1:5000`.

### Docker Setup

To deploy using Docker, follow these steps:

1. Build the Docker image:

   ```bash
   docker build -t document-retrieval-system .
   ```

2. Run the Docker container:

   ```bash
   docker run -p 5000:5000 document-retrieval-system
   ```

## API Endpoints

### Health Check

`GET /health`

- Returns the health status of the system.

**Response:**
```json
{
  "status": "healthy"
}
```

### Search

`POST /search`

- Accepts a search query and returns relevant documents from the indexed news articles.

**Request Body:**
```json
{
  "user_id": "unique_user_id",
  "text": "search query",
  "top_k": 5,
  "threshold": 0.5
}
```

**Response:**
```json
{
  "results": [
    {
      "content": "Article text...",
      "source": "Article URL",
      "score": 0.95
    }
  ],
  "inference_time": 1.23
}
```

### Rate Limiting

- The API limits users to a defined number of requests per hour. If the limit is exceeded, a `429 Too Many Requests` error is returned.

## Project Structure

```
document-retrieval-system/
│
├── app.py                  # Main Flask app
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── .env                    # Environment variables
└── README.md               # Project documentation
```

## Notes
- add your own OpenAi api key in app.py
