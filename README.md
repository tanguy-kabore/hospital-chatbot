# Hospital Chatbot 

Un chatbot intelligent pour gérer les informations hospitalières, utilisant FastAPI, React, et l'IA générative.

## Aperçu du Projet

### Page d'accueil
![Page d'accueil](./assets/Page%20d'accueil.PNG)
*La page d'accueil montre des exemples de questions pour aider les utilisateurs à démarrer*

### Exemple de Conversation
![Exemple de chat](./assets/Exemple%20de%20chat.PNG)
*Un exemple de conversation avec le chatbot montrant ses capacités de réponse*

## Fonctionnalités

-  **Chatbot Intelligent**: Utilise l'IA générative pour des réponses naturelles et contextuelles
-  **Données Hospitalières**: Gère les informations sur les hôpitaux, médecins, et patients
-  **Interface Conviviale**: Interface utilisateur moderne et responsive
-  **Suggestions de Questions**: Exemples de questions pour guider les utilisateurs
-  **Gestion des Données**: Traitement efficace des données depuis des fichiers CSV

## Architecture Technique

### Backend (FastAPI)
- FastAPI pour l'API REST
- LangChain pour le traitement du langage naturel
- FAISS pour la recherche vectorielle
- Pandas pour la manipulation des données
- Google Gemini pour la génération de réponses

### Frontend (React)
- React avec TypeScript
- Chakra UI pour l'interface utilisateur
- Gestion d'état avec React Hooks
- Communication asynchrone avec l'API

## Installation

1. **Cloner le projet**
```bash
git clone https://github.com/tanguy-kabore/hospital-chatbot.git
cd hospital-chatbot
```

2. **Configuration du Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # ou `venv\Scripts\activate` sur Windows
pip install -r requirements.txt
```

3. **Configuration du Frontend**
```bash
cd frontend
npm install
```

4. **Variables d'Environnement**
Créer un fichier `.env` dans le dossier backend :
```env
GOOGLE_API_KEY=votre_clé_api_google
```

## Démarrage

1. **Lancer le Backend**
```bash
cd backend
python -m uvicorn main:app --reload
```

2. **Lancer le Frontend**
```bash
cd frontend
npm start
```

## Utilisation

1. Ouvrez votre navigateur et accédez à `http://localhost:3000`
2. Vous verrez des exemples de questions que vous pouvez poser
3. Cliquez sur une question suggérée ou tapez votre propre question
4. Le chatbot répondra avec les informations pertinentes basées sur les données hospitalières

## Structure des Données

Le système utilise plusieurs fichiers CSV pour stocker les données :
- `hospitals.csv`: Informations sur les hôpitaux
- `physicians.csv`: Données des médecins
- `patients.csv`: Informations des patients
- `visits.csv`: Historique des visites
- `reviews.csv`: Avis des patients
- `payers.csv`: Informations sur les assureurs
