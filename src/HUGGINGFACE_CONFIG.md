# Hugging Face Configuration Guide

This document explains how to effectively use Hugging Face models in the AI-Powered Document Drafting Assistant.

## Available Models

The application has been configured to use the following Hugging Face models by default:

1. **Mistral-7B-Instruct-v0.2** - Default language model for text generation
2. **Sentence Transformers (all-mpnet-base-v2)** - Default model for embeddings

## Custom Model Configuration

You can use different Hugging Face models by selecting them in the web interface or by modifying the `models.py` file.

### Language Models

When choosing a language model, ensure it:
- Supports instruction following
- Can handle chat/conversation format
- Has appropriate context length for your needs

Good options include:
- mistralai/Mistral-7B-Instruct-v0.2
- HuggingFaceH4/zephyr-7b-beta
- microsoft/phi-2
- google/flan-t5-large

### Embedding Models

For the embedding model, ensure you select one that:
- Creates quality vector representations
- Has good semantic search capabilities
- Works well with your document types

Good options include:
- sentence-transformers/all-mpnet-base-v2
- sentence-transformers/all-MiniLM-L6-v2
- BAAI/bge-small-en-v1.5

## Environment Configuration

Make sure your `.env` file contains your Hugging Face API token:

```
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
```

You can obtain a token by signing up at [Hugging Face](https://huggingface.co/settings/tokens).

## Performance Considerations

- Larger models provide better quality but require more resources
- Consider using smaller models for quicker responses on limited hardware
- The Hugging Face Inference API has rate limits depending on your account type
