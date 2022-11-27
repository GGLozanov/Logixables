import models.logixable as logix_blueprint

class FileHandler:
    def save_logixable(self, logixable: logix_blueprint.Logixable):
        file = open("%s.txt" % logixable.name, "w")
        file.write(logixable)
        file.close()

    def read_logixable(self, file_name: str):
        # TODO: Define
        pass