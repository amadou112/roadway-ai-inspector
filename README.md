Roadway Construction RAG Assistant

https://next-app-mauve-nu.vercel.app/

An AI-powered engineering assistant that helps transportation professionals quickly access roadway design standards, construction specifications, inspection requirements, and best practices using Retrieval-Augmented Generation (RAG).

Overview

The Roadway Construction RAG Assistant is an enterprise AI application designed to assist civil engineers, construction inspectors, project managers, consultants, and transportation agencies by providing intelligent, context-aware answers from roadway engineering documentation.

Instead of manually searching through hundreds of pages of engineering manuals and specifications, users can simply ask questions in natural language and receive accurate, source-grounded responses in seconds.

This project demonstrates how modern Artificial Intelligence can improve engineering productivity, knowledge management, and decision-making within transportation infrastructure projects.

Business Problem

Transportation agencies and engineering firms rely on thousands of pages of documentation, including:

Roadway Design Manuals
Construction Specifications
Standard Drawings
Inspection Procedures
Materials Specifications
Safety Regulations
Traffic Control Standards
FHWA Guidance
DOT Manuals
Project Documentation

Finding the correct information can be time-consuming and may lead to inconsistent decisions or delays.

Solution

The Roadway Construction RAG Assistant centralizes engineering knowledge into a searchable AI-powered platform that enables users to:

Ask engineering questions in plain English
Search across multiple engineering documents simultaneously
Receive AI-generated answers grounded in official documentation
Quickly locate relevant specification sections
Improve engineering decision making
Reduce time spent searching manuals
Increase consistency across projects
Key Features
🤖 AI-powered engineering assistant
📄 Retrieval-Augmented Generation (RAG)
🔍 Semantic document search
💬 Natural language question answering
📚 Engineering knowledge base
📑 PDF document ingestion
🧠 Context-aware AI responses
📊 Engineering document management
🔐 Secure user authentication
📈 Executive dashboard
📱 Responsive web interface
Example Questions
What is the minimum pavement thickness for this roadway classification?
What are the FHWA requirements for guardrail installation?
Explain the requirements for concrete curing.
What traffic control devices are required during lane closures?
What are the compaction requirements for subgrade?
How should asphalt density testing be performed?
What inspection items are required before paving begins?
Which specification section discusses bridge expansion joints?
Architecture
                    Users
                      │
                      ▼
           Next.js Web Application
                      │
                      ▼
          FastAPI REST Backend
                      │
      ┌───────────────┴───────────────┐
      ▼                               ▼
 Authentication                  Prompt Processing
      │                               │
      └───────────────┬───────────────┘
                      ▼
              OpenAI GPT-5.5
                      │
                      ▼
              LangChain Pipeline
                      │
                      ▼
           ChromaDB Vector Database
                      │
                      ▼
     Engineering Documents (PDFs)
                      │
                      ▼
     AI Grounded Response Generation
Technology Stack
Frontend
Next.js
React
TypeScript
Tailwind CSS
Backend
FastAPI
Python
Artificial Intelligence
OpenAI GPT-5.5
LangChain
Retrieval-Augmented Generation (RAG)
Vector Embeddings
Database
PostgreSQL
ChromaDB (Vector Database)
Authentication
OAuth2
JWT
Deployment
Docker
Docker Compose
Nginx
Hostinger VPS
Engineering Knowledge Sources

The platform can be configured to ingest documentation such as:

FHWA Manuals
State DOT Construction Specifications
State DOT Design Manuals
AASHTO Guidance
MUTCD
Standard Drawings
Project Specifications
Engineering Reports
Construction Inspection Manuals
Quality Assurance Documentation
Business Value
Faster access to engineering information
Reduced manual document searching
Improved project consistency
Better engineering decisions
Increased inspector productivity
Faster onboarding of new engineers
Improved knowledge retention
Enhanced collaboration across teams
Reduced project risk
AI-enabled engineering support
Future Enhancements
AI-powered roadway defect detection
Drone image analysis
GIS integration
Construction schedule analysis
Voice-enabled engineering assistant
Mobile inspection application
Multi-agent engineering workflows
Automated specification compliance checking
Risk prediction analytics
Digital engineering knowledge management
Portfolio Project

This project is part of the Sidibe Enterprises AI Engineering Portfolio, demonstrating enterprise AI, Retrieval-Augmented Generation (RAG), modern web development, and intelligent knowledge management for transportation infrastructure.

License

This repository is intended for educational, research, and portfolio demonstration purposes.

Author

Amadou Sidibe, MBA, PMP, CSM, SPC
AI Technical Program Manager | Enterprise AI Solutions | Civil Engineer

