import styles from "./LeadCard.module.css";

export default function LeadCard() {
  return (
    <div className={styles.card}>
      <h2 className={styles.title}>🔥 Hot Lead</h2>

      <p className={styles.company}>TOGILE</p>

      <p className={styles.score}>87% Conversion Chance</p>
    </div>
  );
}
