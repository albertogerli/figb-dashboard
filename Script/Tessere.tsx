import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Tessere() {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Tipologie Tessera</h2>
        <p className="text-muted-foreground mt-2">
          Analisi delle diverse tipologie di tesseramento FIGB
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Distribuzione Tipologie Tessera - 2024</CardTitle>
          <CardDescription>Percentuale di tesserati per tipo di tessera</CardDescription>
        </CardHeader>
        <CardContent>
          <img
            src="/charts/06_tipologie_tessera.png"
            alt="Tipologie Tessera"
            className="w-full h-auto rounded-lg"
          />
        </CardContent>
      </Card>

      <Card className="border-l-4 border-l-primary">
        <CardHeader>
          <CardTitle>Descrizione Tipologie Tessera</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-muted rounded-lg">
              <h4 className="font-semibold mb-2">Ordinario Sportivo</h4>
              <p className="text-sm text-muted-foreground">
                Tessera standard per giocatori regolari che partecipano a tornei e attività del circolo. 
                Rappresenta la maggioranza dei tesserati (54.7% nel 2024).
              </p>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <h4 className="font-semibold mb-2">Agonista</h4>
              <p className="text-sm text-muted-foreground">
                Tessera per giocatori competitivi che partecipano regolarmente a tornei ufficiali 
                e campionati. Secondo gruppo più numeroso (19.9% nel 2024).
              </p>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <h4 className="font-semibold mb-2">Scuola Bridge</h4>
              <p className="text-sm text-muted-foreground">
                Tessera per partecipanti ai corsi di bridge, generalmente principianti. 
                Importante canale di acquisizione (11.8% nel 2024).
              </p>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <h4 className="font-semibold mb-2">Ordinario Amatoriale</h4>
              <p className="text-sm text-muted-foreground">
                Tessera per giocatori occasionali o ricreativi che non partecipano a tornei ufficiali. 
                Rappresenta il 9.5% dei tesserati nel 2024.
              </p>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <h4 className="font-semibold mb-2">Non Agonista</h4>
              <p className="text-sm text-muted-foreground">
                Tessera per giocatori che pur avendo competenze non partecipano a competizioni ufficiali. 
                Circa 2% dei tesserati.
              </p>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <h4 className="font-semibold mb-2">Ist. Scolastici / Studente CAS</h4>
              <p className="text-sm text-muted-foreground">
                Tessere speciali per studenti e istituzioni scolastiche, parte delle iniziative 
                di promozione del bridge nelle scuole.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="border-l-4 border-l-chart-2">
        <CardHeader>
          <CardTitle>Analisi Tipologie Tessera - Key Findings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-primary mt-2" />
            <p className="text-sm">
              <strong>Ordinario Sportivo dominante:</strong> Oltre la metà dei tesserati (54.7%) 
              ha una tessera Ordinario Sportivo, confermando il bridge come attività sportiva regolare.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-2 mt-2" />
            <p className="text-sm">
              <strong>Agonisti attivi:</strong> Gli Agonisti (19.9%) giocano in media 70 gare all'anno 
              e hanno punti medi molto alti (44.419), dimostrando alto engagement e competenza.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-3 mt-2" />
            <p className="text-sm">
              <strong>Scuola Bridge: canale critico:</strong> Le tessere Scuola Bridge (11.8%) 
              rappresentano il principale canale di acquisizione, ma hanno basso retention (vedi sezione Churn).
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-4 mt-2" />
            <p className="text-sm">
              <strong>Amatoriali meno attivi:</strong> Gli Ordinari Amatoriali giocano in media 
              26 gare/anno (vs 44 degli Sportivi), suggerendo un engagement più casual.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-5 mt-2" />
            <p className="text-sm">
              <strong>Ist. Scolastici in calo:</strong> Le tessere per istituzioni scolastiche sono 
              diminuite significativamente, passando da centinaia negli anni pre-COVID a poche decine nel 2024.
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Confronto Attività per Tipologia Tessera (2024)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-4 text-sm font-semibold border-b pb-2">
              <div>Tipologia</div>
              <div className="text-right">Gare Medie</div>
              <div className="text-right">Punti Medi</div>
            </div>
            <div className="grid grid-cols-3 gap-4 text-sm items-center">
              <div>Agonista</div>
              <div className="text-right font-mono">69.8</div>
              <div className="text-right font-mono">44,419</div>
            </div>
            <div className="grid grid-cols-3 gap-4 text-sm items-center bg-muted/50 p-2 rounded">
              <div>Non Agonista</div>
              <div className="text-right font-mono">60.7</div>
              <div className="text-right font-mono">21,839</div>
            </div>
            <div className="grid grid-cols-3 gap-4 text-sm items-center">
              <div>Ordinario Sportivo</div>
              <div className="text-right font-mono">43.7</div>
              <div className="text-right font-mono">7,913</div>
            </div>
            <div className="grid grid-cols-3 gap-4 text-sm items-center bg-muted/50 p-2 rounded">
              <div>Ordinario Amatoriale</div>
              <div className="text-right font-mono">26.6</div>
              <div className="text-right font-mono">3,247</div>
            </div>
            <div className="grid grid-cols-3 gap-4 text-sm items-center">
              <div>Scuola Bridge</div>
              <div className="text-right font-mono">21.1</div>
              <div className="text-right font-mono">462</div>
            </div>
            <div className="grid grid-cols-3 gap-4 text-sm items-center bg-muted/50 p-2 rounded">
              <div>Normale</div>
              <div className="text-right font-mono">12.4</div>
              <div className="text-right font-mono">3,096</div>
            </div>
            <div className="grid grid-cols-3 gap-4 text-sm items-center">
              <div>Aderente</div>
              <div className="text-right font-mono">6.7</div>
              <div className="text-right font-mono">1,978</div>
            </div>
            <div className="grid grid-cols-3 gap-4 text-sm items-center bg-muted/50 p-2 rounded">
              <div>Ist. Scolastici</div>
              <div className="text-right font-mono">1.3</div>
              <div className="text-right font-mono">5</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
