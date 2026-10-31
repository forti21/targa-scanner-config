# Pannello amministratore Windows

## Aprire
Scarica il repository con **Code → Download ZIP**, estrailo e fai doppio clic su **AVVIA-PANNELLO.cmd**. Usa lo stesso Python già installato per la configurazione della firma; non occorrono altri pacchetti. Se l'installazione di Python non include Tcl/Tk, aggiungi il componente Tcl/Tk dall'installer ufficiale.

## Primo collegamento
Premi **Rileggi da GitHub**: la lettura pubblica non richiede credenziali. Per poter salvare:
1. Apri <https://github.com/settings/personal-access-tokens/new>.
2. Dai un nome al token, per esempio `Pannello Targa Scanner`, e scegli una scadenza.
3. In Repository access scegli **Only select repositories** e seleziona soltanto **targa-scanner-config**.
4. In Repository permissions assegna **Contents → Read and write**. Non servono Secrets, Administration o Workflows.
5. Genera il token e incollalo nel campo **Token GitHub** del pannello. Non inviarlo in chat. Il programma non lo salva: rimane in memoria finché la finestra è aperta.

Il token del pannello e la chiave privata di firma sono due cose diverse: non inserire la chiave privata nel pannello. GitHub Actions continua a firmare usando il secret già configurato.

## Uso
1. **Rileggi da GitHub** prima di lavorare.
2. Cambia interruttori, messaggi, versione minima o codici installazione.
3. Premi **Rivedi modifiche e pubblica**. Controlla il riepilogo e premi **Conferma: salva e pubblica**.
4. Il pannello aumenta la revisione e salva il JSON; poi controlla che il workflow abbia pubblicato il payload nel file firmato. Se la firma non arriva, usa **Stato firma su GitHub**. Un salvataggio del JSON non è ancora la conferma di una pubblicazione firmata.

Il confronto con lo SHA letto impedisce di sovrascrivere modifiche fatte nel frattempo. In caso di conflitto rileggi il file e riapplica le modifiche. I campi che il pannello non gestisce sono conservati, non ricreati da un modello.

I controlli della scheda **Controlli Italia** agiscono sull'Italia. La scheda **Paesi** agisce sull'intero paese. Le voci preparatorie del JSON che l'app non implementa non sono proposte. Per bloccare una singola installazione incolla solo il codice copiato dall'app, uno per riga: non scrivere nomi nel file pubblico.

L'app deve avere almeno la build 3.92 (194) con il feed collegato. Le ricerche già avviate non vengono annullate; le modifiche si applicano dopo il prossimo aggiornamento della configurazione, con intervallo minimo di 30 minuti fra tentativi nella sessione.

## Verifiche
`python pannello/test_core.py`: verifica conservazione dei campi, incremento revisioni, validazione, codici, conflitti e richieste di salvataggio. L'interfaccia Tkinter deve essere provata sul PC Windows; i test automatici non simulano il desktop Windows.
