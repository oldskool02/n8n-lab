import { useEffect, useState } from "react";

const API = "http://localhost:8002";

export default function Sidebar({ onSelect }) {
  const [data, setData] = useState({
    active: [],
    coming: [],
    completed: []
  });

  const token = localStorage.getItem("token");

  const load = async () => {
    const res = await fetch(`${API}/interactions/grouped`, {
      headers: { Authorization: `Bearer ${token}` }
    });

    const json = await res.json();
    setData(json);
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div style={styles.sidebar}>
      <h2>Follow-ups</h2>

      <Section title="Active" items={data.active} onSelect={onSelect} />
      <Section title="Coming" items={data.coming} onSelect={onSelect} />
      <Section title="Completed" items={data.completed} onSelect={onSelect} />
    </div>
  );
}

/* ---------------- SECTION ---------------- */

function Section({ title, items, onSelect }) {
  return (
    <div style={{ marginBottom: 20 }}>
      <h4>{title} ({items.length})</h4>

      {(!items && items.length === 0) && (
        <div style={{ color: "#888", fontSize: 12 }}>No items</div>
      )}

      {items.map(item => {
        const overdue =
          item.follow_up_date &&
          new Date(item.follow_up_date) < new Date();

        return (
          <div
            key={item.id}
            style={{
              padding: 10,
              cursor: "pointer",
              borderBottom: "1px solid #eee",
              background: overdue && title === "Active" ? "#ffe5e5" : "white"
            }}
            onClick={() => onSelect(item)}
          >
            <strong>{item.account_name}</strong>

            {overdue && title === "Active" && (
              <span style={styles.badge}>OVERDUE</span>
            )}

            <br />

            <small>
              {item.follow_up_date
                ? new Date(item.follow_up_date).toLocaleString()
                : ""}
            </small>
          </div>
        );
      })}
    </div>
  );
}

/* ---------------- STYLES ---------------- */

const styles = {
  sidebar: {
    width: 300,
    borderRight: "1px solid #ddd",
    padding: 10,
    overflowY: "auto",
    height: "100vh",
    background: "white"
  },
  badge: {
    marginLeft: 6,
    background: "red",
    color: "white",
    padding: "2px 5px",
    fontSize: 10,
    borderRadius: 3
  }
};