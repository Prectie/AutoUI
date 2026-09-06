import { defineConfig } from "allure";

const hasLabel = (labels, name, value) =>
  labels.some((label) => label.name === name && label.value === value);

const sites = {
  cn: "DesignKit CN",
  com: "DesignKit COM",
  zawa: "Zawa",
};
const deployments = ["pre", "beta", "release"];
const runtimeOs =
  {
    win32: "Windows",
    linux: "Linux",
    darwin: "macOS",
  }[process.platform] ?? process.platform;
const runtimeOsKey = runtimeOs.toLowerCase();

const environments = Object.fromEntries(
  Object.entries(sites).flatMap(([site, siteName]) =>
    deployments.map((deployment) => [
      `desktop-web-${site}-${deployment}-chromium-${runtimeOsKey}`,
      {
        name: `${siteName} · ${deployment} · Chromium · ${runtimeOs}`,
        matcher: ({ labels }) =>
          hasLabel(labels, "testTarget", "desktop-web") &&
          hasLabel(labels, "site", site) &&
          hasLabel(labels, "deployment", deployment) &&
          hasLabel(labels, "browser", "chromium") &&
          hasLabel(labels, "os", runtimeOs),
      },
    ]),
  ),
);

export default defineConfig({
  name: "AutoUI Test Report",
  output: "./artifacts/allure-report",
  // Allure 3 负责生成并追加跨运行历史；CI 在运行前恢复、运行后保存此目录。
  historyPath: "./artifacts/allure-history/history.jsonl",
  historyLimit: 30,
  plugins: {
    awesome: {
      options: {
        reportName: "AutoUI Test Report",
        groupBy: ["testTarget", "product", "feature", "story"],
      },
    },
  },
  environments,
});
