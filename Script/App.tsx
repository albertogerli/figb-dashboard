import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import DashboardLayout from "./components/DashboardLayout";
import Overview from "./pages/Overview";
import Temporale from "./pages/Temporale";
import Regionale from "./pages/Regionale";
import Demografia from "./pages/Demografia";
import Categorie from "./pages/Categorie";
import Retention from "./pages/Retention";
import Churn from "./pages/Churn";
import Tessere from "./pages/Tessere";
import Statistiche from "./pages/Statistiche";

function Router() {
  return (
    <DashboardLayout>
      <Switch>
        <Route path="/" component={Overview} />
        <Route path="/temporale" component={Temporale} />
        <Route path="/regionale" component={Regionale} />
        <Route path="/demografia" component={Demografia} />
        <Route path="/categorie" component={Categorie} />
        <Route path="/retention" component={Retention} />
        <Route path="/churn" component={Churn} />
        <Route path="/tessere" component={Tessere} />
        <Route path="/statistiche" component={Statistiche} />
        <Route path="/404" component={NotFound} />
        <Route component={NotFound} />
      </Switch>
    </DashboardLayout>
  );
}

// NOTE: About Theme
// - First choose a default theme according to your design style (dark or light bg), than change color palette in index.css
//   to keep consistent foreground/background color across components
// - If you want to make theme switchable, pass `switchable` ThemeProvider and use `useTheme` hook

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider
        defaultTheme="light"
        // switchable
      >
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
