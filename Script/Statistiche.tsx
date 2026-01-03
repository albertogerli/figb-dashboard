import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

interface Stats {
  generale?: Record<string, any>;
  demografiche?: Record<string, any>;
  regionali?: Record<string, any>;
  attivita?: Record<string, any>;
  punti?: Record<string, any>;
  categorie?: Record<string, any>;
  tipologie_tessera?: Record<string, any>;
  retention?: Record<string, any>;
  circoli?: Record<string, any>;
  per_anno?: Record<string, any>;
}

export default function Statistiche() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/results/statistiche_avanzate.json")
      .then((res) => res.json())
      .then((data) => {
        setStats(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Errore caricamento statistiche:", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-lg text-muted-foreground">Caricamento statistiche...</div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-lg text-destructive">Errore nel caricamento delle statistiche</div>
      </div>
    );
  }

  const formatValue = (value: any): string => {
    if (typeof value === 'number') {
      if (Number.isInteger(value)) {
        return value.toLocaleString('it-IT');
      }
      return value.toLocaleString('it-IT', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    return String(value);
  };

  const formatKey = (key: string): string => {
    return key
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (l) => l.toUpperCase());
  };

  const renderStatsTable = (data: Record<string, any>, title: string) => {
    const entries = Object.entries(data).filter(([key]) => !key.startsWith('_'));
    
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
          <CardDescription>{entries.length} metriche disponibili</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[60%]">Metrica</TableHead>
                  <TableHead className="text-right">Valore</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {entries.map(([key, value]) => (
                  <TableRow key={key}>
                    <TableCell className="font-medium">{formatKey(key)}</TableCell>
                    <TableCell className="text-right font-mono">{formatValue(value)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    );
  };

  const renderYearlyTable = (data: Record<string, any>) => {
    const years = Object.keys(data).sort();
    const metrics = Object.keys(data[years[0]] || {});

    return (
      <Card>
        <CardHeader>
          <CardTitle>Statistiche per Anno</CardTitle>
          <CardDescription>Confronto temporale 2017-2024</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="sticky left-0 bg-background">Metrica</TableHead>
                  {years.map((year) => (
                    <TableHead key={year} className="text-right">{year}</TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {metrics.map((metric) => (
                  <TableRow key={metric}>
                    <TableCell className="sticky left-0 bg-background font-medium">
                      {formatKey(metric)}
                    </TableCell>
                    {years.map((year) => (
                      <TableCell key={`${year}-${metric}`} className="text-right font-mono">
                        {formatValue(data[year][metric])}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Statistiche Avanzate</h2>
        <p className="text-muted-foreground mt-2">
          230+ metriche professionali per analisi approfondita
        </p>
      </div>

      <Card className="border-l-4 border-l-primary">
        <CardHeader>
          <CardTitle>Panoramica Statistiche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-muted rounded-lg">
              <div className="text-3xl font-bold text-primary">230+</div>
              <div className="text-sm text-muted-foreground mt-1">Metriche Totali</div>
            </div>
            <div className="text-center p-4 bg-muted rounded-lg">
              <div className="text-3xl font-bold text-chart-2">10</div>
              <div className="text-sm text-muted-foreground mt-1">Sezioni Analitiche</div>
            </div>
            <div className="text-center p-4 bg-muted rounded-lg">
              <div className="text-3xl font-bold text-chart-3">8</div>
              <div className="text-sm text-muted-foreground mt-1">Anni Analizzati</div>
            </div>
            <div className="text-center p-4 bg-muted rounded-lg">
              <div className="text-3xl font-bold text-chart-4">123.770</div>
              <div className="text-sm text-muted-foreground mt-1">Record Totali</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="generale" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5 lg:grid-cols-10">
          <TabsTrigger value="generale">Generale</TabsTrigger>
          <TabsTrigger value="anno">Per Anno</TabsTrigger>
          <TabsTrigger value="demografiche">Demografia</TabsTrigger>
          <TabsTrigger value="regionali">Regioni</TabsTrigger>
          <TabsTrigger value="attivita">Attività</TabsTrigger>
          <TabsTrigger value="punti">Punti</TabsTrigger>
          <TabsTrigger value="categorie">Categorie</TabsTrigger>
          <TabsTrigger value="tessere">Tessere</TabsTrigger>
          <TabsTrigger value="retention">Retention</TabsTrigger>
          <TabsTrigger value="circoli">Circoli</TabsTrigger>
        </TabsList>

        <TabsContent value="generale" className="space-y-4">
          {stats.generale && renderStatsTable(stats.generale, "Statistiche Generali")}
        </TabsContent>

        <TabsContent value="anno" className="space-y-4">
          {stats.per_anno && renderYearlyTable(stats.per_anno)}
        </TabsContent>

        <TabsContent value="demografiche" className="space-y-4">
          {stats.demografiche && renderStatsTable(stats.demografiche, "Statistiche Demografiche")}
        </TabsContent>

        <TabsContent value="regionali" className="space-y-4">
          {stats.regionali && renderStatsTable(stats.regionali, "Statistiche Regionali")}
        </TabsContent>

        <TabsContent value="attivita" className="space-y-4">
          {stats.attivita && renderStatsTable(stats.attivita, "Statistiche Attività")}
        </TabsContent>

        <TabsContent value="punti" className="space-y-4">
          {stats.punti && renderStatsTable(stats.punti, "Statistiche Punti")}
        </TabsContent>

        <TabsContent value="categorie" className="space-y-4">
          {stats.categorie && renderStatsTable(stats.categorie, "Statistiche Categorie")}
        </TabsContent>

        <TabsContent value="tessere" className="space-y-4">
          {stats.tipologie_tessera && renderStatsTable(stats.tipologie_tessera, "Statistiche Tipologie Tessera")}
        </TabsContent>

        <TabsContent value="retention" className="space-y-4">
          {stats.retention && renderStatsTable(stats.retention, "Statistiche Retention")}
        </TabsContent>

        <TabsContent value="circoli" className="space-y-4">
          {stats.circoli && renderStatsTable(stats.circoli, "Statistiche Circoli")}
        </TabsContent>
      </Tabs>

      <Card className="border-l-4 border-l-chart-2">
        <CardHeader>
          <CardTitle>Note Metodologiche</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <p>
            <strong>Fonte Dati:</strong> File Excel "Datidal17.xlsx" fornito dalla FIGB, contenente 
            123.770 record distribuiti su 8 anni (2017-2024).
          </p>
          <p>
            <strong>Tecniche Statistiche:</strong> Analisi descrittiva multivariata, analisi di coorte, 
            segmentazione demografica e comportamentale, analisi temporale con serie storiche.
          </p>
          <p>
            <strong>Software:</strong> Python 3.11 (pandas, numpy), React + TypeScript per visualizzazione.
          </p>
          <p>
            <strong>Validazione:</strong> Test di consistenza interna, verifica outlier e anomalie, 
            cross-validation con dati federali.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
