# API Setup Guide

This project can run in **Local Deterministic Mode** without any API keys, which is the recommended way to demo the core deterministic logic.

However, if you want to test the full Google ADK agentic generative features, follow these steps.

## 1. Google Gemini / ADK Setup
1. Go to Google AI Studio or Google Cloud Console.
2. Generate an API Key for Gemini.
3. Update your `.env` file:
   ```env
   GOOGLE_API_KEY=your_key_here
   GEMINI_MODEL=gemini-1.5-pro
   ```

## 2. Qdrant Cloud Setup (Optional)
The project defaults to a local Qdrant instance. If you want to use Qdrant Cloud:
1. Create a cluster on Qdrant Cloud.
2. Get the Cluster URL and API Key.
3. Update your `.env`:
   ```env
   QDRANT_URL=https://your-cluster-url.qdrant.tech
   QDRANT_API_KEY=your_qdrant_key
   QDRANT_COLLECTION=zera_safety_memory
   ```

## 3. Lyzr Supervisor Setup (Optional)
If you are integrating Lyzr for an additional supervisor check:
1. Obtain Lyzr API credentials.
2. Update your `.env`:
   ```env
   LYZR_API_KEY=your_lyzr_key
   LYZR_AGENT_ID=your_lyzr_agent_id
   LYZR_API_URL=https://api.lyzr.ai/
   ```
