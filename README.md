# Targa Scanner — configurazione remota

## Pannello Windows
Apri **AVVIA-PANNELLO.cmd** dal repository estratto per usare interruttori e campi senza modificare JSON. Rilettura dello stato corrente, riepilogo prima della pubblicazione, revisione automatica e controllo dei conflitti. Istruzioni: [pannello/LEGGIMI.md](pannello/LEGGIMI.md). Serve un token personale limitato a questo repository con Contents in lettura/scrittura; non la chiave privata di firma.

Questo repository pubblico contiene solo configurazione e strumenti di firma. Il codice iOS resta privato. Nessuna targa o informazione sugli utenti viene inviata qui dall'app.

## Prima attivazione su Windows
1. Usa **Code → Download ZIP**, estrai lo ZIP e apri `SETUP-WINDOWS.cmd`.
2. Lo script genera la chiave privata **sul tuo PC**, ne conserva una copia nella tua cartella utente e la copia negli appunti. Non inviarla in chat e non caricarla nei file del repository.
3. Vai in **Settings → Secrets and variables → Actions → New repository secret**. Nome `REMOTE_CONFIG_SIGNING_KEY`; nel valore incolla dagli appunti. Salva.
4. Vai in **Actions → Pubblica configurazione firmata → Run workflow**. Dopo il successo compaiono `config-signed.json` e `public-key.txt`.
5. URL e chiave pubblica sono già incorporati nell’app dalla versione **3.92 (194)**: avvia la build Codemagic del ramo `build/iphone-ipa` e installala. Non devi impostare variabili Codemagic.

## Modifiche successive
Modifica `config.json`, aumenta `config_revision` e salva. La procedura GitHub Actions firma e pubblica automaticamente. L'app controlla all'avvio/rientro con intervallo minimo di 30 minuti e conserva l'ultima configurazione valida. Se il workflow fallisce, il file firmato precedente resta invariato.

La chiave privata deve rimanere la stessa: cambiarla richiede una nuova build dell'app con la nuova chiave pubblica. Conserva una copia privata sicura del file generato.

## Comandi supportati dalla 3.91
Blocchi generali e manutenzione (`app_control`), versioni minime (`version_control` con `force_update`), paesi (`countries`, GB per UK), banner/avviso bloccante (`notices`), codici installazione (`access_control.blocked_installation_tokens`), interruttori dei controlli italiani e categorie (`features`), blocco nuove ricerche e cooldown italiano (`search`).

Gli altri campi del JSON sono preparatori e non operativi: endpoint, connettori/fallback, parametri CAPTCHA, parallelismo/timeout, StoreKit/quote, flags e singole funzioni estere. Non cambiano prezzi o abbonamenti.

I codici installazione sono pseudonimi: non aggiungere nomi o dati personali al file pubblico. I blocchi locali non sono una protezione contro IPA modificate o reinstallazioni.
