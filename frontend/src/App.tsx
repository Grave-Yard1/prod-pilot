import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Shell } from "./components/Shell";
import { Call } from "./pages/Call";
import { Floor } from "./pages/Floor";
import { Handoff } from "./pages/Handoff";
import { Machine } from "./pages/Machine";
import { Repair } from "./pages/Repair";
import { Report } from "./pages/Report";
import { Walk } from "./pages/Walk";
import { PersonaProvider } from "./persona";

export default function App() {
  return (
    <PersonaProvider>
      <BrowserRouter>
        <Shell>
          <Routes>
            <Route path="/" element={<Walk />} />
            <Route path="/call/:number" element={<Call />} />
            <Route path="/floor" element={<Floor />} />
            <Route path="/machine/:code" element={<Machine />} />
            <Route path="/report" element={<Report />} />
            <Route path="/repair/:number" element={<Repair />} />
            <Route path="/handoff" element={<Handoff />} />
          </Routes>
        </Shell>
      </BrowserRouter>
    </PersonaProvider>
  );
}
