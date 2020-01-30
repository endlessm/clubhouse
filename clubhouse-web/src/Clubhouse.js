import React from 'react';

class Character extends React.Component {
  render() {
    const charStyles = {
      height: 306 * this.props.scale,
      width: 147 * this.props.scale,
      position: 'fixed',
      top: this.props.pos.top,
      left: this.props.pos.left,
    };

    const className = "Character ada animation";

    return (
      <div className={className} style={charStyles} onClick={this.props.onClick} >
        <div className="tooltip">
          Games
        </div>
      </div>
    );
  }
}

class Clubhouse extends React.Component {
  constructor(props) {
    super(props);
    this.bg = {width: 1304, height: 864};

    this.state = {
        pathways: [
            { character: 'ada', name: 'games' },
        ],
    };
  }

  showPathway(pathway) {
    this.props.app.pathway(pathway);
  }

  render() {
    const scale = window.innerHeight / this.bg.height;
    const posx = (window.innerWidth - (this.bg.width * scale)) / 2;
    const p1 = {left: posx + 200, top: 100 * scale};

    return (
      <div className="Clubhouse">
        { this.state.pathways.map(p =>
            <Character
                key={p.character}
                pathway={p}
                pos={p1}
                scale={scale}
                onClick={this.showPathway.bind(this, p)}/>
        )}
      </div>
    );
  }
}

export default Clubhouse;
