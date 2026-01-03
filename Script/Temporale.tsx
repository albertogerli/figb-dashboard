import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Temporale() {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Analisi Temporale</h2>
        <p className="text-muted-foreground mt-2">
          Evoluzione dei tesseramenti e delle attività dal 2017 al 2024
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Trend Tesseramenti nel Tempo</CardTitle>
          <CardDescription>Numero di tesserati per anno</CardDescription>
        </CardHeader>
        <CardContent>
          <img
            src="/charts/01_trend_tesseramenti.png"
            alt="Trend Tesseramenti"
            className="w-full h-auto rounded-lg"
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Evoluzione Top 5 Regioni</CardTitle>
          <CardDescription>Confronto temporale delle regioni principali</CardDescription>
        </CardHeader>
        <CardContent>
          <img
            src="/charts/10_trend_regionale.png"
            alt="Trend Regionale"
            className="w-full h-auto rounded-lg"
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Heatmap Categorie per Anno</CardTitle>
          <CardDescription>Evoluzione delle top 15 categorie nel tempo</CardDescription>
        </CardHeader>
        <CardContent>
          <img
            src="/charts/07_heatmap_categorie.png"
            alt="Heatmap Categorie"
            className="w-full h-auto rounded-lg"
          />
        </CardContent>
      </Card>

      <Card className="border-l-4 border-l-primary">
        <CardHeader>
          <CardTitle>Analisi Temporale - Key Findings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-primary mt-2" />
            <p className="text-sm">
              <strong>Picco 2018-2019:</strong> I tesseramenti hanno raggiunto il massimo con circa 19.800 tesserati, 
              rappresentando il periodo di maggiore crescita della federazione.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-destructive mt-2" />
            <p className="text-sm">
              <strong>Crollo 2020-2021:</strong> Il periodo pandemico ha causato un calo drastico, 
              con i tesseramenti che sono scesi a 11.655 nel 2021 (-40% rispetto al 2019).
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-3 mt-2" />
            <p className="text-sm">
              <strong>Ripresa parziale 2022-2024:</strong> Si osserva una ripresa graduale ma i numeri 
              pre-pandemia non sono ancora stati recuperati (13.461 tesserati nel 2024).
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-2 mt-2" />
            <p className="text-sm">
              <strong>Stabilità regionale:</strong> Le regioni principali (Lazio, Lombardia, Emilia-Romagna) 
              mantengono la loro posizione dominante nel tempo, con trend paralleli.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
