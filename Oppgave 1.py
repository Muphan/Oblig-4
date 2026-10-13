# A)

class Film:
    I_AM = "A movie" #Klasseattributt, lik for alle instanser av klassen (har dette med kun for demo formål)

    # generer et film objekt, hvis parametere/argumenter mangler får den standardverdi som beskriver hva verdien skal være, her lik nøkkelen til verdien.
    def __init__(self, name="name", year="year", score="score"):

        #gjør parametrene til objektattributter med self., slik at de er tilgjengelig for alle metoder i objektet/instansen
        self.name = name
        self.year = year
        self.score = score

        # Oppretter en dict som samler attributtene og gjør de tilgjengelige i dict-form (*1)
        self.movie = {"name":self.name, "year":self.year, "score":self.score}

        #(*1): Det bør bemerkes at det ikke trengs å gjøre begge deler her, dict kunne blitt laget rett fra input-argumentene
        #      og de enkeltstående attributtene kan brukes individuelt av metodene i klassen, uten å måtte gå om dict.
        #      De er også separate attributter etter init oppretter dem, hvis man senere lager en metode som foranderer
        #      self.name, vil ikke den forandringen gjenspeiles i self.movie["name"]

        #Alternativ konstruksjon av self.movie:
        # self.movie = {"name":name, "year":year, "score":score}
        # Da kan man også skippe å definere self.name = name, ... etc

    # metode for å forandre verdi, ikke nødvendig for oppgaven, men fin for demonstrasjon.
    def change_attribute(self, attribute, value):
        self.movie[attribute] = value

    # Metode som returnerer verdien for forespurt attributt
    # (*2) Glemte at det ikke trengs en egen metode for å kalle på objekt-attributt/instansvariabel,
    #      Så denne metoden er unødvendig.
    def output_attribute(self, attribute):
        return self.movie[attribute]

    # B)
    # Denne trenger ingen argumenter, den henter verdiene rett fra objektets attributter
    # Oppdaget __str__ etter jeg lagde denne, men lar metoden stå.
    def output_object_string(self):
        return f"{self.movie['name']} was released in {self.movie['year']} and currently has a score of {self.movie['score']}"

    # eller!:
    def __str__(self): # denne gjør at python automatisk kaller denne hvis man prøver å behandle objektet som en streng:
        return f"{self.movie['name']} was released in {self.movie['year']} and currently has a score of {self.movie['score']}"



# Film-objekt konstrueres med attributtene: (name = string, year = int, score = float)
# Genererer objekter for hver film:
Inception = Film("Inception", 2010, 8.8)
The_Martian = Film("The Martian", 2015, 8.0)
Joker = Film("Joker", 2019, 8.4)

# Legger objektene i en liste for å iterere over dem:
movies = [Inception, The_Martian, Joker]

# Iterer over objektene og henter ut verdiene med 3 separate kall.
"""
(*2)
# Helt oversett eller glemt at man kunne kalle på objekets attributter direkte, endret kallene, men lar metoden stå
for movie in movies:
    print(f"{movie.output_attribute('name')} was released in {movie.output_attribute('year')} and currently has a score of {movie.output_attribute('score')}")
print()
"""

for movie in movies:
    print(f"{movie.movie['name']} was released in {movie.movie['year']} and currently has a score of {movie.movie['score']}")
print()

#================================================================================
# Output:
#================================================================================
# Inception was released in 2010 and currently has a score of 8.8
# The Martian was released in 2015 and currently has a score of 8.0
# Joker was released in 2019 and currently has a score of 8.4
#================================================================================

# Med change_attribute metoden kan ett objekt oppdateres dersom det skulle mangle en verdi ved generering:
# Genererer en film som mangler årstall
Going_Postal = Film(score=7.7, name="Going Postal") #Dette er egentlig en miniserie men ¯\_(ツ)_/¯

# Printer før og etter forandring:
print("Original input:")
print(Going_Postal.output_object_string())
print()

# Her forandres attributten "year":
Going_Postal.change_attribute("year", 2010)

print("Corrected input:")
print(Going_Postal.output_object_string())
print()
#================================================================================
# Output:
#================================================================================
# Original input:
# Going Postal was released in year and currently has a score of 7.7
#
# Corrected input:
# Going Postal was released in 2010 and currently has a score of 7.7
#================================================================================

movies.append(Going_Postal)

# B)
# Som man kan se over har output samme struktur som når vi kalte på hvert enkelt element, men nå er kallet for å få
# stringen mye renere enn å måtte ha en lang f-streng hver gang dette skal skrives ut.

# Men vi kan også ta i bruk __str__ metoden og behandle objektet som en streng:
for movie in movies:
    print(movie)

#================================================================================
# Output:
#================================================================================
# Inception was released in 2010 and currently has a score of 8.8
# The Martian was released in 2015 and currently has a score of 8.0
# Joker was released in 2019 and currently has a score of 8.4
# Going Postal was released in 2010 and currently has a score of 7.7
#================================================================================