// import axios from 'axios';
const baseURL = 'http://192.168.1.188:8180';
// import { mainStore } from '@/store';

// const store = mainStore();

// const $http = axios.create({
//     baseURL: 'http://127.0.0.1:8180',
//     // baseURL: 'http://192.168.1.214:8080',
//     timeout: 5000,
//     headers: {
//         'Content-Type': 'application/json;charset=UTF-8'
//     }
// })

// $http.interceptors.request.use(config => {
//     // const token = store.state.token;
//     // if (config.headers != undefined) {
//     //     config.headers.Authorization = token;
//     // }
//     return config;
// }, error => {
//     return Promise.reject(error);
// });

// $http.interceptors.response.use(res => {
//     if (res.status === 200) {
//         return Promise.resolve(res);
//     } else {
//         return Promise.reject(res);
//     }
// }, error => {
//     return Promise.reject(error);
// });

// export default $http;

export default async function request(r: any) {
    const res = await fetch(baseURL + r.url, {
        headers: {
            'Content-Type': 'application/json;charset=UTF-8',
        },
        method: r.method,
        body: r ? JSON.stringify(r.data) : '',
    });
    if (res.ok) {
        return { data: await res.json() };
    } else {
        console.log('访问失败：' + res.statusText);
        return { data: { success: false, message: res.statusText } };
    }
}