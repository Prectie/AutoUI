import Application from "./entity/application.js";

console.log(process.argv);

const d = process.argv.filter(one => one.startsWith('testDir='));
if (d.length === 0) {
  console.log('请指定测试数据目录');
} else {
  const app = new Application();
  app.run(d[0].substring('testDir='.length));
}