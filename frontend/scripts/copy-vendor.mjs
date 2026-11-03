import { copyFileSync, mkdirSync } from "node:fs";

mkdirSync("../app/static/js/vendor", { recursive: true });
const copies = [
  ["node_modules/preline/dist/preline.js", "../app/static/js/preline.js"],
  ["node_modules/htmx.org/dist/htmx.min.js", "../app/static/js/htmx.min.js"],
  ["node_modules/apexcharts/dist/apexcharts.min.js", "../app/static/js/vendor/apexcharts.min.js"],
  ["node_modules/preline/dist/helper-apexcharts.mjs", "../app/static/js/vendor/helper-apexcharts.mjs"],
  ["node_modules/preline/dist/helper-shared.mjs", "../app/static/js/vendor/helper-shared.mjs"],
  ["node_modules/lodash/lodash.min.js", "../app/static/js/vendor/lodash.min.js"],
];
for (const [from, to] of copies) copyFileSync(from, to);
console.log(`vendored ${copies.length} files`);


