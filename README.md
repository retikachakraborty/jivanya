# Jivanya

**AI-powered Indian food, recipe, nutrition, packaged-food, and visual
food-intelligence platform.**

Jivanya combines structured food data, personalized dietary profiles,
recipe discovery, meal planning, packaged-food intelligence, specialized
computer-vision models, and **Jiv**, a conversational interface for
accessing these capabilities.

Its core architecture is data-grounded: food facts and safety-sensitive
filtering come from Jivanya's databases, deterministic backend logic,
and trained models. The language model is used for conversation and
orchestration rather than as the source of recipe, nutrition, product,
allergy, or vision facts.

------------------------------------------------------------------------

## Features

### Authentication and Food Profiles

Jivanya uses Supabase-backed authentication and persistent user
profiles. Profiles can store supported dietary preferences, allergies,
ingredient exclusions, and no-onion/no-garlic restrictions.

Where supported by the project's data, these restrictions act as hard
constraints when recipes and food options are retrieved.

### Recipe Intelligence

Jivanya contains **6,871 recipes** from the project's processed Indian
Food Dataset.

The current application performs structured, database-backed recipe
discovery using fields such as course, cuisine, ingredients, ingredient
exclusions, diet, preparation/cooking time, profile constraints, result
count, and pagination.

Jiv can translate natural-language requests into structured backend
searches, but it does not invent recipes or missing recipe facts.
Historical TF-IDF/Jaccard experiments may remain in the repository, but
they are not the current user-facing recipe runtime.

### Saved Recipes and Guided Cooking

Authenticated users can save recipes. Guided Cook Mode uses instructions
stored with the selected recipe rather than fabricating missing cooking
steps.

### 7-Day Meal Planning

The meal-plan backend supports plan generation, meal swapping, and
grocery-list generation using Jivanya's available recipe data and
applicable profile constraints.

### Nutrition Intelligence

The nutrition API supports structured food lookup, ingredient
normalization, and recipe-nutrition calculation using available project
nutrition data. Missing nutrient data is not silently replaced with
LLM-generated values.

### Packaged Food Intelligence

Jivanya's product system uses the project's processed Open Food Facts
data and supports product listing, barcode lookup, product comparison,
and a deterministic Jivanya Health Score implemented in backend logic.

------------------------------------------------------------------------

# Computer Vision

Jivanya uses specialized local computer-vision models for supported food
and ingredient categories. Image recognition is performed by these
trained models, **not by Gemini Vision**.

## Supported Vision Categories

The user-facing vision system includes specialized categories for
fruits, vegetables, spices, lentils, nuts, chicken, egg, fish, mutton,
coffee, green tea, red tea, grocery items, grocery ingredients,
allergens, and farmer/seed ingredients.

Runtime availability depends on the corresponding trained checkpoint and
metadata being present.

## Vision Architecture

``` text
Selected food category
        ↓
Corresponding local model
        ↓
Raw prediction
        ↓
Canonical food / ingredient resolution
        ↓
Dietary restriction and allergy checks
        ↓
Recipe / database handoff
```

The backend loads models lazily and keeps a bounded model cache. The
default cache size is **2 models**, configurable through
`VISION_MODEL_CACHE_SIZE`.

The project uses task-specific object-detection, image-classification,
and instance-segmentation pipelines. Final trained models and metadata
are organized under `database/vision_engine/`.

------------------------------------------------------------------------

# Model Performance

The following values are recorded results from Jivanya's
model-development and evaluation pipelines.

Results should be interpreted in the context of each dataset,
preprocessing pipeline, class distribution, split strategy, and
evaluation procedure. Where train or validation counts were not
documented in the final evaluation results, they are not inferred.

## Object Detection

  ----------------------------------------------------------------------------------------
  Model                Classes Train / Val /       Precision   Recall   mAP@50   mAP@50-95
                               Test
  ------------------ --------- ----------------- ----------- -------- -------- -----------
  Fruit --- YOLO11n          6 7,108 / 914 / 457       0.614    0.435    0.477       0.313

  Vegetable ---             24 3,962 / 380 / 192       0.617    0.671    0.671       0.530
  YOLO11n

  Mutton --- YOLOv8n         1 70% / 20% / 10%         0.795    0.518    0.632       0.297

  Grocery ---                3 308 / 87 / 42           0.590    0.586    0.491       0.304
  YOLO11n

  Allergen ---              19 --- / --- / 427\*      0.6033   0.4715   0.5164      0.2710
  YOLO11n

  Egg --- YOLO11n            2 1,880 / 176 / 91       0.8265   0.7795   0.8678      0.6303

  Fish ---                  10 1,670 / 476 / 238      0.7880   0.8074   0.8457      0.5765
  YOLO11n\*\*

  Green Tea ---              1 900 / 300 / 300         0.991    0.993    0.994       0.915
  YOLOv8n

  Red Tea ---                1 900 / 300 / 300         1.000    1.000    0.995       0.936
  YOLOv8n

  Chicken ---                2 2,800 / 80 / 40         0.991    1.000    0.995       0.986
  YOLOv8n
  ----------------------------------------------------------------------------------------

-   **Allergen:** Final evaluation was performed on a 427-image test set
    containing 1,144 instances at 640×640. Train and validation image
    counts are not stated in the final evaluation results.

\*\* **Fish:** The listed values are recorded training/validation-run
metrics and are not presented as final held-out test results.

## Image Classification

  ------------------------------------------------------------------------------
  Model     Architecture        Train / Val  Recorded Performance
                                / Test
  --------- ------------------- ------------ -----------------------------------
  Indian    MobileNetV3-Small   Test: 1,113  Accuracy 97.48%; Macro F1 96.91%;
  Spices                                     Weighted F1 97.43%

  Coffee    YOLOv8n             960 / 240 /  Top-1 100%; Top-5 100%
            Classification      400

  Nuts      YOLOv8n             1,108 / 282  Top-1 100%; Top-5 100%
            Classification      / 352

  Indian    YOLO11n             7,505 /      Top-1 100%; Top-5 100%; recorded
  Lentils   Classification      1,035 / 850  per-class accuracy 100%
  ------------------------------------------------------------------------------

Perfect recorded evaluation scores should be considered together with
the corresponding dataset construction and split strategy rather than
interpreted as expected real-world accuracy.

## Instance Segmentation

The Sequel Farmer model performs instance segmentation, so both
bounding-box and segmentation-mask performance are reported.

  ----------------------------------------------------------------------------------------------------------------
  Model                Classes Train /     Box P   Box R      Box         Box  Mask P  Mask R     Mask        Mask
                               Val /                       mAP@50   mAP@50-95                   mAP@50   mAP@50-95
                               Test
  ------------------ --------- --------- ------- ------- -------- ----------- ------- ------- -------- -----------
  Sequel Farmer ---         43 1,666 /     0.262   0.591    0.407       0.307   0.220   0.543    0.353       0.202
  YOLO Segmentation            297 / 149

  ----------------------------------------------------------------------------------------------------------------

These are **final test-set results** evaluated on the 149-image Sequel
Farmer test split.

------------------------------------------------------------------------

# Datasets

Jivanya uses third-party datasets for its recipe, packaged-food, and
machine-learning pipelines. Dataset ownership remains with the
respective creators and publishers.

  -------------------------------------------------------------------------------------------------------------------------
  Component     Dataset / Source                                                                           Purpose
  ------------- ------------------------------------------------------------------------------------------ ----------------
  Recipe Engine [Indian Food Dataset ---                                                                   Recipe
                Kaggle](https://www.kaggle.com/datasets/sukhmandeepsinghbrar/indian-food-dataset)          processing and
                                                                                                           recommendation

  Fruit         [Fruit Detection Dataset ---                                                               Object detection
                Kaggle](https://www.kaggle.com/datasets/lakshaytyagi01/fruit-detection)

  Vegetable     [Emam Vegetable Detection Dataset ---                                                      Object detection
                Roboflow](https://universe.roboflow.com/emam-uuopz/yolo-jmiqx-4ff49)

  Mutton        [Mutton Dataset --- Roboflow](https://universe.roboflow.com/muttondataset/mutton)          Object detection

  Grocery       [Grocery Detection ---                                                                     Object detection
                Roboflow](https://universe.roboflow.com/grocdetect/grocery_detection-insij)

  Indian        [Sequel Farmer Dataset ---                                                                 Instance
  Ingredients   Roboflow](https://universe.roboflow.com/ayushi-beutb/sequel-farmer-dataset-ijnyl)          segmentation

  Allergen      [Allergen30 --- Mendeley Data](https://data.mendeley.com/datasets/9ygs9vhnpw/1)            Object detection

  Egg           [Derived from Allergen30 --- Mendeley                                                      Object detection
                Data](https://data.mendeley.com/datasets/9ygs9vhnpw/1)

  Fish          [10 Classification Fish ---                                                                Object detection
                Roboflow](https://universe.roboflow.com/nevin-q1id7/10-classification-fish-nevin)

  Indian Spices [Indian Spices Dataset --- Mendeley Data](https://data.mendeley.com/datasets/vg77y9rtjb/3) Image
                                                                                                           classification

  Coffee        [Coffee Bean Dataset Resized (224×224) ---                                                 Image
                Kaggle](https://www.kaggle.com/datasets/gpiosenka/coffee-bean-dataset-resized-224-x-224)   classification

  Nuts          [Nuts Dataset --- Mendeley Data](https://data.mendeley.com/datasets/fmrnybgxb9/1)          Image
                                                                                                           classification

  Green Tea     [Green Tea --- Roboflow](https://universe.roboflow.com/tea-advuw/green-tea)                Object detection

  Red Tea       [Puer / Red Tea --- Roboflow](https://universe.roboflow.com/puertea/puer-tea)              Object detection

  Indian        [Indian Lentils Dataset --- Mendeley                                                       Image
  Lentils       Data](https://data.mendeley.com/datasets/r4yhfnzc5y/1)                                     classification

  Chicken       [Chicken Meat Detection ---                                                                Object detection
                Roboflow](https://universe.roboflow.com/bagass-workspace/chicken-meat-detection-oju85)

  Packaged Food [Open Food Facts](https://world.openfoodfacts.org/)                                        Packaged-food
                                                                                                           intelligence
  -------------------------------------------------------------------------------------------------------------------------

Detailed licensing, attribution, derivations, and dataset modifications
are documented in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

Raw third-party datasets remain subject to their respective licenses and
terms.

------------------------------------------------------------------------

# How Jivanya's Components Work Together

Jivanya follows this data-grounded architecture:

``` text
Datasets / Supabase / Local Trained Models
                    ↓
          FastAPI Backend Logic
                    ↓
       Jiv Orchestration / Frontend
```

The backend exposes dedicated APIs for recipes, nutrition, products,
meal planning, speech, vision, and Jiv.

Gemini is Jiv's conversational/orchestration layer. It can interpret
requests and select backend capabilities, while factual food information
remains grounded in Jivanya's own data and deterministic services.

``` text
User
 │
 ├── Profile ───────────────→ restrictions / allergies / exclusions
 ├── Recipe request ────────→ Recipe API
 ├── Nutrition request ─────→ Nutrition API
 ├── Product request ───────→ Products API
 ├── Meal planning ─────────→ Meal Plan API
 ├── Image ─────────────────→ Vision API → local trained model
 ├── Voice ─────────────────→ Speech API → Groq Whisper
 └── Natural language ──────→ Jiv → appropriate backend capability
```

# Technology Stack

### Frontend

-   Next.js
-   React
-   TypeScript
-   Tailwind CSS
-   Supabase client libraries

### Backend

-   Python
-   FastAPI
-   Uvicorn
-   SQLAlchemy
-   PostgreSQL / Supabase

### AI and Machine Learning

-   Google Gemini --- Jiv conversation and orchestration
-   Groq Whisper --- speech-to-text
-   PyTorch / torchvision
-   Ultralytics YOLO
-   MobileNetV3
-   Object detection, image classification, and instance segmentation

# Repository Structure

``` text
jivanya/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── jiv/
│   │   └── services/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   └── package.json
├── database/
│   ├── market_engine/
│   ├── nutrition_engine/
│   ├── recipe_engine/
│   ├── vision_engine/
│   ├── migrations/
│   ├── scripts/
│   └── seed/
├── .env.example
├── README.md
└── THIRD_PARTY_NOTICES.md
```

# Jiv --- Conversational Food Intelligence

**Jiv** is Jivanya's conversational interface. Gemini provides
natural-language understanding and orchestration; recipe, nutrition,
product, allergy, meal-plan, and vision facts remain grounded in
Jivanya's backend systems.

Jiv is designed not to silently fill missing food data from general LLM
knowledge. When required project data is unavailable, the application
should return an unavailable or insufficient-data result rather than
fabricate one.

### Image Recognition

Jiv can hand image requests to Jivanya's local Vision API. The local
category-specific model performs recognition; Gemini does not perform
the image classification/detection.

### Recipe Recommendations

Jiv converts suitable natural-language requests into structured recipe
searches and returns recipes found in Jivanya's database while
respecting supported hard constraints.

### Speech-to-Text

Voice input uses this flow:

``` text
Browser MediaRecorder
        ↓
FastAPI /api/v1/speech/transcribe
        ↓
Groq Whisper
        ↓
Editable transcript
        ↓
User submits transcript to Jiv
```

The current application does **not** require local Faster-Whisper.
Text-to-speech is not documented as a current runtime feature.

# Local Development Setup

## Prerequisites

Install Git, Git LFS, Python, Node.js/npm, and obtain access to the
Supabase project/configuration plus Gemini and Groq API credentials for
the corresponding features.

## Clone

``` bash
git clone <repository-url>
cd jivanya
git lfs install
```

The repository uses Git LFS for model/data artifacts. Retrieve the LFS
objects required for the functionality you intend to run.

## Backend

``` bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt

cd backend
uvicorn app.main:app
```

While the backend is running, FastAPI's interactive documentation is
available at `/docs`.

## Frontend

In another terminal:

``` bash
cd frontend
npm install
npm run dev
```

Open the Local URL printed by Next.js.

# Environment Configuration

Use `.env.example` as the configuration template. Never commit real
`.env` or `frontend/.env.local` files.

  ----------------------------------------------------------------------------
  Variable                                 Purpose
  ---------------------------------------- -----------------------------------
  `DATABASE_URL`                           Backend PostgreSQL connection

  `NEXT_PUBLIC_SUPABASE_URL`               Supabase project URL used by the
                                           frontend

  `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`   Browser-safe Supabase publishable
                                           key

  `SUPABASE_SERVICE_ROLE_KEY`              Backend-only privileged Supabase
                                           key

  `GEMINI_API_KEY`                         Gemini access for Jiv

  `GROQ_API_KEY`                           Backend Groq access for speech
                                           transcription

  `GROQ_WHISPER_MODEL`                     Whisper model used for STT

  `GEMINI_TIMEOUT`                         Optional Gemini request timeout

  `VISION_MODEL_CACHE_SIZE`                Maximum number of cached vision
                                           models; default `2`

  `NEXT_PUBLIC_API_URL`                    Optional frontend backend-API URL

  `LLM_PROVIDER`                           Optional LLM provider override

  `LLM_MODEL`                              Optional LLM model override

  `LLM_API_KEY`                            Optional generic provider API key

  `LLM_BASE_URL`                           Optional OpenAI-compatible provider
                                           base URL
  ----------------------------------------------------------------------------

Variables beginning with `NEXT_PUBLIC_` are browser-visible. Never place
service-role keys, Gemini/Groq keys, database passwords, or other
private credentials in them.

# Database and Migrations

Jivanya uses a PostgreSQL/Supabase runtime database. Current migrations
are:

-   `database/migrations/001_initial_runtime_schema.sql`
-   `database/migrations/002_user_profiles.sql`
-   `database/migrations/003_saved_recipes.sql`

Cloning the Git repository does **not** duplicate the hosted Supabase
database. Developers must configure access to an appropriate database
and apply the required schema/migrations where necessary.

# Testing and Validation

Backend tests cover health scoring, Jiv orchestration, meal planning,
recipe filtering/querying, speech, and vision.

``` bash
cd backend
python -m pytest tests
```

Frontend production validation:

``` bash
cd frontend
npm run build
```

Repository whitespace validation:

``` bash
git diff --check
```

# Security

-   Never commit `.env` or `frontend/.env.local`.
-   Keep `.env.example` limited to variable names, placeholders, and
    safe defaults.
-   Supabase service-role credentials, Gemini/Groq API keys, and
    database credentials are backend-only.
-   `NEXT_PUBLIC_*` values are exposed to the browser.
-   Rotate credentials immediately if they are accidentally published.

# Third-Party Data and Models

Jivanya does not claim ownership of third-party datasets, services,
libraries, or pretrained model architectures used by the project.

Dataset preprocessing, class normalization, data preparation, model
training/evaluation, backend logic, frontend integration, and other
Jivanya-specific implementation are project work built using those
external resources.

See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for attribution
and licensing information.
