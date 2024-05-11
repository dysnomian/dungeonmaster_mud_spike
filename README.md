# Dungeonmaster MUD Spike

(more like a text adventure spike, but whatevs)

## Requirements
- Python 3.10+
- LM Studio

## Installation

### LM Studio setup and config

1. Install [LM Studio](https://lmstudio.ai/).
2. Start it up and install a model. I've been using `lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF`.
3. Bootstrap `lms`:
```shell
~/.cache/lm-studio/bin/lms bootstrap
```
4. Load the model:
```shell
lms load lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF
```
5. Start the server:
```shell
lms server start
```

## To start it

```shell
git clone git@github.com:dysnomian/dungeonmaster_mud_spike.git`
cd dungeonmaster_mud_spike
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python .
```
