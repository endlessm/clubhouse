import React from 'react';

import Clubhouse from './Clubhouse';
import Pathway from './Pathway';
import Quest from './Quest';

import './App.css';

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = { view: 'clubhouse', pathway: null, quest: null };

    if (window.location.hash) {
      const q = {
        name: 'HTML - Using Colors',
        dificulty: 'easy',
        id: 'htmlintro2',
        url: 'https://codepen.io/madetohack/pen/BaaKggj?editors=1000#code-area',
      };
      this.state = { view: 'quest', quest: q, small: true, };
    }
  }

  pathway(p) {
    this.setState({view: 'pathway', pathway: p});
  }

  clubhouse() {
    this.setState({view: 'clubhouse'});
  }

  openQuest(q) {
    this.setState({view: 'quest', quest: q});
  }

  showHackNews() {
    this.setState({view: 'news'});
  }

  render() {
    const iframeStyles = {
      width: window.innerWidth - 400,
      height: window.innerHeight - 100,
    };

    return (
      <div className="App">
        { this.state.view === 'clubhouse' && <Clubhouse app={this} /> }
        { this.state.view === 'pathway' && <Pathway app={this} pathway={this.state.pathway} /> }
        { this.state.view === 'quest' && <Quest app={this} quest={this.state.quest} small={!!this.state.small} /> }
        { this.state.view === 'news' &&
            <iframe src="https://www.hack-computer.com/blog" style={iframeStyles} title="news">
              <p>Your browser does not support iframes.</p>
            </iframe>
        }

        { !this.state.small &&
          <ul className="Menu">
             { this.state.view !== 'clubhouse' && <li onClick={() => this.clubhouse()}>Clubhouse</li> }
             { this.state.view === 'clubhouse' && <li onClick={() => this.showHackNews()}>Hack News</li> }
          </ul>
        }
      </div>
    );
  }
}

export default App;
