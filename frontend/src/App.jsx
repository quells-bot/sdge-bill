import { BrowserRouter, Routes, Route } from "react-router-dom";
import BillsList from "./components/BillsList";
import BillForm from "./components/BillForm";
import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Routes>
          <Route path="/" element={<BillsList />} />
          <Route path="/add" element={<BillForm />} />
          <Route path="/edit/:id" element={<BillForm />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
