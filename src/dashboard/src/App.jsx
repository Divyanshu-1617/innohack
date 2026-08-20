import './index.css'

function App() {
  return (
    <div className="app">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">CM</div>
          <div>
            <h1>CrowdSense</h1>
            <span>Venue Intelligence</span>
          </div>
        </div>

        <nav className="nav">
          <button className="nav-item active">
            <span>▦</span>
            Dashboard
          </button>

          <button className="nav-item">
            <span>◉</span>
            Live Monitoring
          </button>

          <button className="nav-item">
            <span>⌁</span>
            Crowd Analysis
          </button>

          <button className="nav-item">
            <span>↗</span>
            Exit Routes
          </button>

          <button className="nav-item">
            <span>⚙</span>
            Settings
          </button>
        </nav>

        <div className="sidebar-bottom">
          <div className="system-status">
            <span className="online-dot"></span>
            <div>
              <strong>System Online</strong>
              <small>AI monitoring active</small>
            </div>
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="main">
        {/* HEADER */}
        <header className="topbar">
          <div>
            <p className="eyebrow">CONTROL CENTER</p>
            <h2>Crowd Management Dashboard</h2>
            <p className="subtitle">
              Real-time venue monitoring and intelligent evacuation guidance
            </p>
          </div>

          <div className="header-actions">
            <div className="live-indicator">
              <span></span>
              LIVE
            </div>

            <div className="time">
              <strong>Live Monitoring</strong>
              <small>AI detection active</small>
            </div>
          </div>
        </header>

        {/* STAT CARDS */}
        <section className="stats-grid">
          <div className="stat-card">
            <div className="stat-top">
              <span>Total People</span>
              <div className="stat-icon blue">♟</div>
            </div>
            <h3>1,284</h3>
            <p className="positive">↑ 8.4% <span>vs last scan</span></p>
          </div>

          <div className="stat-card">
            <div className="stat-top">
              <span>Safe Zones</span>
              <div className="stat-icon green">✓</div>
            </div>
            <h3>06</h3>
            <p className="positive">All operating normally</p>
          </div>

          <div className="stat-card">
            <div className="stat-top">
              <span>Warning Zones</span>
              <div className="stat-icon yellow">!</div>
            </div>
            <h3>02</h3>
            <p className="warning-text">Needs observation</p>
          </div>

          <div className="stat-card critical-card">
            <div className="stat-top">
              <span>Critical Zones</span>
              <div className="stat-icon red">!</div>
            </div>
            <h3>01</h3>
            <p className="danger-text">Immediate action required</p>
          </div>
        </section>

        {/* MAIN GRID */}
        <section className="dashboard-grid">
          {/* VENUE MAP */}
          <div className="panel map-panel">
            <div className="panel-header">
              <div>
                <p className="panel-label">LIVE VENUE MAP</p>
                <h3>Crowd Density Overview</h3>
              </div>

              <div className="legend">
                <span><i className="dot safe-dot"></i> Safe</span>
                <span><i className="dot warning-dot"></i> Warning</span>
                <span><i className="dot critical-dot"></i> Critical</span>
              </div>
            </div>

            <div className="venue-map">
              <div className="map-grid"></div>

              <div className="venue-title">MAIN VENUE</div>

              <div className="map-zone zone-a">
                <strong>ZONE A</strong>
                <span>218 people</span>
              </div>

              <div className="map-zone zone-b">
                <strong>ZONE B</strong>
                <span>342 people</span>
              </div>

              <div className="map-zone zone-c">
                <strong>ZONE C</strong>
                <span>516 people</span>
                <small>CRITICAL</small>
              </div>

              <div className="map-zone zone-d">
                <strong>ZONE D</strong>
                <span>208 people</span>
              </div>

              <div className="corridor corridor-1"></div>
              <div className="corridor corridor-2"></div>

              <div className="exit exit-1">
                <span>↗</span>
                EXIT 1
              </div>

              <div className="exit exit-2">
                <span>↗</span>
                EXIT 2
              </div>

              <div className="you-are-here">
                <span></span>
                MONITORING AREA
              </div>
            </div>
          </div>

          {/* MANAGEMENT PANEL */}
          <div className="panel management-panel">
            <div className="panel-header">
              <div>
                <p className="panel-label">AI RECOMMENDATION</p>
                <h3>Management Actions</h3>
              </div>

              <span className="priority-badge">HIGH PRIORITY</span>
            </div>

            <div className="alert-box">
              <div className="alert-icon">!</div>
              <div>
                <strong>Critical crowd detected</strong>
                <p>
                  Zone C has crossed the safe density threshold.
                </p>
              </div>
            </div>

            <div className="action-block">
              <span className="action-label">RECOMMENDED ACTION</span>
              <h4>Divert incoming crowd from Zone C</h4>
              <p>
                Redirect movement through Corridor B to reduce pressure
                on the critical zone.
              </p>
            </div>

            <div className="route-card">
              <span className="action-label">BEST EVACUATION ROUTE</span>

              <div className="route-line">
                <div className="route-point">
                  <span className="route-dot danger"></span>
                  <strong>Zone C</strong>
                </div>

                <span className="arrow">→</span>

                <div className="route-point">
                  <span className="route-dot"></span>
                  <strong>Corridor B</strong>
                </div>

                <span className="arrow">→</span>

                <div className="route-point">
                  <span className="route-dot success"></span>
                  <strong>Exit 1</strong>
                </div>
              </div>
            </div>

            <button className="action-button">
              Activate Crowd Diversion
              <span>→</span>
            </button>
          </div>
        </section>

        {/* BOTTOM SECTION */}
        <section className="bottom-grid">
          {/* ZONE STATUS */}
          <div className="panel">
            <div className="panel-header">
              <div>
                <p className="panel-label">ZONE ANALYSIS</p>
                <h3>Current Zone Status</h3>
              </div>

              <button className="view-all">View details →</button>
            </div>

            <div className="zone-list">
              <div className="zone-row">
                <div className="zone-name">
                  <span className="status-circle safe"></span>
                  <div>
                    <strong>Zone A</strong>
                    <small>Normal density</small>
                  </div>
                </div>

                <div className="density">
                  <div className="density-bar">
                    <span style={{ width: '35%' }}></span>
                  </div>
                  <strong>35%</strong>
                </div>

                <span className="status-tag safe-tag">SAFE</span>
              </div>

              <div className="zone-row">
                <div className="zone-name">
                  <span className="status-circle warning"></span>
                  <div>
                    <strong>Zone B</strong>
                    <small>Increasing density</small>
                  </div>
                </div>

                <div className="density">
                  <div className="density-bar">
                    <span style={{ width: '67%' }}></span>
                  </div>
                  <strong>67%</strong>
                </div>

                <span className="status-tag warning-tag">WARNING</span>
              </div>

              <div className="zone-row">
                <div className="zone-name">
                  <span className="status-circle critical"></span>
                  <div>
                    <strong>Zone C</strong>
                    <small>High crowd density</small>
                  </div>
                </div>

                <div className="density">
                  <div className="density-bar">
                    <span style={{ width: '94%' }}></span>
                  </div>
                  <strong>94%</strong>
                </div>

                <span className="status-tag critical-tag">CRITICAL</span>
              </div>
            </div>
          </div>

          {/* EXIT ROUTES */}
          <div className="panel">
            <div className="panel-header">
              <div>
                <p className="panel-label">ROUTE INTELLIGENCE</p>
                <h3>Exit Availability</h3>
              </div>
            </div>

            <div className="exit-list">
              <div className="exit-row recommended">
                <div className="exit-info">
                  <div className="exit-number">01</div>
                  <div>
                    <strong>Exit 1</strong>
                    <small>Recommended route</small>
                  </div>
                </div>

                <div className="exit-capacity">
                  <span>Low crowd</span>
                  <strong>18%</strong>
                </div>

                <span className="recommended-tag">BEST</span>
              </div>

              <div className="exit-row">
                <div className="exit-info">
                  <div className="exit-number">02</div>
                  <div>
                    <strong>Exit 2</strong>
                    <small>Alternative route</small>
                  </div>
                </div>

                <div className="exit-capacity">
                  <span>Moderate</span>
                  <strong>52%</strong>
                </div>

                <span className="available-tag">OPEN</span>
              </div>
            </div>
          </div>
        </section>

        <footer>
          <span>AI Crowd Management System</span>
          <span>Real-time intelligence • Route optimization • Venue safety</span>
        </footer>
      </main>
    </div>
  )
}

export default App