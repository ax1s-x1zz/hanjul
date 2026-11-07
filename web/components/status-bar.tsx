export function StatusBar() {
  return (
    <div className="statusbar">
      <span>9:41</span>
      <span className="island" />
      <span className="status-icons">
        <span className="signal">
          <i />
          <i />
          <i />
          <i />
        </span>
        <span className="battery" />
      </span>
    </div>
  );
}
