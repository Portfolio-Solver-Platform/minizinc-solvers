import os


class Config:
    class App:
        NAME = "solver"
        VERSION = "0.1.0"
        DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    class Api:
        TITLE = "Solver API"
        DESCRIPTION = "API to see information about the solver"
        VERSION = "v1"
        ROOT_PATH = "/"
