from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import asyncio
import logging
import sqlite3
from datetime import datetime
import torch
import torch.nn as nn
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Centralized NN Backend", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models for API
class Token(BaseModel):
    id: Optional[int] = None
    value: str
    category: str = "general"
    
class Layer(BaseModel):
    id: Optional[int] = None
    name: str
    layer_type: str
    input_size: int
    output_size: int
    activation: str = "relu"
    order: int
    
class Head(BaseModel):
    id: Optional[int] = None
    name: str
    layer_id: int
    head_type: str
    order: int
    loss_function: str = "mse"
    
class Dataset(BaseModel):
    id: Optional[int] = None
    name: str
    dataset_type: str
    data: List[Dict[str, Any]]
    
class ModelConfig(BaseModel):
    name: str
    layers: List[Layer]
    heads: List[Head]
    tokens: List[Token]

# Global storage
active_models = {}
websocket_connections = []
training_logs = []

# Database setup
def init_db():
    conn = sqlite3.connect('nn_backend.db')
    cursor = conn.cursor()
    
    # Tokens table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Layers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS layers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            layer_type TEXT NOT NULL,
            input_size INTEGER NOT NULL,
            output_size INTEGER NOT NULL,
            activation TEXT DEFAULT 'relu',
            order_pos INTEGER NOT NULL,
            model_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Heads table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS heads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            layer_id INTEGER NOT NULL,
            head_type TEXT NOT NULL,
            order_pos INTEGER NOT NULL,
            loss_function TEXT DEFAULT 'mse',
            model_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Datasets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dataset_type TEXT NOT NULL,
            data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Training logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            log_type TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("Database initialized")

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle WebSocket messages if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Token management endpoints
@app.post("/api/tokens")
async def create_token(token: Token):
    conn = sqlite3.connect('nn_backend.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tokens (value, category) VALUES (?, ?)",
        (token.value, token.category)
    )
    token_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    await manager.broadcast({
        "type": "token_created",
        "token": {"id": token_id, "value": token.value, "category": token.category}
    })
    
    return {"id": token_id, "message": "Token created successfully"}

@app.get("/api/tokens")
async def get_tokens():
    conn = sqlite3.connect('nn_backend.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, value, category FROM tokens ORDER BY category, value")
    tokens = [{"id": row[0], "value": row[1], "category": row[2]} for row in cursor.fetchall()]
    conn.close()
    return tokens

@app.delete("/api/tokens/{token_id}")
async def delete_token(token_id: int):
    conn = sqlite3.connect('nn_backend.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tokens WHERE id = ?", (token_id,))
    conn.commit()
    conn.close()
    
    await manager.broadcast({
        "type": "token_deleted",
        "token_id": token_id
    })
    
    return {"message": "Token deleted successfully"}

# Layer management endpoints
@app.post("/api/layers")
async def create_layer(layer: Layer):
    conn = sqlite3.connect('nn_backend.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO layers (name, layer_type, input_size, output_size, activation, order_pos) VALUES (?, ?, ?, ?, ?, ?)",
        (layer.name, layer.layer_type, layer.input_size, layer.output_size, layer.activation, layer.order)
    )
    layer_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    await manager.broadcast({
        "type": "layer_created",
        "layer": {
            "id": layer_id,
            "name": layer.name,
            "layer_type": layer.layer_type,
            "input_size": layer.input_size,
            "output_size": layer.output_size,
            "activation": layer.activation,
            "order": layer.order
        }
    })
    
    return {"id": layer_id, "message": "Layer created successfully"}

@app.get("/api/layers")
async def get_layers():
    conn = sqlite3.connect('nn_backend.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, layer_type, input_size, output_size, activation, order_pos FROM layers ORDER BY order_pos")
    layers = [{
        "id": row[0],
        "name": row[1],
        "layer_type": row[2],
        "input_size": row[3],
        "output_size": row[4],
        "activation": row[5],
        "order": row[6]
    } for row in cursor.fetchall()]
    conn.close()
    return layers

@app.put("/api/layers/{layer_id}/order")
async def update_layer_order(layer_id: int, new_order: dict):
    conn = sqlite3.connect('nn_backend.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE layers SET order_pos = ? WHERE id = ?", (new_order["order"], layer_id))
    conn.commit()
    conn.close()
    
    await manager.broadcast({
        "type": "layer_order_updated",
        "layer_id": layer_id,
        "new_order": new_order["order"]
    })
    
    return {"message": "Layer order updated successfully"}

# Head management endpoints
@app.post("/api/heads")
async def create_head(head: Head):
    conn = sqlite3.connect('nn_backend.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO heads (name, layer_id, head_type, order_pos, loss_function) VALUES (?, ?, ?, ?, ?)",
        (head.name, head.layer_id, head.head_type, head.order, head.loss_function)
    )
    head_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    await manager.broadcast({
        "type": "head_created",
        "head": {
            "id": head_id,
            "name": head.name,
            "layer_id": head.layer_id,
            "head_type": head.head_type,
            "order": head.order,
            "loss_function": head.loss_function
        }
    })
    
    return {"id": head_id, "message": "Head created successfully"}

@app.get("/api/heads")
async def get_heads():
    conn = sqlite3.connect('nn_backend.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, layer_id, head_type, order_pos, loss_function FROM heads ORDER BY order_pos")
    heads = [{
        "id": row[0],
        "name": row[1],
        "layer_id": row[2],
        "head_type": row[3],
        "order": row[4],
        "loss_function": row[5]
    } for row in cursor.fetchall()]
    conn.close()
    return heads

# Dataset management endpoints
@app.post("/api/datasets")
async def create_dataset(dataset: Dataset):
    conn = sqlite3.connect('nn_backend.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO datasets (name, dataset_type, data) VALUES (?, ?, ?)",
        (dataset.name, dataset.dataset_type, json.dumps(dataset.data))
    )
    dataset_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {"id": dataset_id, "message": "Dataset created successfully"}

@app.get("/api/datasets")
async def get_datasets():
    conn = sqlite3.connect('nn_backend.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, dataset_type, data FROM datasets")
    datasets = [{
        "id": row[0],
        "name": row[1],
        "dataset_type": row[2],
        "data": json.loads(row[3])
    } for row in cursor.fetchall()]
    conn.close()
    return datasets

# Model training and monitoring
@app.post("/api/models/create")
async def create_model(config: ModelConfig):
    try:
        # Create PyTorch model from config
        class DynamicModel(nn.Module):
            def __init__(self, layers_config):
                super().__init__()
                self.layers = nn.ModuleList()
                
                for layer_config in sorted(layers_config, key=lambda x: x.order):
                    if layer_config.layer_type == "linear":
                        self.layers.append(nn.Linear(layer_config.input_size, layer_config.output_size))
                    elif layer_config.layer_type == "conv1d":
                        self.layers.append(nn.Conv1d(layer_config.input_size, layer_config.output_size, 3))
                    elif layer_config.layer_type == "lstm":
                        self.layers.append(nn.LSTM(layer_config.input_size, layer_config.output_size, batch_first=True))
            
            def forward(self, x):
                for layer in self.layers:
                    x = layer(x)
                return x
        
        model = DynamicModel(config.layers)
        active_models[config.name] = {
            "model": model,
            "config": config,
            "created_at": datetime.now()
        }
        
        await manager.broadcast({
            "type": "model_created",
            "model_name": config.name,
            "layers_count": len(config.layers),
            "heads_count": len(config.heads)
        })
        
        return {"message": f"Model '{config.name}' created successfully"}
    
    except Exception as e:
        logger.error(f"Error creating model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models/{model_name}/weights")
async def get_model_weights(model_name: str):
    if model_name not in active_models:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model = active_models[model_name]["model"]
    weights = {}
    
    for name, param in model.named_parameters():
        weights[name] = {
            "shape": list(param.shape),
            "mean": float(param.data.mean()),
            "std": float(param.data.std()),
            "min": float(param.data.min()),
            "max": float(param.data.max())
        }
    
    return weights

@app.get("/api/logs")
async def get_logs(limit: int = 100, log_type: str = None):
    conn = sqlite3.connect('nn_backend.db')
    cursor = conn.cursor()
    
    query = "SELECT model_name, log_type, message, timestamp FROM training_logs"
    params = []
    
    if log_type:
        query += " WHERE log_type = ?"
        params.append(log_type)
    
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    logs = [{
        "model_name": row[0],
        "log_type": row[1],
        "message": row[2],
        "timestamp": row[3]
    } for row in cursor.fetchall()]
    
    conn.close()
    return logs

# Utility function to log training events
async def log_training_event(model_name: str, log_type: str, message: str):
    conn = sqlite3.connect('nn_backend.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO training_logs (model_name, log_type, message) VALUES (?, ?, ?)",
        (model_name, log_type, message)
    )
    conn.commit()
    conn.close()
    
    await manager.broadcast({
        "type": "training_log",
        "model_name": model_name,
        "log_type": log_type,
        "message": message,
        "timestamp": datetime.now().isoformat()
    })

# Static files
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 