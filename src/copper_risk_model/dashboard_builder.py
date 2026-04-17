"""Build a self-contained HTML dashboard showcase from BI-ready exports."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

KPI_SPECS = [
    ("total_revenue_usd", "Revenue Exposure", "currency"),
    ("total_ebitda_usd", "Total EBITDA", "currency"),
    ("average_processed_tonnes", "Avg Throughput", "number"),
    ("average_unit_opex_usd_per_tonne", "Avg Unit Opex", "usd_per_tonne"),
    ("scenario_npv_usd", "Scenario NPV", "currency"),
    ("payback_year", "Payback", "year"),
]

CASH_FLOW_SERIES = [
    ("revenue_usd", "Revenue", "#E07A3F"),
    ("ebitda_usd", "EBITDA", "#4F7C82"),
    ("free_cash_flow_usd", "Free Cash Flow", "#7A9E46"),
]

DRIVER_SERIES = [
    ("scenario_net_price_usd_per_lb", "Net Realized Price", "#E07A3F", "usd_per_lb", 1.0),
    ("scenario_grade", "Head Grade", "#D4A373", "percent", 100.0),
    ("scenario_recovery", "Recovery", "#4F7C82", "percent", 100.0),
]

SCENARIO_SHORT_NAMES = {
    "base": "Base",
    "bull_market": "Bull Mkt",
    "bear_market": "Bear Mkt",
    "operational_stress": "Op Stress",
    "capex_overrun": "Capex",
    "committee_downside": "Committee DS",
}

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Copper Mining Planning and Performance Command Center</title>
  <style>
    :root {
      --bg: #171412;
      --bg-soft: #221c19;
      --panel: rgba(31, 25, 22, 0.88);
      --panel-strong: rgba(43, 34, 30, 0.96);
      --line: rgba(255, 255, 255, 0.08);
      --text: #f5ede2;
      --muted: #c9b8a5;
      --accent: #e07a3f;
      --accent-soft: #d4a373;
      --teal: #4f7c82;
      --olive: #7a9e46;
      --danger: #c75746;
      --surface: #2b221e;
      --shadow: 0 24px 60px rgba(0, 0, 0, 0.35);
      --radius: 22px;
      --radius-sm: 14px;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: "Segoe UI", "Trebuchet MS", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(224, 122, 63, 0.16), transparent 28%),
        radial-gradient(circle at top right, rgba(79, 124, 130, 0.18), transparent 25%),
        linear-gradient(180deg, #171412 0%, #120f0d 100%);
      color: var(--text);
      min-height: 100vh;
    }

    .page {
      max-width: 1520px;
      margin: 0 auto;
      padding: 28px 24px 40px;
    }

    .hero {
      display: grid;
      grid-template-columns: 1.45fr 0.95fr;
      gap: 18px;
      margin-bottom: 18px;
    }

    .hero-card,
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      backdrop-filter: blur(18px);
    }

    .hero-copy {
      padding: 28px 30px;
      position: relative;
      overflow: hidden;
    }

    .hero-copy:before {
      content: "";
      position: absolute;
      inset: 0;
      background:
        radial-gradient(circle at 16% 20%, rgba(224, 122, 63, 0.18), transparent 35%),
        radial-gradient(circle at 90% 18%, rgba(79, 124, 130, 0.18), transparent 25%);
      pointer-events: none;
    }

    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      color: var(--accent-soft);
      text-transform: uppercase;
      letter-spacing: 0.14em;
      font-size: 12px;
      margin-bottom: 14px;
    }

    h1, h2, h3 {
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      font-weight: 700;
      letter-spacing: -0.03em;
    }

    h1 {
      font-size: clamp(34px, 4vw, 54px);
      line-height: 0.96;
      max-width: 10ch;
      position: relative;
      z-index: 1;
    }

    .hero-copy p {
      margin: 18px 0 0;
      max-width: 58ch;
      color: var(--muted);
      font-size: 15px;
      line-height: 1.7;
      position: relative;
      z-index: 1;
    }

    .hero-metrics {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      padding: 24px;
    }

    .hero-metric {
      background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
      border: 1px solid rgba(255,255,255,0.06);
      border-radius: 18px;
      padding: 18px 18px 16px;
    }

    .hero-metric .label,
    .kpi-card .label,
    .chart-meta,
    .mini-stat .label,
    .insight-card .label,
    .benchmark-table th {
      color: var(--muted);
      font-size: 12px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    .hero-metric .value,
    .kpi-card .value,
    .mini-stat .value {
      margin-top: 10px;
      font-size: 28px;
      font-weight: 700;
      letter-spacing: -0.04em;
    }

    .hero-metric .subtext,
    .kpi-card .subtext,
    .insight-card .body {
      margin-top: 8px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.55;
    }

    .panel {
      padding: 22px;
    }

    .panel-header {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 16px;
    }

    .panel-title {
      font-size: 28px;
      line-height: 1;
    }

    .panel-subtitle {
      color: var(--muted);
      font-size: 13px;
      max-width: 44ch;
      line-height: 1.6;
    }

    .selector-row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 18px;
    }

    .selector {
      background: rgba(255,255,255,0.03);
      color: var(--text);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 999px;
      padding: 10px 14px;
      font-size: 13px;
      cursor: pointer;
      transition: all 140ms ease;
    }

    .selector:hover {
      border-color: rgba(224, 122, 63, 0.4);
      transform: translateY(-1px);
    }

    .selector.active {
      background: linear-gradient(135deg, rgba(224, 122, 63, 0.18), rgba(224, 122, 63, 0.1));
      border-color: rgba(224, 122, 63, 0.5);
      color: #fff3e8;
    }

    .content-grid {
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 18px;
      margin-bottom: 18px;
    }

    .stack {
      display: grid;
      gap: 18px;
    }

    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }

    .kpi-card,
    .mini-stat,
    .insight-card {
      background: var(--panel-strong);
      border: 1px solid rgba(255,255,255,0.06);
      border-radius: var(--radius-sm);
      padding: 16px;
    }

    .kpi-card .trend {
      margin-top: 10px;
      color: var(--accent-soft);
      font-size: 12px;
    }

    .mini-stat-grid,
    .insight-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }

    .chart-wrap {
      background: rgba(255,255,255,0.02);
      border: 1px solid rgba(255,255,255,0.06);
      border-radius: 18px;
      padding: 14px;
    }

    .chart-legend {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 12px;
      color: var(--muted);
      font-size: 12px;
    }

    .legend-item {
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }

    .legend-dot {
      width: 10px;
      height: 10px;
      border-radius: 999px;
      display: inline-block;
    }

    svg {
      width: 100%;
      height: auto;
      display: block;
    }

    .insight-card .title {
      margin-top: 10px;
      font-size: 20px;
      font-family: Georgia, "Times New Roman", serif;
      letter-spacing: -0.03em;
    }

    .two-column {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
      margin-bottom: 18px;
    }

    .benchmark-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 8px;
    }

    .benchmark-table th,
    .benchmark-table td {
      padding: 10px 0;
      border-bottom: 1px solid rgba(255,255,255,0.06);
      font-size: 13px;
      text-align: left;
    }

    .benchmark-table td {
      color: var(--text);
    }

    .heatmap-table {
      width: 100%;
      border-collapse: separate;
      border-spacing: 6px;
      margin-top: 8px;
    }

    .heatmap-table th,
    .heatmap-table td {
      text-align: center;
      padding: 10px 8px;
      border-radius: 12px;
      font-size: 12px;
    }

    .heatmap-table th {
      color: var(--muted);
      background: rgba(255,255,255,0.03);
      font-weight: 500;
    }

    .footer-note {
      margin-top: 18px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.6;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border-radius: 999px;
      padding: 8px 12px;
      background: rgba(255,255,255,0.04);
      border: 1px solid rgba(255,255,255,0.07);
      font-size: 12px;
      color: var(--muted);
    }

    @media (max-width: 1200px) {
      .hero,
      .content-grid,
      .two-column {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 900px) {
      .kpi-grid,
      .mini-stat-grid,
      .insight-grid,
      .hero-metrics {
        grid-template-columns: 1fr;
      }

      .page {
        padding: 18px 14px 30px;
      }

      .panel-title {
        font-size: 24px;
      }
    }
  </style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <div class="hero-card hero-copy">
        <div class="eyebrow">Mining Analytics Portfolio</div>
        <h1>Copper Mining Planning and Performance Command Center</h1>
        <p>
          Workbook-seeded mining inputs are translated into reproducible KPI marts for planning,
          performance monitoring, cost review, scenario planning, and BI delivery, with valuation
          and downside analytics preserved as an advanced secondary layer.
        </p>
        <div style="margin-top:18px; display:flex; flex-wrap:wrap; gap:10px;">
          <div class="pill">Operational KPI layer</div>
          <div class="pill">Scenario planning and price exposure</div>
          <div class="pill">Power BI and Tableau ready marts</div>
        </div>
      </div>
      <div class="hero-card hero-metrics" id="hero-metrics"></div>
    </section>

    <section class="panel">
      <div class="panel-header">
        <div>
          <div class="eyebrow">Planning Layer</div>
          <h2 class="panel-title">Executive Planning and Performance View</h2>
        </div>
        <div class="panel-subtitle">
          Switch scenarios to see how throughput, pricing, operating margin, cost pressure, and advanced valuation outputs move across market and operating cases.
        </div>
      </div>
      <div class="selector-row" id="scenario-selector"></div>
      <div class="kpi-grid" id="scenario-kpis"></div>
      <div class="mini-stat-grid" id="scenario-mini-stats"></div>
    </section>

    <section class="content-grid">
      <div class="stack">
        <section class="panel">
          <div class="panel-header">
            <div>
              <div class="eyebrow">Selected Scenario</div>
              <h2 class="panel-title">Revenue and Cash Generation Profile</h2>
            </div>
            <div class="panel-subtitle" id="scenario-caption"></div>
          </div>
          <div class="chart-wrap">
            <div class="chart-legend" id="cashflow-legend"></div>
            <div id="cashflow-chart"></div>
          </div>
        </section>

        <section class="panel">
          <div class="panel-header">
            <div>
              <div class="eyebrow">Scenario Planning</div>
              <h2 class="panel-title">Value Spread Across Deterministic Cases</h2>
            </div>
            <div class="panel-subtitle">
              The spread between upside and downside cases shows how exposed the planning case is to commodity prices, operating execution, and capital discipline.
            </div>
          </div>
          <div class="chart-wrap">
            <div id="scenario-comparison-chart"></div>
          </div>
        </section>
      </div>

      <div class="stack">
        <section class="panel">
          <div class="panel-header">
            <div>
              <div class="eyebrow">Operational Drivers</div>
              <h2 class="panel-title">Price, Grade, and Recovery Profile</h2>
            </div>
            <div class="panel-subtitle">
              Net price, head grade, and recovery are shown as indexed trajectories so the dashboard highlights direction and slippage rather than mixing incompatible units on one axis.
            </div>
          </div>
          <div class="chart-wrap">
            <div class="chart-legend" id="driver-legend"></div>
            <div id="driver-chart"></div>
          </div>
        </section>

        <section class="panel">
          <div class="panel-header">
            <div>
              <div class="eyebrow">Method Transparency</div>
              <h2 class="panel-title">Workbook Benchmark Reconciliation</h2>
            </div>
            <div class="panel-subtitle">
              The portfolio is stronger when it is explicit about what is directly comparable, what is reference-only, and where the planning platform intentionally departs from the original workbook logic.
            </div>
          </div>
          <table class="benchmark-table" id="benchmark-table"></table>
        </section>
      </div>
    </section>

    <section class="two-column">
      <section class="panel">
        <div class="panel-header">
          <div>
            <div class="eyebrow">Advanced Module</div>
            <h2 class="panel-title">Valuation Distribution and Tail Risk</h2>
          </div>
          <div class="panel-subtitle">
            This is the advanced layer of the platform: use it to frame downside exposure and capital fragility, not as the sole identity of the project.
          </div>
        </div>
        <div class="chart-wrap">
          <div id="distribution-chart"></div>
        </div>
      </section>

      <section class="panel">
        <div class="panel-header">
          <div>
            <div class="eyebrow">Decision Drivers</div>
            <h2 class="panel-title">Tornado Ranking</h2>
          </div>
          <div class="panel-subtitle">
            The tornado chart isolates which levers matter most for planning resilience and capital outcomes relative to the base case.
          </div>
        </div>
        <div class="chart-wrap">
          <div id="tornado-chart"></div>
        </div>
      </section>
    </section>

    <section class="two-column">
      <section class="panel">
        <div class="panel-header">
          <div>
            <div class="eyebrow">Stress Grid</div>
            <h2 class="panel-title">Price vs Grade Heatmap</h2>
          </div>
          <div class="panel-subtitle">
            A reviewer should be able to see immediately where the planning case moves from value creation to value destruction.
          </div>
        </div>
        <div id="heatmap-table"></div>
      </section>

      <section class="panel">
        <div class="panel-header">
          <div>
            <div class="eyebrow">Management Layer</div>
            <h2 class="panel-title">Portfolio Messages</h2>
          </div>
          <div class="panel-subtitle">
            These are the signals the dashboard is designed to communicate to planning, management control, business analysis, or investment-review audiences.
          </div>
        </div>
        <div class="insight-grid" id="insight-grid"></div>
      </section>
    </section>

    <div class="footer-note" id="footer-note"></div>
  </div>

  <script>
    const dashboardData = __DATA_JSON__;
    const scenarioOrder = dashboardData.scenario_order;
    let activeScenarioId = dashboardData.default_scenario_id;

    const formatters = {
      currency(value) {
        if (value === null || value === undefined) return "n/a";
        return new Intl.NumberFormat("en-US", {
          style: "currency",
          currency: "USD",
          notation: "compact",
          maximumFractionDigits: 1
        }).format(value);
      },
      currencyLong(value) {
        if (value === null || value === undefined) return "n/a";
        return new Intl.NumberFormat("en-US", {
          style: "currency",
          currency: "USD",
          maximumFractionDigits: 0
        }).format(value);
      },
      percent(value) {
        if (value === null || value === undefined) return "n/a";
        return `${value.toFixed(2)}%`;
      },
      number(value) {
        if (value === null || value === undefined) return "n/a";
        return new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 1 }).format(value);
      },
        usdPerLb(value) {
          if (value === null || value === undefined) return "n/a";
          return `${value.toFixed(2)} $/lb`;
        },
        usdPerTonne(value) {
          if (value === null || value === undefined) return "n/a";
          return `${value.toFixed(2)} $/t`;
        },
        year(value) {
          if (value === null || value === undefined) return "No payback";
          return `Year ${Math.round(value)}`;
        },
      gap(value) {
        if (value === null || value === undefined) return "n/a";
        const sign = value >= 0 ? "+" : "";
        return `${sign}${formatters.currency(value)}`;
      }
    };

    function interpolateColor(value, min, max) {
      const safeMax = max === min ? min + 1 : max;
      const t = Math.max(0, Math.min(1, (value - min) / (safeMax - min)));
      const r = Math.round(199 + (79 - 199) * t);
      const g = Math.round(87 + (158 - 87) * t);
      const b = Math.round(70 + (70 - 70) * t);
      return `rgba(${r}, ${g}, ${b}, 0.72)`;
    }

    function linePath(points, xScale, yScale) {
      return points
        .map((point, index) => `${index === 0 ? "M" : "L"} ${xScale(point.x).toFixed(2)} ${yScale(point.y).toFixed(2)}`)
        .join(" ");
    }

      function formatMetric(value, format) {
        if (format === "currency") return formatters.currency(value);
        if (format === "percent") return formatters.percent(value);
        if (format === "usd_per_lb") return formatters.usdPerLb(value);
        if (format === "usd_per_tonne") return formatters.usdPerTonne(value);
        if (format === "year") return formatters.year(value);
        return formatters.number(value);
      }

      function formatAxisValue(value, format) {
        if (format === "currency") return formatters.currency(value);
        if (format === "percent") return `${value.toFixed(1)}%`;
        if (format === "usd_per_lb") return `${value.toFixed(2)}`;
        if (format === "usd_per_tonne") return `${value.toFixed(2)}`;
        return formatters.number(value);
      }

    function formatBenchmarkValue(value, unit, currency) {
      if (value === null || value === undefined) return "n/a";
      if (unit === "decimal") return `${(value * 100).toFixed(1)}%`;
      if (unit === "USD" || currency === "USD") return formatters.currency(value);
      return formatters.number(value);
    }

    function formatBenchmarkGap(row) {
      if (!row.comparable_flag || row.gap === null || row.gap === undefined) return "n/a";
      if (row.python_unit === "decimal") {
        const sign = row.gap >= 0 ? "+" : "";
        return `${sign}${(row.gap * 100).toFixed(1)} pp`;
      }
      return formatters.gap(row.gap);
    }

    function formatBenchmarkStatus(row) {
      if (row.reconciliation_status === "close_match") return "Comparable";
      if (row.reconciliation_status === "material_gap") return "Comparable, material gap";
      return "Reference only";
    }

    function renderHeroMetrics() {
      const metrics = dashboardData.hero_metrics.map((metric) => `
        <div class="hero-metric">
          <div class="label">${metric.label}</div>
          <div class="value">${formatMetric(metric.value, metric.format)}</div>
          <div class="subtext">${metric.subtext}</div>
        </div>
      `).join("");
      document.getElementById("hero-metrics").innerHTML = metrics;
    }

    function renderScenarioSelector() {
      const html = scenarioOrder.map((scenarioId) => {
        const scenario = dashboardData.scenarios[scenarioId];
        const active = scenarioId === activeScenarioId ? "active" : "";
        return `<button class="selector ${active}" data-scenario="${scenarioId}">${scenario.name}</button>`;
      }).join("");
      document.getElementById("scenario-selector").innerHTML = html;
      document.querySelectorAll(".selector").forEach((button) => {
        button.addEventListener("click", () => {
          activeScenarioId = button.dataset.scenario;
          renderAll();
        });
      });
    }

    function renderScenarioKpis() {
      const scenario = dashboardData.scenarios[activeScenarioId];
      const kpiHtml = dashboardData.kpi_specs.map((spec) => {
        const value = scenario.kpis[spec.key];
        const baseValue = dashboardData.scenarios[dashboardData.default_scenario_id].kpis[spec.key];
        const delta = typeof value === "number" && typeof baseValue === "number" ? value - baseValue : null;
        const deltaText = activeScenarioId === dashboardData.default_scenario_id || delta === null
          ? "Selected reference scenario"
          : `${delta >= 0 ? "Above" : "Below"} base by ${spec.format === "currency" ? formatters.currency(Math.abs(delta)) : formatMetric(Math.abs(delta), spec.format)}`;
        return `
          <div class="kpi-card">
            <div class="label">${spec.label}</div>
            <div class="value">${formatMetric(value, spec.format)}</div>
            <div class="trend">${deltaText}</div>
          </div>
        `;
      }).join("");
      document.getElementById("scenario-kpis").innerHTML = kpiHtml;

      const miniStats = scenario.mini_stats.map((item) => `
        <div class="mini-stat">
          <div class="label">${item.label}</div>
          <div class="value">${formatMetric(item.value, item.format)}</div>
        </div>
      `).join("");
      document.getElementById("scenario-mini-stats").innerHTML = miniStats;
      document.getElementById("scenario-caption").textContent = `${scenario.name} | ${scenario.category}`;
    }

    function renderLegend(targetId, items) {
      document.getElementById(targetId).innerHTML = items.map((item) => `
        <span class="legend-item">
          <span class="legend-dot" style="background:${item.color}"></span>
          ${item.label}
        </span>
      `).join("");
    }

    function renderLineChart(targetId, seriesCollection, options = {}) {
      const width = 780;
      const height = options.height || 300;
      const margin = { top: 14, right: 18, bottom: 34, left: 78 };
      const allValues = seriesCollection.flatMap((series) => series.points.map((point) => point.value));
      const allYears = seriesCollection.flatMap((series) => series.points.map((point) => point.year));
      const yMinBase = Math.min(...allValues);
      const yMaxBase = Math.max(...allValues);
      const yMin = options.includeZero ? Math.min(0, yMinBase) : yMinBase;
      const yMax = options.includeZero ? Math.max(0, yMaxBase) : yMaxBase;
      const safeSpan = yMax === yMin ? Math.abs(yMax || 1) : yMax - yMin;
      const minYear = Math.min(...allYears);
      const maxYear = Math.max(...allYears);
      const plotWidth = width - margin.left - margin.right;
      const plotHeight = height - margin.top - margin.bottom;
      const xScale = (year) => margin.left + ((year - minYear) / Math.max(1, maxYear - minYear)) * plotWidth;
      const yScale = (value) => margin.top + (1 - ((value - yMin) / safeSpan)) * plotHeight;
      const ticks = 5;
      const yTicks = Array.from({ length: ticks }, (_, index) => yMin + (safeSpan / (ticks - 1)) * index);
      const xTicks = Array.from({ length: maxYear - minYear + 1 }, (_, index) => minYear + index);

      const gridLines = yTicks.map((tick) => `
        <g>
          <line x1="${margin.left}" x2="${width - margin.right}" y1="${yScale(tick)}" y2="${yScale(tick)}" stroke="rgba(255,255,255,0.08)" stroke-dasharray="4 6"></line>
          <text x="${margin.left - 12}" y="${yScale(tick) + 4}" fill="rgba(201,184,165,0.9)" font-size="11" text-anchor="end">${formatAxisValue(tick, options.axisFormat)}</text>
        </g>
      `).join("");

      const xLabels = xTicks.map((tick) => `
        <text x="${xScale(tick)}" y="${height - 8}" fill="rgba(201,184,165,0.9)" font-size="11" text-anchor="middle">Y${tick}</text>
      `).join("");

      const paths = seriesCollection.map((series) => {
        const points = series.points.map((point) => ({ x: point.year, y: point.value }));
        const path = linePath(points, xScale, yScale);
        return `
          <path d="${path}" fill="none" stroke="${series.color}" stroke-width="3" stroke-linecap="round"></path>
          ${points.map((point) => `
            <circle cx="${xScale(point.x)}" cy="${yScale(point.y)}" r="3.4" fill="${series.color}">
              <title>${series.label}: ${formatMetric(point.y, series.format)}</title>
            </circle>
          `).join("")}
        `;
      }).join("");

      const zeroLine = yMin < 0 && yMax > 0
        ? `<line x1="${margin.left}" x2="${width - margin.right}" y1="${yScale(0)}" y2="${yScale(0)}" stroke="rgba(255,255,255,0.3)" stroke-width="1.2"></line>`
        : "";

      document.getElementById(targetId).innerHTML = `
        <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${options.title || 'Line chart'}">
          ${gridLines}
          ${zeroLine}
          ${paths}
          ${xLabels}
        </svg>
      `;
    }

    function renderScenarioComparison() {
      const data = dashboardData.scenario_comparison;
      const width = 720;
      const height = 310;
      const margin = { top: 16, right: 10, bottom: 74, left: 84 };
      const values = data.map((item) => item.scenario_npv_usd);
      const yMin = Math.min(0, ...values);
      const yMax = Math.max(0, ...values);
      const span = yMax === yMin ? 1 : yMax - yMin;
      const plotWidth = width - margin.left - margin.right;
      const plotHeight = height - margin.top - margin.bottom;
      const barWidth = plotWidth / data.length;
      const yScale = (value) => margin.top + (1 - ((value - yMin) / span)) * plotHeight;
      const zero = yScale(0);

      const bars = data.map((item, index) => {
        const x = margin.left + index * barWidth + 12;
        const barHeight = Math.abs(yScale(item.scenario_npv_usd) - zero);
        const y = item.scenario_npv_usd >= 0 ? yScale(item.scenario_npv_usd) : zero;
        const color = item.scenario_id === activeScenarioId ? "#E07A3F" : item.scenario_npv_usd >= 0 ? "#4F7C82" : "#C75746";
        const opacity = item.scenario_id === activeScenarioId ? 1 : 0.74;
        return `
          <g>
            <rect x="${x}" y="${y}" width="${barWidth - 24}" height="${Math.max(4, barHeight)}" rx="10" fill="${color}" opacity="${opacity}"></rect>
            <text x="${x + (barWidth - 24) / 2}" y="${item.scenario_npv_usd >= 0 ? y - 10 : y + barHeight + 18}" text-anchor="middle" fill="rgba(245,237,226,0.92)" font-size="11">${formatters.currency(item.scenario_npv_usd)}</text>
            <text x="${x + (barWidth - 24) / 2}" y="${height - 38}" text-anchor="middle" fill="rgba(201,184,165,0.92)" font-size="11">${item.short_name}</text>
          </g>
        `;
      }).join("");

      document.getElementById("scenario-comparison-chart").innerHTML = `
        <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Scenario comparison chart">
          <line x1="${margin.left}" x2="${width - margin.right}" y1="${zero}" y2="${zero}" stroke="rgba(255,255,255,0.3)" stroke-width="1.2"></line>
          ${bars}
        </svg>
      `;
    }

    function renderDistributionChart() {
      const histogram = dashboardData.simulation.histogram;
      const percentiles = dashboardData.simulation.percentiles;
      const width = 720;
      const height = 320;
      const margin = { top: 18, right: 18, bottom: 34, left: 64 };
      const maxCount = Math.max(...histogram.map((bin) => bin.count));
      const minX = histogram[0].bin_start;
      const maxX = histogram[histogram.length - 1].bin_end;
      const plotWidth = width - margin.left - margin.right;
      const plotHeight = height - margin.top - margin.bottom;
      const xScale = (value) => margin.left + ((value - minX) / (maxX - minX)) * plotWidth;
      const yScale = (value) => margin.top + (1 - value / maxCount) * plotHeight;
      const bars = histogram.map((bin) => {
        const x = xScale(bin.bin_start);
        const y = yScale(bin.count);
        const barWidth = Math.max(2, xScale(bin.bin_end) - x - 2);
        const fill = bin.midpoint < 0 ? "rgba(199,87,70,0.72)" : "rgba(79,124,130,0.76)";
        return `<rect x="${x}" y="${y}" width="${barWidth}" height="${height - margin.bottom - y}" rx="4" fill="${fill}"></rect>`;
      }).join("");
      const markers = percentiles.map((item) => `
        <g>
          <line x1="${xScale(item.npv_usd)}" x2="${xScale(item.npv_usd)}" y1="${margin.top}" y2="${height - margin.bottom}" stroke="rgba(224,122,63,0.95)" stroke-dasharray="6 6"></line>
          <text x="${xScale(item.npv_usd)}" y="${margin.top - 4}" text-anchor="middle" fill="rgba(245,237,226,0.92)" font-size="10">P${Math.round(item.percentile * 100)}</text>
        </g>
      `).join("");

      document.getElementById("distribution-chart").innerHTML = `
        <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Monte Carlo NPV distribution">
          <line x1="${margin.left}" x2="${width - margin.right}" y1="${height - margin.bottom}" y2="${height - margin.bottom}" stroke="rgba(255,255,255,0.25)"></line>
          ${bars}
          ${markers}
          <text x="${margin.left}" y="${height - 8}" fill="rgba(201,184,165,0.92)" font-size="11">${formatters.currency(minX)}</text>
          <text x="${width - margin.right}" y="${height - 8}" text-anchor="end" fill="rgba(201,184,165,0.92)" font-size="11">${formatters.currency(maxX)}</text>
        </svg>
      `;
    }

    function renderTornadoChart() {
      const data = dashboardData.tornado;
      const width = 720;
      const height = 330;
      const margin = { top: 20, right: 18, bottom: 22, left: 158 };
      const plotWidth = width - margin.left - margin.right;
      const rowHeight = (height - margin.top - margin.bottom) / data.length;
      const maxAbs = Math.max(...data.flatMap((row) => [Math.abs(row.down_impact_usd), Math.abs(row.up_impact_usd)]));
      const xScale = (value) => margin.left + ((value + maxAbs) / (maxAbs * 2)) * plotWidth;
      const zero = xScale(0);

      const rows = data.map((row, index) => {
        const y = margin.top + index * rowHeight + 4;
        const downX = xScale(row.down_impact_usd);
        const upX = xScale(0);
        return `
          <g>
            <text x="${margin.left - 14}" y="${y + rowHeight / 2 + 4}" text-anchor="end" fill="rgba(245,237,226,0.92)" font-size="12">${row.driver_label}</text>
            <rect x="${downX}" y="${y}" width="${zero - downX}" height="${rowHeight - 10}" rx="8" fill="rgba(199,87,70,0.82)"></rect>
            <rect x="${upX}" y="${y}" width="${xScale(row.up_impact_usd) - zero}" height="${rowHeight - 10}" rx="8" fill="rgba(79,124,130,0.88)"></rect>
          </g>
        `;
      }).join("");

      document.getElementById("tornado-chart").innerHTML = `
        <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Tornado sensitivity chart">
          <line x1="${zero}" x2="${zero}" y1="${margin.top - 6}" y2="${height - margin.bottom}" stroke="rgba(255,255,255,0.25)" stroke-width="1.2"></line>
          ${rows}
          <text x="${margin.left}" y="${height - 4}" fill="rgba(201,184,165,0.92)" font-size="11">${formatters.currency(-maxAbs)}</text>
          <text x="${zero}" y="${height - 4}" text-anchor="middle" fill="rgba(201,184,165,0.92)" font-size="11">Base</text>
          <text x="${width - margin.right}" y="${height - 4}" text-anchor="end" fill="rgba(201,184,165,0.92)" font-size="11">${formatters.currency(maxAbs)}</text>
        </svg>
      `;
    }

    function renderHeatmap() {
      const heatmap = dashboardData.heatmap;
      const values = heatmap.values.flat();
      const min = Math.min(...values);
      const max = Math.max(...values);
      const table = `
        <table class="heatmap-table">
          <thead>
            <tr>
              <th>Price / Grade</th>
              ${heatmap.grade_factors.map((value) => `<th>${(value * 100).toFixed(0)}%</th>`).join("")}
            </tr>
          </thead>
          <tbody>
            ${heatmap.price_factors.map((priceFactor, rowIndex) => `
              <tr>
                <th>${(priceFactor * 100).toFixed(0)}%</th>
                ${heatmap.values[rowIndex].map((cellValue) => `
                  <td style="background:${interpolateColor(cellValue, min, max)}" title="${formatters.currencyLong(cellValue)}">
                    ${formatters.currency(cellValue)}
                  </td>
                `).join("")}
              </tr>
            `).join("")}
          </tbody>
        </table>
      `;
      document.getElementById("heatmap-table").innerHTML = table;
    }

    function renderBenchmarkTable() {
      const rows = dashboardData.benchmark.map((row) => `
        <tr>
          <th>${row.label}</th>
          <td>${formatBenchmarkValue(row.benchmark_value, row.benchmark_unit, row.benchmark_currency)}</td>
          <td>${formatBenchmarkValue(row.python_value, row.python_unit, row.python_currency)}</td>
          <td>${formatBenchmarkStatus(row)}</td>
          <td>${formatBenchmarkGap(row)}</td>
          <td>${row.reconciliation_note}</td>
        </tr>
      `).join("");
      document.getElementById("benchmark-table").innerHTML = `
        <thead>
          <tr>
            <th>Metric</th>
            <th>Workbook</th>
            <th>Python</th>
            <th>Status</th>
            <th>Gap</th>
            <th>Interpretation</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      `;
    }

    function renderInsights() {
      document.getElementById("insight-grid").innerHTML = dashboardData.insights.map((insight) => `
        <div class="insight-card">
          <div class="label">${insight.label}</div>
          <div class="title">${insight.title}</div>
          <div class="body">${insight.body}</div>
        </div>
      `).join("");
    }

    function renderScenarioCharts() {
      const scenario = dashboardData.scenarios[activeScenarioId];
      renderLegend("cashflow-legend", scenario.cash_flow_series.map((item) => ({ label: item.label, color: item.color })));
      renderLegend("driver-legend", scenario.driver_series.map((item) => ({ label: item.label, color: item.color })));
      renderLineChart("cashflow-chart", scenario.cash_flow_series, { includeZero: true, axisFormat: "currency", title: "Cash flow trajectory" });
      renderLineChart("driver-chart", scenario.driver_series, { includeZero: false, axisFormat: "number", title: "Operating drivers" });
    }

    function renderFooter() {
      document.getElementById("footer-note").textContent =
        `Generated from Python exports on ${dashboardData.generated_at}. This dashboard is a portfolio showcase built from BI-ready mining KPI marts, scenario tables, benchmark transparency outputs, and advanced risk tables.`;
    }

    function renderAll() {
      renderScenarioSelector();
      renderScenarioKpis();
      renderScenarioCharts();
      renderScenarioComparison();
      renderDistributionChart();
      renderTornadoChart();
      renderHeatmap();
      renderBenchmarkTable();
      renderInsights();
      renderFooter();
    }

    renderHeroMetrics();
    renderAll();
  </script>
</body>
</html>
"""


def _clean_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, (np.floating, float)):
        return float(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    return value


def _series_points(frame: pd.DataFrame, scenario_id: str, metric: str, factor: float = 1.0) -> list[dict[str, float]]:
    subset = (
        frame.loc[(frame["scenario_id"] == scenario_id) & (frame["metric"] == metric), ["year", "value"]]
        .sort_values("year")
        .reset_index(drop=True)
    )
    return [{"year": int(row.year), "value": float(row.value) * factor} for row in subset.itertuples(index=False)]


def _index_points(points: list[dict[str, float]]) -> list[dict[str, float]]:
    if not points:
        return []
    base = points[0]["value"] if points[0]["value"] not in (0, None) else 1.0
    return [{"year": int(point["year"]), "value": float(point["value"]) / float(base) * 100} for point in points]


def _build_histogram(distribution: pd.Series, bins: int = 36) -> list[dict[str, float]]:
    counts, edges = np.histogram(distribution.to_numpy(), bins=bins)
    records: list[dict[str, float]] = []
    for index, count in enumerate(counts):
        start = float(edges[index])
        end = float(edges[index + 1])
        records.append(
            {
                "bin_start": start,
                "bin_end": end,
                "midpoint": float((start + end) / 2),
                "count": int(count),
            }
        )
    return records


def _build_percentile_markers(distribution: pd.Series, percentiles: list[float]) -> list[dict[str, float]]:
    return [{"percentile": percentile, "npv_usd": float(distribution.quantile(percentile))} for percentile in percentiles]


def _build_insights(snapshot: dict[str, Any]) -> list[dict[str, str]]:
    base = snapshot["scenarios"]["base"]["kpis"]
    committee = snapshot["scenarios"]["committee_downside"]["kpis"]
    probability_of_loss = snapshot["simulation"]["summary"]["probability_of_loss"]
    var_usd = snapshot["simulation"]["summary"]["var_usd"]
    cvar_usd = snapshot["simulation"]["summary"]["cvar_usd"]
    best_case = max(snapshot["scenario_comparison"], key=lambda row: row["scenario_npv_usd"])
    worst_case = min(snapshot["scenario_comparison"], key=lambda row: row["scenario_npv_usd"])
    throughput_mt = base["average_processed_tonnes"] / 1e6
    recovery_pct = base["average_recovery_pct"]
    unit_opex = base["average_unit_opex_usd_per_tonne"]
    margin_pct = base["ebitda_margin_proxy_pct"]

    return [
        {
            "label": "Planning Baseline",
            "title": "The reference case already reads like a mining planning dashboard.",
            "body": (
                f"The base case averages {throughput_mt:.2f} Mt of processed material per year, "
                f"{recovery_pct:.1f}% recovery, and {unit_opex:.2f} USD/t of unit opex. "
                "That combination is easier to discuss in planning, management control, and business analysis contexts than valuation alone."
            ),
        },
        {
            "label": "Business Signal",
            "title": "Scenario spread connects operations, market exposure, and margin pressure.",
            "body": (
                f"The strongest deterministic case is {best_case['name']} while {worst_case['name']} is the weakest. "
                f"The base-case EBITDA margin proxy is {margin_pct:.1f}%, which makes price, throughput, recovery, and unit cost natural executive dashboard drivers."
            ),
        },
        {
            "label": "Advanced Layer",
            "title": "Valuation and tail risk remain useful, but secondary.",
            "body": (
                f"Loss probability is {probability_of_loss:.1%}, 5% VaR is {var_usd / 1e9:.2f}B USD, and "
                f"the committee-downside case reaches {committee['scenario_npv_usd'] / 1e9:.2f}B USD. "
                "Those outputs strengthen the portfolio, but they now sit behind the planning and KPI story instead of replacing it."
            ),
        },
    ]


def _build_snapshot(data_dir: str | Path) -> dict[str, Any]:
    data_dir = Path(data_dir)
    fact_annual = pd.read_csv(data_dir / "fact_annual_metrics.csv")
    fact_scenario_kpis = pd.read_csv(data_dir / "fact_scenario_kpis.csv")
    dim_scenario = pd.read_csv(data_dir / "dim_scenario.csv")
    fact_tornado = pd.read_csv(data_dir / "fact_tornado_sensitivity.csv")
    fact_heatmap = pd.read_csv(data_dir / "fact_heatmap_price_grade.csv")
    simulation_summary = pd.read_csv(data_dir / "simulation_summary.csv")
    simulation_distribution = pd.read_csv(data_dir / "fact_simulation_distribution.csv")
    benchmark = pd.read_csv(data_dir / "benchmark_comparison.csv")

    scenario_order = dim_scenario["scenario_id"].tolist()
    scenario_meta = dim_scenario.set_index("scenario_id")
    kpi_matrix = fact_scenario_kpis.pivot_table(index="scenario_id", columns="metric", values="value", aggfunc="first")

    scenarios: dict[str, Any] = {}
    for scenario_id in scenario_order:
        meta = scenario_meta.loc[scenario_id]
        kpis = {metric: _clean_value(kpi_matrix.loc[scenario_id, metric]) for metric in kpi_matrix.columns}
        kpis["average_head_grade_pct"] = None if kpis["average_head_grade"] is None else kpis["average_head_grade"] * 100
        kpis["average_recovery_pct"] = None if kpis["average_recovery"] is None else kpis["average_recovery"] * 100
        kpis["ebitda_margin_proxy_pct"] = None if kpis["ebitda_margin_proxy"] is None else kpis["ebitda_margin_proxy"] * 100

        cash_flow_series = [
            {
                "metric": metric,
                "label": label,
                "color": color,
                "format": "currency",
                "points": _series_points(fact_annual, scenario_id, metric),
            }
            for metric, label, color in CASH_FLOW_SERIES
        ]
        driver_series = [
            {
                "metric": metric,
                "label": label,
                "color": color,
                "format": "number",
                "points": _index_points(_series_points(fact_annual, scenario_id, metric, factor=factor)),
            }
            for metric, label, color, format_name, factor in DRIVER_SERIES
        ]

        scenarios[scenario_id] = {
            "id": scenario_id,
            "name": str(meta["scenario_name"]),
            "short_name": SCENARIO_SHORT_NAMES.get(
                scenario_id,
                str(meta["scenario_name"]).replace("Market", "Mkt").replace("Case", "").strip(),
            ),
            "category": str(meta["scenario_category"]),
            "kpis": kpis,
            "cash_flow_series": cash_flow_series,
            "driver_series": driver_series,
            "mini_stats": [
                {"label": "Average Head Grade", "value": kpis["average_head_grade_pct"], "format": "percent"},
                {"label": "Average Recovery", "value": kpis["average_recovery_pct"], "format": "percent"},
                {"label": "EBITDA Margin Proxy", "value": kpis["ebitda_margin_proxy_pct"], "format": "percent"},
            ],
        }

    base_npv = scenarios["base"]["kpis"]["scenario_npv_usd"]
    scenario_comparison = []
    for scenario_id in scenario_order:
        scenario = scenarios[scenario_id]
        scenario_comparison.append(
            {
                "scenario_id": scenario_id,
                "name": scenario["name"],
                "short_name": scenario["short_name"],
                "category": scenario["category"],
                "scenario_npv_usd": scenario["kpis"]["scenario_npv_usd"],
                "npv_vs_base_usd": None if scenario["kpis"]["scenario_npv_usd"] is None else scenario["kpis"]["scenario_npv_usd"] - base_npv,
            }
        )

    tornado_grouped = []
    for driver_label, subset in fact_tornado.groupby("driver_label", sort=False):
        down_value = float(subset.loc[subset["direction"] == "down", "impact_vs_base_usd"].iloc[0])
        up_value = float(subset.loc[subset["direction"] == "up", "impact_vs_base_usd"].iloc[0])
        tornado_grouped.append(
            {
                "driver_label": driver_label,
                "down_impact_usd": down_value,
                "up_impact_usd": up_value,
                "rank": float(subset["abs_impact_vs_base_usd"].max()),
            }
        )
    tornado_grouped.sort(key=lambda item: item["rank"], reverse=True)

    heatmap_price = sorted(fact_heatmap["price_factor"].unique().tolist())
    heatmap_grade = sorted(fact_heatmap["grade_factor"].unique().tolist())
    heatmap_values = []
    for price_factor in heatmap_price:
        row_values = []
        for grade_factor in heatmap_grade:
            value = fact_heatmap.loc[
                (fact_heatmap["price_factor"] == price_factor) & (fact_heatmap["grade_factor"] == grade_factor),
                "npv_usd",
            ].iloc[0]
            row_values.append(float(value))
        heatmap_values.append(row_values)

    sim_summary = {row.metric: float(row.value) for row in simulation_summary.itertuples(index=False)}
    percentile_markers = _build_percentile_markers(simulation_distribution["npv_usd"], [0.05, 0.5, 0.95])

    benchmark_labels = {
        "incremental_npv": "Incremental NPV",
        "incremental_irr": "Incremental IRR",
        "expected_npv": "Expected NPV",
        "var_5pct": "VaR 5%",
        "cvar_5pct": "CVaR 5%",
    }

    snapshot: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "default_scenario_id": "base",
        "scenario_order": scenario_order,
        "kpi_specs": [{"key": key, "label": label, "format": format_name} for key, label, format_name in KPI_SPECS],
        "hero_metrics": [
            {
                "label": "Reference Avg Throughput",
                "value": scenarios["base"]["kpis"]["average_processed_tonnes"],
                "format": "number",
                "subtext": "Planning baseline throughput from the reference case.",
            },
            {
                "label": "Reference Recovery",
                "value": scenarios["base"]["kpis"]["average_recovery_pct"],
                "format": "percent",
                "subtext": "Average metallurgical recovery in the reference case.",
            },
            {
                "label": "Reference Unit Opex",
                "value": scenarios["base"]["kpis"]["average_unit_opex_usd_per_tonne"],
                "format": "usd_per_tonne",
                "subtext": "Average unit operating cost in the reference case.",
            },
            {
                "label": "Probability of Loss",
                "value": sim_summary["probability_of_loss"] * 100,
                "format": "percent",
                "subtext": "Advanced downside signal from the stochastic module.",
            },
        ],
        "scenarios": scenarios,
        "scenario_comparison": scenario_comparison,
        "simulation": {
            "summary": sim_summary,
            "histogram": _build_histogram(simulation_distribution["npv_usd"]),
            "percentiles": percentile_markers,
        },
        "tornado": tornado_grouped,
        "heatmap": {
            "price_factors": heatmap_price,
            "grade_factors": heatmap_grade,
            "values": heatmap_values,
        },
        "benchmark": [
            {
                "metric": row.metric,
                "label": benchmark_labels.get(row.metric, row.metric),
                "python_value": float(row.python_value),
                "python_unit": row.python_unit,
                "python_currency": _clean_value(row.python_currency),
                "benchmark_value": _clean_value(row.benchmark_value),
                "benchmark_unit": _clean_value(row.benchmark_unit),
                "benchmark_currency": _clean_value(row.benchmark_currency),
                "comparable_flag": bool(row.comparable_flag),
                "reconciliation_status": row.reconciliation_status,
                "gap": _clean_value(row.gap),
                "pct_gap": _clean_value(row.pct_gap),
                "reconciliation_note": row.reconciliation_note,
            }
            for row in benchmark.itertuples(index=False)
        ],
    }
    snapshot["insights"] = _build_insights(snapshot)
    return snapshot


def build_portfolio_dashboard(data_dir: str | Path = "outputs/bi", output_dir: str | Path = "outputs/dashboard") -> dict[str, Path]:
    """Generate a self-contained dashboard showcase from BI exports."""

    snapshot = _build_snapshot(data_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    snapshot_path = output_dir / "data_snapshot.json"
    html_path = output_dir / "index.html"

    snapshot_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    html_path.write_text(HTML_TEMPLATE.replace("__DATA_JSON__", json.dumps(snapshot, separators=(",", ":"))), encoding="utf-8")

    return {"dashboard_html": html_path, "dashboard_data": snapshot_path}
