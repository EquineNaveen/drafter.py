# Model Selection Guide

This document provides information about the models used in the AI-Powered Document Drafting Assistant.

## Available Models

The application has been configured to use the following Hugging Face models by default:

### Language Models

| Model | Description | Size | Use Case |
|-------|-------------|------|----------|
| `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | Default model - optimized for chat interactions | 1.1B | Email drafting, conversational tasks |
| `google/flan-t5-base` | Good balance of performance and speed | 250M | General text generation |
| `google/flan-t5-small` | Smaller, faster model | 80M | Quick responses, simpler tasks |
| `facebook/bart-large-cnn` | Good for summarization and generation | 400M | More complex writing tasks |

### Embedding Models

| Model | Description | Size | Use Case |
|-------|-------------|------|----------|
| `sentence-transformers/all-mpnet-base-v2` | Default embedding model | 110M | High quality semantic search |

## Changing Models

You can select different models in two ways:

1. **Using the web interface**: Choose from the dropdown menu in the sidebar
2. **In the code**: Edit the default models in `src/models.py`

## Compatible Models

When selecting models, make sure they:

1. Are accessible through the Hugging Face Inference API
2. Support the appropriate task (text generation or embeddings)
3. Have a manageable size for your hardware

## Free vs. API Access

- The models listed above are available through the free Hugging Face Inference API
- More powerful models like Mistral-7B or Llama-2 require:
  - Using the paid Hugging Face Inference API
  - Running the model locally with sufficient hardware
  - Special access permissions from the model creators

## Local Model Setup

If you want to use larger models locally instead of through the API:

1. Install transformers and torch: `pip install transformers torch`
2. Modify `src/models.py` to use local models
3. Ensure your hardware can support the model size

## Troubleshooting

If you encounter a "404 Not Found" error, the model may:
- Not be accessible through the Inference API
- Require special permissions
- Have been moved or renamed

Try using one of the recommended models listed above.
