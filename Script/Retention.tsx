import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Retention() {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Retention Rate</h2>
        <p className="text-muted-foreground mt-2">
          Analisi del tasso di ritesseramento anno su anno
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Tasso di Ritesseramento Anno su Anno</CardTitle>
          <CardDescription>Percentuale di giocatori che si ritesserano l'anno successivo</CardDescription>
        </CardHeader>
        <CardContent>
          <img
            src="/charts/04_retention_rate.png"
            alt="Retention Rate"
            className="w-full h-auto rounded-lg"
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Retention Rate per Fascia d'Età</CardTitle>
          <CardDescription>Tasso medio di ritesseramento per fascia d'età (2017-2023)</CardDescription>
        </CardHeader>
        <CardContent>
          <img
            src="/charts/05_retention_per_eta.png"
            alt="Retention per Età"
            className="w-full h-auto rounded-lg"
          />
        </CardContent>
      </Card>

      <Card className="border-l-4 border-l-chart-3">
        <CardHeader>
          <CardTitle>Analisi Retention - Key Findings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-3 mt-2" />
            <p className="text-sm">
              <strong>Retention elevato pre-COVID:</strong> Nel periodo 2017-2019, il tasso di ritesseramento 
              si attestava tra l'83% e l'88%, indicando una base di giocatori molto fedele.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-destructive mt-2" />
            <p className="text-sm">
              <strong>Crollo 2020:</strong> Il retention rate è sceso al 64.92% nel 2020, il valore più basso 
              del periodo analizzato, a causa delle restrizioni pandemiche e della chiusura dei circoli.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-3 mt-2" />
            <p className="text-sm">
              <strong>Recupero post-pandemia:</strong> Dal 2021 in poi, il retention rate è tornato 
              sopra l'84%, dimostrando la resilienza della community bridgistica.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-primary mt-2" />
            <p className="text-sm">
              <strong>Anziani più fedeli:</strong> Le fasce d'età 60-70, 70-80 e 80-90 mostrano i tassi 
              di retention più alti (88-91%), confermando la loro dedizione allo sport.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-destructive mt-2" />
            <p className="text-sm">
              <strong>Giovani a rischio:</strong> Le fasce under 18 (37%) e 18-30 (29-48%) hanno retention 
              molto bassi, evidenziando difficoltà nel mantenere i giovani giocatori nel lungo periodo.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-2 mt-2" />
            <p className="text-sm">
              <strong>Problema strutturale:</strong> Nonostante l'alto retention complessivo, il numero 
              di nuovi acquisiti non compensa i giocatori persi, causando il trend decrescente generale.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
