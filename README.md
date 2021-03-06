# Nom_Ref
This repository contains experiments on the Nominal Reference Game dataset produced in (Graf, et al. 2016).

Currently, the project is focused on developing speaker models to produce utterances provided by human speakers in the game. Specifically, we have been focusing on inferring different lexicons based on the game data, before running RSA to produce utterances. Below is a list of the proposed models that are contained and documented within this repository.

## Models
* Beta-Draw for Lexicon Seeding
* Deterinsitic Lexicon
* Vision-Inferred Lexicon

## Directory Layout
### alexnet
Directory contains all code pertaining to deriving dense image embeddings of the objects used in the nominal reference game.

### nom_ref_preprocessing
Directory contains code pertaining to preprocessing the Nominal Reference Data.

### imgs
Directory containing imgs of objects from nominal reference game and additional generalization tasks.