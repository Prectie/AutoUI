import request from '../utils/request.js';

export function list() {
    return request({
        url: '/ds/task/list',
        method: 'post',
    });
}
export function info(taskId: String) {
    return request({
        url: '/ds/task/info',
        method: 'post',
        data: { taskId }
    });
}
export function create(task: any) {
    return request({
        url: '/ds/task/create',
        method: 'post',
        data: task,
    });
}
export function stop(taskId: String) {
    return request({
        url: '/ds/task/stop',
        method: 'post',
        data: { taskId },
    });
}
export function pause(taskId: String) {
    return request({
        url: '/ds/task/pause',
        method: 'post',
        data: { taskId },
    });
}
export function resume(taskId: String) {
    return request({
        url: '/ds/task/resume',
        method: 'post',
        data: { taskId },
    });
}
export function objectCounts(taskId: String) {
    return request({
        url: '/ds/task/objects/id2count',
        method: 'post',
        data: { taskId },
    });
}
export function oi2n(taskId: String) {
    return request({
        url: '/ds/task/objects/id2name',
        method: 'post',
        data: { taskId },
    });
}
export function objectInstancesById(taskId: string, id: string) {
    return request({
        url: '/ds/task/objects/id2instances',
        method: 'post',
        data: { taskId, id },
    });
}
export function processCounts(taskId: String) {
    return request({
        url: '/ds/task/processes/id2count',
        method: 'post',
        data: { taskId },
    });
}
export function pi2n(taskId: String) {
    return request({
        url: '/ds/task/processes/id2name',
        method: 'post',
        data: { taskId },
    });
}
export function processInstancesById(taskId: string, id: string) {
    return request({
        url: '/ds/task/processes/id2instances',
        method: 'post',
        data: { taskId, id },
    });
}
export function oneObjectByIdAndName(taskId: String, id: string, name: String) {
    return request({
        url: '/ds/task/object/idname2instance',
        method: 'post',
        data: { taskId, id, name },
    });
}
export function oneProcessByIdAndName(taskId: String, id: string, name: String) {
    return request({
        url: '/ds/task/process/idname2instance',
        method: 'post',
        data: { taskId, id, name },
    });
}
export function setObjectAttributeValue(taskId: String, thingId: String, instIndex: number, attrName: String, value: String) {
    return request({
        url: '/ds/task/object/attr/value',
        method: 'post',
        data: { taskId, thingId, instIndex, sub: attrName, value },
    });
}
export function setObjectCurrentState(taskId: String, thingId: String, instIndex: number, value: String) {
    return request({
        url: '/ds/task/object/state',
        method: 'post',
        data: { taskId, thingId, instIndex, value },
    });
}
export function removeTask(taskId: string) {
    return request({
        url: '/ds/task/remove',
        method: 'post',
        data: { taskId },
    });
}
export function removeTaskEvent(taskId: string) {
    return request({
        url: '/ds/task/remove/event',
        method: 'post',
        data: { taskId },
    });
}
export function removeTaskMessage(taskId: string) {
    return request({
        url: '/ds/task/remove/message',
        method: 'post',
        data: { taskId },
    });
}
export function oi2f(taskId: string) {
  return request({
      url: '/ds/task/objects/id2filename',
      method: 'post',
      data: { taskId },
  });
}
export function pi2f(taskId: string) {
  return request({
      url: '/ds/task/processes/id2filename',
      method: 'post',
      data: { taskId },
  });
}
export function oi2code(taskId: string, id: string) {
  return request({
      url: '/ds/task/objects/id2code',
      method: 'post',
      data: { taskId, id },
  });
}
export function pi2code(taskId: string, id: string) {
  return request({
      url: '/ds/task/processes/id2code',
      method: 'post',
      data: { taskId, id },
  });
}
export function rootCode(taskId: string) {
  return request({
      url: '/ds/task/root/code',
      method: 'post',
      data: { taskId },
  });
}
export function fetchWholeView(taskId: string) {
  return request({
    url: '/ds/model/read?taskId=' + taskId,
    method: 'post',
  });
}
export function fetchDsResult(taskId: string) {
    return request({
      url: '/ds/task/result?taskId=' + taskId,
      method: 'post',
    });
  }
  