import { Entity } from 'ds-entities';
import { create, fetchDsResult, info, removeTask, stop } from '../api/task.js';
/**
 * 单个推演测试
 * 只要推演达成停止条件，就算成功结束
 * 特殊的停止条件：永不停止，只要稳定运行（一直处于RUNNING状态），步进100就算成功（这时候主动停止任务）
 */
export default class Test {
  index: number;
  name: string;
  // 对应推演任务的ID
  dsTaskId: string;
  success: boolean;
  startTime: number;
  stopTime: number;
  // 当前状态
  status: string;
  task: any;

  constructor(name: string, task: any, index: number) {
    this.task = new Entity.Task(task);
    this.index = index;
    this.name = name; // || task.name || task.easyModel.name || '未命名测试';

    this.dsTaskId = '';
    this.success = false;
    this.startTime = Date.now();
    this.stopTime = Date.now();
    this.status = '';
  }
  /**
   * 创建推演任务
   */
  async createDs() {
    console.log("创建推演任务。。。");
    const res = await create(this.task);
    if (res && res.data && res.data.success) {
      console.log('创建任务成功');
      this.dsTaskId = res.data.data.taskId;
      return true;
    } else {
      console.log('创建任务失败：' + res.data.message);
      return false;
    }
  }
  async wait(seconds: number) {
    return new Promise((resolve, reject) => {
      try {
        setTimeout(() => {
          resolve(true);
        }, seconds * 1000);
      } catch (ex) {
        reject(ex);
      }
    });
  }
  async countDsTaskStep(count: number) {
    if (typeof count != 'number' || count <= 0) count = 1;
    count = Math.round(count);
    let got = 0;
    let finish = false;
    while (got < count && !finish) {
      const res = await info(this.dsTaskId);
      if (!res || !res.data || !res.data.success) {
        console.log('获取推演任务信息失败:' + (res && res.data && res.data.message || '未知错误'));
        continue;
      }
      await this.wait(1);
      const show = new Entity.TaskShow(res.data.data);
      if (!show.alive) {
        finish = true;
        if (show.reason) {
          console.log(show.reason);
        }
      } else {
        if (show.checkIndex > count) {
          await stop(this.dsTaskId);
          this.success = true;
          break;
        }
      }
    }
  }
  async getDsTaskInfo() {
    let finish = false;
    while(!finish) {
      const res = await info(this.dsTaskId);
      if (!res || !res.data || !res.data.success) {
        console.log('获取推演任务信息失败:' + (res && res.data && res.data.message || '未知错误'));
        continue;
      }
      await this.wait(1);
      const show = new Entity.TaskShow(res.data.data);
      if (!show.alive) {
        console.log('推演任务执行完毕，任务状态:' + Entity.TaskStatusMap.get(show.status));
        finish = true;
        if (show.reason) {
          console.log('失败原因：' + show.reason);
        }
        const curTask = new Entity.Task(this.task);
        if (curTask.successCondition && curTask.successCondition.status) {
          if (curTask.successCondition.status === show.status) {
            if (curTask.successCondition.result) {
              const dsResult = await fetchDsResult(this.dsTaskId);
              // console.log(dsResult);
              if (!dsResult || !dsResult.data || !dsResult.data.success || !dsResult.data.data) {
                console.log('获取推演任务结果失败:' + (dsResult && dsResult.data && dsResult.data.message || '未知错误'));
              } else {
                if (typeof dsResult.data.data.result === 'string') {
                  const gotResult = dsResult.data.data.result as string;
                  const results = (typeof curTask.successCondition.result === 'string') ? [ curTask.successCondition.result ] : curTask.successCondition.result;
                  if (curTask.successCondition.resultMatchType === 'equals') {
                    for (var i = 0; i < results.length; i ++) {
                      if (results[i] === gotResult) {
                        this.success = true;
                        break;
                      }
                    }
                  } else if (curTask.successCondition.resultMatchType === 'regex') {
                    for (var i = 0; i < results.length; i ++) {
                      const re = new RegExp(results[i]);
                      if (re.test(gotResult)) {
                        this.success = true;
                        break;
                      }
                    }
                  } else if (curTask.successCondition.resultMatchType === 'substring') {
                    for (var i = 0; i < results.length; i ++) {
                      if (gotResult.indexOf(results[i]) > -1) {
                        this.success = true;
                        break;
                      }
                    }
                  }
                }
              }
            } else {
              this.success = true;
            }
          }
        }
      }
    }
  }
  async removeDs() {
    console.log('删除推演任务。。。');
    const res = await removeTask(this.dsTaskId);
    if (res && res.data && res.data.success) {
      console.log('推演任务已删除');
    } else {
      console.log('推演任务删除失败：' + res.data.message);
    }
  }
  async run() {
    try {
      const curTask = new Entity.Task(this.task);
      console.log('============================BEGIN=================================');
      console.log('测试索引：' + this.index);
      console.log('测试名称：' + this.name);
      this.startTime = Date.now();
      const st = await this.createDs();
      if (!st) {
        return;
      }
      console.log('成功条件为：推演结束状态为' + curTask.successCondition.status);
      if (curTask.successCondition.result) console.log('，并且推演中要设置推演结果为“' + curTask.successCondition.result + "”");
      try {
        if (curTask.stopCondition && curTask.stopCondition.isNoStop) {
          console.log('没有停止条件，步进100次检查。。。');
          await this.countDsTaskStep(100);
        } else {
          console.log(curTask.stopCondition.desc);
          await this.getDsTaskInfo();
        }
      } finally {
        await this.removeDs();
      }
    } catch (ex) {
      console.log('异常：' + ex);
    } finally {
      this.stopTime = Date.now();
      console.log('测试' + (this.success ? '成功' : '失败'));
      console.log('测试耗时：' + (this.stopTime - this.startTime) + '毫秒');
      console.log('=============================END==================================');
    }
  }
}