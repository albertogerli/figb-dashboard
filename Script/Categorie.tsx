import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Categorie() {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Analisi Categorie</h2>
        <p className="text-muted-foreground mt-2">
          Distribuzione per categorie d'età (CatLabel) e livello di competenza
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Evoluzione Categorie nel Tempo</CardTitle>
          <CardDescription>Heatmap delle top 15 categorie 2017-2024</CardDescription>
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
          <CardTitle>Sistema di Categorizzazione FIGB</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h4 className="font-semibold mb-2">Categorie per Livello di Competenza:</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              <div className="p-3 bg-muted rounded-lg">
                <strong>NC (Non Classificato):</strong> Giocatori senza punti o con punteggio minimo
              </div>
              <div className="p-3 bg-muted rounded-lg">
                <strong>4Q, 4P, 4F, 4C:</strong> Quarta categoria (livello base)
              </div>
              <div className="p-3 bg-muted rounded-lg">
                <strong>3Q, 3P, 3F, 3C:</strong> Terza categoria (livello intermedio)
              </div>
              <div className="p-3 bg-muted rounded-lg">
                <strong>2Q, 2P, 2F, 2C:</strong> Seconda categoria (livello avanzato)
              </div>
              <div className="p-3 bg-muted rounded-lg">
                <strong>1Q, 1P, 1F, 1C:</strong> Prima categoria (livello esperto)
              </div>
              <div className="p-3 bg-muted rounded-lg">
                <strong>LM, HQ, HK, HJ, HA, GM, MS:</strong> Categorie speciali e master
              </div>
            </div>
          </div>
          
          <div className="pt-4 border-t">
            <p className="text-sm text-muted-foreground">
              <strong>Nota:</strong> Le lettere Q, P, F, C indicano sottocategorie basate sul punteggio 
              specifico all'interno di ciascuna categoria principale.
            </p>
          </div>
        </CardContent>
      </Card>

      <Card className="border-l-4 border-l-chart-2">
        <CardHeader>
          <CardTitle>Analisi Categorie - Key Findings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-primary mt-2" />
            <p className="text-sm">
              <strong>NC dominante:</strong> La categoria "Non Classificato" è la più numerosa, 
              indicando molti giocatori occasionali o principianti che non accumulano punti significativi.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-2 mt-2" />
            <p className="text-sm">
              <strong>Terza categoria popolare:</strong> Le categorie 3F, 3P, 3C, 3Q rappresentano 
              il cuore del movimento, con giocatori intermedi attivi e costanti.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-3 mt-2" />
            <p className="text-sm">
              <strong>Elite ristretta:</strong> Le categorie 1C, 1F, 1P, 1Q e le categorie speciali 
              (LM, HQ) sono numericamente limitate, come atteso per i livelli più alti.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-4 mt-2" />
            <p className="text-sm">
              <strong>Stabilità temporale:</strong> La distribuzione delle categorie rimane relativamente 
              stabile nel tempo, con variazioni proporzionali al numero totale di tesserati.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
