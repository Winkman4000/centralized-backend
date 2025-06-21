class NeuralNetworkBackend {
    constructor() {
        this.baseUrl = 'http://localhost:8000';
        this.websocket = null;
        this.tokenBanks = [];
        this.tokens = [];
        this.selectedBank = null;
        this.layers = [];
        this.heads = [];
        this.datasets = [];
        this.models = {};
        this.logs = [];
        this.logsHidden = false;
        
        this.init();
    }

    init() {
        this.setupWebSocket();
        this.setupEventListeners();
        this.setupTabs();
        this.loadInitialData();
        this.setupDatasetTypeChanger();
    }

    setupWebSocket() {
        this.websocket = new WebSocket('ws://localhost:8000/ws');
        
        this.websocket.onopen = () => {
            console.log('WebSocket connected');
            this.addLog('info', 'WebSocket connection established');
        };
        
        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.websocket.onclose = () => {
            console.log('WebSocket disconnected');
            this.addLog('warning', 'WebSocket connection lost');
            // Attempt to reconnect after 3 seconds
            setTimeout(() => this.setupWebSocket(), 3000);
        };
    }

    handleWebSocketMessage(data) {
        switch(data.type) {
            case 'bank_created':
                this.tokenBanks.push(data.bank);
                this.renderBanks();
                this.updateBankSelectors();
                this.addLog('info', `Token bank created: ${data.bank.name}`);
                break;
            case 'bank_deleted':
                this.tokenBanks = this.tokenBanks.filter(b => b.id !== data.bank_id);
                this.renderBanks();
                this.updateBankSelectors();
                this.addLog('info', `Token bank deleted: ID ${data.bank_id}`);
                break;
            case 'token_created':
                this.tokens.push(data.token);
                this.renderTokens();
                this.addLog('info', `Token created: ${data.token.value} in bank ${data.token.bank_id}`);
                break;
            case 'tokens_bulk_created':
                this.tokens.push(...data.tokens);
                this.renderTokens();
                this.addLog('info', `Bulk created ${data.tokens.length} tokens`);
                break;
            case 'token_deleted':
                this.tokens = this.tokens.filter(t => t.id !== data.token_id);
                this.renderTokens();
                this.addLog('info', `Token deleted: ID ${data.token_id}`);
                break;
            case 'layer_created':
                this.layers.push(data.layer);
                this.renderLayers();
                this.updateHeadLayerOptions();
                this.addLog('info', `Layer created: ${data.layer.name}`);
                break;
            case 'head_created':
                this.heads.push(data.head);
                this.renderHeads();
                this.addLog('info', `Head created: ${data.head.name}`);
                break;
            case 'model_created':
                this.addLog('info', `Model created: ${data.model_name} with ${data.layers_count} layers and ${data.heads_count} heads`);
                this.loadModels();
                break;
            case 'training_log':
                this.addLog(data.log_type, data.message, data.model_name);
                break;
        }
    }

    setupEventListeners() {
        // Token bank management
        document.getElementById('create-bank-btn').addEventListener('click', () => this.createBank());
        document.getElementById('bank-name-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.createBank();
        });
        
        // Token management
        document.getElementById('add-token-btn').addEventListener('click', () => this.addToken());
        document.getElementById('token-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.addToken();
        });
        document.getElementById('bulk-add-btn').addEventListener('click', () => this.toggleBulkModal());
        document.getElementById('process-bulk-btn').addEventListener('click', () => this.processBulkTokens());
        document.getElementById('cancel-bulk-btn').addEventListener('click', () => this.toggleBulkModal());
        document.getElementById('bank-filter').addEventListener('change', () => this.renderTokens());
        document.getElementById('token-search').addEventListener('input', () => this.renderTokens());
        document.getElementById('search-btn').addEventListener('click', () => this.renderTokens());

        // Layer management
        document.getElementById('add-layer-btn').addEventListener('click', () => this.addLayer());
        
        // Head management
        document.getElementById('add-head-btn').addEventListener('click', () => this.addHead());
        
        // Model creation
        document.getElementById('create-model-btn').addEventListener('click', () => this.createModel());
        
        // Dataset management
        document.getElementById('dataset-type').addEventListener('change', () => this.updateDatasetCreator());
        document.getElementById('create-dataset-btn').addEventListener('click', () => this.createDataset());
        
        // Monitoring
        document.getElementById('refresh-weights-btn').addEventListener('click', () => this.refreshWeights());
        document.getElementById('model-select').addEventListener('change', () => this.refreshWeights());
        
        // Logs
        document.getElementById('toggle-logs-btn').addEventListener('click', () => this.toggleLogs());
        document.getElementById('clear-logs-btn').addEventListener('click', () => this.clearLogs());
        document.getElementById('log-filter').addEventListener('change', () => this.renderLogs());
    }

    setupTabs() {
        const tabButtons = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tabName = button.getAttribute('data-tab');
                
                // Update button styles
                tabButtons.forEach(btn => {
                    btn.classList.remove('border-blue-400', 'text-blue-400');
                    btn.classList.add('border-transparent', 'text-gray-400');
                });
                button.classList.remove('border-transparent', 'text-gray-400');
                button.classList.add('border-blue-400', 'text-blue-400');
                
                // Show/hide content
                tabContents.forEach(content => {
                    content.classList.add('hidden');
                });
                document.getElementById(`${tabName}-tab`).classList.remove('hidden');
            });
        });
    }

    async loadInitialData() {
        await Promise.all([
            this.loadTokenBanks(),
            this.loadTokens(),
            this.loadLayers(),
            this.loadHeads(),
            this.loadDatasets(),
            this.loadLogs()
        ]);
    }

    // Token Bank Management
    async createBank() {
        const name = document.getElementById('bank-name-input').value.trim();
        const description = document.getElementById('bank-description').value.trim();
        
        if (!name) return;
        
        try {
            const response = await fetch(`${this.baseUrl}/api/token-banks`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, description })
            });
            
            const result = await response.json();
            if (response.ok) {
                document.getElementById('bank-name-input').value = '';
                document.getElementById('bank-description').value = '';
                // Bank will be added via WebSocket
            } else {
                this.addLog('error', result.error || 'Failed to create bank');
            }
        } catch (error) {
            this.addLog('error', `Failed to create bank: ${error.message}`);
        }
    }

    async loadTokenBanks() {
        try {
            const response = await fetch(`${this.baseUrl}/api/token-banks`);
            this.tokenBanks = await response.json();
            this.renderBanks();
            this.updateBankSelectors();
        } catch (error) {
            this.addLog('error', `Failed to load token banks: ${error.message}`);
        }
    }

    renderBanks() {
        const container = document.getElementById('banks-list');
        
        container.innerHTML = this.tokenBanks.map(bank => `
            <div class="p-3 bg-gray-600 rounded border border-gray-500 hover:bg-gray-500 transition-colors">
                <div class="flex items-center justify-between">
                    <div class="flex-1">
                        <h5 class="font-semibold text-gray-100">${bank.name}</h5>
                        <p class="text-xs text-gray-300 mt-1">${bank.description || 'No description'}</p>
                    </div>
                    <div class="flex space-x-2">
                        <button onclick="app.selectBank(${bank.id})" class="text-blue-400 hover:text-blue-300 text-sm">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button onclick="app.deleteBank(${bank.id})" class="text-red-400 hover:text-red-300 text-sm">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    updateBankSelectors() {
        const selectors = ['selected-bank', 'bank-filter'];
        
        selectors.forEach(selectorId => {
            const selector = document.getElementById(selectorId);
            const currentValue = selector.value;
            
            selector.innerHTML = selectorId === 'selected-bank' 
                ? '<option value="">Select a bank first</option>'
                : '<option value="all">All Banks</option>';
            
            this.tokenBanks.forEach(bank => {
                selector.innerHTML += `<option value="${bank.id}">${bank.name}</option>`;
            });
            
            if (currentValue) selector.value = currentValue;
        });
    }

    selectBank(bankId) {
        this.selectedBank = bankId;
        document.getElementById('selected-bank').value = bankId;
        document.getElementById('bank-filter').value = bankId;
        this.renderTokens();
        
        const bank = this.tokenBanks.find(b => b.id === bankId);
        document.getElementById('selected-bank-name').textContent = bank ? bank.name : 'None';
    }

    async deleteBank(bankId) {
        if (!confirm('Delete this token bank? This will also delete all tokens in it.')) return;
        
        try {
            const response = await fetch(`${this.baseUrl}/api/token-banks/${bankId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                // Bank will be removed via WebSocket
                if (this.selectedBank === bankId) {
                    this.selectedBank = null;
                    document.getElementById('selected-bank-name').textContent = 'None';
                }
            }
        } catch (error) {
            this.addLog('error', `Failed to delete bank: ${error.message}`);
        }
    }

    // Token Management
    async addToken() {
        const bankId = parseInt(document.getElementById('selected-bank').value);
        const value = document.getElementById('token-input').value.trim();
        const tokenId = document.getElementById('token-id').value;
        
        if (!bankId || !value) {
            this.addLog('warning', 'Please select a bank and enter a token value');
            return;
        }
        
        try {
            const payload = { bank_id: bankId, value };
            if (tokenId) payload.token_id = parseInt(tokenId);
            
            const response = await fetch(`${this.baseUrl}/api/tokens`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            const result = await response.json();
            if (response.ok) {
                document.getElementById('token-input').value = '';
                document.getElementById('token-id').value = '';
                // Token will be added via WebSocket
            } else {
                this.addLog('error', result.error || 'Failed to add token');
            }
        } catch (error) {
            this.addLog('error', `Failed to add token: ${error.message}`);
        }
    }

    toggleBulkModal() {
        const modal = document.getElementById('bulk-modal');
        modal.classList.toggle('hidden');
    }

    async processBulkTokens() {
        const bankId = parseInt(document.getElementById('selected-bank').value);
        const tokensText = document.getElementById('bulk-tokens').value.trim();
        
        if (!bankId || !tokensText) {
            this.addLog('warning', 'Please select a bank and enter tokens');
            return;
        }
        
        const tokens = tokensText.split('\n').map(t => t.trim()).filter(t => t);
        
        try {
            const response = await fetch(`${this.baseUrl}/api/tokens/bulk`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ bank_id: bankId, tokens })
            });
            
            if (response.ok) {
                document.getElementById('bulk-tokens').value = '';
                this.toggleBulkModal();
                // Tokens will be added via WebSocket
            }
        } catch (error) {
            this.addLog('error', `Failed to bulk add tokens: ${error.message}`);
        }
    }

    async loadTokens() {
        try {
            const response = await fetch(`${this.baseUrl}/api/tokens`);
            this.tokens = await response.json();
            this.renderTokens();
        } catch (error) {
            this.addLog('error', `Failed to load tokens: ${error.message}`);
        }
    }

    renderTokens() {
        const container = document.getElementById('tokens-container');
        const bankFilter = document.getElementById('bank-filter').value;
        const searchTerm = document.getElementById('token-search').value.toLowerCase();
        
        let filteredTokens = this.tokens;
        
        // Filter by bank
        if (bankFilter !== 'all') {
            filteredTokens = filteredTokens.filter(token => token.bank_id == bankFilter);
        }
        
        // Filter by search term
        if (searchTerm) {
            filteredTokens = filteredTokens.filter(token => 
                token.value.toLowerCase().includes(searchTerm) ||
                token.bank_name.toLowerCase().includes(searchTerm)
            );
        }
        
        container.innerHTML = filteredTokens.map(token => `
            <div class="flex items-center justify-between p-2 bg-gray-600 rounded border border-gray-500 hover:bg-gray-500 transition-colors">
                <div class="flex items-center space-x-2">
                    <span class="px-2 py-1 text-xs rounded-full bg-blue-600 text-blue-100">
                        ID: ${token.token_id}
                    </span>
                    <span class="px-2 py-1 text-xs rounded-full bg-green-600 text-green-100">
                        ${token.bank_name}
                    </span>
                    <span class="font-mono text-sm text-gray-100">${token.value}</span>
                </div>
                <button onclick="app.deleteToken(${token.id})" class="text-red-400 hover:text-red-300">
                    <i class="fas fa-trash text-xs"></i>
                </button>
            </div>
        `).join('');
        
        document.getElementById('token-count').textContent = filteredTokens.length;
    }



    async deleteToken(tokenId) {
        try {
            await fetch(`${this.baseUrl}/api/tokens/${tokenId}`, { method: 'DELETE' });
            // Token will be removed via WebSocket
        } catch (error) {
            this.addLog('error', `Failed to delete token: ${error.message}`);
        }
    }

    // Layer Management
    async addLayer() {
        const name = document.getElementById('layer-name').value.trim();
        const layerType = document.getElementById('layer-type').value;
        const inputSize = parseInt(document.getElementById('layer-input-size').value);
        const outputSize = parseInt(document.getElementById('layer-output-size').value);
        const activation = document.getElementById('layer-activation').value;
        
        if (!name || !inputSize || !outputSize) {
            this.addLog('warning', 'Please fill all layer fields');
            return;
        }
        
        const order = this.layers.length + 1;
        
        try {
            const response = await fetch(`${this.baseUrl}/api/layers`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name,
                    layer_type: layerType,
                    input_size: inputSize,
                    output_size: outputSize,
                    activation,
                    order
                })
            });
            
            if (response.ok) {
                document.getElementById('layer-name').value = '';
                document.getElementById('layer-input-size').value = '';
                document.getElementById('layer-output-size').value = '';
                // Layer will be added via WebSocket
            }
        } catch (error) {
            this.addLog('error', `Failed to add layer: ${error.message}`);
        }
    }

    async loadLayers() {
        try {
            const response = await fetch(`${this.baseUrl}/api/layers`);
            this.layers = await response.json();
            this.renderLayers();
            this.updateHeadLayerOptions();
        } catch (error) {
            this.addLog('error', `Failed to load layers: ${error.message}`);
        }
    }

    renderLayers() {
        const container = document.getElementById('layers-list');
        
        container.innerHTML = this.layers.map(layer => `
            <div class="sortable-item bg-white p-3 rounded border hover:shadow-md transition-shadow" data-layer-id="${layer.id}">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                        <div class="flex items-center space-x-1">
                            <i class="fas fa-grip-vertical text-gray-400"></i>
                            <span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">${layer.order}</span>
                        </div>
                        <div>
                            <div class="font-medium text-sm">${layer.name}</div>
                            <div class="text-xs text-gray-500">${layer.layer_type} | ${layer.input_size} → ${layer.output_size} | ${layer.activation}</div>
                        </div>
                    </div>
                    <div class="flex items-center space-x-2">
                        <button onclick="app.moveLayer(${layer.id}, 'up')" class="text-green-500 hover:text-green-700">
                            <i class="fas fa-arrow-up text-xs"></i>
                        </button>
                        <button onclick="app.moveLayer(${layer.id}, 'down')" class="text-blue-500 hover:text-blue-700">
                            <i class="fas fa-arrow-down text-xs"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    updateHeadLayerOptions() {
        const select = document.getElementById('head-layer');
        select.innerHTML = '<option value="">Select Layer</option>' + 
            this.layers.map(layer => `<option value="${layer.id}">${layer.name}</option>`).join('');
    }

    async moveLayer(layerId, direction) {
        const layer = this.layers.find(l => l.id === layerId);
        if (!layer) return;
        
        const newOrder = direction === 'up' ? layer.order - 1 : layer.order + 1;
        if (newOrder < 1 || newOrder > this.layers.length) return;
        
        try {
            await fetch(`${this.baseUrl}/api/layers/${layerId}/order`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ order: newOrder })
            });
            
            // Update order locally and re-render
            const otherLayer = this.layers.find(l => l.order === newOrder);
            if (otherLayer) {
                otherLayer.order = layer.order;
            }
            layer.order = newOrder;
            
            this.layers.sort((a, b) => a.order - b.order);
            this.renderLayers();
        } catch (error) {
            this.addLog('error', `Failed to move layer: ${error.message}`);
        }
    }

    // Head Management
    async addHead() {
        const name = document.getElementById('head-name').value.trim();
        const layerId = parseInt(document.getElementById('head-layer').value);
        const headType = document.getElementById('head-type').value;
        const lossFunction = document.getElementById('head-loss').value;
        
        if (!name || !layerId) {
            this.addLog('warning', 'Please fill all head fields');
            return;
        }
        
        const order = this.heads.length + 1;
        
        try {
            const response = await fetch(`${this.baseUrl}/api/heads`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name,
                    layer_id: layerId,
                    head_type: headType,
                    order,
                    loss_function: lossFunction
                })
            });
            
            if (response.ok) {
                document.getElementById('head-name').value = '';
                document.getElementById('head-layer').value = '';
                // Head will be added via WebSocket
            }
        } catch (error) {
            this.addLog('error', `Failed to add head: ${error.message}`);
        }
    }

    async loadHeads() {
        try {
            const response = await fetch(`${this.baseUrl}/api/heads`);
            this.heads = await response.json();
            this.renderHeads();
        } catch (error) {
            this.addLog('error', `Failed to load heads: ${error.message}`);
        }
    }

    renderHeads() {
        const container = document.getElementById('heads-list');
        
        container.innerHTML = this.heads.map(head => {
            const layer = this.layers.find(l => l.id === head.layer_id);
            return `
                <div class="bg-white p-3 rounded border">
                    <div class="flex justify-between items-start">
                        <div>
                            <div class="font-medium text-sm">${head.name}</div>
                            <div class="text-xs text-gray-500 mt-1">
                                ${head.head_type} | ${layer ? layer.name : 'Unknown Layer'} | ${head.loss_function}
                            </div>
                        </div>
                        <span class="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full">${head.order}</span>
                    </div>
                </div>
            `;
        }).join('');
    }

    // Model Creation
    async createModel() {
        if (this.layers.length === 0) {
            this.addLog('warning', 'Please add at least one layer before creating a model');
            return;
        }
        
        const modelName = prompt('Enter model name:');
        if (!modelName) return;
        
        try {
            const config = {
                name: modelName,
                layers: this.layers,
                heads: this.heads,
                tokens: this.tokens
            };
            
            const response = await fetch(`${this.baseUrl}/api/models/create`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            
            if (response.ok) {
                const result = await response.json();
                this.addLog('info', result.message);
            }
        } catch (error) {
            this.addLog('error', `Failed to create model: ${error.message}`);
        }
    }

    // Dataset Management
    setupDatasetTypeChanger() {
        this.updateDatasetCreator();
    }

    updateDatasetCreator() {
        const type = document.getElementById('dataset-type').value;
        const container = document.getElementById('dataset-creator');
        
        const creators = {
            binary_classification: this.createBinaryClassificationForm(),
            multi_classification: this.createMultiClassificationForm(),
            qa: this.createQAForm(),
            article_approximation: this.createArticleForm(),
            regression: this.createRegressionForm(),
            text_generation: this.createTextGenerationForm()
        };
        
        container.innerHTML = creators[type] || '';
    }

    createBinaryClassificationForm() {
        return `
            <div class="space-y-3">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Sample Input</label>
                    <textarea id="binary-input" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm" rows="2" placeholder="Enter sample input"></textarea>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Label (0 or 1)</label>
                    <select id="binary-label" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm">
                        <option value="0">0 (Negative)</option>
                        <option value="1">1 (Positive)</option>
                    </select>
                </div>
                <div id="binary-samples" class="max-h-32 overflow-y-auto border border-gray-200 rounded-md p-2">
                    <!-- Samples will be added here -->
                </div>
                <button type="button" onclick="app.addDatasetSample()" class="w-full bg-blue-500 text-white py-1 px-3 rounded-md hover:bg-blue-600 text-sm">
                    Add Sample
                </button>
            </div>
        `;
    }

    createMultiClassificationForm() {
        return `
            <div class="space-y-3">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Sample Input</label>
                    <textarea id="multi-input" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm" rows="2" placeholder="Enter sample input"></textarea>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Class Label</label>
                    <input type="text" id="multi-label" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm" placeholder="Enter class name">
                </div>
                <div id="multi-samples" class="max-h-32 overflow-y-auto border border-gray-200 rounded-md p-2">
                    <!-- Samples will be added here -->
                </div>
                <button type="button" onclick="app.addDatasetSample()" class="w-full bg-blue-500 text-white py-1 px-3 rounded-md hover:bg-blue-600 text-sm">
                    Add Sample
                </button>
            </div>
        `;
    }

    createQAForm() {
        return `
            <div class="space-y-3">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Question</label>
                    <textarea id="qa-question" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm" rows="2" placeholder="Enter question"></textarea>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Answer</label>
                    <textarea id="qa-answer" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm" rows="2" placeholder="Enter answer"></textarea>
                </div>
                <div id="qa-samples" class="max-h-32 overflow-y-auto border border-gray-200 rounded-md p-2">
                    <!-- Samples will be added here -->
                </div>
                <button type="button" onclick="app.addDatasetSample()" class="w-full bg-blue-500 text-white py-1 px-3 rounded-md hover:bg-blue-600 text-sm">
                    Add Q&A Pair
                </button>
            </div>
        `;
    }

    createArticleForm() {
        return `
            <div class="space-y-3">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Article Text</label>
                    <textarea id="article-text" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm" rows="4" placeholder="Enter article text"></textarea>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Summary/Approximation</label>
                    <textarea id="article-summary" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm" rows="2" placeholder="Enter summary"></textarea>
                </div>
                <div id="article-samples" class="max-h-32 overflow-y-auto border border-gray-200 rounded-md p-2">
                    <!-- Samples will be added here -->
                </div>
                <button type="button" onclick="app.addDatasetSample()" class="w-full bg-blue-500 text-white py-1 px-3 rounded-md hover:bg-blue-600 text-sm">
                    Add Article
                </button>
            </div>
        `;
    }

    createRegressionForm() {
        return `
            <div class="space-y-3">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Input Features (comma-separated)</label>
                    <input type="text" id="regression-input" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm" placeholder="1.5, 2.3, 0.8">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Target Value</label>
                    <input type="number" step="any" id="regression-target" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm" placeholder="3.14">
                </div>
                <div id="regression-samples" class="max-h-32 overflow-y-auto border border-gray-200 rounded-md p-2">
                    <!-- Samples will be added here -->
                </div>
                <button type="button" onclick="app.addDatasetSample()" class="w-full bg-blue-500 text-white py-1 px-3 rounded-md hover:bg-blue-600 text-sm">
                    Add Sample
                </button>
            </div>
        `;
    }

    createTextGenerationForm() {
        return `
            <div class="space-y-3">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Input Text</label>
                    <textarea id="text-input" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm" rows="2" placeholder="Enter input text"></textarea>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Target Text</label>
                    <textarea id="text-target" class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm" rows="2" placeholder="Enter target text"></textarea>
                </div>
                <div id="text-samples" class="max-h-32 overflow-y-auto border border-gray-200 rounded-md p-2">
                    <!-- Samples will be added here -->
                </div>
                <button type="button" onclick="app.addDatasetSample()" class="w-full bg-blue-500 text-white py-1 px-3 rounded-md hover:bg-blue-600 text-sm">
                    Add Text Pair
                </button>
            </div>
        `;
    }

    addDatasetSample() {
        const type = document.getElementById('dataset-type').value;
        const methods = {
            binary_classification: () => this.addBinarySample(),
            multi_classification: () => this.addMultiSample(),
            qa: () => this.addQASample(),
            article_approximation: () => this.addArticleSample(),
            regression: () => this.addRegressionSample(),
            text_generation: () => this.addTextSample()
        };
        
        if (methods[type]) {
            methods[type]();
        }
    }

    addBinarySample() {
        const input = document.getElementById('binary-input').value.trim();
        const label = document.getElementById('binary-label').value;
        
        if (!input) return;
        
        const container = document.getElementById('binary-samples');
        const sampleDiv = document.createElement('div');
        sampleDiv.className = 'flex justify-between items-center p-2 bg-gray-50 rounded mb-1';
        sampleDiv.innerHTML = `
            <div class="text-sm">
                <span class="font-mono">${input}</span> → <span class="font-bold">${label}</span>
            </div>
            <button onclick="this.parentElement.remove()" class="text-red-500 hover:text-red-700">
                <i class="fas fa-times text-xs"></i>
            </button>
        `;
        container.appendChild(sampleDiv);
        
        document.getElementById('binary-input').value = '';
    }

    addMultiSample() {
        const input = document.getElementById('multi-input').value.trim();
        const label = document.getElementById('multi-label').value.trim();
        
        if (!input || !label) return;
        
        const container = document.getElementById('multi-samples');
        const sampleDiv = document.createElement('div');
        sampleDiv.className = 'flex justify-between items-center p-2 bg-gray-50 rounded mb-1';
        sampleDiv.innerHTML = `
            <div class="text-sm">
                <span class="font-mono">${input}</span> → <span class="font-bold">${label}</span>
            </div>
            <button onclick="this.parentElement.remove()" class="text-red-500 hover:text-red-700">
                <i class="fas fa-times text-xs"></i>
            </button>
        `;
        container.appendChild(sampleDiv);
        
        document.getElementById('multi-input').value = '';
        document.getElementById('multi-label').value = '';
    }

    addQASample() {
        const question = document.getElementById('qa-question').value.trim();
        const answer = document.getElementById('qa-answer').value.trim();
        
        if (!question || !answer) return;
        
        const container = document.getElementById('qa-samples');
        const sampleDiv = document.createElement('div');
        sampleDiv.className = 'p-2 bg-gray-50 rounded mb-1';
        sampleDiv.innerHTML = `
            <div class="flex justify-between items-start">
                <div class="text-sm flex-1">
                    <div><strong>Q:</strong> ${question}</div>
                    <div><strong>A:</strong> ${answer}</div>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" class="text-red-500 hover:text-red-700 ml-2">
                    <i class="fas fa-times text-xs"></i>
                </button>
            </div>
        `;
        container.appendChild(sampleDiv);
        
        document.getElementById('qa-question').value = '';
        document.getElementById('qa-answer').value = '';
    }

    addArticleSample() {
        const text = document.getElementById('article-text').value.trim();
        const summary = document.getElementById('article-summary').value.trim();
        
        if (!text || !summary) return;
        
        const container = document.getElementById('article-samples');
        const sampleDiv = document.createElement('div');
        sampleDiv.className = 'p-2 bg-gray-50 rounded mb-1';
        sampleDiv.innerHTML = `
            <div class="flex justify-between items-start">
                <div class="text-sm flex-1">
                    <div><strong>Article:</strong> ${text.substring(0, 100)}${text.length > 100 ? '...' : ''}</div>
                    <div><strong>Summary:</strong> ${summary}</div>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" class="text-red-500 hover:text-red-700 ml-2">
                    <i class="fas fa-times text-xs"></i>
                </button>
            </div>
        `;
        container.appendChild(sampleDiv);
        
        document.getElementById('article-text').value = '';
        document.getElementById('article-summary').value = '';
    }

    addRegressionSample() {
        const input = document.getElementById('regression-input').value.trim();
        const target = document.getElementById('regression-target').value;
        
        if (!input || !target) return;
        
        const container = document.getElementById('regression-samples');
        const sampleDiv = document.createElement('div');
        sampleDiv.className = 'flex justify-between items-center p-2 bg-gray-50 rounded mb-1';
        sampleDiv.innerHTML = `
            <div class="text-sm">
                <span class="font-mono">[${input}]</span> → <span class="font-bold">${target}</span>
            </div>
            <button onclick="this.parentElement.remove()" class="text-red-500 hover:text-red-700">
                <i class="fas fa-times text-xs"></i>
            </button>
        `;
        container.appendChild(sampleDiv);
        
        document.getElementById('regression-input').value = '';
        document.getElementById('regression-target').value = '';
    }

    addTextSample() {
        const input = document.getElementById('text-input').value.trim();
        const target = document.getElementById('text-target').value.trim();
        
        if (!input || !target) return;
        
        const container = document.getElementById('text-samples');
        const sampleDiv = document.createElement('div');
        sampleDiv.className = 'p-2 bg-gray-50 rounded mb-1';
        sampleDiv.innerHTML = `
            <div class="flex justify-between items-start">
                <div class="text-sm flex-1">
                    <div><strong>Input:</strong> ${input}</div>
                    <div><strong>Target:</strong> ${target}</div>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" class="text-red-500 hover:text-red-700 ml-2">
                    <i class="fas fa-times text-xs"></i>
                </button>
            </div>
        `;
        container.appendChild(sampleDiv);
        
        document.getElementById('text-input').value = '';
        document.getElementById('text-target').value = '';
    }

    async createDataset() {
        const name = document.getElementById('dataset-name').value.trim();
        const type = document.getElementById('dataset-type').value;
        
        if (!name) {
            this.addLog('warning', 'Please enter a dataset name');
            return;
        }
        
        const data = this.collectDatasetSamples(type);
        
        if (data.length === 0) {
            this.addLog('warning', 'Please add at least one sample to the dataset');
            return;
        }
        
        try {
            const response = await fetch(`${this.baseUrl}/api/datasets`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name,
                    dataset_type: type,
                    data
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                this.addLog('info', `Dataset '${name}' created with ${data.length} samples`);
                document.getElementById('dataset-name').value = '';
                this.clearDatasetSamples(type);
                this.loadDatasets();
            }
        } catch (error) {
            this.addLog('error', `Failed to create dataset: ${error.message}`);
        }
    }

    collectDatasetSamples(type) {
        const containerIds = {
            binary_classification: 'binary-samples',
            multi_classification: 'multi-samples',
            qa: 'qa-samples',
            article_approximation: 'article-samples',
            regression: 'regression-samples',
            text_generation: 'text-samples'
        };
        
        const container = document.getElementById(containerIds[type]);
        if (!container) return [];
        
        // This is a simplified extraction - in a real implementation,
        // you'd want to store the actual data structure rather than parsing HTML
        return Array.from(container.children).map((child, index) => ({
            id: index,
            content: child.textContent.trim()
        }));
    }

    clearDatasetSamples(type) {
        const containerIds = {
            binary_classification: 'binary-samples',
            multi_classification: 'multi-samples',
            qa: 'qa-samples',
            article_approximation: 'article-samples',
            regression: 'regression-samples',
            text_generation: 'text-samples'
        };
        
        const container = document.getElementById(containerIds[type]);
        if (container) {
            container.innerHTML = '';
        }
    }

    async loadDatasets() {
        try {
            const response = await fetch(`${this.baseUrl}/api/datasets`);
            this.datasets = await response.json();
            this.renderDatasets();
        } catch (error) {
            this.addLog('error', `Failed to load datasets: ${error.message}`);
        }
    }

    renderDatasets() {
        const container = document.getElementById('datasets-list');
        
        container.innerHTML = this.datasets.map(dataset => `
            <div class="bg-white p-4 rounded border hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start mb-2">
                    <h4 class="font-medium">${dataset.name}</h4>
                    <span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">${dataset.dataset_type}</span>
                </div>
                <div class="text-sm text-gray-600">
                    ${dataset.data.length} samples
                </div>
                <div class="mt-2 flex space-x-2">
                    <button onclick="app.viewDataset(${dataset.id})" class="bg-blue-500 text-white px-2 py-1 rounded text-xs hover:bg-blue-600">
                        View
                    </button>
                    <button onclick="app.deleteDataset(${dataset.id})" class="bg-red-500 text-white px-2 py-1 rounded text-xs hover:bg-red-600">
                        Delete
                    </button>
                </div>
            </div>
        `).join('');
    }

    viewDataset(datasetId) {
        const dataset = this.datasets.find(d => d.id === datasetId);
        if (dataset) {
            alert(`Dataset: ${dataset.name}\nType: ${dataset.dataset_type}\nSamples: ${dataset.data.length}\n\nFirst few samples:\n${JSON.stringify(dataset.data.slice(0, 3), null, 2)}`);
        }
    }

    async deleteDataset(datasetId) {
        if (!confirm('Are you sure you want to delete this dataset?')) return;
        
        try {
            const response = await fetch(`${this.baseUrl}/api/datasets/${datasetId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.datasets = this.datasets.filter(d => d.id !== datasetId);
                this.renderDatasets();
                this.addLog('info', 'Dataset deleted successfully');
            }
        } catch (error) {
            this.addLog('error', `Failed to delete dataset: ${error.message}`);
        }
    }

    // Monitoring
    async loadModels() {
        // This would load available models from the backend
        // For now, we'll update the model select dropdown
        const select = document.getElementById('model-select');
        select.innerHTML = '<option value="">Select Model</option>';
        
        // Add any active models
        Object.keys(this.models).forEach(modelName => {
            const option = document.createElement('option');
            option.value = modelName;
            option.textContent = modelName;
            select.appendChild(option);
        });
    }

    async refreshWeights() {
        const modelName = document.getElementById('model-select').value;
        if (!modelName) {
            this.addLog('warning', 'Please select a model first');
            return;
        }
        
        try {
            const response = await fetch(`${this.baseUrl}/api/models/${modelName}/weights`);
            const weights = await response.json();
            this.renderWeights(weights);
        } catch (error) {
            this.addLog('error', `Failed to load weights: ${error.message}`);
        }
    }

    renderWeights(weights) {
        const tbody = document.getElementById('weights-table-body');
        
        tbody.innerHTML = Object.entries(weights).map(([name, data]) => `
            <tr class="hover:bg-gray-50">
                <td class="px-4 py-2 weight-cell font-semibold">${name}</td>
                <td class="px-4 py-2 weight-cell">[${data.shape.join(', ')}]</td>
                <td class="px-4 py-2 weight-cell">${data.mean.toFixed(6)}</td>
                <td class="px-4 py-2 weight-cell">${data.std.toFixed(6)}</td>
                <td class="px-4 py-2 weight-cell">${data.min.toFixed(6)}</td>
                <td class="px-4 py-2 weight-cell">${data.max.toFixed(6)}</td>
            </tr>
        `).join('');
    }

    // Logging
    addLog(type, message, modelName = 'system') {
        const timestamp = new Date().toLocaleTimeString();
        const log = {
            timestamp,
            type,
            message,
            model_name: modelName
        };
        
        this.logs.unshift(log);
        
        // Keep only last 1000 logs
        if (this.logs.length > 1000) {
            this.logs = this.logs.slice(0, 1000);
        }
        
        this.renderLogs();
    }

    async loadLogs() {
        try {
            const response = await fetch(`${this.baseUrl}/api/logs?limit=100`);
            const logs = await response.json();
            this.logs = logs;
            this.renderLogs();
        } catch (error) {
            console.error('Failed to load logs:', error);
        }
    }

    renderLogs() {
        const container = document.getElementById('logs-container');
        const filter = document.getElementById('log-filter').value;
        
        let filteredLogs = this.logs;
        if (filter) {
            filteredLogs = this.logs.filter(log => log.log_type === filter);
        }
        
        if (this.logsHidden) {
            // Hide "spammy" logs (frequent info logs)
            filteredLogs = filteredLogs.filter(log => 
                log.log_type !== 'info' || 
                !log.message.includes('Token') && 
                !log.message.includes('Layer') && 
                !log.message.includes('Head')
            );
        }
        
        container.innerHTML = filteredLogs.slice(0, 100).map(log => {
            const typeColor = {
                info: 'text-green-400',
                warning: 'text-yellow-400',
                error: 'text-red-400',
                training: 'text-blue-400'
            }[log.log_type] || 'text-gray-400';
            
            return `
                <div class="mb-1">
                    <span class="text-gray-500">[${log.timestamp || log.timestamp}]</span>
                    <span class="${typeColor}">[${log.log_type?.toUpperCase() || 'INFO'}]</span>
                    <span class="text-purple-400">[${log.model_name}]</span>
                    <span class="text-white">${log.message}</span>
                </div>
            `;
        }).join('');
        
        // Auto-scroll to bottom
        container.scrollTop = container.scrollHeight;
    }

    toggleLogs() {
        this.logsHidden = !this.logsHidden;
        const btn = document.getElementById('toggle-logs-btn');
        
        if (this.logsHidden) {
            btn.innerHTML = '<i class="fas fa-eye mr-1"></i>Show All';
            btn.classList.remove('bg-yellow-600', 'hover:bg-yellow-700');
            btn.classList.add('bg-green-600', 'hover:bg-green-700');
        } else {
            btn.innerHTML = '<i class="fas fa-eye-slash mr-1"></i>Hide Spammy';
            btn.classList.remove('bg-green-600', 'hover:bg-green-700');
            btn.classList.add('bg-yellow-600', 'hover:bg-yellow-700');
        }
        
        this.renderLogs();
    }

    clearLogs() {
        if (confirm('Are you sure you want to clear all logs?')) {
            this.logs = [];
            this.renderLogs();
        }
    }
}

// Initialize the application
const app = new NeuralNetworkBackend(); 