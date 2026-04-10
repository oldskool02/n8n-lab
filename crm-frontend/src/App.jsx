import { useState } from "react";
import Sidebar from "./components/Sidebar.jsx";

export default function App() {
  const [selected, setSelected] = useState(null);

  return (
    <div style={{ display: "flex" }}>
      <Sidebar onSelect={setSelected} />

      <div style={{ flex: 1, padding: 20 }}>
        {selected ? (
          <div>
            <h2>{selected.account_name}</h2>
            <p>{selected.notes}</p>
          </div>
        ) : (
          <p>Select an interaction</p>
        )}
      </div>
    </div>
  );
}