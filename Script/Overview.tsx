import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, TrendingDown, TrendingUp, Award, MapPin, Activity } from "lucide-react";

interface SummaryStats {
  periodo: string;
  totale_tesseramenti: number;
  giocatori_unici: number;
  circoli_unici: number;
  regioni: number;
  eta_media: number;
  eta_mediana: number;
  gare_media: number;
  punti_medi: number;
  percentuale_maschi: number;
  percentuale_femmine: number;
  retention_rate_medio: number;
}

export default function Overview() {
  const [stats, setStats] = useState<SummaryStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/results/summary_stats.json")
      .then((res) => res.json())
      .then((data) => {
        setStats(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Errore caricamento dati:", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-lg text-muted-foreground">Caricamento dati...</div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-lg text-destructive">Errore nel caricamento dei dati</div>
      </div>
    );
  }

  const kpiCards = [
    {
      title: "Giocatori Unici",
      value: stats.giocatori_unici.toLocaleString("it-IT"),
      description: "Dal 2017 al 2024",
      icon: <Users className="w-8 h-8 text-primary" />,
      trend: null,
    },
    {
      title: "Circoli Attivi",
      value: stats.circoli_unici.toLocaleString("it-IT"),
      description: "In tutta Italia",
      icon: <MapPin className="w-8 h-8 text-chart-2" />,
      trend: null,
    },
    {
      title: "Retention Rate Medio",
      value: `${stats.retention_rate_medio}%`,
      description: "Tasso di ritesseramento",
      icon: <TrendingUp className="w-8 h-8 text-chart-3" />,
      trend: stats.retention_rate_medio >= 80 ? "positive" : "negative",
    },
    {
      title: "Età Media",
      value: `${stats.eta_media} anni`,
      description: `Mediana: ${stats.eta_mediana} anni`,
      icon: <Award className="w-8 h-8 text-chart-4" />,
      trend: null,
    },
    {
      title: "Gare Medie",
      value: stats.gare_media.toLocaleString("it-IT"),
      description: "Per giocatore/anno",
      icon: <Activity className="w-8 h-8 text-chart-5" />,
      trend: null,
    },
    {
      title: "Punti Medi",
      value: Math.round(stats.punti_medi).toLocaleString("it-IT"),
      description: "Punti totali cumulati",
      icon: <TrendingUp className="w-8 h-8 text-primary" />,
      trend: null,
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Dashboard Overview</h2>
        <p className="text-muted-foreground mt-2">
          Analisi completa dei tesseramenti FIGB dal 2017 al 2024
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {kpiCards.map((kpi, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{kpi.title}</CardTitle>
              {kpi.icon}
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{kpi.value}</div>
              <p className="text-xs text-muted-foreground mt-1">{kpi.description}</p>
              {kpi.trend && (
                <div className="mt-2">
                  {kpi.trend === "positive" ? (
                    <span className="text-xs text-green-600 font-medium flex items-center gap-1">
                      <TrendingUp className="w-3 h-3" />
                      Positivo
                    </span>
                  ) : (
                    <span className="text-xs text-red-600 font-medium flex items-center gap-1">
                      <TrendingDown className="w-3 h-3" />
                      Attenzione
                    </span>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Distribuzione Sesso */}
      <Card>
        <CardHeader>
          <CardTitle>Distribuzione per Sesso</CardTitle>
          <CardDescription>Percentuale tesserati per genere</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Maschi</span>
                <span className="text-sm font-bold">{stats.percentuale_maschi}%</span>
              </div>
              <div className="w-full bg-secondary rounded-full h-3">
                <div
                  className="bg-primary h-3 rounded-full transition-all"
                  style={{ width: `${stats.percentuale_maschi}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Femmine</span>
                <span className="text-sm font-bold">{stats.percentuale_femmine}%</span>
              </div>
              <div className="w-full bg-secondary rounded-full h-3">
                <div
                  className="bg-chart-2 h-3 rounded-full transition-all"
                  style={{ width: `${stats.percentuale_femmine}%` }}
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Grafici Statici */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Trend Tesseramenti</CardTitle>
            <CardDescription>Evoluzione 2017-2024</CardDescription>
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
            <CardTitle>Distribuzione Regionale</CardTitle>
            <CardDescription>Top 15 regioni per tesserati 2024</CardDescription>
          </CardHeader>
          <CardContent>
            <img
              src="/charts/02_distribuzione_regionale.png"
              alt="Distribuzione Regionale"
              className="w-full h-auto rounded-lg"
            />
          </CardContent>
        </Card>
      </div>

      {/* Insights */}
      <Card className="border-l-4 border-l-primary">
        <CardHeader>
          <CardTitle>Insights Principali</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-primary mt-2" />
            <p className="text-sm">
              <strong>Trend decrescente:</strong> I tesseramenti sono passati da circa 19.800 nel 2018-2019 
              a 13.461 nel 2024, con un calo significativo nel periodo 2020-2021 (impatto COVID-19).
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-3 mt-2" />
            <p className="text-sm">
              <strong>Retention positivo:</strong> Il tasso medio di ritesseramento è dell'{stats.retention_rate_medio}%, 
              indicando una buona fedeltà dei giocatori esistenti.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-2 mt-2" />
            <p className="text-sm">
              <strong>Età avanzata:</strong> L'età media di {stats.eta_media} anni suggerisce la necessità 
              di strategie di acquisizione mirate ai giovani.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-chart-4 mt-2" />
            <p className="text-sm">
              <strong>Equilibrio di genere:</strong> La distribuzione tra maschi ({stats.percentuale_maschi}%) 
              e femmine ({stats.percentuale_femmine}%) è relativamente bilanciata.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
