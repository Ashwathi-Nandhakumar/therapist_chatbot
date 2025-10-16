# Therapist Chatbot

## Project Overview
A Flask-based AI therapist chatbot designed to provide supportive, empathetic conversations in the style of Cognitive Behavioral Therapy (CBT).  
Users can register, log in, and interact with the chatbot, which responds in a comforting tone using the Groq API (Llama-3 model). Conversations and user data are securely stored with SQLite.

## Core Features

- **User Authentication:** Register, log in, log out securely.
- **Personalized Therapy Chat:** Each user gets a private, persistent conversation.
- **Multi-language Support:** Users can select their preferred conversation language.
- **AI Therapist Engine:** Responses generated via the Groq API, always concise, caring, and relevant.
- **Data Storage:** All user credentials (hashed), histories, and settings stored in SQLite (`therapist_app.db`).

## Workflow

1. **User Management**
    - Registration with username and password (hashed for security)
    - Login/Logout with session management

2. **Chat Functionality**
    - User sends a message from the browser
    - Message passed to Groq API along with system prompt (CBT therapist instructions)
    - Response returned and shown in conversation history
    - Conversation stored in SQLite

3. **Error Handling/Edge Cases**
    - Handles invalid input, duplicate users, and missing credentials
    - All API keys managed via environment variables

## Results

- **Deployment-ready Flask app** with multi-user authentication and persistent chat histories.
- **Empathetic, LLM-based conversations** that adapt to the user's emotional language and needs.
- **Easy to extend** with new templates, additional API support, or more advanced therapist personas.

***

*This project is for demonstration and educational purposes. The chatbot does not replace real therapists.*

***
