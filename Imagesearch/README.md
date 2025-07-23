Image Search — Image Similarity Search

Imagesearch is an web application built with Django that allows users to upload a product image and find visually similar items. It uses DINOv2 model for feature extraction and OpenSearch for scalable product retrieval.

##  Features

-  Upload, paste URL, or capture an image via webcam
-  Image embeddings via Meta AI's DINOv2 ViT-G14 model
-  Cosine similarity search using precomputed `embeddings.npy`
-  Backend powered by PyTorch, OpenSearch, and NumPy
-  Frontend styled with TailwindCSS + smooth UI animations
-  Product browsing with pagination (`/all-products/`)


## Project Workflow

1. **User Uploads Image**  
   → Image is converted to tensor and passed through DINOv2
2. **Embedding Generation**  
   → DINOv2 generates a 1536-dimensional vector
3. **Similarity Search**  
   → Cosine similarity is computed between input and all stored embeddings
4. **Metadata Display**  
   → Top 5 similar images shown with title and category
5. **All Products Page**  
   → Images loaded from OpenSearch index (with pagination)

##  Tech Stack

| Layer       | Tech Used                                   |
|-------------|---------------------------------------------|
| Backend     | Django 5.2, Python 3.12                     |
| Frontend    | HTML, TailwindCSS ,Javascript               |
| ML Model    | DINOv2 (`dinov2_vitg14` via Torch Hub)      |
| Search      | OpenSearch (Bonsai Elasticsearch)           |
| Data Format | `.npy` for embeddings, `.json` for metadata |

##  Project Structure

      core/
      │
      ├── templates/core/
      │   ├── index.html             # Home page with image input
      │   └── all_products.html      # Paginated product viewer
      │
      ├── views.py                   # Handles logic & similarity
      ├── urls.py                    # URL routing
      ├── forms.py                   # Upload form definitions
      ├── embeddings.npy             # Precomputed DINOv2 embeddings
      ├── metadata.json              # Image metadata

## OpenSearch Index
1. Index name: products_new
2. Must contain fields: image, title, type
3. Pagination and filtering done using OpenSearch queries

## Install dependencies
 pip install django torch torchvision scikit-learn opensearch-py pillow numpy requests

## Run the server
 python manage.py runserver

## Acknowledgements
1.Meta AI - DINOv2

2.OpenSearch

3.TailwindCSS