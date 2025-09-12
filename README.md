# ARK2.0

ARK (Automated Resource Knowledgebase) revolutionizes resource management via automation. Using advanced algorithms, it streamlines collection, organization, and access to resource data, facilitating efficient decision-making.

tl;dr. It'll be an open source interface for a local LLM agent building utilizing long term memory for personalized requests. We are primarily focusing on targeting MIT students for the time being.


# Languages and dependencies

NOTE: This is not a complete list.

* Python
* Pydantic
* Openai (needed to standardize inference engine communication)
* Requests
* Pyyaml

# File structure

(As of July 30, 2025; update as needed.)

This repo is currently a bit chaotic, but from a top-level point of view, here's each file or folder is for:

* `base_module/` for MCP- and database-related stuff
* `config_module/` for YAML configuration files
* `model_module/` for core LLM-related logic
* `schemas/` for JSON schemas when communicating between frontend and backend
* `.gitignore` (standard)
* `README.md` (this very file!)
* `requirements.txt` (Python dependencies)

# Instructions

## Start Inference Engine (SGLANG)
* Run latest SGLANG image 
* cmd: bash model_module/run.sh
* Note: Qwen 2.5 is what is currently in use 

## Test base_module
* cmd: python main_interface.py

# Contributors + contact

| Name                  | Role           | GitHub username | Affiliation |
| --------------------  | -------------- | --------------- | ----------- |
| Nathaniel Morgan      | Project leader | nmorgan         | MIT         |
| Joshua Guo            | Frontend       | duck_master     | MIT         |
| Ilya Gulko            | Backend        | gulkily         | MIT         |
| Yeabkal Abeje         | (departed)     | Yebe-Abe        | MIT         |
| Jack Luo              | Backend        | thejackluo      | GT          |
| Bryce Roberts         | Backend        | BryceRoberts13  | MIT         | 

