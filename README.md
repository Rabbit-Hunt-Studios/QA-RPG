# QA-RPG
![Test](https://github.com/QA-RPG/QA-RPG/actions/workflows/unittest.yml/badge.svg)
[![codecov](https://codecov.io/gh/QA-RPG/QA-RPG/branch/main/graph/badge.svg?token=D3ZLS8LZ12)](https://codecov.io/gh/QA-RPG/QA-RPG)

QA-RPG is a text-based question answering RPG game. The game aims to be educative by using question answering system while maintaining the features that makes up an RPG. In this game, the monsters are represented by questions, and the player defeats them by answering the question.

## Project Documents

Project documents are in the [Project Wiki](../../wiki/Home).

- [User stories](https://github.com/QA-RPG/QA-RPG/wiki/User-Stories)

- [Vision Statement](https://github.com/QA-RPG/QA-RPG/wiki/Vision-Statement)

- [Requirements](https://github.com/QA-RPG/QA-RPG/wiki/Requirements)

- [Development Plan](https://github.com/QA-RPG/QA-RPG/wiki/Development-Plan)

- [Trello board](https://trello.com/b/87UXzdzR/information)

## Prerequisites
- ```Python``` version 3.8 or greater
- ```Node.js``` version 16 or greater

## Installation
1. Make sure that you have the prerequisites downloaded in your computer.
2. Clone this repository into your desired directory by using the command:
    ```sh
    git clone https://github.com/QA-RPG/QA-RPG.git
    ```
3. Go to the directory where you cloned the repository, and create a virtual environment using:
    ```sh
    python -m venv env
    ```
4. then run to activate a virtual environment.
    - For Windows use this command:
    ```sh
    . env/Scripts/activate
    ```
    - For Mac/Linux use this command:
    ```sh
    . env/bin/activate  
    ```
    
5. In the virtual environment, download the requirements using:
    ```sh
    pip install -r requirements.txt
    ```
6. Next, create a ```.env``` file in the project directory. Follow the example file called
```sample.env``` provided in the project directory. To generate a secret key go to [this site](https://djecrety.ir/)
7. Then, create an empty database using:
    ```sh
    python manage.py migrate
    ```
8. Then, load the preset data of questions, choices, and 1 demo user and 1 admin into the database.
    ```sh
   python manage.py loaddata data/users.json data/qa_rpg.json
   ```
9. Go to ```QA-RPG/Dungeon/static_src/``` directory then install npm.
    ```sh
    npm install
    ```
10. Lastly run this command to initiate the tailwind or the front-end framework.
    ```sh
    python manage.py tailwind start
    ```
## How to run
- To run the server please use
    ```sh
    python manage.py runserver
    ```
- To Then exit the environment then use the command:
    ```sh
    deactivate
    ```
