# FLUX node automation

## How it works
There are two scripts in this repo - config and main.

The config will make a config.txt file that will hold your configurations with this schema:
```
[
    {
        "ip": "xxx.xxx.xxx.xxx",
        "username": "xxxx",
        "password": "xxxx",
        "nickname": "xxxxxx"
    },
]
```

The main script will check if there is a config, and then will let you choose from several actions. Right now, these actions are two:

* Update node
* Restart node

Each action can be executed for one or more nodes, depending on your needs.

## How to run
1. Clone the repo and cd into the folder.
2. Create a virtual environment - `python -m venv env` for Windows and `python3 -m venv env` for UNIX.
3. Activate the environment - `env\Scripts\Activate` for Windows and `source env/bin/activate` for UNIX.
4. Install the requirements - `pip install -r requirements.txt` for Windows and `pip3 install -r requirements.txt` for UNIX.
5. Run the script - `python main.py` for Windows and `python3 main.py` for UNIX.

## TODO

- [ ] Create interactive server select
- [ ] Create server groups
- [ ] Add more functions
- [ ] Add a check for the SSH when adding a server
