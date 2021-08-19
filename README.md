# insta485
## Set up instructions:
python3 -m venv env

source env/bin/activate

pip install --upgrade pip setuptools wheel

pip install -r requirements.txt

chmod +x bin/insta485db

./bin/insta485db reset

## Starting up the server:
chmod +x bin/insta485run

./bin/insta485run

# Project Description
This project is an imitation instagram web-app created with full stack development tools, including client-side dynamic pages.

Majority of source code can be found in insta485/views, insta485/js, and insta485/api.
