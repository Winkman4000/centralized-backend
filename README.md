# 🧠 Centralized Neural Network Backend

A comprehensive, user-friendly interface for building, training, and monitoring neural networks from scratch. This system provides a centralized backend where you can manage all aspects of neural network development through an intuitive web interface.

## ✨ Features

### 🏗️ **Complete NN Component Management**
- **Token Management**: Type and store tokens with categorization and dropdown selection
- **Layer Architecture**: Create and order layers with drag-and-drop functionality
- **Head Management**: Attach heads to layers with customizable loss functions
- **Real-time Updates**: All changes broadcast instantly via WebSocket

### 📊 **Comprehensive Monitoring**
- **Weight Visualization**: Live weight sheets showing parameter statistics
- **Training Logs**: Complete input/output logging with spam filtering
- **Real-time Stats**: Live training metrics and loss/accuracy plots
- **Model Analytics**: Parameter counts, memory usage, gradient analysis

### 🗂️ **Dataset Creation Tools**
- **Binary Classification**: Simple positive/negative labeling
- **Multi-class Classification**: Custom category labeling  
- **Question & Answer**: Q&A pair creation for training
- **Article Approximation**: Text summarization datasets
- **Regression**: Numerical input/output pairs
- **Text Generation**: Input/target text sequences

### 🎯 **Advanced Training Engine**
- **Custom Model Creation**: Build models from your layer configurations
- **Multi-task Training**: Support for classification, regression, and Q&A
- **Real-time Monitoring**: Live weight updates during training
- **Gradient Analysis**: Detailed gradient statistics and clipping
- **Learning Rate Scheduling**: Automatic LR decay

## 🚀 Quick Start

### 1. Installation & Setup

```bash
# Clone or download the project
cd centralised-backend

# Run the startup script (installs dependencies and starts server)
python start_server.py
```

### 2. Access the Interface

Open your browser and navigate to:
```
http://localhost:8000
```

### 3. Build Your First Model

1. **Add Tokens** (Tokens tab)
   - Type tokens in the input field
   - Select category (general, special, numeric, etc.)
   - Tokens are stored in categorized dropdowns

2. **Design Architecture** (Architecture tab)
   - Add layers with input/output dimensions
   - Specify layer types (Linear, Conv1D, LSTM, etc.)
   - Drag layers to reorder them
   - Attach heads to layers with loss functions

3. **Create Datasets** (Datasets tab)
   - Choose dataset type
   - Add samples using the interactive forms
   - Datasets are automatically stored

4. **Monitor Training** (Monitoring tab)
   - View real-time weight statistics
   - Track parameter changes during training
   - Analyze model performance metrics

5. **Check Logs** (Logs tab)
   - View comprehensive training logs
   - Filter by log type (info, warning, error)
   - Hide/show spammy logs as needed

## 🛠️ System Architecture

### Backend Components
- **FastAPI Server**: RESTful API with WebSocket support
- **SQLite Database**: Persistent storage for all configurations
- **PyTorch Integration**: Dynamic model creation and training
- **Real-time Broadcasting**: Live updates via WebSocket

### Frontend Components  
- **Tabbed Interface**: Organized sections for different tasks
- **Drag & Drop**: Intuitive layer ordering
- **Real-time Updates**: Live data synchronization
- **Responsive Design**: Works on desktop and tablet

## 📋 Detailed Usage

### Token Management
```javascript
// Tokens are automatically categorized and stored
// Access via dropdown menus throughout the interface
Categories: general, special, numeric, alphabetic, punctuation
```

### Layer Configuration
```python
# Supported layer types:
- Linear/Dense: Fully connected layers
- Conv1D: 1D convolutional layers  
- LSTM: Long Short-Term Memory
- GRU: Gated Recurrent Units
- Attention: Attention mechanisms
```

### Head Management
```python
# Head types with appropriate loss functions:
Classification: CrossEntropyLoss, BCELoss
Regression: MSELoss, HuberLoss  
Generation: Custom loss functions
```

### Dataset Types
```python
# Supported dataset formats:
{
    "binary_classification": {"input": "text", "label": 0/1},
    "multi_classification": {"input": "text", "label": "category"},
    "qa": {"question": "text", "answer": "text"},
    "article_approximation": {"text": "article", "summary": "summary"},
    "regression": {"input": [features], "target": value},
    "text_generation": {"input": "text", "target": "text"}
}
```

## 🔧 API Endpoints

### Token Management
```
POST   /api/tokens          - Create new token
GET    /api/tokens          - List all tokens  
DELETE /api/tokens/{id}     - Delete token
```

### Layer Management
```
POST   /api/layers          - Create new layer
GET    /api/layers          - List all layers
PUT    /api/layers/{id}/order - Update layer order
```

### Head Management
```
POST   /api/heads           - Create new head
GET    /api/heads           - List all heads
```

### Model Operations
```
POST   /api/models/create   - Create model from config
GET    /api/models/{name}/weights - Get model weights
```

### Dataset Operations
```
POST   /api/datasets        - Create new dataset
GET    /api/datasets        - List all datasets
```

### Monitoring
```
GET    /api/logs            - Get training logs
WebSocket /ws               - Real-time updates
```

## 📊 Real-time Features

### WebSocket Events
```javascript
// Real-time events broadcast to all clients:
{
    "type": "token_created",     // New token added
    "type": "layer_created",     // New layer added  
    "type": "head_created",      // New head added
    "type": "model_created",     // Model created
    "type": "training_log",      // Training progress
    "type": "weights_update",    // Weight changes
    "type": "training_stats"     // Performance metrics
}
```

### Live Monitoring
- **Weight Sheet**: Updates every 50 training batches
- **Training Logs**: Real-time log streaming
- **Performance Metrics**: Live loss/accuracy tracking
- **Model Status**: Training state and progress

## 🎨 UI Components

### Tabbed Interface
- **Tokens**: Token management and storage
- **Architecture**: Layer and head configuration
- **Datasets**: Dataset creation and management  
- **Monitoring**: Real-time model monitoring
- **Logs**: Comprehensive logging system

### Interactive Elements
- **Drag & Drop**: Reorder layers visually
- **Dropdown Storage**: Organized token storage
- **Real-time Forms**: Dynamic dataset creation
- **Filter Controls**: Log filtering and search
- **Toggle Switches**: Show/hide functionality

## 🔍 Advanced Features

### Training Engine
- **Automatic Batching**: Configurable batch sizes
- **Gradient Clipping**: Prevents exploding gradients
- **Learning Rate Scheduling**: Automatic decay
- **Multi-task Support**: Different loss functions per head
- **Early Stopping**: Manual training interruption

### Model Analytics
- **Parameter Counting**: Total and trainable parameters
- **Memory Usage**: Model memory consumption
- **Gradient Analysis**: Gradient norm and statistics
- **Training History**: Loss and accuracy tracking

### Data Management
- **Persistent Storage**: SQLite database backend
- **Real-time Sync**: WebSocket synchronization
- **Export/Import**: Model and dataset portability
- **Backup System**: Automatic data backups

## 🛡️ Error Handling

### Comprehensive Logging
- **Info Logs**: Normal operations and progress
- **Warning Logs**: Non-critical issues
- **Error Logs**: Failures and exceptions
- **Training Logs**: Detailed training progress

### User-friendly Messages
- **Form Validation**: Client-side input validation
- **API Error Handling**: Graceful error responses
- **WebSocket Reconnection**: Automatic reconnection
- **Fallback Systems**: Graceful degradation

## 🔧 Customization

### Extending Layer Types
```python
# Add new layer types in backend/main.py
elif layer_config.layer_type == "custom":
    self.layers.append(CustomLayer(...))
```

### Custom Dataset Types
```python
# Add new dataset types in backend/training_engine.py
elif self.dataset_type == "custom":
    return custom_processing(item)
```

### UI Modifications
```javascript
// Modify frontend/app.js for custom UI behavior
// Add new tabs, forms, or visualizations
```

## 📈 Performance

### Optimization Features
- **Efficient Database**: SQLite with indexed queries
- **WebSocket Batching**: Reduced message overhead
- **Lazy Loading**: Load data on demand
- **Caching**: Client-side data caching

### Scalability
- **Multi-model Support**: Handle multiple models simultaneously  
- **Concurrent Training**: Parallel training processes
- **Memory Management**: Efficient memory usage
- **Resource Monitoring**: Track system resources

## 🤝 Contributing

This system is designed to be easily extensible. Key areas for contribution:

1. **New Layer Types**: Add support for more PyTorch layers
2. **Dataset Formats**: Support additional data formats
3. **Visualization**: Enhanced monitoring and plotting
4. **Training Algorithms**: Advanced optimization methods
5. **UI Improvements**: Better user experience features

## 📝 License

This project is designed for educational and research purposes. Modify and extend as needed for your specific use cases.

---

**Happy Neural Network Building! 🎯** 