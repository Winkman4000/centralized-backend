import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import numpy as np
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)

class CustomDataset(Dataset):
    """Custom dataset for handling different data types"""
    
    def __init__(self, data: List[Dict[str, Any]], dataset_type: str, tokenizer=None):
        self.data = data
        self.dataset_type = dataset_type
        self.tokenizer = tokenizer
        
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        
        if self.dataset_type == "binary_classification":
            # Assume item has 'input' and 'label' keys
            return {
                'input': torch.tensor(self.tokenize_input(item['input']), dtype=torch.float32),
                'label': torch.tensor(item['label'], dtype=torch.long)
            }
        elif self.dataset_type == "qa":
            # Question-Answer pairs
            return {
                'question': torch.tensor(self.tokenize_input(item['question']), dtype=torch.float32),
                'answer': torch.tensor(self.tokenize_input(item['answer']), dtype=torch.float32)
            }
        elif self.dataset_type == "regression":
            return {
                'input': torch.tensor(item['input'], dtype=torch.float32),
                'target': torch.tensor(item['target'], dtype=torch.float32)
            }
        else:
            # Generic handling
            return item
    
    def tokenize_input(self, text):
        """Simple tokenization - replace with actual tokenizer"""
        if isinstance(text, str):
            # Convert to ASCII values and normalize
            return [ord(c) / 255.0 for c in text[:100]]  # Limit to 100 chars
        return text

class TrainingEngine:
    """Comprehensive training engine with monitoring and logging"""
    
    def __init__(self, model, websocket_manager=None, log_callback=None):
        self.model = model
        self.websocket_manager = websocket_manager
        self.log_callback = log_callback
        self.training_stats = {
            'epoch': 0,
            'step': 0,
            'loss': 0.0,
            'accuracy': 0.0,
            'learning_rate': 0.001,
            'training_time': 0.0
        }
        self.loss_history = []
        self.accuracy_history = []
        self.weight_history = []
        self.is_training = False
        
    async def log_event(self, level: str, message: str, model_name: str = "training"):
        """Log training events"""
        if self.log_callback:
            await self.log_callback(model_name, level, message)
        
        if self.websocket_manager:
            await self.websocket_manager.broadcast({
                "type": "training_log",
                "level": level,
                "message": message,
                "model_name": model_name,
                "timestamp": datetime.now().isoformat()
            })
    
    async def broadcast_stats(self, model_name: str):
        """Broadcast training statistics"""
        if self.websocket_manager:
            await self.websocket_manager.broadcast({
                "type": "training_stats",
                "model_name": model_name,
                "stats": self.training_stats,
                "loss_history": self.loss_history[-100:],  # Last 100 points
                "accuracy_history": self.accuracy_history[-100:]
            })
    
    async def broadcast_weights(self, model_name: str):
        """Broadcast current model weights"""
        if self.websocket_manager:
            weights = {}
            for name, param in self.model.named_parameters():
                weights[name] = {
                    "shape": list(param.shape),
                    "mean": float(param.data.mean()),
                    "std": float(param.data.std()),
                    "min": float(param.data.min()),
                    "max": float(param.data.max()),
                    "grad_norm": float(param.grad.norm()) if param.grad is not None else 0.0
                }
            
            await self.websocket_manager.broadcast({
                "type": "weights_update",
                "model_name": model_name,
                "weights": weights
            })
    
    def calculate_accuracy(self, predictions, targets, task_type="classification"):
        """Calculate accuracy based on task type"""
        if task_type == "classification":
            pred_classes = torch.argmax(predictions, dim=1)
            correct = (pred_classes == targets).float()
            return correct.mean().item()
        elif task_type == "regression":
            # Use R² score for regression
            ss_res = torch.sum((targets - predictions) ** 2)
            ss_tot = torch.sum((targets - torch.mean(targets)) ** 2)
            r2 = 1 - (ss_res / ss_tot)
            return r2.item()
        else:
            return 0.0
    
    async def train_epoch(self, dataloader, optimizer, criterion, model_name: str, 
                         epoch: int, task_type: str = "classification"):
        """Train for one epoch with comprehensive logging"""
        self.model.train()
        total_loss = 0.0
        total_accuracy = 0.0
        num_batches = len(dataloader)
        
        await self.log_event("info", f"Starting epoch {epoch} with {num_batches} batches", model_name)
        
        for batch_idx, batch in enumerate(dataloader):
            optimizer.zero_grad()
            
            # Forward pass
            if task_type == "classification":
                inputs = batch['input']
                targets = batch['label']
                outputs = self.model(inputs)
                loss = criterion(outputs, targets)
                accuracy = self.calculate_accuracy(outputs, targets, "classification")
            elif task_type == "regression":
                inputs = batch['input']
                targets = batch['target']
                outputs = self.model(inputs)
                loss = criterion(outputs, targets)
                accuracy = self.calculate_accuracy(outputs, targets, "regression")
            elif task_type == "qa":
                questions = batch['question']
                answers = batch['answer']
                outputs = self.model(questions)
                loss = criterion(outputs, answers)
                accuracy = self.calculate_accuracy(outputs, answers, "regression")
            else:
                # Generic handling
                inputs = batch['input'] if 'input' in batch else batch[0]
                targets = batch['target'] if 'target' in batch else batch[1]
                outputs = self.model(inputs)
                loss = criterion(outputs, targets)
                accuracy = 0.0
            
            # Backward pass
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            
            optimizer.step()
            
            # Update statistics
            total_loss += loss.item()
            total_accuracy += accuracy
            self.training_stats['step'] += 1
            
            # Log every 10 batches
            if batch_idx % 10 == 0:
                current_loss = loss.item()
                current_acc = accuracy
                
                await self.log_event("training", 
                    f"Epoch {epoch}, Batch {batch_idx}/{num_batches}, "
                    f"Loss: {current_loss:.4f}, Accuracy: {current_acc:.4f}", 
                    model_name)
                
                # Broadcast weights every 50 batches
                if batch_idx % 50 == 0:
                    await self.broadcast_weights(model_name)
        
        # Calculate epoch averages
        avg_loss = total_loss / num_batches
        avg_accuracy = total_accuracy / num_batches
        
        # Update training stats
        self.training_stats['epoch'] = epoch
        self.training_stats['loss'] = avg_loss
        self.training_stats['accuracy'] = avg_accuracy
        self.training_stats['learning_rate'] = optimizer.param_groups[0]['lr']
        
        # Store history
        self.loss_history.append(avg_loss)
        self.accuracy_history.append(avg_accuracy)
        
        # Log epoch summary
        await self.log_event("info", 
            f"Epoch {epoch} completed - Loss: {avg_loss:.4f}, Accuracy: {avg_accuracy:.4f}", 
            model_name)
        
        # Broadcast final stats
        await self.broadcast_stats(model_name)
        
        return avg_loss, avg_accuracy
    
    async def train(self, dataset, model_name: str, epochs: int = 10, 
                   batch_size: int = 32, learning_rate: float = 0.001, 
                   task_type: str = "classification"):
        """Main training loop"""
        
        self.is_training = True
        start_time = time.time()
        
        await self.log_event("info", f"Starting training for model '{model_name}'", model_name)
        await self.log_event("info", f"Epochs: {epochs}, Batch size: {batch_size}, LR: {learning_rate}", model_name)
        
        try:
            # Create data loader
            dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
            
            # Set up optimizer and loss function
            optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
            
            if task_type == "classification":
                criterion = nn.CrossEntropyLoss()
            elif task_type == "regression":
                criterion = nn.MSELoss()
            else:
                criterion = nn.MSELoss()  # Default
            
            # Training loop
            for epoch in range(epochs):
                if not self.is_training:  # Check for early stopping
                    break
                
                epoch_loss, epoch_accuracy = await self.train_epoch(
                    dataloader, optimizer, criterion, model_name, epoch + 1, task_type
                )
                
                # Learning rate scheduling (simple step decay)
                if (epoch + 1) % 10 == 0:
                    for param_group in optimizer.param_groups:
                        param_group['lr'] *= 0.9
                    await self.log_event("info", 
                        f"Learning rate reduced to {optimizer.param_groups[0]['lr']:.6f}", 
                        model_name)
            
            # Training completed
            total_time = time.time() - start_time
            self.training_stats['training_time'] = total_time
            
            await self.log_event("info", 
                f"Training completed in {total_time:.2f} seconds", 
                model_name)
            
            # Final weight broadcast
            await self.broadcast_weights(model_name)
            
        except Exception as e:
            await self.log_event("error", f"Training failed: {str(e)}", model_name)
            raise
        finally:
            self.is_training = False
    
    def stop_training(self):
        """Stop training early"""
        self.is_training = False
    
    def get_training_summary(self):
        """Get comprehensive training summary"""
        return {
            "stats": self.training_stats,
            "loss_history": self.loss_history,
            "accuracy_history": self.accuracy_history,
            "total_steps": self.training_stats['step'],
            "is_training": self.is_training
        }

class ModelMetrics:
    """Advanced model metrics and analysis"""
    
    @staticmethod
    def calculate_parameter_count(model):
        """Calculate total parameters and trainable parameters"""
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        
        return {
            "total_parameters": total_params,
            "trainable_parameters": trainable_params,
            "non_trainable_parameters": total_params - trainable_params
        }
    
    @staticmethod
    def analyze_gradients(model):
        """Analyze gradient statistics"""
        grad_stats = {}
        
        for name, param in model.named_parameters():
            if param.grad is not None:
                grad_norm = param.grad.norm().item()
                grad_stats[name] = {
                    "gradient_norm": grad_norm,
                    "gradient_mean": param.grad.mean().item(),
                    "gradient_std": param.grad.std().item(),
                    "gradient_max": param.grad.max().item(),
                    "gradient_min": param.grad.min().item()
                }
        
        return grad_stats
    
    @staticmethod
    def memory_usage(model):
        """Calculate model memory usage"""
        param_size = 0
        for param in model.parameters():
            param_size += param.nelement() * param.element_size()
        
        buffer_size = 0
        for buffer in model.buffers():
            buffer_size += buffer.nelement() * buffer.element_size()
        
        return {
            "parameter_memory_mb": param_size / (1024 * 1024),
            "buffer_memory_mb": buffer_size / (1024 * 1024),
            "total_memory_mb": (param_size + buffer_size) / (1024 * 1024)
        } 