import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Churn() {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Churn Analysis</h2>
        <p className="text-muted-foreground mt-2">
          Analisi dei mancati ritesseramenti per fascia d'età e tipologia tessera
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Distribuzione Mancati Ritesseramenti per Fascia d'Età</CardTitle>
          <CardDescription>Giocatori persi anno su anno per fascia d'età</CardDescription>
        </CardHeader>
        <CardContent>
          <img
            src="/charts/08_churn_per_eta.png"
            alt="Churn per Età"
            className="w-full h-auto rounded-lg"
          />
        </CardContent>
      </Card>

      <Card className="border-l-4 border-l-destructive">
        <CardHeader>
          <CardTitle>Churn Analysis - Key Findings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-destructive mt-2" />
            <p className="text-sm">
              <strong>Picco di churn 2019-2020:</strong> Il periodo della pandemia ha visto il maggior 
              numero di mancati ritesseramenti, con quasi 5.000 giocatori persi nel 2019-2020.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-4 mt-2" />
            <p className="text-sm">
              <strong>Anziani più colpiti in volume:</strong> Le fasce 70-80 e 80-90 rappresentano 
              il maggior numero assoluto di giocatori persi, essendo anche le più numerose.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-2 mt-2" />
            <p className="text-sm">
              <strong>Giovani: churn percentuale alto:</strong> Anche se in numeri assoluti bassi, 
              le fasce under 30 mostrano tassi di abbandono percentuali molto elevati (50-70%).
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-primary mt-2" />
            <p className="text-sm">
              <strong>Tipologie tessera a rischio:</strong> I tesserati "Scuola Bridge" e "Ist. Scolastici" 
              mostrano tassi di churn molto alti, suggerendo difficoltà nel convertire principianti in giocatori stabili.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-3 mt-2" />
            <p className="text-sm">
              <strong>Agonisti e Ordinari Sportivi più stabili:</strong> Le tessere "Agonista" e 
              "Ordinario Sportivo" hanno retention migliori, indicando che l'engagement competitivo aumenta la fedeltà.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-5 mt-2" />
            <p className="text-sm">
              <strong>Mortalità naturale:</strong> Una parte significativa del churn nelle fasce 80-90 e 90+ 
              è probabilmente dovuta a cause naturali, non a disaffezione allo sport.
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Raccomandazioni per Ridurre il Churn</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-4 bg-primary/10 rounded-lg border-l-4 border-primary">
            <h4 className="font-semibold mb-2">1. Programmi di Retention per Giovani</h4>
            <p className="text-sm text-muted-foreground">
              Creare percorsi dedicati per under 30 con tornei, eventi sociali e mentorship 
              per aumentare l'engagement e ridurre l'abbandono precoce.
            </p>
          </div>
          <div className="p-4 bg-chart-2/10 rounded-lg border-l-4 border-chart-2">
            <h4 className="font-semibold mb-2">2. Follow-up Scuole Bridge</h4>
            <p className="text-sm text-muted-foreground">
              Implementare programmi di follow-up strutturati per i partecipanti alle scuole bridge, 
              con incentivi per il primo anno di tesseramento completo.
            </p>
          </div>
          <div className="p-4 bg-chart-3/10 rounded-lg border-l-4 border-chart-3">
            <h4 className="font-semibold mb-2">3. Engagement Digitale</h4>
            <p className="text-sm text-muted-foreground">
              Sviluppare piattaforme online per mantenere l'engagement anche quando i giocatori 
              non possono frequentare fisicamente i circoli (lezioni, tornei online, community).
            </p>
          </div>
          <div className="p-4 bg-chart-4/10 rounded-lg border-l-4 border-chart-4">
            <h4 className="font-semibold mb-2">4. Analisi Predittiva</h4>
            <p className="text-sm text-muted-foreground">
              Identificare i segnali di rischio churn (calo frequenza gare, inattività prolungata) 
              e intervenire proattivamente con contatti personalizzati.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
