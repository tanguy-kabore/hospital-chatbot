from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import pandas as pd
import os
import logging
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

# Configuration de l'API Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")
genai.configure(api_key=api_key)

# Initialisation de FastAPI
app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[Dict]] = None

# Chargement et préparation des données
def load_and_process_data():
    """Charge et traite les données depuis les fichiers CSV"""
    try:
        data_path = "data"
        data = {
            'hospitals': pd.read_csv(f"{data_path}/hospitals.csv"),
            'physicians': pd.read_csv(f"{data_path}/physicians.csv"),
            'patients': pd.read_csv(f"{data_path}/patients.csv"),
            'visits': pd.read_csv(f"{data_path}/visits.csv"),
            'payers': pd.read_csv(f"{data_path}/payers.csv"),
            'reviews': pd.read_csv(f"{data_path}/reviews.csv")
        }
        
        documents = []
        
        # Traitement des hôpitaux
        for _, hospital in data['hospitals'].iterrows():
            doc = {
                'content': f"L'hôpital {hospital['hospital_name']} est situé dans l'état de {hospital['hospital_state']}.",
                'metadata': {
                    'type': 'hospital',
                    'id': hospital['hospital_id'],
                    'name': hospital['hospital_name']
                }
            }
            documents.append(doc)
        
        # Traitement des médecins
        for _, physician in data['physicians'].iterrows():
            doc = {
                'content': f"Dr. {physician['physician_name']} a obtenu son diplôme de {physician['medical_school']} " + \
                          f"en {physician['physician_grad_year'][:4]}.",
                'metadata': {
                    'type': 'physician',
                    'id': physician['physician_id'],
                    'name': physician['physician_name']
                }
            }
            documents.append(doc)
        
        # Traitement des patients
        for _, patient in data['patients'].iterrows():
            birth_year = pd.to_datetime(patient['patient_dob']).year
            age = pd.Timestamp.now().year - birth_year
            
            doc = {
                'content': f"Patient(e) {patient['patient_name']}, {patient['patient_sex']}, " + \
                          f"né(e) en {birth_year} ({age} ans). Groupe sanguin: {patient['patient_blood_type']}",
                'metadata': {
                    'type': 'patient',
                    'id': patient['patient_id'],
                    'name': patient['patient_name']
                }
            }
            documents.append(doc)
        
        # Traitement des assureurs
        for _, payer in data['payers'].iterrows():
            doc = {
                'content': f"Assureur: {payer['payer_name']}",
                'metadata': {
                    'type': 'payer',
                    'id': payer['payer_id'],
                    'name': payer['payer_name']
                }
            }
            documents.append(doc)
        
        # Traitement des visites
        for _, visit in data['visits'].iterrows():
            content = f"Visite à l'hôpital le {visit['date_of_admission']}, type d'admission: {visit['admission_type']}"
            if pd.notna(visit['chief_complaint']) and pd.notna(visit['treatment_description']):
                content += f". Motif: {visit['chief_complaint']}. Traitement: {visit['treatment_description']}"
            if pd.notna(visit['discharge_date']):
                content += f". Date de sortie: {visit['discharge_date']}"
            content += f". Statut: {visit['visit_status']}"
            
            doc = {
                'content': content,
                'metadata': {
                    'type': 'visit',
                    'id': visit['visit_id'],
                    'hospital_id': visit['hospital_id'],
                    'physician_id': visit['physician_id']
                }
            }
            documents.append(doc)
        
        # Traitement des avis
        for _, review in data['reviews'].iterrows():
            doc = {
                'content': f"Avis sur l'hôpital {review['hospital_name']} par {review['patient_name']} concernant le Dr. {review['physician_name']}: {review['review']}",
                'metadata': {
                    'type': 'review',
                    'id': review['review_id'],
                    'hospital': review['hospital_name'],
                    'physician': review['physician_name']
                }
            }
            documents.append(doc)

        logger.info(f"Processed {len(documents)} documents")
        return documents
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise

# Configuration du text splitter pour le traitement des documents
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)

# Configuration des embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Chargement initial des documents
print("🏥 Chargement des données...")
documents = load_and_process_data()
print("✨ Données chargées avec succès!")

# Création de la base de données vectorielle
texts = [doc['content'] for doc in documents]
metadatas = [doc['metadata'] for doc in documents]
text_chunks = text_splitter.create_documents(texts, metadatas=metadatas)
vector_store = FAISS.from_documents(text_chunks, embeddings)

# Configuration du template de prompt
prompt_template = """Tu es un assistant hospitalier professionnel et empathique. Tu t'appelles Jane. Utilise le contexte suivant pour répondre à la question de manière naturelle et précise.

Contexte:
{context}

Question: {question}

Instructions:
1. Réponds de manière professionnelle et chaleureuse
2. Utilise uniquement les informations du contexte
3. Si tu n'as pas assez d'informations, dis-le poliment
4. Évite le jargon technique sauf si nécessaire
5. Personnalise la réponse en fonction du type de question

Réponse:"""

PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

# Mémoire de conversation
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

@app.post("/chat")
async def chat_endpoint(chat_message: ChatMessage):
    try:
        # Recherche des documents pertinents
        relevant_docs = vector_store.similarity_search(
            chat_message.message,
            k=5  # Nombre de documents à récupérer
        )
        
        # Préparation du contexte
        context = "\n".join([doc.page_content for doc in relevant_docs])
        
        # Création du prompt
        prompt = PROMPT.format(context=context, question=chat_message.message)
        
        # Génération de la réponse
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            raise HTTPException(status_code=500, detail="Failed to generate response")
        
        # Préparation des sources
        sources = [
            {
                "type": doc.metadata.get("type", "unknown"),
                "id": doc.metadata.get("id", "unknown"),
                "name": doc.metadata.get("name", "unknown")
            }
            for doc in relevant_docs
        ]
        
        return {
            "response": response.text,
            "sources": sources
        }
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🏥 Démarrage du serveur backend...")
    print("✨ Le serveur sera disponible sur http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
