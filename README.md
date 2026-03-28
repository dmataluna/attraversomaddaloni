# Maddaloni attraverso i tuoi occhi — Dashboard

## Struttura del progetto

```
├── maddaloni_dashboard.py          # App principale Streamlit
├── requirements.txt                # Dipendenze Python
├── Maddaloni_..._Risposte.csv      # Dataset (stesso nome del file originale)
└── README.md
```

## Deploy su Streamlit Cloud

1. Crea un repository GitHub con questi file
2. Accedi a [share.streamlit.io](https://share.streamlit.io)
3. Connetti il repo e imposta `maddaloni_dashboard.py` come file principale
4. Il CSV deve essere nella stessa cartella dell'app **oppure** caricato manualmente dalla sidebar

## Run locale

```bash
pip install -r requirements.txt
streamlit run maddaloni_dashboard.py
```

## Funzionalità

| Tab | Contenuto |
|-----|-----------|
| 📊 Profilo Semantico | Differenziale Semantico −2/+2, statistiche descrittive, personaggio |
| 🔥 Heatmap Correlazione | r di Pearson interattiva + tabella top correlazioni con p-value |
| 🕸️ Radar Chart | Profilo identitario segmentato per età o rapporto con la città |
| 🔭 Gap Analysis | Polarità attuali vs aggettivi desiderati per il futuro |
| 🔬 Analisi per Segmento | Boxplot per fascia d'età + ANOVA one-way |

Ogni grafico è **esportabile in PNG alta risoluzione** (scala 3×, ~300 dpi).

## Metodologia

- **Differenziale Semantico** (Osgood, 1957): scala bipolare da −2 a +2
- **Correlazione**: r di Pearson con test di significatività
- **ANOVA one-way**: verifica differenze tra fasce d'età
- **Filtri**: per fascia d'età e tipo di rapporto con la città
