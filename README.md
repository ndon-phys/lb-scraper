# Introduction
This repository contains a number of scripts to download from major German schoolbook publishers

# Westermann (e.g. BiBox)
You need the book id and the authorization token.
You can get both by using Firefox Inspect and watching the network and looking for the book manifest to be transferred.
It has the url https://backend.bibox2.westermann.de/v1/api/sync/ followed by the book-id and some arguments.
The book-id is in the url and the token is the request header called "Authorization".

![grafik](https://github.com/user-attachments/assets/6f084f45-7c7c-4ef9-b3c4-d1a590509021)


# Cornelsen (all PSPDF-Kit Apps)
Again you need the book id (ISBN) and a token.
Use Firefox Inspect to look at a POST request for a url like https://pspdfkit.prod.cornelsen.de/i/d/[ISBN]/auth.
It shows the book-id / ISBN and the token is in the post request calles "jwt".

![grafik](https://github.com/user-attachments/assets/b97888e7-f93a-4c4e-80cc-284fc134caac)
