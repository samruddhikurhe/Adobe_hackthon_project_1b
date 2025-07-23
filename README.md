Persona-Driven Document Intelligence
A semantic analysis pipeline that extracts and ranks the most relevant information from a collection of PDF documents based on a user's persona and objective.

This project was developed for the Adobe Hackathon (Round 1B). It intelligently processes multiple documents to provide a user with a prioritized and context-aware summary, enabling faster and more effective decision-making.

Table of Contents
How It Works

Tech Stack

Getting Started

Prerequisites

Installation

Running the Application

Step 1: Prepare Your Input

Step 2: Build the Docker Image

Step 3: Run the Docker Container

Project Structure

Configuration & Tuning

How It Works
The system operates as a sophisticated pipeline that emulates human-like document analysis.

Data Flow:

Input: The process starts with a collection of PDF documents and a query.json file that defines the user's persona and job_to_be_done.

Hierarchical Parsing (pdf_parser.py): Each PDF is analyzed to identify section headers based on font size and weight. All text between two headers is consolidated into a single, cohesive chunk of content. This preserves the full context of each section.

Query Enhancement (semantic_ranker.py): A simple query is not enough. The system creates a rich, descriptive search query by combining the user's persona, their objective, and a set of keywords relevant to the task (e.g., "nightlife," "food," "beaches").

Semantic Ranking (semantic_ranker.py):

The powerful msmarco-distilbert-base-v2 sentence-transformer model converts the enhanced query and each document section into numerical vector embeddings.

The system calculates the cosine similarity between the query vector and each section vector to determine relevance.

Output Generation (output_builder.py): The ranked sections and their corresponding content are formatted into a structured output.json file, presenting the most important information first.

The entire application is containerized with Docker, ensuring it runs consistently in any environment after a one-time setup.

Tech Stack
Language: Python 3.9

Core Libraries:

sentence-transformers: For state-of-the-art semantic embedding models.

PyMuPDF (fitz): For high-performance and accurate PDF text extraction.

numpy: For numerical operations.

Containerization: Docker

Semantic Model: sentence-transformers/msmarco-distilbert-base-v2 (chosen for its excellent balance of performance and speed on a CPU).

Getting Started
Follow these instructions to get the project running on your local machine.

Prerequisites
You must have the following software installed:

Git

Docker Desktop

Installation
Clone the repository:
Open your terminal or command prompt and run the following command:

git clone <your-repository-url>
cd <repository-folder-name>

Understand the Directory:
The project is pre-organized. You will primarily interact with the input/ and output/ directories.

Running the Application
Step 1: Prepare Your Input
Add your PDFs: Place all the PDF documents you want to analyze into the input/ directory.

Define your Query: Open the input/query.json file and modify the persona and job_to_be_done fields to match your objective.

Example query.json:

{
  "persona": {
    "role": "Travel Planner"
  },
  "job_to_be_done": {
    "description": "Plan a trip of 4 days for a group of 10 college friends."
  }
}

Step 2: Build the Docker Image
In your terminal, at the root of the project directory, run the following command. This will build a Docker image named document-intelligence.

docker build -t document-intelligence .

This command reads the Dockerfile, installs all the Python dependencies, and packages the application.

Step 3: Run the Docker Container
Execute the following command to run the application.

docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" document-intelligence

What this command does:

docker run: The command to start a new container.

--rm: Automatically removes the container when it finishes running, keeping your system clean.

-v "$(pwd)/input:/app/input": Mounts your local input folder into the container. This is how the container reads your PDFs and query.json.

-v "$(pwd)/output:/app/output": Mounts your local output folder into the container. This is where the container will save the final output.json.

document-intelligence: The name of the image you built in the previous step.

Important Note: The very first time you run this command, the container will require an internet connection to download and cache the sentence-transformer model. All subsequent runs will be fully offline as they will use the cached model.

Once the command finishes, you will find the output.json file in your local output/ directory.

Project Structure
.
├── Dockerfile
├── README.md
├── requirements.txt
├── input/
│   ├── query.json
│   └── (place your PDFs here)
├── output/
│   └── (output.json will be generated here)
└── src/
    ├── __init__.py
    ├── config.py
    ├── main.py
    ├── output_builder.py
    ├── pdf_parser.py
    └── semantic_ranker.py

Configuration & Tuning
For advanced users, the PDF parsing logic can be fine-tuned for different document structures by adjusting the HEADER_FONT_SIZE_THRESHOLD variable in src/config.py.

Lowering this value (e.g., to 1.05) makes header detection more sensitive.

Increasing this value (e.g., to 1.2) makes it less sensitive.