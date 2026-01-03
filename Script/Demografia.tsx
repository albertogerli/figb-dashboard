import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Demografia() {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Analisi Demografica</h2>
        <p className="text-muted-foreground mt-2">
          Distribuzione per fascia d'età, sesso e livello di attività
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Piramide dell'Età per Sesso - 2024</CardTitle>
          <CardDescription>Distribuzione tesserati per fascia d'età e genere</CardDescription>
        </CardHeader>
        <CardContent>
          <img
            src="/charts/03_piramide_eta.png"
            alt="Piramide Età"
            className="w-full h-auto rounded-lg"
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Attività Media per Fascia d'Età - 2024</CardTitle>
          <CardDescription>Numero medio di gare giocate per fascia d'età</CardDescription>
        </CardHeader>
        <CardContent>
          <img
            src="/charts/09_gare_per_eta.png"
            alt="Gare per Età"
            className="w-full h-auto rounded-lg"
          />
        </CardContent>
      </Card>

      <Card className="border-l-4 border-l-primary">
        <CardHeader>
          <CardTitle>Analisi Demografica - Key Findings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-destructive mt-2" />
            <p className="text-sm">
              <strong>Popolazione anziana:</strong> La maggior parte dei tesserati si concentra nelle fasce 
              70-80 e 80-90 anni, evidenziando un problema di invecchiamento della base giocatori.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-destructive mt-2" />
            <p className="text-sm">
              <strong>Carenza di giovani:</strong> Le fasce under 18, 18-30 e 30-40 sono drammaticamente 
              sottorappresentate, con numeri molto bassi che mettono a rischio il futuro del movimento.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-primary mt-2" />
            <p className="text-sm">
              <strong>Equilibrio di genere:</strong> La distribuzione tra maschi e femmine è relativamente 
              bilanciata in tutte le fasce d'età, un aspetto positivo per l'inclusività dello sport.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-3 mt-2" />
            <p className="text-sm">
              <strong>Attività correlata all'età:</strong> I giocatori più giovani (quando presenti) 
              tendono a giocare meno gare, mentre le fasce 60-80 mostrano il maggior livello di attività.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-2 mt-2" />
            <p className="text-sm">
              <strong>Urgenza strategica:</strong> È necessaria una strategia di acquisizione mirata 
              ai giovani (scuole, università, marketing digitale) per garantire la sostenibilità futura.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
