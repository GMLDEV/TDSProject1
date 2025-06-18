import json
import os
import torch
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
import cohere
import base64
import uuid

# ------------------- Cohere Setup -------------------

api_key = os.getenv("COHERE_API_KEY") 

# ------------------- Load Sentence Embedding Model -------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# ------------------- Load and Preprocess Data -------------------

def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

# Load Discourse posts
with open("scraped_posts.json", "r", encoding="utf-8") as f:
    discourse_posts = json.load(f)

# Load course content
with open("course_content.json", "r", encoding="utf-8") as f:
    course_content = json.load(f)

# Prepare corpus and metadata
corpus = []
metadata = []

# Process Discourse content
for post in discourse_posts:
    text = clean_html(post.get("excerpt") or post.get("title", ""))
    if text.strip():
        corpus.append(text)
        metadata.append({
            "source": "discourse",
            "title": post.get("title"),
            "url": f"https://discourse.onlinedegree.iitm.ac.in/t/{post.get('slug')}/{post.get('id')}"
        })

# Process Course content
for item in course_content:
    if item.get("text", "").strip():
        corpus.append(item["text"])
        metadata.append({
            "source": "course",
            "path": item.get("path", "")
        })

# Precompute corpus embeddings
corpus_embeddings = model.encode(corpus, convert_to_tensor=True)

# ------------------- Main Answer Function -------------------

def search_answers(question: str, extra_note: str = "") -> dict:
    if not corpus_embeddings.shape[0]:
        return {"answer": "No course data or forum posts found.", "links": []}

    query_embedding = model.encode(question, convert_to_tensor=True)
    scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
    top_hits = torch.topk(scores, k=5)

    context_parts = []
    links = []

    for score, idx in zip(top_hits[0], top_hits[1]):
        entry = metadata[int(idx)]
        source = entry.get("source")

        if source == "discourse":
            context_parts.append(f"(Forum) {corpus[int(idx)]}")
            links.append({
                "url": entry.get("url", ""),
                "text": entry.get("title", "")
            })
        elif source == "course":
            snippet = corpus[int(idx)][:500]
            context_parts.append(f"(Course) {snippet}")

    context = "\n\n".join(context_parts)

    prompt = f"""You are a helpful TA assistant for IITM students. Use both course material and Discourse forum content to answer clearly and accurately.

Question: {question}

Relevant Context:
{context}
{extra_note}

Your answer must be:
- Specific and concise
- Include **numerical values** if relevant (e.g., 110 marks)
- Return only valid JSON with this format:
{{
  "answer": "your helpful answer here",
  "links": [{{"url": "...", "text": "..."}}]
}}

Begin your response now.
"""

    try:
        co = cohere.Client(api_key)
        response = co.chat(
            model="command-r-plus",
            message=prompt,
            temperature=0.3
        )
        reply = response.text.strip()

        try:
            parsed = json.loads(reply)
            return parsed
        except:
            return {"answer": reply, "links": links}

    except Exception as e:
        return {"answer": f"Error generating answer: {e}", "links": []}
