import re
import sys


def DetectDefinition(Text):
    Keywords = ["adalah", "merupakan", "yang selanjutnya disebut", "yang selanjutnya disingkat",]
    return any(Keyword in Text for Keyword in Keywords)


def ExtractDefinition(Text):
    Parts = Text.split("adalah")
    if len(Parts) == 1:
        Parts = Text.split("merupakan")
    if len(Parts) == 1:
        Parts = Text.split("yang selanjutnya disebut")
    if len(Parts) == 1:
        Parts = Text.split("yang selanjutnya disingkat")
    return Parts[-1].strip()


def DetectDefinitionsInText(Text):
    Sentences = re.split(r'\b\d+\.\s*', Text)
    Sentences = [Sentence.strip()
                for Sentence in Sentences if Sentence.strip()]

    Results = []
    for Sentence in Sentences:
        Sentence = re.sub(r'\s+', ' ', Sentence)

        if DetectDefinition(Sentence):
            Term = None
            if "yang selanjutnya disebut" in Sentence:
                Term = Sentence.split("yang selanjutnya disebut")[0].strip()
            elif "yang selanjutnya disingkat" in Sentence:
                Term = Sentence.split("yang selanjutnya disingkat")[0].strip()
            elif "adalah" in Sentence:
                Term = Sentence.split("adalah")[0].strip()
            elif "merupakan" in Sentence:
                Term = Sentence.split("merupakan")[0].strip()

            Definition = ExtractDefinition(Sentence)

            ShortTerm = None
            if "yang selanjutnya disebut" in Sentence:
                ShortTerm = re.search(
                    r'yang selanjutnya disebut(.*?)adalah', Sentence)
            elif "yang selanjutnya disingkat" in Sentence:
                ShortTerm = re.search(
                    r'yang selanjutnya disingkat(.*?)merupakan', Sentence)

            if ShortTerm:
                ShortTerm = ShortTerm.group(1).strip()

            result = {
                "Text": Sentence,
                "Term": Term,
                "ShortTerm": ShortTerm,
                "Definition": Definition,
                "Type": "DEFINITION"
            }
            Results.append(result)

    return Results


def get_doc_definitionterms(first_article_content):
    '''
    Get definition terms from the first article content.
    '''
    definition_terms = DetectDefinitionsInText(first_article_content)
    terms = []
    if definition_terms:
        for term in definition_terms:
            if term['Term'] is not None:
                terms.append(term['Term'])
    
    return terms