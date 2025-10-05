# 🚀 AI Stock Trading Dashboard - Makefile
# Commandes simplifiées pour un workflow professionnel

.PHONY: help install run test clean backup update lint format

# Variables
PYTHON = python3
VENV = venv
PIP = $(VENV)/bin/pip
STREAMLIT = $(VENV)/bin/streamlit

# Couleurs pour output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

##@ Aide

help: ## Afficher cette aide
	@echo "╔═══════════════════════════════════════════════════════════╗"
	@echo "║                                                           ║"
	@echo "║         💎 AI STOCK TRADING DASHBOARD 💎                 ║"
	@echo "║                                                           ║"
	@echo "╚═══════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "📋 Commandes disponibles:"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(BLUE)%-15s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Installation & Setup

install: ## Installation complète (première utilisation)
	@echo "$(GREEN)📦 Installation de l'environnement...$(NC)"
	@$(PYTHON) -m venv $(VENV)
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@mkdir -p data logs
	@echo "$(GREEN)✅ Installation terminée!$(NC)"
	@echo "$(BLUE)Utilisez 'make run' pour démarrer$(NC)"

setup: install ## Alias pour install

##@ Lancement

run: ## Lancer le dashboard (mode principal)
	@echo "$(GREEN)🚀 Lancement du dashboard...$(NC)"
	@./run.sh

dashboard: ## Lancer directement Streamlit
	@echo "$(GREEN)📊 Lancement Streamlit...$(NC)"
	@$(STREAMLIT) run app.py --server.port=8501

scanner: ## Lancer le scanner de trading
	@echo "$(GREEN)🔍 Lancement du scanner...$(NC)"
	@$(STREAMLIT) run trading_dashboard.py --server.port=8502

##@ Automation

daily-update: ## Mise à jour quotidienne des données
	@echo "$(GREEN)📈 Mise à jour des données...$(NC)"
	@$(VENV)/bin/python scripts/daily_update.py

monitor: ## Monitoring temps réel
	@echo "$(GREEN)⚡ Démarrage monitoring...$(NC)"
	@$(VENV)/bin/python scripts/realtime_monitor.py

auto-scan: ## Scan automatique des opportunités
	@echo "$(GREEN)🤖 Scan automatique...$(NC)"
	@$(VENV)/bin/python scripts/auto_scan_opportunities.py

##@ Maintenance

backup: ## Backup de la base de données
	@echo "$(GREEN)💾 Backup en cours...$(NC)"
	@$(VENV)/bin/python scripts/backup_database.py
	@echo "$(GREEN)✅ Backup terminé!$(NC)"

clean: ## Nettoyer les fichiers temporaires
	@echo "$(YELLOW)🧹 Nettoyage...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name ".DS_Store" -delete
	@rm -rf .pytest_cache
	@echo "$(GREEN)✅ Nettoyage terminé!$(NC)"

clean-all: clean ## Nettoyer tout (inclut venv)
	@echo "$(RED)⚠️  Suppression de l'environnement virtuel...$(NC)"
	@rm -rf $(VENV)
	@echo "$(GREEN)✅ Nettoyage complet terminé!$(NC)"

update: ## Mettre à jour les dépendances
	@echo "$(GREEN)🔄 Mise à jour des dépendances...$(NC)"
	@$(PIP) install --upgrade pip
	@$(PIP) install --upgrade -r requirements.txt
	@echo "$(GREEN)✅ Mise à jour terminée!$(NC)"

##@ Développement

test: ## Lancer les tests
	@echo "$(GREEN)🧪 Lancement des tests...$(NC)"
	@$(VENV)/bin/python test_system.py

lint: ## Vérifier le code (linting)
	@echo "$(GREEN)🔍 Linting du code...$(NC)"
	@$(PIP) install flake8 pylint 2>/dev/null || true
	@$(VENV)/bin/flake8 modules/ --max-line-length=120 --exclude=__pycache__ || true
	@$(VENV)/bin/pylint modules/*.py --disable=C0111,R0913,R0914 || true

format: ## Formatter le code
	@echo "$(GREEN)✨ Formatage du code...$(NC)"
	@$(PIP) install black isort 2>/dev/null || true
	@$(VENV)/bin/black modules/ scripts/ --line-length=120 || true
	@$(VENV)/bin/isort modules/ scripts/ || true
	@echo "$(GREEN)✅ Formatage terminé!$(NC)"

##@ Informations

status: ## Afficher le statut du système
	@echo "$(BLUE)📊 Statut du système:$(NC)"
	@echo ""
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Venv: $(shell [ -d $(VENV) ] && echo '✅ Installé' || echo '❌ Non installé')"
	@echo "Database: $(shell [ -f data/stock_data.db ] && echo '✅ Trouvée' || echo '❌ Non trouvée')"
	@echo "Config: $(shell [ -f config.yaml ] && echo '✅ Trouvé' || echo '❌ Non trouvé')"
	@echo "Modules: $(shell ls -1 modules/*.py | wc -l | xargs) fichiers"
	@echo "Scripts: $(shell ls -1 scripts/*.py | wc -l | xargs) fichiers"

info: status ## Alias pour status

##@ Docker (Unraid-ready)

docker-build: ## Construire l'image Docker
	@echo "$(GREEN)🐳 Construction de l'image Docker...$(NC)"
	@docker build -t ai-stock-dashboard:latest .
	@echo "$(GREEN)✅ Image construite!$(NC)"

docker-run: ## Lancer le container Docker
	@echo "$(GREEN)🐳 Lancement du container...$(NC)"
	@docker run -d \
		--name stock-dashboard \
		-p 8501:8501 \
		-v $(PWD)/data:/app/data \
		-v $(PWD)/logs:/app/logs \
		--restart unless-stopped \
		ai-stock-dashboard:latest
	@echo "$(GREEN)✅ Container démarré!$(NC)"
	@echo "$(BLUE)Dashboard: http://localhost:8501$(NC)"

docker-stop: ## Arrêter le container Docker
	@docker stop stock-dashboard
	@docker rm stock-dashboard

##@ Raccourcis

quick-start: install run ## Installation + lancement (première fois)

dev: clean lint format test ## Workflow développeur complet
