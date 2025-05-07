# Twitter AI Agent

![Twitter AI Agent](public/twitter_agent.png)

## Description

Twitter AI Agent is a Python-based tool that leverages the Gemini AI model to create compelling Twitter posts based on user input. The application allows users to:

- Generate AI-crafted Twitter posts based on prompts
- Review and approve posts before publishing
- Provide feedback to refine posts that need improvement
- Publish approved content directly to Twitter

## Features

- **AI-Powered Content**: Uses Google's Gemini 2.0 Flash model to create engaging Twitter posts
- **Interactive CLI**: Beautiful command-line interface with rich text formatting
- **Review Process**: Preview generated posts before publishing
- **Feedback Loop**: Provide feedback to improve posts that don't meet expectations
- **Direct Publishing**: Post directly to Twitter through the Twitter API
- **Character Limit Enforcement**: Ensures posts adhere to Twitter's 280 character limit

## Requirements

- Python 3.x
- Twitter API credentials
- Google Gemini API key

## Environment Variables

Create a `.env` file in the project root with the following variables:
```
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_SECRET=your_twitter_access_secret
GEMINI_API_KEY=your_gemini_api_key
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables as described above
4. Run the application:
   ```
   python main.py
   ```

## Usage

1. Enter a prompt describing the Twitter post you want to create
2. Review the AI-generated post
3. Choose to publish or provide feedback for refinement
4. If feedback is provided, review the revised post
5. Publish when satisfied with the content

## Technical Details

The application uses:
- LangGraph for workflow management
- Rich library for beautiful CLI formatting
- Python Twitter API for posting to Twitter
- Google's Gemini AI for content generation

## License

[MIT License](LICENSE)
