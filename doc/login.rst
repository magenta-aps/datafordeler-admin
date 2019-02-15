Login i DAFO Admin
==================

For at få adgang til funktionaliteten i DAFO Admin er det nødvendigt at logge
ind i systemet. Dette kan ske på to måder:

* Ved at angive brugernavn og adgangskode for en bruger registreret i systemet
  med passende rettigheder
* Ved at logge ind via en ekstern SAML Identity Provider for en organisation
  der er registreret i systemet med passende rettigheder

Med "passende rettigheder" forstås at den identificerede bruger/IdP gennem
brugerprofiler er blevet tildelt adgang til enten ``DAFO Administrator``
systemrollen eller ``DAFO Serviceudbyder`` systemrollen. Hvis du får en fejl
``403 Forbidden`` efter login skyldes det sandsynligvis at din bruger ikke er
konfigureret med en af disse roller.


Login via Brugernavn og Adgangskode
-----------------------------------

For at logge ind via brugernavn og adgangskode klikkes på "Log ind" ikonet i
øverste højre hjørne.

.. image:: static/login_button.png

Hvis ikke fanebladet med "Brugernavn og kodeord" er
aktivt klikkes der på dette. Derefter udfyldes brugernavn og adganskode
felterne og der klikkes på "LOG IND".



Login via Organisation
----------------------

For at logge ind via organisation klikkes på "Log ind" ikonet i øverst højre
hjørne. Hvis fanebladet "Organisation login" ikke er aktivt klikkes på dette.
Derefter vælges den ønskede organisation i dropdown'en og der klikkes på
"LOG IND".

Systemet viderestiller herefter til **DAFO STS**, hvor der eventuelt skal
foretages et login i den eksterne IdP der er tilknyttet den valgte
organisation. Ved successfuldt login og udstedelse af token fra STS'en
returneres brugeren til DAFO Admin og logges ind.

Logout
------

For at logge ud af DAFO Admin klikkes på "Log ud" knappen i øverste højre
hjørne. Vær opmærksom på at dette kun logger ud af DAFO Admin og ikke ud fra
en eventuel ekstern IdP brugt ved login via organisation.

