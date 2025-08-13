# Financial Statement Analysis API

A powerful, production-ready API that uses LangGraph and Google's Gemini AI to analyze financial statements from PDF files.

## 🚀 Features

- 📄 **PDF Processing**: Upload and analyze PDF financial statements
- 💰 **Metric Extraction**: Automatic extraction of key financial figures
- 📊 **Ratio Calculation**: Financial ratio computation and analysis
- 🤖 **AI Analysis**: Google Gemini-powered financial insights
- 🔄 **Async Processing**: Background task processing with status tracking
- 📚 **Auto-documentation**: Interactive API docs with Swagger/ReDoc
- 🐳 **Docker Ready**: Containerized deployment with Docker
- 🔒 **Error Handling**: Comprehensive error handling and validation

## 🏗️ Architecture

- **FastAPI**: Modern, fast web framework for building APIs
- **LangGraph**: Workflow orchestration for analysis pipeline
- **Google Gemini**: AI-powered financial analysis
- **Background Tasks**: Asynchronous processing for large files
- **Status Tracking**: Real-time analysis progress monitoring

## 📋 Requirements

- Python 3.8+
- Google AI API key
- PDF financial statements

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up Environment

Create a `.env` file:

```bash
# .env
GOOGLE_API_KEY=your_google_api_key_here
DEBUG=false
```

### 3. Start the API

```bash
python api.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📖 API Usage

### Health Check

```bash
curl http://localhost:8000/health
```

### Upload and Analyze PDF

```bash
curl -X POST "http://localhost:8000/analyze/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_statement.pdf" \
  -F "analysis_type=full"
```

### Analyze Existing File

```bash
curl -X POST "http://localhost:8000/analyze/file" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "path/to/statement.pdf", "analysis_type": "full"}'
```

### Check Analysis Status

```bash
curl http://localhost:8000/status/{request_id}
```

### Get Results

```bash
curl http://localhost:8000/results/{request_id}
```

### Queue Status

```bash
curl http://localhost:8000/queue
```

## 🔧 Analysis Types

- **`metrics`**: Extract financial metrics only
- **`ratios`**: Calculate financial ratios only  
- **`full`**: Complete analysis (metrics + ratios + AI insights)

## 🐳 Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t financial-analysis-api .

# Run the container
docker run -p 8000:8000 \
  -e GOOGLE_API_KEY=your_key_here \
  financial-analysis-api
```

### Using Docker Compose

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

## 🧪 Testing

### Test Client

Use the included test client:

```bash
python test_api.py
```

### Manual Testing

1. Start the API server
2. Open http://localhost:8000/docs
3. Use the interactive Swagger UI to test endpoints
4. Upload a PDF and monitor the analysis process

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information |
| `GET` | `/health` | Health check |
| `POST` | `/analyze/upload` | Upload and analyze PDF |
| `POST` | `/analyze/file` | Analyze existing file |
| `GET` | `/status/{id}` | Check analysis status |
| `GET` | `/results/{id}` | Get analysis results |
| `GET` | `/queue` | Queue status |
| `DELETE` | `/cleanup/{id}` | Clean up analysis |
| `DELETE` | `/cleanup/all` | Clean up all analyses |

## 🔄 Workflow

1. **Upload/Select**: Choose PDF file or provide file path
2. **Queue**: Analysis request is queued with unique ID
3. **Process**: Background task processes the PDF
4. **Extract**: Financial metrics are extracted using regex patterns
5. **Calculate**: Financial ratios are computed
6. **Analyze**: AI generates insights using Google Gemini
7. **Complete**: Results are stored and available for retrieval

## 🛠️ Development

### Project Structure

```
├── api.py              # FastAPI application
├── analyse.py          # Core analysis logic
├── test_api.py         # Test client
├── requirements.txt    # Dependencies
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose
├── README.md          # This file
└── uploads/           # Temporary file storage
```

### Adding New Features

1. **New Metrics**: Update regex patterns in `analyse.py`
2. **New Ratios**: Add calculation logic in `calculate_ratios()`
3. **New Endpoints**: Add routes in `api.py`
4. **Validation**: Update Pydantic models as needed

## 🚀 Production Deployment

### Environment Variables

```bash
GOOGLE_API_KEY=your_production_key
DEBUG=false
LOG_LEVEL=info
```

### Scaling Considerations

- **Database**: Replace in-memory storage with PostgreSQL/Redis
- **Queue**: Use Celery or Redis for job queuing
- **Storage**: Use cloud storage (S3, GCS) for PDFs
- **Monitoring**: Add Prometheus metrics and logging
- **Load Balancing**: Use Nginx or cloud load balancer

### Security

- **Authentication**: Add JWT or API key authentication
- **Rate Limiting**: Implement request throttling
- **File Validation**: Enhanced file type and content validation
- **HTTPS**: Use SSL/TLS in production

## 🐛 Troubleshooting

### Common Issues

- **API Key Error**: Ensure `GOOGLE_API_KEY` is set in `.env`
- **PDF Not Found**: Check file path and permissions
- **Analysis Fails**: Verify PDF contains financial data
- **Port Already in Use**: Change port in `api.py` or Docker config

### Logs

```bash
# View API logs
docker-compose logs -f financial-analysis-api

# Check health status
curl http://localhost:8000/health
```

## 📈 Performance

- **Concurrent Processing**: Multiple analyses can run simultaneously
- **Background Tasks**: Non-blocking PDF processing
- **File Cleanup**: Automatic temporary file removal
- **Memory Management**: Efficient state handling with LangGraph

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check the logs for error details
4. Open an issue with detailed information