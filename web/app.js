/**
 *
 */
//import React from 'react'; // comment out for production build
import API from './api';

const inputClass = 'b pa2 input-reset ba bg-transparent w-100';
const getButtonClass = (colorClass = 'bg-dark-blue') => `f6 link br1 ph3 pv2 mb2 dib white ${colorClass}`;
const sendButtonClass = getButtonClass();

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      liveText: false,
      textMessage: '',
      imageURL: '',
      lcOptions: {
        onInit: this.onInit.bind(this)
      }
    };
    this.api = new API();
  }

  onInit(lc) {
    this.lc = lc;
  }

  toggleLiveText(e) {
    this.setState({ liveText: !this.state.liveText });
  }

  onMessageChange(e) {
    this.setState({ textMessage: e.target.value }, () => {
      if (this.state.liveText) {
        this.api.sendTextMessage(this.state.textMessage);
      }
    });
  }

  sendMessage(e) {
    this.api.sendTextMessage(this.state.textMessage);
  }

  onimageURLChange(e) {
    this.setState({ imageURL: e.target.value });
  }

  sendImageURL() {
    this.api.sendImageURL(this.state.imageURL);
  }

  sendImage(e) {
    var img = this.lc.getImage().toDataURL();
    this.api.sendImage(img);
  }

  clear() {
    this.api.clear();
  }

  funky() {
    this.api.funky();
  }

  clock() {
    this.api.clock();
  }

  colorMatch() {
    this.api.colorMatch();
  }

  onGifURLChange(e) {
    this.setState({ gifURL: e.target.value });
  }

  sendGifURL() {
    this.api.sendGifURL(this.state.gifURL)
  }

  render() {
    let { liveText, lcOptions } = this.state;
    return (
      <div>

        <div className='pa2'>
          <a className={`${getButtonClass('bg-dark-green')} mr4`} href='#0' onClick={this.clear.bind(this)}>
            Clear
          </a>
          <a className={`${getButtonClass('bg-purple')} mr4`} href='#0' onClick={this.clock.bind(this)}>
            Clock
          </a>
          <a className={getButtonClass('bg-dark-pink')} href='#0' onClick={this.funky.bind(this)}>
            Funky
          </a>
          <a className={getButtonClass('bg-dark-pink')} href='#0' onClick={this.colorMatch.bind(this)}>
           Photo
          </a>
        </div>

        <hr />

        <div>
          <form>
            <fieldset className='bn'>
              <legend className='fw7 mb2'>Text</legend>
              <div className='flex items-center mb2'>
                <label htmlFor='live-text-input' className='lh-copy'>live</label>
                <input id='live-text-input' className='mr2' type='checkbox' onChange={this.toggleLiveText.bind(this)} checked={liveText} />
              </div>
              <div className='mt3'>
                <label className='db fw4 lh-copy f6' htmlFor='msg-input'>message</label>
                <input className={inputClass} type='text' id='msg-input' onChange={this.onMessageChange.bind(this)} />
              </div>
              <div className='mt3'>
                <a onClick={this.sendMessage.bind(this)} className={sendButtonClass} href='#0'>send</a>
              </div>
            </fieldset>
          </form>
        </div>

        <hr />

        <div>
          <form>
            <fieldset className='bn'>
              <legend className='fw7 mb2'>Image URL</legend>
              <div className=''>
                <label className='db fw4 lh-copy f6' htmlFor='img-url-input'>url</label>
                <input className={inputClass} type='text' id='img-url-input' onChange={this.onimageURLChange.bind(this)} />
              </div>
              <div className='mt3'>
                <a onClick={this.sendImageURL.bind(this)} className={sendButtonClass} href='#0'>send</a>
              </div>
            </fieldset>
          </form>
        </div>

        <hr />

        <div>
          <form>
            <fieldset className='bn'>
              <legend className='fw7 mb2'>GIF URL</legend>
              <div className=''>
                <label className='db fw4 lh-copy f6' htmlFor='gif-url-input'>url</label>
                <input className={inputClass} type='text' id='gif-url-input' onChange={this.onGifURLChange.bind(this)} />
              </div>
              <div className='mt3'>
                <a onClick={this.sendGifURL.bind(this)} className={sendButtonClass} href='#0'>send</a>
              </div>
            </fieldset>
          </form>
        </div>

        <hr />

        <div>
          <h4 className='f4'>Draw</h4>
          <LC.LiterallyCanvasReactComponent
            imageURLPrefix='/literallycanvas-0.4.14/img'
            {...lcOptions}
          />
          <div className='mt3'>
            <a onClick={this.sendImage.bind(this)} className={sendButtonClass} href='#0'>send</a>
          </div>
        </div>

      </div>
    );
  }
}

export default App;

