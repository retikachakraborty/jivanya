# Third-Party Notices

Jivanya uses third-party datasets, data sources, machine-learning
frameworks, and pretrained model architectures.

Third-party materials remain the property of their respective creators
and publishers and remain subject to their original licenses and terms.
Jivanya does not relicense third-party datasets.

This document records the primary external data and machine-learning
resources used by the project.

------------------------------------------------------------------------

## Recipe Engine

### Indian Food Dataset

**Source:** [Indian Food Dataset ---
Kaggle](https://www.kaggle.com/datasets/sukhmandeepsinghbrar/indian-food-dataset)

Jivanya uses this dataset as the source for its recipe-data pipeline and
recommendation-engine preparation.

The source contains 6,871 Indian and related recipes with fields
including recipe names, ingredients, cuisine, course, diet, preparation
time, cooking time, instructions, and source URLs.

Jivanya performs additional processing including:

-   recipe cleaning
-   ingredient extraction and normalization
-   recipe feature generation
-   dietary feature generation
-   recommendation-data preparation
-   TF-IDF similarity processing
-   Jaccard ingredient similarity

Users downloading or redistributing the source dataset should review and
comply with the license and terms displayed on the Kaggle dataset page.

------------------------------------------------------------------------

## Packaged Food Intelligence

### Open Food Facts

**Source:** [Open Food Facts](https://world.openfoodfacts.org/)
**Licensing information:** [Open Food Facts data
licensing](https://openfoodfacts.github.io/openfoodfacts-server/api/tutorials/license-be-on-the-legal-side/)

Jivanya uses Open Food Facts data in its Market Engine for packaged-food
intelligence.

Open Food Facts states that:

-   its database is available under the **Open Database License (ODbL)**
-   individual database contents are available under the **Database
    Contents License (DbCL)**
-   product images are available under **Creative Commons
    Attribution-ShareAlike (CC BY-SA)**, subject to any additional
    rights that may apply to graphical elements shown in those images

Reuse and redistribution should follow the current Open Food Facts
attribution and licensing requirements.

------------------------------------------------------------------------

# Computer-Vision Datasets

## Fruit Detection

**Source:** [Fruit Detection Dataset ---
Kaggle](https://www.kaggle.com/datasets/lakshaytyagi01/fruit-detection)

Jivanya uses this dataset for its fruit object-detection pipeline.

The Jivanya model works with six supported fruit classes:

-   Apple
-   Banana
-   Grape
-   Orange
-   Pineapple
-   Watermelon

Dataset preprocessing, training, evaluation, and integration into
Jivanya were performed as part of the project.

Users should follow the license and terms provided on the source dataset
page when downloading or redistributing the dataset.

------------------------------------------------------------------------

## Vegetable Detection

**Source:** [Emam Vegetable Detection Dataset --- Roboflow
Universe](https://universe.roboflow.com/emam-uuopz/yolo-jmiqx-4ff49)

Jivanya uses this dataset for its 24-class vegetable object-detection
pipeline.

The project performs its own dataset preparation, model training,
evaluation, and application integration.

Users downloading or redistributing the source data should comply with
the license and attribution requirements shown for the relevant dataset
version on Roboflow Universe.

------------------------------------------------------------------------

## Mutton Detection

**Source:** [Mutton Dataset --- Roboflow
Universe](https://universe.roboflow.com/muttondataset/mutton)

Jivanya uses this dataset for its dedicated mutton-detection model.

The source contains 1,496 annotated images. As part of Jivanya's
processing:

-   the original `objects` class was normalized to `mutton`
-   a reproducible train/validation/test split was created
-   the data was prepared for YOLO object detection
-   a dedicated model was trained and evaluated

The underlying source data remains subject to the terms and license
provided by its original publisher.

------------------------------------------------------------------------

## Grocery Detection

**Source:** [Grocery Detection --- Roboflow
Universe](https://universe.roboflow.com/grocdetect/grocery_detection-insij)

Jivanya uses this dataset for its grocery-ingredient object-detection
pipeline.

The processed Jivanya configuration contains the supported grocery
classes used by the final model.

The exact license for the source version should be checked directly on
its Roboflow Universe page before redistribution. Jivanya does not
assign a license to the original dataset.

------------------------------------------------------------------------

## Indian Ingredient Segmentation

### Sequel Farmer Dataset

**Source:** [Sequel Farmer Dataset --- Roboflow
Universe](https://universe.roboflow.com/ayushi-beutb/sequel-farmer-dataset-ijnyl)

Jivanya uses this dataset for its Indian-ingredient
instance-segmentation pipeline.

The processed Jivanya dataset contains:

-   43 classes
-   1,666 training images
-   297 validation images
-   149 test images
-   2,112 images in total

Segmentation annotations are retained for the segmentation task, while
Jivanya performs its own preprocessing, model training, evaluation, and
integration.

Users should review the applicable license on the source dataset page
before downloading or redistributing the data.

------------------------------------------------------------------------

## Allergen Detection

### Allergen30

**Source:** [Allergen30 --- Mendeley
Data](https://data.mendeley.com/datasets/9ygs9vhnpw/1)

Jivanya uses Allergen30 as the source for its allergen computer-vision
pipeline.

The original data was processed into the **19-class configuration** used
by Jivanya's final allergen model.

The final model was evaluated on 427 test images containing 1,144
instances.

Any redistribution of source or derived dataset content remains subject
to the license and terms attached to the original Mendeley Data
publication.

------------------------------------------------------------------------

## Egg Detection

Jivanya's dedicated Egg dataset is **derived from the Allergen30 data
used by the project** rather than from a separate external dataset.

**Original source:** [Allergen30 --- Mendeley
Data](https://data.mendeley.com/datasets/9ygs9vhnpw/1)

Relevant egg examples were extracted and prepared for a dedicated
two-class object-detection task:

-   `egg`
-   `whole_egg_boiled`

The original Allergen30 attribution and licensing requirements continue
to apply to source material used in this derived dataset.

------------------------------------------------------------------------

## Fish Detection

**Source:** [10 Classification Fish --- Roboflow
Universe](https://universe.roboflow.com/nevin-q1id7/10-classification-fish-nevin)

Jivanya uses this source for its ten-class fish computer-vision
pipeline.

The supported classes are:

-   Bangus
-   Big-Head-Carp
-   Black-Spotted-Barb
-   Catfish
-   Climbing-Perch
-   Fourfinger-Threadfin
-   Freshwater-Eel
-   Glass-Perchlet
-   Goby
-   Gold-Fish

Jivanya performs its own model training, evaluation, and application
integration.

Users should consult the source project for the applicable dataset
license and attribution requirements.

------------------------------------------------------------------------

## Indian Spices Classification

**Source:** [Indian Spices Dataset --- Mendeley
Data](https://data.mendeley.com/datasets/vg77y9rtjb/3)

Jivanya uses this dataset for its 19-class Indian-spice
image-classification pipeline.

A MobileNetV3-Small model is used for the corresponding classification
task.

The original dataset remains subject to the license and terms specified
by the Mendeley Data publication.

------------------------------------------------------------------------

## Coffee Bean Classification

**Source:** [Coffee Bean Dataset Resized (224×224) ---
Kaggle](https://www.kaggle.com/datasets/gpiosenka/coffee-bean-dataset-resized-224-x-224)

Jivanya uses this dataset for its coffee-bean image-classification
pipeline.

The dataset and its contents remain subject to the license and terms
stated on the Kaggle dataset page.

------------------------------------------------------------------------

## Nuts Classification

**Source:** [Nuts Dataset --- Mendeley
Data](https://data.mendeley.com/datasets/fmrnybgxb9/1)

Jivanya uses this source for its nuts image-classification pipeline.

Jivanya performs its own model training, evaluation, and application
integration. The source data remains subject to the license attached to
the original Mendeley Data publication.

------------------------------------------------------------------------

## Green Tea Detection

**Source:** [Green Tea --- Roboflow
Universe](https://universe.roboflow.com/tea-advuw/green-tea)

Jivanya uses this dataset for its one-class Green Tea detection model.

The supported class is:

-   `green-tea`

The source data remains subject to the license and attribution
requirements of the relevant Roboflow dataset version.

------------------------------------------------------------------------

## Red Tea Detection

**Source:** [Puer / Red Tea --- Roboflow
Universe](https://universe.roboflow.com/puertea/puer-tea)

Jivanya uses this dataset for its one-class Red Tea detection model.

The supported class is:

-   `red-tea`

The source data remains subject to the license and attribution
requirements of the relevant Roboflow dataset version.

------------------------------------------------------------------------

## Indian Lentils Classification

**Source:** [Indian Lentils Dataset --- Mendeley
Data](https://data.mendeley.com/datasets/r4yhfnzc5y/1)

Jivanya uses this source for its Indian-lentil image-classification
pipeline.

The project performs its own dataset preparation, model training,
evaluation, and application integration.

The source dataset remains subject to the license and terms specified by
its original Mendeley Data publication.

------------------------------------------------------------------------

## Chicken Meat Detection

**Source:** [Chicken Meat Detection --- Roboflow
Universe](https://universe.roboflow.com/bagass-workspace/chicken-meat-detection-oju85)

Jivanya uses this dataset for its two-class chicken-meat detection
pipeline.

The supported classes are:

-   `chicken-meat-good`
-   `chicken-meat-rooten`

The final dataset configuration contains:

-   2,800 training images
-   80 validation images
-   40 test images

The source data remains subject to the applicable Roboflow dataset
license and attribution requirements.

------------------------------------------------------------------------

# Machine-Learning Frameworks and Models

## Ultralytics YOLO

**Official website:** [Ultralytics](https://www.ultralytics.com/)
**License information:** [Ultralytics
Licensing](https://www.ultralytics.com/license)

Jivanya uses Ultralytics YOLO tooling and model architectures for
several object-detection, image-classification, and
instance-segmentation pipelines.

Ultralytics currently provides its open-source YOLO software and models
under the **GNU Affero General Public License v3.0 (AGPL-3.0)** by
default, with separate commercial licensing options available from
Ultralytics.

Users modifying, redistributing, deploying, or commercially using
Ultralytics software or models should review the current Ultralytics
license terms and determine which license applies to their use case.

------------------------------------------------------------------------

# Attribution and Redistribution

Third-party datasets and resources listed in this document are not owned
or relicensed by Jivanya.

Jivanya-specific work may include:

-   dataset preprocessing
-   dataset organization
-   class normalization
-   train/validation/test preparation
-   feature engineering
-   model training
-   model evaluation
-   recommendation logic
-   inference integration
-   backend integration
-   frontend integration
-   project documentation

These project-specific modifications do not replace or override the
licenses of the underlying third-party materials.

Anyone downloading, reproducing, redistributing, or deploying
third-party data, software, or models referenced by Jivanya is
responsible for reviewing and complying with the applicable original
license and terms.

===== BACKEND EXTERNAL IMPORTS ===== abc app ast collections concurrent
dataclasses dotenv fastapi gc io json logging os pathlib PIL pydantic re
requests sqlalchemy threading time typing uuid

===== ENV VARIABLE NAMES USED BY BACKEND ===== GEMINI_API_KEY
GEMINI_TIMEOUT GROQ_API_KEY GROQ_WHISPER_MODEL LLM_API_KEY LLM_BASE_URL
LLM_MODEL LLM_PROVIDER VISION_MODEL_CACHE_SIZE

===== ENV EXAMPLE VARIABLE NAMES ===== NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY SUPABASE_SERVICE_ROLE_KEY GEMINI_API_KEY
GROQ_API_KEY GROQ_WHISPER_MODEL DATABASE_URL
retika-chakraborty@asus:\~/Documents/jivanya\$

------------------------------------------------------------------------

# Runtime Services and Software

In addition to the datasets and model resources listed above, Jivanya
integrates third-party runtime services and open-source software.

## Google Gemini

**Purpose:** Natural-language understanding and orchestration for Jiv.

**Official site:** https://ai.google.dev/

Gemini is used as a conversational/orchestration layer. Jivanya's
recipe, nutrition, product, allergy, and vision facts are intended to
remain grounded in project data and backend logic.

Use of Gemini is subject to Google's applicable API terms and service
policies.

## Groq

**Purpose:** Hosted Whisper speech-to-text used by Jiv voice input.

**Official site:** https://groq.com/

The backend uses the Groq API for transcription. Use is subject to
Groq's applicable terms and model/service conditions.

## Supabase

**Purpose:** PostgreSQL-backed application data, authentication, and
user profiles.

**Official site:** https://supabase.com/

Supabase software and hosted services are subject to their respective
licenses and service terms.

## FastAPI

**Purpose:** Jivanya backend API framework.

**Official site:** https://fastapi.tiangolo.com/

## Next.js and React

**Purpose:** Jivanya web frontend.

**Official sites:** https://nextjs.org/ and https://react.dev/

## PyTorch and torchvision

**Purpose:** Machine-learning runtime used by Jivanya's local vision
pipelines.

**Official site:** https://pytorch.org/

## Additional Python and JavaScript Dependencies

The authoritative dependency lists for the current source tree are:

-   `backend/requirements.txt`
-   `frontend/package.json`
-   `frontend/package-lock.json`

Individual packages remain subject to their own licenses and terms.
Contributors and redistributors should review the versions and license
metadata shipped by the relevant package registries before
redistribution.

------------------------------------------------------------------------

This notice is provided for attribution and project documentation. It
does not replace the original license text, terms of service, or usage
conditions supplied by each third-party provider.
