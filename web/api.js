/**
 * HTTP API Client
 */
class API {
  constructor() {
    this.host = '/api';
    this.clear = () => this.post('clear');
    this.clock = () => this.post('clock');
    this.funky = () => this.post('funky');
    this.colorMatch = () => this.post('color-match');
    this.sendGifURL = (url) => this.post('gif', { url });
    this.sendImage = (img) => this.post('img/png', { img });
    this.sendImageURL = (url) => this.post('img/url', { url });
    this.sendTextMessage = (message) => this.post('text', { message });
  }

  post(endpoint, body = null) {
    const reqParams = { method: 'POST' };
    if (body) {
      reqParams.body = JSON.stringify(body);
      reqParams.headers = new Headers({
        'Content-Type': 'application/json'
      });
    }
    return new Promise((resolve, reject) => {
      fetch(`${this.host}/${endpoint}`, reqParams)
        .then(res => res.json())
        .then(data => {
          if (data.message === 'ok')
            resolve();
        })
        .catch(err => {
          reject(err);
        });
    });
  }
}

export default API;
