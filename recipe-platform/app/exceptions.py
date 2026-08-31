class RecipeGenericError(Exception):
    """ A recoverable recipe-generation error """
    pass


class RecipeFatalError(Exception):
    """ A critical recipe-generation system failure """
    pass


class RecipeInvalidRequestError(Exception):
    """ The user request is not a recipe request """
    pass
