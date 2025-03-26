# Weer App

Een interactieve weer-app gebouwd met Streamlit die het huidige weer en weersvoorspellingen toont voor elke stad ter wereld.

## Features

- Huidig weer met temperatuur, luchtvochtigheid en windsnelheid
- 5-daagse weersvoorspelling
- Interactieve weerkaart
- Favoriete steden beheren
- Responsive design voor mobiel en desktop

## Installatie

1. Clone de repository:
```bash
git clone [repository-url]
cd weer-app
```

2. Installeer de dependencies:
```bash
pip install -r requirements.txt
```

3. Start de app:
```bash
streamlit run app.py
```

## Gebruik

1. Voer een stad in in de zoekbalk
2. Bekijk het huidige weer op de home pagina
3. Gebruik het menu om te navigeren tussen verschillende weergaven
4. Voeg steden toe aan je favorieten voor snelle toegang

## Deployment

De app is geconfigureerd voor deployment op Streamlit Cloud:

1. Push je code naar een GitHub repository
2. Ga naar [share.streamlit.io](https://share.streamlit.io)
3. Log in met je GitHub account
4. Selecteer je repository
5. Deploy de app

## Technische Details

- Gebruikt de OpenWeatherMap API voor weergegevens
- Gebouwd met Streamlit en Python
- Responsive design met custom CSS
- Lokale opslag voor favoriete steden 