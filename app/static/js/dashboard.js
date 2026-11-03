/* Dashboard charts: Preline's ApexCharts helper (buildChart) + vendored ApexCharts. */
import { buildChart } from "/static/js/vendor/helper-apexcharts.mjs";

const data = JSON.parse(document.getElementById("dashboard-data").textContent);

const COLORS = { available: "#14b8a6", checked_out: "#3b82f6", under_maintenance: "#eab308", retired: "#9ca3af" };
const PRIMARY = "#6366f1";
const TEAL = "#14b8a6";

function same(overrides) {
  return [() => overrides, () => overrides];
}

// Status doughnut
buildChart(
  "#chart-status",
  () => ({
    chart: { height: 230, width: 230, type: "donut", zoom: { enabled: false } },
    plotOptions: { pie: { donut: { size: "76%" } } },
    series: data.status.series,
    labels: data.status.labels,
    legend: { show: false },
    dataLabels: { enabled: false },
    stroke: { width: 5, colors: ["#ffffff"] },
    states: { hover: { filter: { type: "none" } } },
  }),
  ...same({ colors: data.status.slugs.map((k) => COLORS[k]) })
);

// Check-outs vs check-ins area chart
buildChart(
  "#chart-trend",
  () => ({
    chart: { height: 280, type: "area", toolbar: { show: false }, zoom: { enabled: false } },
    series: [
      { name: "Check-outs", data: data.trend.checkouts },
      { name: "Check-ins", data: data.trend.checkins },
    ],
    legend: { show: true, position: "top", horizontalAlign: "right" },
    dataLabels: { enabled: false },
    stroke: { curve: "smooth", width: 2 },
    fill: { type: "gradient", gradient: { opacityFrom: 0.35, opacityTo: 0.02 } },
    grid: { strokeDashArray: 2, borderColor: "#e5e7eb" },
    xaxis: {
      categories: data.trend.labels,
      tickAmount: 7,
      axisBorder: { show: false },
      axisTicks: { show: false },
      labels: { style: { colors: "#6b7280", fontSize: "12px" } },
    },
    yaxis: {
      min: 0,
      forceNiceScale: true,
      labels: { formatter: (v) => String(Math.round(v)), style: { colors: "#6b7280", fontSize: "12px" } },
    },
    tooltip: { shared: true, intersect: false },
  }),
  ...same({ colors: [PRIMARY, TEAL] })
);

// Assets by type, horizontal bars
buildChart(
  "#chart-types",
  () => ({
    chart: { type: "bar", height: 260, toolbar: { show: false } },
    plotOptions: { bar: { horizontal: true, borderRadius: 4, barHeight: "55%" } },
    series: [{ name: "Assets", data: data.types.series }],
    dataLabels: { enabled: false },
    grid: { strokeDashArray: 2, borderColor: "#e5e7eb" },
    xaxis: {
      categories: data.types.labels,
      labels: { formatter: (v) => String(Math.round(v)), style: { colors: "#6b7280", fontSize: "12px" } },
    },
    yaxis: { labels: { style: { colors: "#6b7280", fontSize: "12px" } } },
    tooltip: { y: { formatter: (v) => `${v} asset${v === 1 ? "" : "s"}` } },
  }),
  ...same({ colors: [PRIMARY] })
);

