import path from "path";
import fs from 'fs/promises';
import Test from "./test.js";
import { Entity } from "ds-entities";
import { isArray } from "util";

export default class Application {
  tests: Test[];

  async loadTestData(testDir: string) {
    const di = await fs.readdir(testDir);
    let index = 0;
    for (const d of di) {
      if (d.startsWith('.')) continue;
      let st = await fs.stat(path.join(testDir, d));
      if (!st.isDirectory()) continue;
      const requestJson = path.join(path.join(testDir, d), '请求信息.json');
      try {
        st = await fs.stat(requestJson);
        if (!st.isFile()) continue;
      } catch (ex) {
        console.log('检查：' + requestJson + '异常：' + ex);
        continue;
      }
      const content = await fs.readFile(requestJson, { encoding: 'utf-8' });
      if (!content) {
        console.log(requestJson + ' 读取失败!')
        continue;
      }
      try {
        JSON.parse(content);
      } catch (ex) {
        console.log('解析JSON异常：' + ex);
        continue;
      }
      const request = JSON.parse(content);
      request.from = 'USER';
      request.fromName = 'ds-autotest程序';
      const task = new Entity.Task(request);
      if (!task.easyModel) {
        console.log('请求信息中缺乏easyModel');
        return;
      }
      if (!task.successCondition) {
        task.successCondition = new Entity.SuccessCondition({ status: 'RUN_FINISHED' });
      }
      if (!task.successCondition.status) {
        task.successCondition.status = 'RUN_FINISHED';
      }
      if (task.successCondition.result && Array.isArray(task.successCondition.result) && task.successCondition.result.length === 0) {
        delete task.successCondition.result;
      }
      if (task.successCondition.result && !task.successCondition.resultMatchType) {
        task.successCondition.resultMatchType = 'equals';
      }
      const test = new Test(d, task, index ++);
      console.log('发现测试：' + requestJson);
      this.tests.push(test);
    }
  }
  async run(testDir: string) {
    const st = await fs.stat(testDir);
    if (!st.isDirectory()) {
      console.log('给定目录：' + testDir + ' 不存在');
      return;
    }
    await this.loadTestData(testDir);
    console.log('开始测试，共有' + this.tests.length + '个测试');
    for (const test of this.tests) {
      await test.run();
    }
    console.log('测试结束');
    const successCount = this.tests.filter(one => one.success).length;
    console.log('成功数量：' + successCount + '，失败数量：' + (this.tests.length - successCount));
    if (successCount === this.tests.length) {
      console.log('测试通过！！！');
    } else {
      console.log('测试失败！');
    }
  }

  constructor() {
    this.tests = [];
  }
}

