import { copyFileSync, mkdirSync } from "node:fs";

mkdirSync("../app/static/js", { recursive: true });
copyFileSync("node_modules/preline/dist/preline.js", "../app/static/js/preline.js");
copyFileSync("node_modules/htmx.org/dist/htmx.min.js", "../app/static/js/htmx.min.js");
console.log("vendored preline.js and htmx.min.js");
