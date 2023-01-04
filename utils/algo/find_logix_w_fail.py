import models.logixable as logix_blueprint

def find_logixable_with_fail(name: str, logixables: list[logix_blueprint.Logixable]):
    try:
        logixable = next(l for l in logixables if name == l.name)
    except:
        raise ValueError("No Logixable found with the name provided in the command! Please, check the name and try again!")

    return logixable