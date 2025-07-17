# BiteBot - Your Personal Recipe Health Assistant

BiteBot is a full-stack chatbot application designed to help you make your favorite recipes healthier. Simply provide a recipe, and BiteBot will suggest three minor modifications to improve its nutritional value. It can also provide detailed nutritional information for individual ingredients and entire meals.

## Live Demo

The application is deployed and accessible at: [https://bite-bot.onrender.com](https://bite-bot.onrender.com)

## Features

*   **Recipe Healthification**: Get suggestions to make your recipes healthier.
*   **Nutritional Information**: Get detailed nutritional information for a list of ingredients.
*   **Meal Nutrition Calculation**: Calculate the total nutritional value of a meal.
*   **Personalized Experience**: BiteBot can remember your personal details (age, sex, height, weight, health targets, exercise level) to provide more personalized advice.
*   **Movie Listings**: As a bonus feature, BiteBot can also tell you which movies are playing on TV today in Poland.

## Tech Stack

### Backend

*   **Python**
*   **FastAPI**: For building the REST API.
*   **LangChain**: To power the conversational agent.
*   **OpenAI GPT-4o-mini**: The language model used by the agent.
*   **USDA FoodData Central API**: For fetching nutritional information.

### Frontend

*   **React**
*   **TypeScript**
*   **Create React App**
*   **React Markdown**: For rendering Markdown content.

## Getting Started

### Prerequisites

*   Python 3.11
*   Node.js and npm
*   An OpenAI API key
*   A USDA FoodData Central API key

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/custom_chatbot.git
    cd custom_chatbot
    ```

2.  **Backend Setup:**
    *   Navigate to the `backend` directory:
        ```bash
        cd backend
        ```
    *   Create a virtual environment and activate it:
        ```bash
        python -m venv .venv
        source .venv/bin/activate # On Windows, use `.venv\Scripts\activate`
        ```
    *   Install the required Python packages:
        ```bash
        pip install -r requirements.txt
        ```
    *   Create a `.env` file in the `backend` directory and add your API keys:
        ```
        OPENAI_API_KEY="your-openai-api-key"
        USDA_API_KEY="your-usda-api-key"
        ```

3.  **Frontend Setup:**
    *   Navigate to the `frontend` directory:
        ```bash
        cd ../frontend
        ```
    *   Install the required npm packages:
        ```bash
        npm install
        ```
    *   Create a `.env` file in the `frontend` directory and add the backend API URL:
        ```
        REACT_APP_API_URL=http://localhost:8000
        ```

### Running the Application

1.  **Start the backend server:**
    *   In the `backend` directory, run:
        ```bash
        uvicorn main:app --reload
        ```
    The backend server will be running at `http://localhost:8000`.

2.  **Start the frontend development server:**
    *   In the `frontend` directory, run:
        ```bash
        npm start
        ```
    The frontend application will be running at `http://localhost:3000`.

3.  Open your browser and navigate to `http://localhost:3000` to start chatting with BiteBot.

## How It Works

The application consists of a React frontend and a FastAPI backend. The frontend provides a user-friendly chat interface, while the backend handles the business logic.

When a user sends a message, the frontend sends a POST request to the `/api/chat` endpoint on the backend. The backend then uses a LangChain agent to process the message. The agent has access to a set of tools that allow it to perform various tasks, such as fetching nutritional information or scraping movie listings. The agent's response is streamed back to the frontend and displayed to the user.
