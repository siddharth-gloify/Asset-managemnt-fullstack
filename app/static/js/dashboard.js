/* Dashboard charts: Preline's ApexCharts helper (buildChart) + vendored ApexCharts.
   buildChart re-renders each chart when the theme switches, calling the base config with the new mode. */
import { buildChart } from "/static/js/vendor/helper-apexcharts.mjs";

const data = JSON.parse(document.getElementById("dashboard-data").textContent);

const COLORS = { available: "#14b8a6", checked_out: "#3b82f6", under_maintenance: "#eab308", retired: "#9ca3af" };
const PRIMARY = "#6366f1";
const TEAL = "#14b8a6";

function tones(mode) {
  const dark = mode === "dark";
  return {
    text: dark ? "#a3a3a3" : "#6b7280",
    grid: dark ? "#404040" : "#e5e7eb",
    surface: dark ? "#262626" : "#ffffff",
    foreColor: dark ? "#d4d4d4" : "#374151",
    theme: dark ? "dark" : "light",
  };
}

const none = () => ({});

// Status doughnut
buildChart(
  "#chart-status",
  (mode) => ({
    chart: { height: 230, width: 230, type: "donut", zoom: { enabled: false }, foreColor: tones(mode).foreColor },
    plotOptions: { pie: { donut: { size: "76%" } } },
    series: data.status.series,
    labels: data.status.labels,
    colors: data.status.slugs.map((k) => COLORS[k]),
    legend: { show: false },
    dataLabels: { enabled: false },
    stroke: { width: 5, colors: [tones(mode).surface] },
    states: { hover: { filter: { type: "none" } } },
    tooltip: { theme: tones(mode).theme },
  }),
  none,
  none
);

// Check-outs vs check-ins area chart
buildChart(
  "#chart-trend",
  (mode) => {
    const t = tones(mode);
    return {
      chart: { height: 280, type: "area", toolbar: { show: false }, zoom: { enabled: false }, foreColor: t.foreColor },
      series: [
        { name: "Check-outs", data: data.trend.checkouts },
        { name: "Check-ins", data: data.trend.checkins },
      ],
      colors: [PRIMARY, TEAL],
      legend: { show: true, position: "top", horizontalAlign: "right", labels: { colors: t.foreColor } },
      dataLabels: { enabled: false },
      stroke: { curve: "smooth", width: 2 },
      fill: { type: "gradient", gradient: { opacityFrom: 0.35, opacityTo: 0.02 } },
      grid: { strokeDashArray: 2, borderColor: t.grid },
      xaxis: {
        categories: data.trend.labels,
        tickAmount: 7,
        axisBorder: { show: false },
        axisTicks: { show: false },
        labels: { style: { colors: t.text, fontSize: "12px" } },
      },
      yaxis: {
        min: 0,
        forceNiceScale: true,
        labels: { formatter: (v) => String(Math.round(v)), style: { colors: t.text, fontSize: "12px" } },
      },
      tooltip: { shared: true, intersect: false, theme: t.theme },
    };
  },
  none,
  none
);

// Assets by type, horizontal bars
buildChart(
  "#chart-types",
  (mode) => {
    const t = tones(mode);
    return {
      chart: { type: "bar", height: 260, toolbar: { show: false }, foreColor: t.foreColor },
      plotOptions: { bar: { horizontal: true, borderRadius: 4, barHeight: "55%" } },
      series: [{ name: "Assets", data: data.types.series }],
      colors: [PRIMARY],
      dataLabels: { enabled: false },
      grid: { strokeDashArray: 2, borderColor: t.grid },
      xaxis: {
        categories: data.types.labels,
        labels: { formatter: (v) => String(Math.round(v)), style: { colors: t.text, fontSize: "12px" } },
      },
      yaxis: { labels: { style: { colors: t.text, fontSize: "12px" } } },
      tooltip: { theme: t.theme, y: { formatter: (v) => `${v} asset${v === 1 ? "" : "s"}` } },
    };
  },
  none,
  none
);
