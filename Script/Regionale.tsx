import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Regionale() {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Analisi Regionale</h2>
        <p className="text-muted-foreground mt-2">
          Distribuzione geografica dei tesseramenti per regione
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Top 15 Regioni per Tesserati - 2024</CardTitle>
          <CardDescription>Classifica delle regioni più attive</CardDescription>
        </CardHeader>
        <CardContent>
          <img
            src="/charts/02_distribuzione_regionale.png"
            alt="Distribuzione Regionale"
            className="w-full h-auto rounded-lg"
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Evoluzione Temporale Top 5 Regioni</CardTitle>
          <CardDescription>Trend 2017-2024 delle regioni principali</CardDescription>
        </CardHeader>
        <CardContent>
          <img
            src="/charts/10_trend_regionale.png"
            alt="Trend Regionale"
            className="w-full h-auto rounded-lg"
          />
        </CardContent>
      </Card>

      <Card className="border-l-4 border-l-primary">
        <CardHeader>
          <CardTitle>Analisi Regionale - Key Findings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-primary mt-2" />
            <p className="text-sm">
              <strong>Lazio dominante:</strong> La regione Lazio guida con un ampio margine, 
              concentrando una parte significativa dei tesserati nazionali (Roma come hub principale).
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-2 mt-2" />
            <p className="text-sm">
              <strong>Nord forte:</strong> Lombardia, Emilia-Romagna, Piemonte e Veneto rappresentano 
              i principali bacini del Nord Italia, con una tradizione consolidata nel bridge.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-3 mt-2" />
            <p className="text-sm">
              <strong>Toscana e Liguria:</strong> Regioni del Centro-Nord con una presenza significativa, 
              beneficiando di circoli storici e una base di giocatori fedele.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-4 mt-2" />
            <p className="text-sm">
              <strong>Sud e Isole sottorappresentati:</strong> Campania, Sicilia, Puglia e Calabria 
              mostrano numeri inferiori, suggerendo opportunità di sviluppo territoriale.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-5 mt-2" />
            <p className="text-sm">
              <strong>Concentrazione urbana:</strong> Le grandi città (Roma, Milano, Bologna, Torino, Firenze) 
              concentrano la maggior parte dell'attività bridgistica nazionale.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
