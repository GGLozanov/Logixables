from models.logixable import Logixable

class FileHandler:
    def save_logixable(logixable: Logixable):
        file = open("%s.txt" % logixable.name, "w")
        file.write(logixable)
        file.close()

    def read_logixable(file_name: str):
        # TODO: Define
        pass