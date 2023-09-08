Airbnb Listing Matching
==============================

A toy web service that matches Airbnb listings to the most similar listings in the area in NYC. Given a listing id, returns similar listings from different neighborhoods.

Data source: http://insideairbnb.com/get-the-data/

Requires Python 3.10+

Please keep in mind that data, model, and simulation artifacts are not stored on Git due to their larger size. They are stored in separete directories and referenced using the `src/.env` file.

Project Organization
------------
   **Code directory**

   The structure of the this repo; version controlled.

      ├── abnb-listing-matching
         │
         ├── README.md              <- The top-level README for developers using this project
         │
         ├── docker                 <- docker related files to create docker containers 
         │
         ├── notebooks              <- Jupyter notebooks. Naming convention is a number (for 
         │                             ordering), the creator's initials, and a short `-` delimited 
         │                             description, e.g. `1.0-jqp-initial-data-exploration`.
         │
         ├── references             <- Data dictionaries, manuals, and all other explanatory materials
         │
         ├── requirements.txt           <- requirements file
         │   
         └── src                    <- Source code for use in this project.
            │
            ├── .env               <- Environment / user specific variables to be defined. This 
            |                          file is ignored by git
            │                           
            ├── project_config.py  <- top level configurations for the project (e.g. paths to the
            │                          data and artifacts directory)
            |
            ├── data               <- Scripts to download / generate, and manupulate / 
            |                          preprocess data
            │ 
            └──  models             <- Scripts to define + train models and then use trained 
                                       models to make predictions                      

   
   **Data directory**

   Separate from this repo. Referenced in `src/.env`. Will be automatically created as needed. Not version controlled as of now. 

      ├── data
         └── raw            <- The original, immutable data dump.
      
   
   **Artifacts directory**

   Separate from this repo. Referenced in `src/.env`. Will be automatically created as needed. Not version controlled as of now. 

      ├── artifacts
         ├── hugging_face_cache    <- simulation results and outputs
         └── models         <- Trained and serialized models, model predictions, or
                                 model summaries
--------


`.env` & `project_config.py`
------------
The `.env` & `project_config.py` files make it easier to reference paths to `data` and `artifacts` directories on different computes and different developer environments.

### `.env`
Since `.env` is environment and developer specific, it is ignored by git. So every developer / user  needs to create their own. 

Please create a file called `.env` under the `src` directory, containing the following variables and update the paths accordingly:

```
CODE_DIR = '<absolute-path-to-the-project-directory>'
DATA_DIR = '<absolute-path-to-the-data-directory>'
ARTIFACTS_DIR = '<absolute-path-to-the-artifacts-directory>'
```

### `project_config.py`
The `project_config.py` will automatically load the `.env` file and expose all of its variables + additional variables based on the directory structures of the `data` and `artifacts` directories listed above. In your code, you can load the `project_config.py` and access the variables like so:

```
import os
import sys
sys.path.append(os.path.abspath(<relative-path-to-project-directory>))

from src import project_config as pc

project_config.ENV_VARS['CODE_DIR']
project_config.BASE_DATA_DIR
```