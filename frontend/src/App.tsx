import { Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { Dashboard } from "./pages/Dashboard";
import { ExistingRecords } from "./pages/ExistingRecords";
import { Suppliers } from "./pages/Suppliers";

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="suppliers" element={<Suppliers />} />
        <Route path="existing-records" element={<ExistingRecords />} />
      </Route>
    </Routes>
  );
}

export default App;
