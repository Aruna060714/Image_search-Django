import os, json, base64
import torch, numpy as np
from PIL import Image
from io import BytesIO
from django.shortcuts import render, redirect
from django.conf import settings
from sklearn.metrics.pairwise import cosine_similarity
from torchvision import transforms
from .forms import UploadForm
from opensearchpy import OpenSearch
import requests
model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vitg14')
model.eval()
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=0.5, std=0.5)
])
_vectors = None
_metadata = None
def load_vectors():
    global _vectors, _metadata
    if _vectors is None or _metadata is None:
        _vectors = np.load(os.path.join(settings.BASE_DIR, 'embeddings.npy'))
        with open(os.path.join(settings.BASE_DIR, 'metadata.json')) as f:
            _metadata = json.load(f)
    return _vectors, _metadata
def get_embedding(image: Image.Image):
    img_tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        return model(img_tensor).squeeze().numpy().reshape(1, -1)
def index_view(request):
    form = UploadForm()
    return render(request, 'core/index.html', {'form': form})
def upload_view(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            img = None
            query_image = None
            if request.POST.get('camera_image'):
                base64_str = request.POST['camera_image'].split(",")[1]
                img_data = base64.b64decode(base64_str)
                img = Image.open(BytesIO(img_data)).convert('RGB')
                query_image = request.POST['camera_image']
            elif request.FILES.get('image'):
                img = Image.open(request.FILES['image']).convert('RGB')
                img_io = BytesIO()
                img.save(img_io, format='JPEG')
                img_io.seek(0)
                base64_image = base64.b64encode(img_io.read()).decode('utf-8')
                query_image = f"data:image/jpeg;base64,{base64_image}"
            elif request.POST.get('image_url', '').strip():
                try:
                    image_url = request.POST.get('image_url', '').strip()
                    response = requests.get(image_url, timeout=5)
                    response.raise_for_status()
                    img = Image.open(BytesIO(response.content)).convert('RGB')
                    img_io = BytesIO()
                    img.save(img_io, format='JPEG')
                    img_io.seek(0)
                    base64_image = base64.b64encode(img_io.read()).decode('utf-8')
                    query_image = f"data:image/jpeg;base64,{base64_image}"
                except Exception as e:
                    print(" Error fetching image from URL:", e)
                    return render(request, 'core/index.html', {
                        'form': form,
                        'error': 'Unable to fetch image from URL. Please check the link.'
                    })
            if img is None:
                return render(request, 'core/index.html', {
                    'form': form,
                    'error': 'No valid image provided.'
                })
            query_vec = get_embedding(img)
            vectors, metadata = load_vectors()
            similarities = cosine_similarity(query_vec, vectors)[0]
            top_indices = np.argsort(similarities)[::-1][:5]
            results = [{
                "image": metadata[i].get("image", ""),
                "title": metadata[i].get("title", "No Title"),
                "category": metadata[i].get("type", "Unknown"),
                "distance": round(float(similarities[i]), 4)
            } for i in top_indices]
            return render(request, 'core/index.html', {
                'form': form,
                'results': results,
                'query_image': query_image
            })

    return redirect('index')
def all_products_view(request):
    client = OpenSearch(
        hosts=[{'host': 'superbotics-search-8731633774.eu-central-1.bonsaisearch.net', 'port': 443}],
        http_auth=('JC8YvqRN74', 'T8JEbusxGFN5VXZ'),
        use_ssl=True,
        verify_certs=True
    )
    INDEX_NAME = "products_new"
    PAGE_SIZE = 20
    page = int(request.GET.get('page', 1))
    start = (page - 1) * PAGE_SIZE
    query = {
        "from": start,
        "size": PAGE_SIZE,
        "_source": ["image", "title", "price", "type"],
        "query": {
            "bool": {
                "must": [
                    {"exists": {"field": "image"}},
                    {
                        "script": {
                            "script": {
                                "source": "doc['image'].size() > 0 && doc['image'].value != ''",
                                "lang": "painless"
                            }
                        }
                    }
                ]
            }
        }
    }
    response = client.search(index=INDEX_NAME, body=query)
    docs = [hit["_source"] for hit in response["hits"]["hits"]]
    total = response["hits"]["total"]["value"]
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    return render(request, "core/all_products.html", {
        "products": docs,
        "page": page,
        "total_pages": total_pages
    })